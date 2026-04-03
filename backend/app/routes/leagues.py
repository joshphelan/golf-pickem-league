"""League management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
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
    LeagueDetailResponse,
    LeagueUpdate,
    LeagueCommentCreate,
    LeagueCommentResponse,
)
from ..utils.dependencies import get_current_user, require_league_admin
from ..services.scoring_service import calculate_league_standings
from ..models.league import LeagueComment

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
    
    # REMOVED: Auto-refresh players block
    # Users can click "Refresh Players" button instead
    # Scheduler handles automatic refresh for upcoming tournaments
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
        scoring_count=league_data.scoring_count,
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


@router.get("/my-leagues", response_model=List[LeagueDetailResponse])
def get_my_leagues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all leagues the current user is a member of.
    Note: This must come BEFORE /{league_id} route to avoid path conflicts.
    Returns leagues sorted by tournament status (active first, then upcoming, then completed).
    """
    # Get leagues where user has a team
    teams = db.query(Team).filter(Team.user_id == current_user.id).all()
    league_ids = [team.league_id for team in teams]

    if not league_ids:
        return []

    leagues = db.query(League).filter(League.id.in_(league_ids)).all()

    result = []
    for league in leagues:
        member_count = db.query(Team).filter(Team.league_id == league.id).count()
        league_dict = LeagueDetailResponse.model_validate(league).model_dump()
        league_dict['tournament'] = league.tournament
        league_dict['member_count'] = member_count
        result.append(league_dict)

    # Sort by tournament status priority: active > upcoming > completed
    def get_sort_key(league_dict):
        status_order = {'active': 0, 'in_progress': 0, 'upcoming': 1, 'completed': 2}
        tournament = league_dict.get('tournament')
        if tournament:
            status = tournament.status if hasattr(tournament, 'status') else tournament.get('status', 'completed')
            start = tournament.start_date if hasattr(tournament, 'start_date') else tournament.get('start_date', '9999')
            return (status_order.get(status, 2), str(start) if start else '9999')
        return (2, '9999')

    result.sort(key=get_sort_key)

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


@router.post("/join/{invite_code}")
def join_league(
    invite_code: str,
    team_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join a league via invite code.
    Creates a team for the user in the league.
    If no team_name provided, auto-generates one.
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
    
    # Auto-generate team name if not provided
    if not team_name:
        team_name = f"{current_user.username}'s Team"
    
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
    
    team_dict = {
        'id': str(team.id),
        'league_id': str(team.league_id),
        'user_id': str(team.user_id),
        'team_name': team.team_name,
        'created_at': team.created_at.isoformat()
    }
    
    return {'league': league_dict, 'team': team_dict}


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
    round_num: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get league standings with team scores.

    Returns teams ranked by total score (lowest wins).
    Includes player-by-player breakdown for each team.

    Query params:
    - round_num: Which round to get scores for (default: auto-detect latest)
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
    
    # Calculate standings (auto-detects latest round if round_num is None)
    standings = calculate_league_standings(league_id, db, round_num)

    # Get current round info from the tournament
    from sqlalchemy import func
    from ..models.tournament import PlayerScore

    current_round = db.query(func.max(PlayerScore.round)).filter(
        PlayerScore.tournament_id == league.tournament_id
    ).scalar() or 0

    last_score_sync = db.query(func.max(PlayerScore.updated_at)).filter(
        PlayerScore.tournament_id == league.tournament_id
    ).scalar()

    tournament = league.tournament

    return {
        "league_id": str(league_id),
        "league_name": league.name,
        "current_round": current_round,
        "last_score_sync": last_score_sync.isoformat() if last_score_sync else None,
        "tournament": {
            "id": str(tournament.id),
            "name": tournament.name,
            "status": tournament.status,
            "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
            "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
        } if tournament else None,
        "standings": standings
    }


@router.patch("/{league_id}", response_model=LeagueDetailResponse)
def update_league(
    league_id: UUID,
    update_data: LeagueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update league settings (draft deadline).
    League admin or app owner only.
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")

    if league.admin_id != current_user.id and not current_user.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the league admin can update this league")

    if update_data.draft_deadline is not None:
        league.draft_deadline = update_data.draft_deadline

    db.commit()
    db.refresh(league)

    member_count = db.query(Team).filter(Team.league_id == league_id).count()
    league_dict = LeagueDetailResponse.model_validate(league).model_dump()
    league_dict['tournament'] = league.tournament
    league_dict['member_count'] = member_count
    return league_dict


@router.get("/{league_id}/comments", response_model=List[LeagueCommentResponse])
def get_league_comments(
    league_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments for a league. Must be a member."""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")

    is_member = db.query(Team).filter(
        Team.league_id == league_id,
        Team.user_id == current_user.id
    ).first()
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this league")

    comments = db.query(LeagueComment).filter(
        LeagueComment.league_id == league_id
    ).order_by(LeagueComment.created_at.asc()).all()

    return [
        {
            "id": c.id,
            "league_id": c.league_id,
            "user_id": c.user_id,
            "username": c.user.username if c.user else "Unknown",
            "content": c.content,
            "created_at": c.created_at,
        }
        for c in comments
    ]


@router.post("/{league_id}/comments", response_model=LeagueCommentResponse, status_code=status.HTTP_201_CREATED)
def post_league_comment(
    league_id: UUID,
    comment_data: LeagueCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post a comment to a league chat. Must be a member."""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")

    is_member = db.query(Team).filter(
        Team.league_id == league_id,
        Team.user_id == current_user.id
    ).first()
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this league")

    comment = LeagueComment(
        league_id=league_id,
        user_id=current_user.id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "league_id": comment.league_id,
        "user_id": comment.user_id,
        "username": current_user.username,
        "content": comment.content,
        "created_at": comment.created_at,
    }


@router.delete("/{league_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league_comment(
    league_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment. Own comment or league admin only."""
    comment = db.query(LeagueComment).filter(
        LeagueComment.id == comment_id,
        LeagueComment.league_id == league_id
    ).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    league = db.query(League).filter(League.id == league_id).first()
    is_admin = league and (league.admin_id == current_user.id or current_user.is_owner)

    if comment.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this comment")

    db.delete(comment)
    db.commit()

