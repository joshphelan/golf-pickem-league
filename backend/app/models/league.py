"""League, Team, and TeamPlayer models."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class League(Base):
    """Fantasy league for a tournament."""
    __tablename__ = "leagues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    name = Column(String, nullable=False)
    invite_code = Column(String(8), unique=True, nullable=False, index=True)
    
    max_members = Column(Integer, default=10, nullable=False)
    team_size = Column(Integer, default=4, nullable=False)  # Number of golfers per team
    
    status = Column(String, default='draft', nullable=False)  # 'draft', 'active', 'completed'
    draft_deadline = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tournament = relationship("Tournament", back_populates="leagues")
    admin = relationship("User", back_populates="leagues", foreign_keys=[admin_id])
    teams = relationship("Team", back_populates="league", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('max_members > 0', name='check_max_members_positive'),
        CheckConstraint('team_size > 0', name='check_team_size_positive'),
    )
    
    def __repr__(self):
        return f"<League {self.name} ({self.invite_code})>"


class Team(Base):
    """User's team in a league."""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    team_name = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    league = relationship("League", back_populates="teams")
    user = relationship("User", back_populates="teams")
    team_players = relationship("TeamPlayer", back_populates="team", cascade="all, delete-orphan")
    
    # Constraint: one team per user per league
    __table_args__ = (
        UniqueConstraint('league_id', 'user_id', name='unique_user_per_league'),
    )
    
    def __repr__(self):
        return f"<Team {self.team_name}>"


class TeamPlayer(Base):
    """Players on a team's roster."""
    __tablename__ = "team_players"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamp
    drafted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="team_players")
    player = relationship("Player", back_populates="team_players")
    
    # Constraint: no duplicate players on same team
    __table_args__ = (
        UniqueConstraint('team_id', 'player_id', name='unique_player_per_team'),
    )
    
    def __repr__(self):
        return f"<TeamPlayer team={self.team_id} player={self.player_id}>"

