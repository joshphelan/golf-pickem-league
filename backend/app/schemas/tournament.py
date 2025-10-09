"""Pydantic schemas for tournaments and players."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class PlayerBase(BaseModel):
    """Base player schema."""
    player_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    country: Optional[str] = None


class PlayerResponse(PlayerBase):
    """Player response schema."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TournamentPlayerResponse(BaseModel):
    """Tournament player with status."""
    id: UUID
    tournament_id: UUID
    player_id: UUID
    player: PlayerResponse
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TournamentBase(BaseModel):
    """Base tournament schema."""
    tourn_id: str
    name: str
    year: int
    org_id: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = 'upcoming'


class TournamentCreate(TournamentBase):
    """Schema for creating tournament."""
    pass


class TournamentResponse(TournamentBase):
    """Tournament response schema."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TournamentDetailResponse(TournamentResponse):
    """Tournament with players."""
    players: List[TournamentPlayerResponse] = []
    
    class Config:
        from_attributes = True


class TournamentImportRequest(BaseModel):
    """Request to import tournament from Golf API."""
    tourn_id: str
    year: int


class PlayerScoreResponse(BaseModel):
    """Player score in tournament."""
    id: UUID
    tournament_id: UUID
    player_id: UUID
    player: PlayerResponse
    round: int
    round_score: Optional[int] = None
    total_score: Optional[int] = None
    position: Optional[int] = None
    made_cut: bool = True
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Tournament leaderboard."""
    tournament: TournamentResponse
    scores: List[PlayerScoreResponse]

