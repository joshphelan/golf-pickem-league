"""Authentication endpoints."""
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.auth import (
    UserCreate, UserLogin, Token, UserResponse,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
)
from ..utils.auth import hash_password, verify_password, create_access_token, generate_reset_token
from ..utils.dependencies import get_current_user, require_owner, require_league_admin
from ..utils.email import send_password_reset_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    First user OR user matching PRIMARY_OWNER_EMAIL becomes primary owner automatically.
    Others must wait for owner approval.
    """
    from ..config import settings
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Determine if this should be the primary owner
    user_count = db.query(User).count()
    is_first_user = (user_count == 0)
    matches_primary_email = (
        settings.PRIMARY_OWNER_EMAIL and 
        user_data.email.lower() == settings.PRIMARY_OWNER_EMAIL.lower()
    )
    is_primary_owner = is_first_user or matches_primary_email
    
    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_approved=True,  # All users can log in (approval no longer required)
        is_league_admin=is_primary_owner,  # Only first user gets league admin
        is_owner=is_primary_owner,  # Only first user gets owner
        is_primary_owner=is_primary_owner  # Only first user is primary owner
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if is_primary_owner:
        message = "Account created successfully. You are the primary owner with full admin access!"
    else:
        message = "Account created successfully. You can log in and join leagues. To create leagues, request admin access from an owner."
    
    return {
        "message": message,
        "user_id": str(new_user.id),
        "email": new_user.email,
        "is_primary_owner": is_primary_owner,
        "is_league_admin": is_primary_owner
    }


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to receive JWT token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Note: Removed is_approved check - users can log in without approval
    # They just can't create leagues until they have is_league_admin = True
    
    # Create access token with permission fields
    access_token = create_access_token(
        data={
            "user_id": str(user.id),
            "email": user.email,
            "is_league_admin": user.is_league_admin,
            "is_owner": user.is_owner,
            "is_primary_owner": user.is_primary_owner
        }
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current user's profile (username only).
    """
    from pydantic import BaseModel, Field

    new_username = update_data.get('username', '').strip()
    if not new_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
    if len(new_username) < 3 or len(new_username) > 50:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be 3–50 characters")

    if new_username != current_user.username:
        existing = db.query(User).filter(User.username == new_username).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        current_user.username = new_username
        db.commit()
        db.refresh(current_user)

    return current_user


# Owner-only endpoints (user management)
@router.get("/admin/users", response_model=List[UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    List all users (owner only).
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.patch("/admin/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Approve a user to access the app (owner only).
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_approved = True
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/users/{user_id}/revoke-access", response_model=UserResponse)
def revoke_user_access(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Revoke user's app access (owner only).
    Cannot revoke primary owner access.
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Protect primary owner
    if user.is_primary_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke primary owner's access"
        )
    
    user.is_approved = False
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/users/{user_id}/grant-league-admin", response_model=UserResponse)
def grant_league_admin(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Grant league admin privileges (can create leagues).
    Owner only.
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove approval check - no longer needed
    # Granting permissions implicitly approves the user
    user.is_league_admin = True
    user.is_approved = True  # Ensure user is approved when granted permissions
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/users/{user_id}/revoke-league-admin", response_model=UserResponse)
def revoke_league_admin(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Revoke league admin privileges.
    Owner only. Cannot revoke from owners or primary owner.
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Protect owners
    if user.is_owner or user.is_primary_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke league admin from owners"
        )
    
    user.is_league_admin = False
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/users/{user_id}/grant-owner", response_model=UserResponse)
def grant_owner_status(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Grant owner privileges (can manage users).
    Owner only.
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove approval check - no longer needed
    # Granting permissions implicitly approves the user
    user.is_owner = True
    user.is_league_admin = True  # Owners are automatically league admins
    user.is_approved = True  # Ensure user is approved when granted permissions
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/users/{user_id}/revoke-owner", response_model=UserResponse)
def revoke_owner_status(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Revoke owner privileges.
    Owner only. Cannot revoke primary owner.
    """
    from uuid import UUID
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Protect primary owner
    if user.is_primary_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke primary owner status"
        )
    
    # Ensure at least one owner remains
    owner_count = db.query(User).filter(User.is_owner == True).count()
    if owner_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke the last owner"
        )
    
    user.is_owner = False
    db.commit()
    db.refresh(user)

    return user


# ── Password reset (unauthenticated) ─────────────────────────────────────────

@router.post("/password-reset/request", response_model=dict)
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request a password reset email.

    Always returns 200 so callers cannot enumerate registered emails.
    If SMTP is not configured the reset link is logged to the server console.
    """
    from ..config import settings

    user = db.query(User).filter(User.email == data.email).first()
    if user:
        token = generate_reset_token()
        user.password_reset_token = token
        user.password_reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        try:
            send_password_reset_email(user.email, reset_link)
        except Exception as exc:
            logger.error(f"Failed to send password reset email to {user.email}: {exc}")

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/password-reset/confirm", response_model=dict)
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Set a new password using a valid reset token.
    The token is cleared after use so it cannot be reused.
    """
    user = db.query(User).filter(User.password_reset_token == data.token).first()

    if not user or user.password_reset_token_expires is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    if datetime.now(timezone.utc) > user.password_reset_token_expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user.hashed_password = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


# ── Change password (authenticated) ──────────────────────────────────────────

@router.patch("/me/password", response_model=dict)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change the current user's password.
    Requires the correct current password.
    """
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password changed successfully."}


# ── Admin: generate reset link without sending email ─────────────────────────

@router.post("/admin/users/{user_id}/generate-reset-link", response_model=dict)
def admin_generate_reset_link(
    user_id: str,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner),
):
    """
    Generate a password reset link for any user (owner only).
    Returns the link directly so the admin can send it manually (Slack, text, etc.)
    Does not send an email.
    """
    from uuid import UUID
    from ..config import settings

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    return {"reset_link": reset_link, "expires_in": "1 hour"}

