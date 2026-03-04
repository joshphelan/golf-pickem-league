"""Background scheduler for automated tournament management."""
import asyncio
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import logging
import httpx

from .database import get_db
from .models.tournament import Tournament, Player, TournamentPlayer
from .services.golf_api_service import golf_api
from .utils.score_sync import sync_scores_from_leaderboard
from .utils.date_parser import parse_api_dates, parse_api_date
from .utils.tournament_status import determine_tournament_status
from .config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


# ============================================================================
# JOB #1: DYNAMIC TOURNAMENT IMPORT (Weekly, Monday 6 AM UTC)
# ============================================================================

def import_upcoming_tournaments():
    """
    Weekly job to auto-import tournaments starting within next 12 months.
    On first run (empty DB), imports immediately.
    """
    try:
        asyncio.run(_import_upcoming_tournaments_async())
    except Exception as e:
        logger.error(f"Error in scheduled tournament import job: {e}")


async def _import_upcoming_tournaments_async():
    """Async implementation of tournament import."""
    today = date.today()
    end_date = today + timedelta(days=settings.TOURNAMENT_IMPORT_WINDOW_DAYS)

    # PHASE 1: Fetch all API data first (no DB connection held)
    current_year = today.year
    years_to_fetch = [current_year, current_year + 1]

    all_tournaments = []
    for year in years_to_fetch:
        try:
            schedule = await golf_api.get_schedules(year)
            # Attach year to each tournament (API doesn't include it)
            for t in schedule:
                t['year'] = year
            all_tournaments.extend(schedule)
            logger.warning(f"Fetched {len(schedule)} tournaments for {year}")
        except Exception as e:
            logger.error(f"Failed to fetch schedule for {year}: {e}")
            continue

    # Filter: tournaments that are in progress or start within window
    filtered = []
    for t in all_tournaments:
        try:
            date_info = t.get('date', {})
            start_obj = date_info.get('start')
            end_obj = date_info.get('end')
            if start_obj:
                # Handle both string dates and MongoDB format dicts
                if isinstance(start_obj, str):
                    start = datetime.fromisoformat(start_obj.replace('Z', '+00:00')).date()
                else:
                    start = parse_api_date(start_obj)
                # Parse end date to include in-progress tournaments
                if isinstance(end_obj, str):
                    end = datetime.fromisoformat(end_obj.replace('Z', '+00:00')).date()
                else:
                    end = parse_api_date(end_obj) if end_obj else start
                # Include if: not ended yet AND starts within window
                if end and end >= today and start <= end_date:
                    filtered.append(t)
        except Exception as e:
            logger.warning(f"Failed to parse date for tournament: {e}")
            continue

    logger.warning(f"Found {len(filtered)} tournaments to import (within {settings.TOURNAMENT_IMPORT_WINDOW_DAYS} days)")

    if not filtered:
        logger.warning("No tournaments to import")
        return

    # PHASE 2: Get existing tournament IDs (brief DB query)
    db = next(get_db())
    try:
        existing_keys = set()
        for t in db.query(Tournament.tourn_id, Tournament.year).all():
            existing_keys.add((t.tourn_id, t.year))
    finally:
        db.close()

    # Filter out already-imported tournaments
    to_import = []
    skipped_count = 0
    for tournament in filtered:
        tourn_id = tournament.get('tournId')
        year = tournament.get('year')
        if not tourn_id or not year:
            continue
        if (tourn_id, year) in existing_keys:
            skipped_count += 1
        else:
            to_import.append(tournament)

    logger.warning(f"Will import {len(to_import)} tournaments ({skipped_count} already exist)")

    # PHASE 3: Fetch tournament details from API (no DB connection)
    tournament_data = []
    for tournament in to_import:
        tourn_id = tournament.get('tournId')
        year = tournament.get('year')
        try:
            api_data = await golf_api.get_tournament(tourn_id, year)
            tournament_data.append((tourn_id, year, api_data))
        except Exception as e:
            logger.error(f"Failed to fetch tournament {tourn_id} ({year}): {e}")
            continue

    # PHASE 4: Insert all tournaments into DB (single connection, quick inserts)
    imported_count = 0
    db = next(get_db())
    try:
        for tourn_id, year, api_data in tournament_data:
            try:
                _import_tournament_from_data(tourn_id, year, api_data, db)
                imported_count += 1
            except Exception as e:
                logger.error(f"Failed to import tournament {tourn_id} ({year}): {e}")
                db.rollback()
                continue
    finally:
        db.close()

    logger.warning(f"Tournament import complete: {imported_count} imported, {skipped_count} already exist")


