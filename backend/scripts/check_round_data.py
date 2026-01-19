"""
Check if round scores are cumulative or per-round.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.tournament import Tournament, Player, PlayerScore
from sqlalchemy import and_

def check_round_data():
    db = next(get_db())
    
    try:
        # Get World Wide Technology Championship
        tournament = db.query(Tournament).filter(
            Tournament.name.like('%World Wide%')
        ).first()
        
        if not tournament:
            print("Tournament not found")
            return
        
        print("=" * 80)
        print(f"Tournament: {tournament.name}")
        print("=" * 80)
        
        # Get a player with multiple rounds
        player_scores = db.query(PlayerScore, Player).join(
            Player, PlayerScore.player_id == Player.id
        ).filter(
            PlayerScore.tournament_id == tournament.id
        ).order_by(
            Player.full_name, PlayerScore.round
        ).all()
        
        # Group by player
        from collections import defaultdict
        players_data = defaultdict(list)
        
        for score, player in player_scores:
            players_data[player.full_name].append({
                'round': score.round,
                'round_score': score.round_score,
                'total_score': score.total_score
            })
        
        # Show first 5 players with their rounds
        print("\nShowing first 5 players with round data:")
        print("-" * 80)
        
        for i, (player_name, rounds) in enumerate(list(players_data.items())[:5]):
            print(f"\n{player_name}:")
            for r in rounds:
                print(f"  Round {r['round']}: round_score={r['round_score']}, total_score={r['total_score']}")
            
            # Check if cumulative
            if len(rounds) > 1:
                r1_total = rounds[0]['total_score']
                r2_total = rounds[1]['total_score'] if len(rounds) > 1 else None
                if r2_total and r1_total:
                    print(f"  → Is Round 2 total cumulative? R2 total ({r2_total}) vs R1 total ({r1_total})")
        
        print("\n" + "=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        print("If total_score INCREASES each round → CUMULATIVE")
        print("If total_score is similar each round → PER-ROUND (needs aggregation)")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_round_data()

