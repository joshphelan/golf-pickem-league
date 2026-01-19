"""
Test the standings API to see what data it returns.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.league import League
from app.services.scoring_service import calculate_league_standings

def test_standings():
    db = next(get_db())
    
    try:
        # Get all leagues
        leagues = db.query(League).all()
        
        print("=" * 80)
        print("TESTING STANDINGS API")
        print("=" * 80)
        
        for league in leagues:
            print(f"\n\nLeague: {league.name}")
            print(f"League ID: {league.id}")
            
            # Test Round 1 standings
            print("\n--- Round 1 Standings ---")
            standings_r1 = calculate_league_standings(league.id, db, round_num=1)
            
            if not standings_r1:
                print("  No standings data")
            else:
                for standing in standings_r1:
                    print(f"\n  Rank: #{standing.get('rank', 'N/A')}")
                    print(f"  Team: {standing['team_name']}")
                    print(f"  Owner: {standing['owner_name']}")
                    print(f"  Total Score: {standing['total_score']}")
                    print(f"  Players ({len(standing['players'])}):")
                    for player in standing['players']:
                        print(f"    - {player['name']}: {player['score']}")
            
            # Test Round 4 standings
            print("\n--- Round 4 Standings (Default) ---")
            standings_r4 = calculate_league_standings(league.id, db, round_num=4)
            
            if not standings_r4:
                print("  No standings data")
            else:
                for standing in standings_r4:
                    print(f"\n  Rank: #{standing.get('rank', 'N/A')}")
                    print(f"  Team: {standing['team_name']}")
                    print(f"  Owner: {standing['owner_name']}")
                    print(f"  Total Score: {standing['total_score']}")
        
        print("\n" + "=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    test_standings()

