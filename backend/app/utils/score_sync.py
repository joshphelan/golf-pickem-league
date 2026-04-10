"""Reusable score syncing logic for tournaments."""
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..models.tournament import Player, PlayerScore
from .score_converter import parse_golf_score

logger = logging.getLogger(__name__)


def sync_scores_from_leaderboard(tournament, leaderboard_data: Dict[str, Any], db: Session) -> tuple[int, int]:
    """
    Process leaderboard data and upsert scores for a tournament.

    This function extracts score data from the Golf API leaderboard response
    and updates the database with player scores for each round.

    Args:
        tournament: Tournament model instance
        leaderboard_data: Leaderboard data from Golf API
        db: Database session

    Returns:
        Tuple of (scores_created, scores_updated)
    """
    # Extract leaderboard rows
    leaderboard_rows = leaderboard_data.get('leaderboardRows', [])
    if not leaderboard_rows:
        logger.warning(f"No leaderboard data available for {tournament.name}")
        return (0, 0)

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

        # Handle mid-round players: API only includes completed rounds in the
        # rounds array, so players still on the course are missing their current
        # round. Use top-level total and currentRoundScore for live scores.
        round_complete = row.get('roundComplete', True)
        if not round_complete:
            player_current_round = row.get('currentRound')
            if isinstance(player_current_round, dict):
                player_current_round = int(player_current_round.get('$numberInt', 0))
            elif player_current_round is not None:
                player_current_round = int(player_current_round)

            if player_current_round and player_current_round > 0:
                total_score = parse_golf_score(row.get('total', 'E'))
                current_round_score = parse_golf_score(row.get('currentRoundScore', 'E'))

                if total_score is not None:
                    existing_score = db.query(PlayerScore).filter(
                        PlayerScore.tournament_id == tournament.id,
                        PlayerScore.player_id == player.id,
                        PlayerScore.round == player_current_round
                    ).first()

                    if existing_score:
                        existing_score.round_score = current_round_score
                        existing_score.total_score = total_score
                        existing_score.position = position
                        existing_score.made_cut = made_cut
                        scores_updated += 1
                    else:
                        new_score = PlayerScore(
                            tournament_id=tournament.id,
                            player_id=player.id,
                            round=player_current_round,
                            round_score=current_round_score,
                            total_score=total_score,
                            position=position,
                            made_cut=made_cut
                        )
                        db.add(new_score)
                        scores_created += 1

    db.commit()

    logger.warning(f"Synced {tournament.name}: {scores_created} created, {scores_updated} updated")
    return (scores_created, scores_updated)
