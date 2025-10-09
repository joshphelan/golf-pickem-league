"""FastAPI dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..database import get_db
from ..models.user import User
from .auth import decode_access_token

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account pending approval"
        )
    
    return user


def require_league_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require that the current user is a league admin (can create leagues).
    
    Raises:
        HTTPException: If user is not a league admin or owner
    """
    if not (current_user.is_league_admin or current_user.is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="League admin privileges required"
        )
    return current_user


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """
    Require that the current user is an owner (can manage users).
    
    Raises:
        HTTPException: If user is not an owner
    """
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner privileges required"
        )
    return current_user


def require_primary_owner(current_user: User = Depends(get_current_user)) -> User:
    """
    Require that the current user is the primary owner.
    
    Raises:
        HTTPException: If user is not the primary owner
    """
    if not current_user.is_primary_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Primary owner privileges required"
        )
    return current_user



