"""Team and player draft endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from ..database import get_db
from ..models.league import League, Team, TeamPlayer
from ..models.tournament import Player, TournamentPlayer, PlayerScore
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
    
    # Calculate team score (auto-detects latest round)
    total_score = calculate_team_score(team_id, db)
    
    # Build response with scores
    players_with_scores = []
    
    # Get tournament to fetch scores (if available)
    tournament_id = None
    league = team.league
    try:
        tournament_id = league.tournament_id
    except Exception:
        pass  # No tournament associated yet
    
    for tp in team_players:
        player_dict = {
            'id': str(tp.id),
            'team_id': str(tp.team_id),
            'player_id': str(tp.player_id),
            'drafted_at': tp.drafted_at.isoformat(),
            'player': {
                'id': str(tp.player.id),
                'player_id': tp.player.player_id,
                'first_name': tp.player.first_name,
                'last_name': tp.player.last_name,
                'full_name': tp.player.full_name,
                'country': tp.player.country,
                'created_at': tp.player.created_at.isoformat()
            }
        }
        
        # Fetch scores for this player in this tournament (if tournament exists)
        if tournament_id:
            try:
                scores = db.query(PlayerScore).filter(
                    PlayerScore.tournament_id == tournament_id,
                    PlayerScore.player_id == tp.player_id
                ).all()
                
                # Organize scores by round (use round_score for per-round, not cumulative)
                scores_dict = {}
                for score in scores:
                    if score.round == 1:
                        scores_dict['round_1'] = score.round_score
                    elif score.round == 2:
                        scores_dict['round_2'] = score.round_score
                    elif score.round == 3:
                        scores_dict['round_3'] = score.round_score
                    elif score.round == 4:
                        scores_dict['round_4'] = score.round_score
                
                # Get final total score (round 4 if available)
                final_score = None
                if scores:
                    last_score = max(scores, key=lambda s: s.round)
                    final_score = last_score.total_score
                
                if scores_dict or final_score is not None:
                    player_dict['scores'] = {
                        'round_1': scores_dict.get('round_1'),
                        'round_2': scores_dict.get('round_2'),
                        'round_3': scores_dict.get('round_3'),
                        'round_4': scores_dict.get('round_4'),
                        'total_score': final_score
                    }
            except Exception:
                pass  # If score fetching fails, just skip scores
        
        players_with_scores.append(player_dict)
    
    # Get actual last score sync time from DB
    last_score_sync = None
    if tournament_id:
        last_score_sync = db.query(func.max(PlayerScore.updated_at)).filter(
            PlayerScore.tournament_id == tournament_id
        ).scalar()

    team_dict = TeamDetailResponse.model_validate(team).model_dump()
    team_dict['players'] = players_with_scores
    team_dict['total_score'] = total_score
    team_dict['team_size'] = league.team_size
    team_dict['last_score_sync'] = last_score_sync.isoformat() if last_score_sync else None

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
    
    # Check if player already on this team
    existing_pick = db.query(TeamPlayer).filter(
        and_(
            TeamPlayer.team_id == team_id,
            TeamPlayer.player_id == player_data.player_id
        )
    ).first()

    if existing_pick:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already on your team"
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
    
    # Return updated team using the same logic as get_team
    return get_team(team_id, db, current_user)


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
    
    # Return updated team using the same logic as get_team
    return get_team(team_id, db, current_user)


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

    # Only exclude players already on THIS team (other teams can pick the same player)
    this_team_picks = db.query(TeamPlayer).filter(
        TeamPlayer.team_id == team_id
    ).all()

    this_team_player_ids = {tp.player_id for tp in this_team_picks}

    # Get available players (registered for tournament, not already on this team)
    available_player_ids = [
        pid for pid in tournament_player_ids
        if pid not in this_team_player_ids
    ]

    available_players = db.query(Player).filter(
        Player.id.in_(available_player_ids)
    ).order_by(Player.last_name).all()

    return available_players

