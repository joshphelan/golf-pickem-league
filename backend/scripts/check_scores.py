"""
Quick script to check if scores exist in database for a tournament.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.tournament import Tournament, Player, PlayerScore
from sqlalchemy import func

def check_scores():
    db = next(get_db())
    
    try:
        # Get all tournaments
        tournaments = db.query(Tournament).all()
        
        print("=" * 80)
        print("TOURNAMENTS AND SCORES IN DATABASE")
        print("=" * 80)
        
        for tournament in tournaments:
            score_count = db.query(PlayerScore).filter(
                PlayerScore.tournament_id == tournament.id
            ).count()
            
            print(f"\n{tournament.name} ({tournament.year})")
            print(f"  Tournament ID: {tournament.id}")
            print(f"  Status: {tournament.status}")
            print(f"  Scores in DB: {score_count}")
            
            if score_count > 0:
                # Show sample scores
                sample_scores = db.query(PlayerScore, Player).join(
                    Player, PlayerScore.player_id == Player.id
                ).filter(
                    PlayerScore.tournament_id == tournament.id
                ).limit(5).all()
                
                print(f"  Sample scores:")
                for score, player in sample_scores:
                    print(f"    - {player.full_name}: Round {score.round}, Score: {score.total_score}")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total_tournaments = db.query(Tournament).count()
        total_scores = db.query(PlayerScore).count()
        tournaments_with_scores = db.query(Tournament).join(
            PlayerScore, Tournament.id == PlayerScore.tournament_id
        ).distinct().count()
        
        print(f"Total Tournaments: {total_tournaments}")
        print(f"Tournaments with Scores: {tournaments_with_scores}")
        print(f"Total Score Records: {total_scores}")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_scores()

