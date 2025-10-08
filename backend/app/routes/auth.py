"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
from ..utils.auth import hash_password, verify_password, create_access_token
from ..utils.dependencies import get_current_user, require_admin, require_owner, require_league_admin

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
        is_approved=is_primary_owner,  # Auto-approve primary owner
        is_league_admin=is_primary_owner,
        is_owner=is_primary_owner,
        is_primary_owner=is_primary_owner
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if is_primary_owner:
        message = "Account created successfully. You are the primary owner!"
    else:
        message = "Account created successfully. Please wait for owner approval."
    
    return {
        "message": message,
        "user_id": str(new_user.id),
        "email": new_user.email,
        "is_primary_owner": is_primary_owner
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
    
    # Check if user is approved
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )
    
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
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be approved first"
        )
    
    user.is_league_admin = True
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
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be approved first"
        )
    
    user.is_owner = True
    user.is_league_admin = True  # Owners are automatically league admins
    user.is_approved = True
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

