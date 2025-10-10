"""Pydantic schemas for leagues and teams."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID

from .tournament import TournamentResponse, PlayerResponse


class LeagueCreate(BaseModel):
    """Schema for creating a league."""
    tournament_id: UUID
    name: str = Field(..., min_length=3, max_length=100)
    max_members: int = Field(default=10, ge=2, le=50)
    team_size: int = Field(default=4, ge=1, le=10)
    draft_deadline: datetime
    
    @field_validator('draft_deadline')
    @classmethod
    def validate_draft_deadline(cls, v):
        """Ensure draft deadline is in the future."""
        if v < datetime.now(timezone.utc):
            raise ValueError('Draft deadline must be in the future')
        return v


class LeagueResponse(BaseModel):
    """League response schema."""
    id: UUID
    tournament_id: UUID
    admin_id: Optional[UUID] = None
    name: str
    invite_code: str
    max_members: int
    team_size: int
    status: str
    draft_deadline: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LeagueDetailResponse(LeagueResponse):
    """League with tournament and member count."""
    tournament: TournamentResponse
    member_count: int = 0
    
    class Config:
        from_attributes = True


class TeamPlayerResponse(BaseModel):
    """Player on a team."""
    id: UUID
    team_id: UUID
    player_id: UUID
    player: PlayerResponse
    drafted_at: datetime
    
    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Team response schema."""
    id: UUID
    league_id: UUID
    user_id: UUID
    team_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    """Team with players and current score."""
    players: List[TeamPlayerResponse] = []
    total_score: Optional[int] = None
    
    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    """Schema for creating a team."""
    league_id: UUID
    team_name: str = Field(..., min_length=3, max_length=50)


class AddPlayerToTeam(BaseModel):
    """Schema for adding player to team."""
    player_id: UUID

