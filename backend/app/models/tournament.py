"""Tournament, Player, and Scoring models."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Tournament(Base):
    """PGA Tour tournament."""
    __tablename__ = "tournaments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tourn_id = Column(String, unique=True, nullable=False, index=True)  # From Free Golf API
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    org_id = Column(Integer, default=1)  # 1 = PGA Tour
    
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default='upcoming')  # 'upcoming', 'active', 'completed'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    leagues = relationship("League", back_populates="tournament", cascade="all, delete-orphan")
    player_scores = relationship("PlayerScore", back_populates="tournament", cascade="all, delete-orphan")
    tournament_players = relationship("TournamentPlayer", back_populates="tournament", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tournament {self.name} ({self.year})>"


class Player(Base):
    """PGA Tour player."""
    __tablename__ = "players"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(String, unique=True, nullable=False, index=True)  # From Free Golf API
    first_name = Column(String)
    last_name = Column(String)
    full_name = Column(String, nullable=False)
    country = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team_players = relationship("TeamPlayer", back_populates="player", cascade="all, delete-orphan")
    scores = relationship("PlayerScore", back_populates="player", cascade="all, delete-orphan")
    tournament_players = relationship("TournamentPlayer", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player {self.full_name}>"


class TournamentPlayer(Base):
    """Players registered for a specific tournament."""
    __tablename__ = "tournament_players"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    # Player status in tournament
    status = Column(String, default='registered')  # 'registered', 'withdrawn', 'missed_cut', 'active', 'completed'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="tournament_players")
    player = relationship("Player", back_populates="tournament_players")
    
    # Unique constraint: player can only be registered once per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'player_id', name='unique_player_per_tournament'),
    )
    
    def __repr__(self):
        return f"<TournamentPlayer {self.player_id} in {self.tournament_id}>"


class PlayerScore(Base):
    """Player's score in a tournament round."""
    __tablename__ = "player_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    round = Column(Integer, nullable=False)  # 1, 2, 3, 4
    round_score = Column(Integer)  # Score for this specific round
    total_score = Column(Integer)  # Running total (e.g., -7)
    position = Column(Integer)
    made_cut = Column(Boolean, default=True)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    tournament = relationship("Tournament", back_populates="player_scores")
    player = relationship("Player", back_populates="scores")
    
    # Unique constraint: one score per player per tournament per round
    __table_args__ = (
        UniqueConstraint('tournament_id', 'player_id', 'round', name='unique_player_tournament_round'),
    )
    
    def __repr__(self):
        return f"<PlayerScore {self.player_id} Round {self.round}: {self.total_score}>"