def _import_tournament_from_data(tourn_id: str, year: int, api_data: dict, db: Session):
    """Import a tournament from pre-fetched API data (no API calls, just DB inserts)."""
    tourn_name = api_data.get('name')
    players_data = api_data.get('players', [])

    if not tourn_name:
        raise ValueError("Invalid response from Golf API - missing tournament name")

    # Parse dates from API
    start_date, end_date = parse_api_dates(api_data)

    # Auto-detect status based on dates
    initial_status = api_data.get('status', 'upcoming')
    tournament_status = determine_tournament_status(start_date, end_date, initial_status)

    # Extract timezone
    timezone = api_data.get('timeZone', 'America/New_York')

    # Create tournament record
    tournament = Tournament(
        tourn_id=tourn_id,
        name=tourn_name,
        year=year,
        org_id=api_data.get('orgId', 1),
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        status=tournament_status
    )
    db.add(tournament)
    db.flush()  # Get tournament.id

    # Process players
    players_processed = 0
    for player_data in players_data:
        player_id_api = str(player_data.get('playerId'))
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
                full_name=full_name,
                country=None
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
        players_processed += 1

    db.commit()
    logger.warning(f"Imported {tourn_name} ({year}) with {players_processed} players")


async def _import_tournament_internal(tourn_id: str, year: int, db: Session):
    """Internal helper to import a single tournament (legacy, makes API call)."""
    # Fetch from Golf API
    api_data = await golf_api.get_tournament(tourn_id, year)

    # Extract tournament info
    tourn_name = api_data.get('name')
    players_data = api_data.get('players', [])

    if not tourn_name:
        raise ValueError("Invalid response from Golf API - missing tournament name")

    # Parse dates from API
    start_date, end_date = parse_api_dates(api_data)

    # Auto-detect status based on dates
    initial_status = api_data.get('status', 'upcoming')
    tournament_status = determine_tournament_status(start_date, end_date, initial_status)

    # Extract timezone
    timezone = api_data.get('timeZone', 'America/New_York')

    # Create tournament record
    tournament = Tournament(
        tourn_id=tourn_id,
        name=tourn_name,
        year=year,
        org_id=api_data.get('orgId', 1),
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        status=tournament_status
    )
    db.add(tournament)
    db.flush()  # Get tournament.id

    # Process players
    players_processed = 0
    for player_data in players_data:
        player_id_api = str(player_data.get('playerId'))
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
                full_name=full_name,
                country=None
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
        players_processed += 1

    db.commit()
    logger.warning(f"Imported {tourn_name} ({year}) with {players_processed} players")


# ============================================================================
# JOB #2: PLAYER REFRESH (11x per week - Friday 6pm + Sat-Wed 2x daily)
# ============================================================================

def refresh_tournament_players():
    """
    Refresh player fields for tournaments starting within 7 days.
    Runs 11 times per week:
    - Friday 6 PM ET (initial catch when API updates at 5pm)
    - Saturday-Wednesday: 6 AM, 6 PM ET (2x daily for 5 days)
    """
    try:
        asyncio.run(_refresh_tournament_players_async())
    except Exception as e:
        logger.error(f"Error in scheduled player refresh job: {e}")


async def _refresh_tournament_players_async():
    """Async implementation of player refresh."""
    db = next(get_db())

    try:
        today = date.today()
        window_end = today + timedelta(days=settings.PLAYER_REFRESH_WINDOW_DAYS)

        # Find tournaments starting soon
        tournaments = db.query(Tournament).filter(
            Tournament.start_date >= today,
            Tournament.start_date <= window_end,
            Tournament.status == 'upcoming'
        ).all()

        logger.info(f"Found {len(tournaments)} tournaments starting within {settings.PLAYER_REFRESH_WINDOW_DAYS} days")

        for tournament in tournaments:
            try:
                # Call /tournament endpoint to get latest player field
                api_data = await golf_api.get_tournament(
                    tournament.tourn_id,
                    tournament.year
                )

                # Upsert players
                players_data = api_data.get('players', [])
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

                # Update refresh timestamp
                tournament.last_player_refresh = datetime.now()
                db.commit()

                logger.info(f"Refreshed {players_processed} players for {tournament.name}")

            except Exception as e:
                logger.error(f"Failed to refresh players for {tournament.name}: {e}")
                continue

    finally:
        db.close()


# ============================================================================
# JOB #3: LIVE SCORE SYNC (Every 15 minutes, timezone-aware)
# ============================================================================

def sync_active_tournament_scores():
    """
    Sync scores for active tournaments with timezone awareness.
    Pre-filters: playing hours (7am-9pm local), upcoming before start_date,
    stuck-active completion. Only calls API when useful.
    """
    try:
        asyncio.run(_sync_active_tournament_scores_async())
    except Exception as e:
        logger.error(f"Error in scheduled score sync job: {e}")


