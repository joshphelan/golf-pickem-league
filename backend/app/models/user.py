"""User model for authentication and authorization."""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class User(Base):
    """User account with approval workflow."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    
    # Permission system (three-tier)
    is_approved = Column(Boolean, default=False, nullable=False)  # Basic app access
    is_league_admin = Column(Boolean, default=False, nullable=False)  # Can create leagues
    is_owner = Column(Boolean, default=False, nullable=False)  # Can manage users
    is_primary_owner = Column(Boolean, default=False, nullable=False)  # App owner (protected)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teams = relationship("Team", back_populates="user", cascade="all, delete-orphan")
    leagues = relationship("League", back_populates="admin", foreign_keys="League.admin_id")
    
    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

