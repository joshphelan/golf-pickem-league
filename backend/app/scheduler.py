"""Background scheduler for automated tournament data refresh."""
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import logging

from .database import get_db
from .models.tournament import Tournament
from .models.league import League
from .services.golf_api_service import golf_api
from .config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def refresh_upcoming_tournament_players():
    """Daily job to refresh player fields for upcoming tournaments with leagues."""
    try:
        # Run async code in sync context
        asyncio.run(_refresh_upcoming_tournament_players_async())
    except Exception as e:
        logger.error(f"Error in scheduled player refresh job: {e}")


async def _refresh_upcoming_tournament_players_async():
    """Async implementation of player refresh."""
    db = next(get_db())
    
    try:
        today = date.today()
        
        # Find tournaments with leagues starting within 14 days
        tournaments = (
            db.query(Tournament)
            .join(League)
            .filter(Tournament.start_date >= today)
            .filter(Tournament.start_date <= today + timedelta(days=14))
            .distinct()
            .all()
        )
        
        logger.info(f"Found {len(tournaments)} tournaments with leagues starting within 14 days")
        
        for tournament in tournaments:
            try:
                if tournament.status == 'upcoming':
                    # NOW WORKS: await the async call
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
                        from .models.tournament import Player, TournamentPlayer
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
                    
                    # Update refresh timestamp
                    tournament.last_player_refresh = datetime.now()
                    db.commit()
                    
                    logger.info(f"Refreshed {players_processed} players for {tournament.name}")
                else:
                    logger.info(f"Skipping {tournament.name} - status is {tournament.status}")
                    
            except Exception as e:
                logger.error(f"Failed to refresh players for {tournament.name}: {e}")
                continue
        
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler if auto-sync is enabled."""
    global scheduler
    
    if settings.ENABLE_AUTO_SYNC and scheduler is None:
        scheduler = BackgroundScheduler()
        
        # Add daily job at 6 AM
        scheduler.add_job(
            refresh_upcoming_tournament_players,
            trigger=CronTrigger(hour=6, minute=0),
            id='refresh_tournament_players',
            name='Refresh Tournament Players',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Tournament player refresh scheduler started - will run daily at 6 AM")
        
    elif not settings.ENABLE_AUTO_SYNC:
        logger.info("Auto-sync is disabled - scheduler not started")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Tournament player refresh scheduler stopped")