async def _sync_active_tournament_scores_async():
    """Async implementation of live score sync."""
    db = next(get_db())

    try:
        today = date.today()

        # PHASE 1: Find potentially active tournaments (date filter)
        # Conservative window: start_date - 1 day to end_date + 2 days
        potentially_active = db.query(Tournament).filter(
            Tournament.start_date <= today + timedelta(days=2),
            Tournament.end_date >= today - timedelta(days=1),
            Tournament.status != 'completed'  # Skip confirmed completed
        ).all()

        if not potentially_active:
            logger.debug("No potentially active tournaments found")
            return

        logger.info(f"Checking {len(potentially_active)} potentially active tournaments")

        synced_count = 0
        status_updated_count = 0

        for tournament in potentially_active:
            # 1. Skip tournaments from previous years (they won't have current leaderboards)
            if tournament.year < today.year:
                logger.debug(f"Skipping {tournament.name} - tournament year {tournament.year} is in the past")
                continue

            # 2. Compute tournament-local time (used for playing hours + date checks)
            tz = pytz.timezone(tournament.timezone)
            local_now = datetime.now(tz)
            local_hour = local_now.hour
            local_today = local_now.date()

            # 3. Check playing hours BEFORE making API call (Fix 2 - critical bug fix)
            if not (settings.SCORE_SYNC_PLAYING_HOURS_START <= local_hour < settings.SCORE_SYNC_PLAYING_HOURS_END):
                logger.debug(
                    f"Skipped {tournament.name} - outside playing hours "
                    f"({local_hour:02d}:00 {tournament.timezone})"
                )
                continue

            # 4. Skip upcoming tournaments before their start_date (Fix 5)
            if tournament.status == 'upcoming' and local_today < tournament.start_date:
                logger.debug(f"Skipped {tournament.name} - upcoming, before start_date {tournament.start_date}")
                continue

            # 5. Date-based completion for stuck-active tournaments (Fix 7)
            if tournament.status == 'active' and local_today > tournament.end_date + timedelta(days=2):
                tournament.status = 'completed'
                db.commit()
                status_updated_count += 1
                logger.info(f"{tournament.name}: active → completed (2 days past end_date {tournament.end_date})")
                continue  # Backup sync (Job #4) will handle final score corrections

            try:
                # PHASE 2: Query leaderboard to check status (only reaches here if playing hours + valid)
                leaderboard_data = await golf_api.get_leaderboard(
                    tournament.tourn_id,
                    tournament.year,
                    tournament.org_id
                )

                # Parse lastUpdated timestamp
                last_updated_ms = leaderboard_data.get('lastUpdated', {}).get('$date', {}).get('$numberLong')
                if last_updated_ms:
                    last_updated = datetime.fromtimestamp(int(last_updated_ms) / 1000)
                    days_since_update = (datetime.now() - last_updated).days
                else:
                    days_since_update = 999  # No update info

                # Check if leaderboard has data
                has_scores = len(leaderboard_data.get('leaderboardRows', [])) > 0

                # Determine status based on leaderboard response
                if has_scores and days_since_update <= 7:
                    # Tournament is active (scores updated within last week)
                    new_status = 'active'
                elif days_since_update > 7:
                    # No recent updates - likely completed
                    new_status = 'completed'
                else:
                    # No scores yet - still upcoming
                    new_status = 'upcoming'

                # Update status if changed
                if new_status != tournament.status:
                    old_status = tournament.status
                    tournament.status = new_status
                    db.commit()
                    status_updated_count += 1
                    logger.info(f"{tournament.name}: {old_status} → {new_status}")

                # PHASE 3: Sync scores if active
                if new_status == 'active':
                    created, updated = sync_scores_from_leaderboard(tournament, leaderboard_data, db)
                    synced_count += 1
                    logger.info(
                        f"Synced {tournament.name} ({local_hour:02d}:00 {tournament.timezone}): "
                        f"{created} created, {updated} updated"
                    )

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.warning(f"Skipping {tournament.name} ({tournament.year}) - not available in API")
                else:
                    logger.error(f"HTTP error syncing {tournament.name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error syncing {tournament.name}: {e}")
                continue

        if synced_count > 0 or status_updated_count > 0:
            logger.info(
                f"Score sync complete: {synced_count} tournaments synced, "
                f"{status_updated_count} status updates"
            )

    finally:
        db.close()


# ============================================================================
# JOB #4: BACKUP SYNC (Daily at 4 PM UTC)
# ============================================================================

def sync_completed_tournaments_backup():
    """
    Daily backup sync for recently completed tournaments.
    Catches score corrections, missed syncs, or status transition gaps.
    """
    try:
        asyncio.run(_sync_completed_tournaments_backup_async())
    except Exception as e:
        logger.error(f"Error in backup sync job: {e}")


