"""Tournament management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.tournament import Tournament, Player, TournamentPlayer, PlayerScore
from ..models.league import Team
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
from ..utils.date_parser import parse_api_dates
from ..utils.tournament_status import determine_tournament_status
from ..utils.score_converter import parse_golf_score

router = APIRouter(prefix="/api/tournaments", tags=["Tournaments"])


@router.get("", response_model=List[TournamentResponse])
def list_tournaments(
    db: Session = Depends(get_db)
):
    """
    List all tournaments in database.
    Ordered by start date ascending (upcoming first).
    No authentication required - used by frontend tournament dropdown.
    """
    tournaments = db.query(Tournament).order_by(Tournament.start_date.asc()).all()
    return tournaments


@router.get("/active/live")
def get_live_tournament(
    db: Session = Depends(get_db)
):
    """
    Get the currently active tournament with leaderboard summary.
    Returns None if no tournament is active.
    Used for the live tournament panel on dashboard.
    """
    from sqlalchemy import func

    # Find active tournament
    tournament = db.query(Tournament).filter(
        Tournament.status.in_(['active', 'in_progress'])
    ).order_by(Tournament.start_date.desc()).first()

    if not tournament:
        return {"tournament": None, "leaderboard": [], "current_round": 0}

    # Get current round
    current_round = db.query(func.max(PlayerScore.round)).filter(
        PlayerScore.tournament_id == tournament.id
    ).scalar() or 0

    # Get top 10 leaderboard
    leaderboard = []
    if current_round > 0:
        scores = (
            db.query(PlayerScore)
            .filter(
                PlayerScore.tournament_id == tournament.id,
                PlayerScore.round == current_round
            )
            .order_by(PlayerScore.total_score.asc())
            .limit(10)
            .all()
        )

        for score in scores:
            leaderboard.append({
                "position": score.position,
                "player_name": score.player.full_name if score.player else "Unknown",
                "total_score": score.total_score,
                "made_cut": score.made_cut
            })

    last_score_sync = db.query(func.max(PlayerScore.updated_at)).filter(
        PlayerScore.tournament_id == tournament.id
    ).scalar()

    return {
        "tournament": {
            "id": str(tournament.id),
            "name": tournament.name,
            "status": tournament.status,
            "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
            "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
        },
        "current_round": current_round,
        "last_score_sync": last_score_sync.isoformat() if last_score_sync else None,
        "leaderboard": leaderboard
    }


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


@router.get("/{tournament_id}/available-players")
async def get_available_players(
    tournament_id: UUID,
    league_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get list of players available to draft in a league for this tournament.
    
    Returns players who:
    - Are registered for the tournament
    - Have not been drafted in this league yet
    """
    from ..models.tournament import Player, TournamentPlayer
    from ..models.league import League, TeamPlayer
    
    # Verify tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Verify league exists
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    
    # Get all players in this tournament
    tournament_players = (
        db.query(TournamentPlayer)
        .filter(TournamentPlayer.tournament_id == tournament_id)
        .all()
    )
    
    # Get IDs of players already drafted in this league
    drafted_player_ids = (
        db.query(TeamPlayer.player_id)
        .join(Team)
        .filter(Team.league_id == league_id)
        .all()
    )
    drafted_ids = [str(p[0]) for p in drafted_player_ids]
    
    # Filter out drafted players
    available = []
    for tp in tournament_players:
        if str(tp.player_id) not in drafted_ids:
            player = tp.player
            available.append({
                'id': str(player.id),
                'player_id': player.player_id,
                'first_name': player.first_name,
                'last_name': player.last_name,
                'full_name': player.full_name,
                'is_amateur': False  # Can add this field to Player model if needed
            })
    
    return available


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
    db: Session = Depends(get_db)
):
    """
    Import tournament from Golf API.
    System function - no authentication required.
    
    Fetches tournament details and player field from API,
    stores tournament, players, and tournament_players records.
    Called by automated scheduler or for manual testing.
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
    
    # Parse dates from API
    start_date, end_date = parse_api_dates(api_data)
    
    # Auto-detect status based on dates
    initial_status = api_data.get('status', 'upcoming')
    tournament_status = determine_tournament_status(start_date, end_date, initial_status)
    
    # Extract timezone
    timezone = api_data.get('timeZone', 'America/New_York')
    
    # Create tournament record
    tournament = Tournament(
        tourn_id=request.tourn_id,
        name=tourn_name,
        year=request.year,
        org_id=api_data.get('orgId', 1),
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        status=tournament_status
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


@router.post("/admin/import-tournaments")
async def admin_import_tournaments(owner: User = Depends(require_owner)):
    """Manually trigger tournament import (owner only)."""
    from ..scheduler import _import_upcoming_tournaments_async
    await _import_upcoming_tournaments_async()
    return {"message": "Tournament import complete"}


@router.post("/{tournament_id}/sync-scores", response_model=TournamentResponse)
async def sync_tournament_scores(
    tournament_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Sync scores from Golf API leaderboard.
    Owner only.
    
    Fetches latest scores from /leaderboard endpoint and updates PlayerScore records.
    Also updates tournament status based on dates.
    """
    # Get tournament
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Update status based on dates
    new_status = determine_tournament_status(
        tournament.start_date,
        tournament.end_date,
        tournament.status
    )
    if new_status != tournament.status:
        tournament.status = new_status
        db.commit()
    
    # Fetch leaderboard from API
    try:
        leaderboard_data = await golf_api.get_leaderboard(
            tournament.tourn_id,
            tournament.year,
            tournament.org_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard from Golf API: {str(e)}"
        )
    
    # Extract leaderboard rows
    leaderboard_rows = leaderboard_data.get('leaderboardRows', [])
    if not leaderboard_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No leaderboard data available for this tournament"
        )
    
    # Get current round from API
    current_round = leaderboard_data.get('roundId', 4)
    if isinstance(current_round, dict):
        current_round = int(current_round.get('$numberInt', 4))
    
    scores_updated = 0
    scores_created = 0
    
    # Process each player's score
    for row in leaderboard_rows:
        player_id_api = str(row.get('playerId'))
        if not player_id_api:
            continue
        
        # Find player in database
        player = db.query(Player).filter(Player.player_id == player_id_api).first()
        if not player:
            # Player not in our database yet (not imported with tournament)
            continue
        
        # Parse position and status (same for all rounds)
        position_str = row.get('position', '')
        try:
            position = int(position_str.replace('T', ''))
        except (ValueError, AttributeError):
            position = None
        
        player_status = row.get('status', '')
        made_cut = player_status not in ['CUT', 'WD', 'WITHDRAWN']
        
        # Parse rounds array to get per-round scores
        rounds = row.get('rounds', [])
        if not rounds:
            # Fallback: use top-level total for current round only
            total_score_str = row.get('total', 'E')
            total_score = parse_golf_score(total_score_str)
            
            if total_score is not None:
                existing_score = db.query(PlayerScore).filter(
                    PlayerScore.tournament_id == tournament.id,
                    PlayerScore.player_id == player.id,
                    PlayerScore.round == current_round
                ).first()
                
                if existing_score:
                    existing_score.total_score = total_score
                    existing_score.position = position
                    existing_score.made_cut = made_cut
                    scores_updated += 1
                else:
                    new_score = PlayerScore(
                        tournament_id=tournament.id,
                        player_id=player.id,
                        round=current_round,
                        total_score=total_score,
                        position=position,
                        made_cut=made_cut
                    )
                    db.add(new_score)
                    scores_created += 1
            continue
        
        # Process each round and calculate cumulative scores
        cumulative_score = 0
        for round_data in rounds:
            round_num = round_data.get('roundId')
            
            # Parse roundId if it's in MongoDB format
            if isinstance(round_num, dict):
                round_num = int(round_num.get('$numberInt', 0))
            elif round_num is not None:
                round_num = int(round_num)
            
            score_to_par_str = round_data.get('scoreToPar', 'E')
            round_score = parse_golf_score(score_to_par_str)
            
            if round_num is None or round_num == 0 or round_score is None:
                continue
            
            # Add this round's score to cumulative total
            cumulative_score += round_score
            
            # Upsert score record for this round
            existing_score = db.query(PlayerScore).filter(
                PlayerScore.tournament_id == tournament.id,
                PlayerScore.player_id == player.id,
                PlayerScore.round == round_num
            ).first()
            
            if existing_score:
                existing_score.round_score = round_score
                existing_score.total_score = cumulative_score
                existing_score.position = position
                existing_score.made_cut = made_cut
                scores_updated += 1
            else:
                new_score = PlayerScore(
                    tournament_id=tournament.id,
                    player_id=player.id,
                    round=round_num,
                    round_score=round_score,
                    total_score=cumulative_score,
                    position=position,
                    made_cut=made_cut
                )
                db.add(new_score)
                scores_created += 1
    
    db.commit()
    db.refresh(tournament)
    
    # Log sync result
    print(f"Synced scores for tournament {tournament.name}: {scores_created} created, {scores_updated} updated")
    
    return tournament


