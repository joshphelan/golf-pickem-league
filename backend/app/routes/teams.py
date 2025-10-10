"""Team and player draft endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from ..database import get_db
from ..models.league import League, Team, TeamPlayer
from ..models.tournament import Player, TournamentPlayer
from ..models.user import User
from ..schemas.league import (
    TeamDetailResponse,
    AddPlayerToTeam,
    TeamPlayerResponse
)
from ..schemas.tournament import PlayerResponse
from ..utils.dependencies import get_current_user
from ..services.scoring_service import calculate_team_score

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.get("/{team_id}", response_model=TeamDetailResponse)
def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get team details with players.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has access (member of league or owner)
    is_member = db.query(Team).filter(
        Team.league_id == team.league_id,
        Team.user_id == current_user.id
    ).first()
    
    if not is_member and not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this team"
        )
    
    # Get team players
    team_players = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).all()
    
    # Calculate team score (final round by default)
    total_score = calculate_team_score(team_id, db, round_num=4)
    
    team_dict = TeamDetailResponse.model_validate(team).model_dump()
    team_dict['players'] = team_players
    team_dict['total_score'] = total_score
    
    return team_dict


@router.post("/{team_id}/players", response_model=TeamDetailResponse, status_code=status.HTTP_201_CREATED)
def add_player_to_team(
    team_id: UUID,
    player_data: AddPlayerToTeam,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a player to your team (draft).
    
    Validates:
    - User owns the team
    - Draft deadline not passed
    - Player is registered for tournament
    - Player not already drafted in league
    - Team not full
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check ownership
    if team.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own team"
        )
    
    league = team.league
    
    # Check draft deadline
    if datetime.now(timezone.utc) > league.draft_deadline.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft deadline has passed"
        )
    
    # Check if player exists
    player = db.query(Player).filter(Player.id == player_data.player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Check if player is registered for the tournament
    tournament_player = db.query(TournamentPlayer).filter(
        and_(
            TournamentPlayer.tournament_id == league.tournament_id,
            TournamentPlayer.player_id == player_data.player_id
        )
    ).first()
    
    if not tournament_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is not registered for this tournament"
        )
    
    # Check if player already drafted in this league
    teams_in_league = db.query(Team).filter(Team.league_id == league.id).all()
    team_ids = [t.id for t in teams_in_league]
    
    existing_draft = db.query(TeamPlayer).filter(
        and_(
            TeamPlayer.team_id.in_(team_ids),
            TeamPlayer.player_id == player_data.player_id
        )
    ).first()
    
    if existing_draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player already drafted by another team in this league"
        )
    
    # Check team size limit
    current_player_count = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).count()
    if current_player_count >= league.team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is full (max {league.team_size} players)"
        )
    
    # Add player to team
    team_player = TeamPlayer(
        team_id=team_id,
        player_id=player_data.player_id
    )
    db.add(team_player)
    db.commit()
    
    # Return updated team
    team_players = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).all()
    team_dict = TeamDetailResponse.model_validate(team).model_dump()
    team_dict['players'] = team_players
    team_dict['total_score'] = None
    
    return team_dict


@router.delete("/{team_id}/players/{player_id}", response_model=TeamDetailResponse)
def remove_player_from_team(
    team_id: UUID,
    player_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a player from your team.
    Only allowed before draft deadline.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check ownership
    if team.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own team"
        )
    
    league = team.league
    
    # Check draft deadline
    if datetime.now(timezone.utc) > league.draft_deadline.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Draft deadline has passed"
        )
    
    # Find and remove team player
    team_player = db.query(TeamPlayer).filter(
        and_(
            TeamPlayer.team_id == team_id,
            TeamPlayer.player_id == player_id
        )
    ).first()
    
    if not team_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not on this team"
        )
    
    db.delete(team_player)
    db.commit()
    
    # Return updated team
    team_players = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).all()
    team_dict = TeamDetailResponse.model_validate(team).model_dump()
    team_dict['players'] = team_players
    team_dict['total_score'] = None
    
    return team_dict


@router.get("/{team_id}/available-players", response_model=List[PlayerResponse])
def get_available_players(
    team_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of players available to draft for this team.
    
    Returns players who:
    - Are registered for the tournament
    - Have not been drafted in this league yet
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has access
    is_member = db.query(Team).filter(
        Team.league_id == team.league_id,
        Team.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this league"
        )
    
    league = team.league
    
    # Get all players registered for the tournament
    tournament_players = db.query(TournamentPlayer).filter(
        TournamentPlayer.tournament_id == league.tournament_id
    ).all()
    
    tournament_player_ids = [tp.player_id for tp in tournament_players]
    
    # Get already drafted players in this league
    teams_in_league = db.query(Team).filter(Team.league_id == league.id).all()
    team_ids = [t.id for t in teams_in_league]
    
    drafted_players = db.query(TeamPlayer).filter(
        TeamPlayer.team_id.in_(team_ids)
    ).all()
    
    drafted_player_ids = [tp.player_id for tp in drafted_players]
    
    # Get available players (registered but not drafted)
    available_player_ids = [
        pid for pid in tournament_player_ids
        if pid not in drafted_player_ids
    ]
    
    available_players = db.query(Player).filter(
        Player.id.in_(available_player_ids)
    ).order_by(Player.last_name).all()
    
    return available_players

