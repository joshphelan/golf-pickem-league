"""
Diagnose why team scores aren't showing up.
Traces through the exact same logic as the API endpoint.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.tournament import Tournament, Player, PlayerScore
from app.models.league import League, Team, TeamPlayer

def diagnose():
    db = next(get_db())
    
    try:
        # List all teams
        teams = db.query(Team).all()
        
        print("=" * 80)
        print("TEAMS IN DATABASE")
        print("=" * 80)
        
        for team in teams:
            print(f"\n{team.team_name}")
            print(f"  Team ID: {team.id}")
            print(f"  League ID: {team.league_id}")
            
            # Get league and tournament info
            league = db.query(League).filter(League.id == team.league_id).first()
            if league:
                print(f"  League: {league.name}")
                tournament = db.query(Tournament).filter(Tournament.id == league.tournament_id).first()
                if tournament:
                    print(f"  Tournament: {tournament.name} ({tournament.year})")
                    print(f"  Tournament ID: {tournament.id}")
                    
                    # Get team players
                    team_players = db.query(TeamPlayer).filter(TeamPlayer.team_id == team.id).all()
                    print(f"\n  Drafted Players ({len(team_players)}):")
                    
                    for tp in team_players:
                        player = tp.player
                        print(f"\n    {player.full_name}")
                        print(f"      Player UUID: {player.id}")
                        print(f"      Player API ID: {player.player_id}")
                        
                        # Check for scores
                        scores = db.query(PlayerScore).filter(
                            PlayerScore.tournament_id == tournament.id,
                            PlayerScore.player_id == player.id
                        ).all()
                        
                        print(f"      Scores found: {len(scores)}")
                        
                        if scores:
                            for score in scores:
                                print(f"        Round {score.round}: {score.total_score} (position: {score.position})")
                        else:
                            # Debug: Check if any scores exist for this player in any tournament
                            any_scores = db.query(PlayerScore).filter(
                                PlayerScore.player_id == player.id
                            ).count()
                            print(f"        (This player has {any_scores} scores in other tournaments)")
                            
                            # Check if scores exist for this tournament at all
                            tournament_scores = db.query(PlayerScore).filter(
                                PlayerScore.tournament_id == tournament.id
                            ).count()
                            print(f"        (Tournament has {tournament_scores} total scores)")
        
        print("\n" + "=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    diagnose()

