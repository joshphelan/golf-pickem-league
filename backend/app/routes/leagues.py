"""League management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import secrets
import string

from ..database import get_db
from ..models.league import League, Team
from ..models.tournament import Tournament
from ..models.user import User
from ..schemas.league import (
    LeagueCreate,
    LeagueResponse,
    LeagueDetailResponse
)
from ..utils.dependencies import get_current_user, require_league_admin
from ..services.scoring_service import calculate_league_standings

router = APIRouter(prefix="/api/leagues", tags=["Leagues"])


def generate_invite_code() -> str:
    """Generate random 8-character alphanumeric invite code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


@router.post("", response_model=LeagueDetailResponse, status_code=status.HTTP_201_CREATED)
def create_league(
    league_data: LeagueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_league_admin)
):
    """
    Create a new league.
    League admin or owner only.
    
    Generates unique invite code and creates league for specified tournament.
    """
    # Verify tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == league_data.tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Can't create league for completed tournaments
    # NOTE: Temporarily disabled for testing with historical data
    # if tournament.status == 'completed':
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot create league for completed tournament"
    #     )
    
    # Generate unique invite code
    invite_code = generate_invite_code()
    while db.query(League).filter(League.invite_code == invite_code).first():
        invite_code = generate_invite_code()
    
    # Create league
    league = League(
        tournament_id=league_data.tournament_id,
        admin_id=current_user.id,
        name=league_data.name,
        invite_code=invite_code,
        max_members=league_data.max_members,
        team_size=league_data.team_size,
        draft_deadline=league_data.draft_deadline,
        status='draft'
    )
    db.add(league)
    db.commit()
    db.refresh(league)
    
    # Create team for creator
    team = Team(
        league_id=league.id,
        user_id=current_user.id,
        team_name=f"{current_user.username}'s Team"
    )
    db.add(team)
    db.commit()
    
    # Prepare response
    league_dict = LeagueDetailResponse.model_validate(league).model_dump()
    league_dict['tournament'] = tournament
    league_dict['member_count'] = 1
    
    return league_dict


@router.get("", response_model=List[LeagueDetailResponse])
def list_my_leagues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all leagues the current user is a member of.
    """
    # Get leagues where user has a team
    teams = db.query(Team).filter(Team.user_id == current_user.id).all()
    league_ids = [team.league_id for team in teams]
    
    leagues = db.query(League).filter(League.id.in_(league_ids)).all()
    
    result = []
    for league in leagues:
        member_count = db.query(Team).filter(Team.league_id == league.id).count()
        league_dict = LeagueDetailResponse.model_validate(league).model_dump()
        league_dict['tournament'] = league.tournament
        league_dict['member_count'] = member_count
        result.append(league_dict)
    
    return result


@router.get("/{league_id}", response_model=LeagueDetailResponse)
def get_league(
    league_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get league details.
    Must be a member of the league.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    # Check if user is a member
    is_member = db.query(Team).filter(
        Team.league_id == league_id,
        Team.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this league"
        )
    
    member_count = db.query(Team).filter(Team.league_id == league_id).count()
    
    league_dict = LeagueDetailResponse.model_validate(league).model_dump()
    league_dict['tournament'] = league.tournament
    league_dict['member_count'] = member_count
    
    return league_dict


@router.post("/join/{invite_code}", response_model=LeagueDetailResponse)
def join_league(
    invite_code: str,
    team_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join a league via invite code.
    Creates a team for the user in the league.
    """
    # Find league by invite code
    league = db.query(League).filter(League.invite_code == invite_code.upper()).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )
    
    # Check if already a member
    existing_team = db.query(Team).filter(
        Team.league_id == league.id,
        Team.user_id == current_user.id
    ).first()
    
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this league"
        )
    
    # Check if league is full
    member_count = db.query(Team).filter(Team.league_id == league.id).count()
    if member_count >= league.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is full"
        )
    
    # Create team
    team = Team(
        league_id=league.id,
        user_id=current_user.id,
        team_name=team_name
    )
    db.add(team)
    db.commit()
    
    member_count += 1
    
    league_dict = LeagueDetailResponse.model_validate(league).model_dump()
    league_dict['tournament'] = league.tournament
    league_dict['member_count'] = member_count
    
    return league_dict


@router.get("/{league_id}/members", response_model=List[dict])
def get_league_members(
    league_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all members (teams) in a league.
    Must be a member of the league.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    # Check if user is a member
    is_member = db.query(Team).filter(
        Team.league_id == league_id,
        Team.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this league"
        )
    
    teams = db.query(Team).filter(Team.league_id == league_id).all()
    
    result = []
    for team in teams:
        result.append({
            "team_id": team.id,
            "team_name": team.team_name,
            "user_id": team.user_id,
            "username": team.user.username,
            "created_at": team.created_at
        })
    
    return result


@router.get("/{league_id}/standings")
def get_league_standings(
    league_id: UUID,
    round_num: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get league standings with team scores.
    
    Returns teams ranked by total score (lowest wins).
    Includes player-by-player breakdown for each team.
    
    Query params:
    - round_num: Which round to get scores for (default: 4 = final)
    """
    # Verify league exists
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    # Check if user is member
    user_team = db.query(Team).filter(
        Team.league_id == league_id,
        Team.user_id == current_user.id
    ).first()
    
    if not user_team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this league"
        )
    
    # Calculate standings
    standings = calculate_league_standings(league_id, db, round_num)
    
    return {
        "league_id": str(league_id),
        "league_name": league.name,
        "round": round_num,
        "standings": standings
    }

