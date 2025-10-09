"""Tournament management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.tournament import Tournament, Player, TournamentPlayer, PlayerScore
from ..models.user import User
from ..schemas.tournament import (
    TournamentResponse,
    TournamentDetailResponse,
    TournamentImportRequest,
    LeaderboardResponse,
    PlayerScoreResponse
)
from ..services.golf_api_service import golf_api
from ..utils.dependencies import get_current_user, require_owner

router = APIRouter(prefix="/api/tournaments", tags=["Tournaments"])


@router.get("", response_model=List[TournamentResponse])
def list_tournaments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tournaments in database.
    Ordered by start date descending (most recent first).
    """
    tournaments = db.query(Tournament).order_by(Tournament.start_date.desc()).all()
    return tournaments


@router.get("/{tournament_id}", response_model=TournamentDetailResponse)
def get_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tournament details including registered players.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Eager load players
    tournament_players = (
        db.query(TournamentPlayer)
        .filter(TournamentPlayer.tournament_id == tournament_id)
        .all()
    )
    
    return tournament


@router.get("/{tournament_id}/leaderboard", response_model=LeaderboardResponse)
def get_tournament_leaderboard(
    tournament_id: UUID,
    round_num: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get leaderboard for a tournament at specific round.
    Defaults to round 4 (final scores).
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    scores = (
        db.query(PlayerScore)
        .filter(
            PlayerScore.tournament_id == tournament_id,
            PlayerScore.round == round_num
        )
        .order_by(PlayerScore.total_score.asc())
        .all()
    )
    
    return {"tournament": tournament, "scores": scores}


@router.post("/import", response_model=TournamentDetailResponse, status_code=status.HTTP_201_CREATED)
async def import_tournament(
    request: TournamentImportRequest,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Import tournament from Golf API.
    Owner only.
    
    Fetches tournament details and player field from API,
    stores tournament, players, and tournament_players records.
    """
    # Check if tournament already exists
    existing = db.query(Tournament).filter(
        Tournament.tourn_id == request.tourn_id,
        Tournament.year == request.year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tournament {request.tourn_id} ({request.year}) already exists"
        )
    
    # Fetch from Golf API
    try:
        api_data = await golf_api.get_tournament(request.tourn_id, request.year)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tournament from Golf API: {str(e)}"
        )
    
    # Extract tournament info (at top level, not nested)
    tourn_name = api_data.get('name')
    players_data = api_data.get('players', [])
    
    if not tourn_name:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid response from Golf API - missing tournament name"
        )
    
    # Create tournament record
    tournament = Tournament(
        tourn_id=request.tourn_id,
        name=tourn_name,
        year=request.year,
        org_id=api_data.get('orgId', 1),
        start_date=None,  # Parse from date object if needed
        end_date=None,
        status=api_data.get('status', 'completed')
    )
    db.add(tournament)
    db.flush()  # Get tournament.id
    
    # Process players
    for player_data in players_data:
        player_id_api = str(player_data.get('playerId'))
        if not player_id_api:
            continue
        
        first_name = player_data.get('firstName', '')
        last_name = player_data.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip()
        
        if not full_name:
            continue  # Skip players without names
        
        # Get or create player
        player = db.query(Player).filter(Player.player_id == player_id_api).first()
        if not player:
            player = Player(
                player_id=player_id_api,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                country=None  # Not provided by this API
            )
            db.add(player)
            db.flush()
        
        # Create tournament_player entry
        tournament_player = TournamentPlayer(
            tournament_id=tournament.id,
            player_id=player.id,
            status=player_data.get('status', 'registered')
        )
        db.add(tournament_player)
    
    db.commit()
    db.refresh(tournament)
    
    return tournament


@router.patch("/{tournament_id}/activate", response_model=TournamentResponse)
def activate_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Set tournament status to 'active' for testing.
    Owner only.
    
    This simulates a tournament being in progress.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    tournament.status = 'active'
    db.commit()
    db.refresh(tournament)
    
    return tournament


@router.patch("/{tournament_id}/complete", response_model=TournamentResponse)
def complete_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):
    """
    Set tournament status to 'completed'.
    Owner only.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    tournament.status = 'completed'
    db.commit()
    db.refresh(tournament)
    
    return tournament