async def _sync_completed_tournaments_backup_async():
    """Async implementation of backup sync."""
    db = next(get_db())

    try:
        # Get recently completed/straggler tournaments (last 7 days past end_date)
        cutoff_date = date.today() - timedelta(days=settings.COMPLETED_SYNC_LOOKBACK_DAYS)

        tournaments = db.query(Tournament).filter(
            Tournament.status.in_(['completed', 'active']),
            Tournament.end_date >= cutoff_date,
            Tournament.end_date < date.today()  # Only past-end tournaments
        ).all()

        if not tournaments:
            logger.debug("No recently completed tournaments to sync")
            return

        logger.info(f"Running backup sync for {len(tournaments)} recently completed/straggler tournaments")

        synced_count = 0

        for tournament in tournaments:
            try:
                logger.info(f"Running backup sync for {tournament.name} (status: {tournament.status})")

                # Call leaderboard API
                leaderboard_data = await golf_api.get_leaderboard(
                    tournament.tourn_id,
                    tournament.year,
                    tournament.org_id
                )

                # Sync scores
                created, updated = sync_scores_from_leaderboard(tournament, leaderboard_data, db)
                synced_count += 1

                # Mark active stragglers as completed
                if tournament.status == 'active':
                    tournament.status = 'completed'
                    db.commit()
                    logger.info(f"{tournament.name}: active → completed (backup sync, past end_date)")

                logger.info(
                    f"Backup sync {tournament.name}: {created} created, {updated} updated"
                )

            except Exception as e:
                logger.error(f"Error in backup sync for {tournament.name}: {e}")
                continue

        if synced_count > 0:
            logger.info(f"Backup sync complete: {synced_count} tournaments synced")

    finally:
        db.close()


# ============================================================================
# SCHEDULER CONTROL
# ============================================================================

def start_scheduler():
    """Start the background scheduler with all 4 jobs if auto-sync is enabled."""
    global scheduler

    if settings.ENABLE_AUTO_SYNC and scheduler is None:
        scheduler = BackgroundScheduler()

        # Job #1: Weekly tournament import (Monday 6 AM UTC)
        scheduler.add_job(
            import_upcoming_tournaments,
            trigger=CronTrigger(day_of_week='mon', hour=6, minute=0, timezone='UTC'),
            id='import_tournaments',
            name='Import Upcoming Tournaments',
            replace_existing=True
        )
        logger.info("Scheduled Job #1: Tournament Import (Weekly, Monday 6 AM UTC)")

        # Job #2: Player refresh - Friday 6 PM ET only
        scheduler.add_job(
            refresh_tournament_players,
            trigger=CronTrigger(day_of_week='fri', hour=18, minute=0, timezone='America/New_York'),
            id='refresh_players_friday',
            name='Refresh Tournament Players (Friday 6pm)',
            replace_existing=True
        )
        logger.info("Scheduled Job #2a: Player Refresh (Friday 6 PM ET)")

        # Job #2: Player refresh - Saturday through Wednesday: 6 AM, 6 PM ET
        scheduler.add_job(
            refresh_tournament_players,
            trigger=CronTrigger(
                day_of_week='sat,sun,mon,tue,wed',
                hour='6,18',
                minute=0,
                timezone='America/New_York'
            ),
            id='refresh_players_multi',
            name='Refresh Tournament Players (Sat-Wed 2x daily)',
            replace_existing=True
        )
        logger.info("Scheduled Job #2b: Player Refresh (Sat-Wed 6 AM, 6 PM ET)")

        # Job #3: Live score sync (every 10 minutes)
        scheduler.add_job(
            sync_active_tournament_scores,
            trigger=IntervalTrigger(minutes=settings.SYNC_INTERVAL_MINUTES),
            id='sync_active_scores',
            name='Sync Active Tournament Scores',
            replace_existing=True
        )
        logger.info(f"Scheduled Job #3: Live Score Sync (Every {settings.SYNC_INTERVAL_MINUTES} minutes)")

        # Job #4: Backup sync (daily at 4 PM UTC)
        scheduler.add_job(
            sync_completed_tournaments_backup,
            trigger=CronTrigger(hour=16, minute=0, timezone='UTC'),
            id='backup_sync',
            name='Backup Sync Completed Tournaments',
            replace_existing=True
        )
        logger.info("Scheduled Job #4: Backup Sync (Daily at 4 PM UTC)")

        scheduler.start()
        logger.info("=" * 60)
        logger.info("All 4 background jobs scheduled successfully!")
        logger.info("=" * 60)

    elif not settings.ENABLE_AUTO_SYNC:
        print("\n" + "=" * 60)
        print("SCHEDULER: Auto-sync is DISABLED - scheduler not started")
        print("=" * 60 + "\n")
        logger.info("Auto-sync is disabled - scheduler not started")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler

    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background scheduler stopped")
