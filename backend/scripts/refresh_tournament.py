"""
Refresh player data for tournaments.

This script calls the /refresh-players endpoint to update player fields
for tournaments. Useful when player data becomes available or changes
(typically Friday 5pm before tournament starts on Thursday).

Usage:
    # Refresh specific tournament by UUID
    python scripts/refresh_tournament.py --tournament-id <uuid>
    
    # Refresh specific tournament by API tourn_id
    python scripts/refresh_tournament.py --tourn-id 457 --year 2025
    
    # Refresh all tournaments starting within 7 days
    python scripts/refresh_tournament.py --days-ahead 7
    
    # Refresh all upcoming tournaments with leagues
    python scripts/refresh_tournament.py --all-upcoming
"""
import argparse
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000/api/tournaments"


def call_api(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib."""
    req = urllib.request.Request(url, method=method)
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    if data:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req, data=data) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return e.code, error_json
        except:
            return e.code, {"detail": error_body}
    except Exception as e:
        return None, {"detail": str(e)}


def get_tournament_by_tourn_id(tourn_id: str, year: int):
    """Find tournament in database by tourn_id and year."""
    status, tournaments = call_api(BASE_URL)
    if status != 200:
        return None
    
    for t in tournaments:
        if t.get('tourn_id') == tourn_id and t.get('year') == year:
            return t
    return None


def get_player_count(tournament_id: str):
    """Get current player count for a tournament."""
    # We'll use the available-players endpoint with a dummy league to count
    # But actually, we need to query the tournament players differently
    # For now, we'll just return from the tournament data if available
    status, tournament = call_api(f"{BASE_URL}/{tournament_id}")
    if status == 200:
        # Count tournament_players if available in response
        return tournament.get('player_count', 0)
    return 0


def refresh_tournament(tournament_id: str, tournament_name: str):
    """Refresh player data for a single tournament."""
    print(f"\n  {tournament_name} (ID: {tournament_id[:8]}...)... ", end="", flush=True)
    
    # Call refresh endpoint
    status, response = call_api(
        f"{BASE_URL}/{tournament_id}/refresh-players",
        method="POST"
    )
    
    if status == 200:
        message = response.get('message', 'Refreshed')
        players_added = response.get('players_added', 0)
        print(f"[OK] {message}")
        return True, players_added
    else:
        error_detail = response.get('detail', 'Unknown error')
        print(f"[ERROR {status}] {error_detail}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(
        description='Refresh player data for tournaments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/refresh_tournament.py --tournament-id a1b2c3d4-...
  python scripts/refresh_tournament.py --tourn-id 457 --year 2025
  python scripts/refresh_tournament.py --days-ahead 7
  python scripts/refresh_tournament.py --all-upcoming
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tournament-id', help='Tournament UUID from database')
    group.add_argument('--tourn-id', help='Tournament ID from Golf API (requires --year)')
    group.add_argument('--days-ahead', type=int, help='Refresh tournaments starting within N days')
    group.add_argument('--all-upcoming', action='store_true', help='Refresh all upcoming tournaments')
    
    parser.add_argument('--year', type=int, help='Year (required with --tourn-id)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.tourn_id and not args.year:
        parser.error("--year is required when using --tourn-id")
    
    print("=" * 60)
    print("Tournament Player Data Refresh")
    print("=" * 60)
    
    # Get list of tournaments to refresh
    tournaments_to_refresh = []
    
    if args.tournament_id:
        # Single tournament by UUID
        print(f"\n[1] Fetching tournament {args.tournament_id}...")
        status, tournament = call_api(f"{BASE_URL}/{args.tournament_id}")
        if status == 200:
            tournaments_to_refresh.append(tournament)
            print(f"[OK] Found: {tournament['name']}")
        else:
            print(f"[ERROR] Tournament not found")
            return
    
    elif args.tourn_id:
        # Single tournament by tourn_id + year
        print(f"\n[1] Searching for tournament {args.tourn_id} ({args.year})...")
        tournament = get_tournament_by_tourn_id(args.tourn_id, args.year)
        if tournament:
            tournaments_to_refresh.append(tournament)
            print(f"[OK] Found: {tournament['name']}")
        else:
            print(f"[ERROR] Tournament {args.tourn_id} ({args.year}) not found in database")
            print("Hint: Run import_2025_tournaments.py first to import tournaments")
            return
    
    elif args.days_ahead or args.all_upcoming:
        # Multiple tournaments
        print(f"\n[1] Fetching all tournaments from database...")
        status, all_tournaments = call_api(BASE_URL)
        if status != 200:
            print(f"[ERROR] Failed to fetch tournaments")
            return
        
        print(f"[OK] Found {len(all_tournaments)} tournaments")
        
        # Filter by criteria
        today = datetime.now().date()
        
        for t in all_tournaments:
            start_date_str = t.get('start_date')
            if not start_date_str:
                continue
            
            # Parse date
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            except:
                continue
            
            # Check if upcoming
            if start_date < today:
                continue  # Skip past tournaments
            
            # Apply filters
            if args.all_upcoming:
                tournaments_to_refresh.append(t)
            elif args.days_ahead:
                days_until = (start_date - today).days
                if 0 <= days_until <= args.days_ahead:
                    tournaments_to_refresh.append(t)
        
        if args.all_upcoming:
            print(f"[OK] Selected {len(tournaments_to_refresh)} upcoming tournaments")
        else:
            print(f"[OK] Selected {len(tournaments_to_refresh)} tournaments starting within {args.days_ahead} days")
    
    if not tournaments_to_refresh:
        print("\n[INFO] No tournaments to refresh")
        return
    
    # Display tournaments to refresh
    print(f"\n[2] Tournaments to refresh:")
    for t in tournaments_to_refresh:
        start_date = t.get('start_date', 'N/A')
        print(f"  - {t['name']} ({start_date})")
    
    # Confirm if multiple tournaments
    if len(tournaments_to_refresh) > 1:
        print(f"\nAbout to refresh {len(tournaments_to_refresh)} tournaments.")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Refresh each tournament
    print(f"\n[3] Refreshing player data...")
    success_count = 0
    error_count = 0
    total_players_added = 0
    
    for tournament in tournaments_to_refresh:
        success, players_added = refresh_tournament(
            tournament['id'],
            tournament['name']
        )
        if success:
            success_count += 1
            total_players_added += players_added
        else:
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Refresh Summary")
    print("=" * 60)
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total Players Added/Updated: {total_players_added}")
    print(f"  Total Tournaments: {len(tournaments_to_refresh)}")
    
    if success_count > 0:
        print("\n[DONE] Player data refresh complete!")
    else:
        print("\n[WARNING] No tournaments were successfully refreshed")


if __name__ == "__main__":
    main()