@router.post("/{tournament_id}/refresh-players")
async def refresh_tournament_players(
    tournament_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refresh player field for a tournament.
    For upcoming tournaments: calls /tournament endpoint
    For active/completed tournaments: calls /leaderboard endpoint
    """
    from datetime import datetime
    
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    try:
        if tournament.status == 'upcoming':
            # Use /tournament endpoint for player field
            api_data = await golf_api.get_tournament(tournament.tourn_id, tournament.year)
            players_data = api_data.get('players', [])
            
            # Process and upsert players
            players_processed = 0
            for player_data in players_data:
                player_id_api = str(player_data.get('playerId', ''))
                if not player_id_api:
                    continue
                
                first_name = player_data.get('firstName', '')
                last_name = player_data.get('lastName', '')
                full_name = f"{first_name} {last_name}".strip()
                
                if not full_name:
                    continue
                
                # Get or create player
                player = db.query(Player).filter(Player.player_id == player_id_api).first()
                if not player:
                    player = Player(
                        player_id=player_id_api,
                        first_name=first_name,
                        last_name=last_name,
                        full_name=full_name
                    )
                    db.add(player)
                    db.flush()  # Get player.id
                
                # Upsert tournament player relationship
                tournament_player = db.query(TournamentPlayer).filter(
                    TournamentPlayer.tournament_id == tournament.id,
                    TournamentPlayer.player_id == player.id
                ).first()
                
                if not tournament_player:
                    tournament_player = TournamentPlayer(
                        tournament_id=tournament.id,
                        player_id=player.id
                    )
                    db.add(tournament_player)
                    players_processed += 1
            
            db.commit()
            tournament.last_player_refresh = datetime.now()
            db.commit()
            
            return {
                "message": f"Refreshed {players_processed} players for {tournament.name}",
                "players_added": players_processed
            }
            
        else:
            # Tournament is active or completed - use leaderboard
            leaderboard_data = await golf_api.get_leaderboard(
                tournament.tourn_id, 
                tournament.year
            )
            leaderboard_rows = leaderboard_data.get('leaderboardRows', [])
            
            # This will update both players and scores
            # Reuse the existing sync logic
            return await sync_tournament_scores(tournament_id, db, current_user)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh players: {str(e)}"
        )

