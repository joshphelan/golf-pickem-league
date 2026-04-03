"""Service for calculating fantasy golf scores."""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from ..models.league import League, Team, TeamPlayer
from ..models.tournament import PlayerScore
from ..models.user import User


def calculate_team_score(
    team_id: UUID,
    db: Session,
    round_num: Optional[int] = None
) -> Optional[int]:
    """
    Calculate total score for a team in a specific round.
    
    Sums the total_score of all players on the team.
    Returns None if any player is missing scores.
    
    Args:
        team_id: Team UUID
        db: Database session
        round_num: Round number (if None, uses latest available round)
        
    Returns:
        Total team score (lower is better), or None if incomplete
    """
    # Get team and league
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None
    
    league = team.league
    if not league:
        return None
    
    tournament_id = league.tournament_id
    
    # If no round specified, find the latest available round for this tournament
    if round_num is None:
        from sqlalchemy import func
        latest_round = db.query(func.max(PlayerScore.round)).filter(
            PlayerScore.tournament_id == tournament_id
        ).scalar()
        round_num = latest_round if latest_round else 4
    
    # Get all players on this team
    team_players = (
        db.query(TeamPlayer)
        .filter(TeamPlayer.team_id == team_id)
        .all()
    )
    
    if not team_players:
        return None
    
    collected_scores = []

    for tp in team_players:
        # Get player's score for this round, falling back to their latest available round
        score = (
            db.query(PlayerScore)
            .filter(
                PlayerScore.tournament_id == tournament_id,
                PlayerScore.player_id == tp.player_id,
                PlayerScore.round == round_num
            )
            .first()
        )
        if score is None:
            score = (
                db.query(PlayerScore)
                .filter(
                    PlayerScore.tournament_id == tournament_id,
                    PlayerScore.player_id == tp.player_id,
                )
                .order_by(PlayerScore.round.desc())
                .first()
            )

        # Player has no tournament records — did not participate, count as 0
        collected_scores.append(score.total_score if (score and score.total_score is not None) else 0)

    # Only return score if we have data for all players
    if len(collected_scores) < len(team_players):
        return None  # Incomplete scores

    # Apply best-N logic if scoring_count is configured
    n = league.scoring_count
    if n and n < len(collected_scores):
        # Sort ascending (lower = better in golf), keep the best N
        scores_to_sum = sorted(collected_scores)[:n]
    else:
        scores_to_sum = collected_scores

    return sum(scores_to_sum)


def calculate_league_standings(
    league_id: UUID,
    db: Session,
    round_num: Optional[int] = None
) -> List[Dict]:
    """
    Calculate standings for a league.
    
    Returns teams ranked by score (lowest first).
    
    Args:
        league_id: League UUID
        db: Database session
        round_num: Round number (if None, uses latest available round)
        
    Returns:
        List of team standings with scores
    """
    # Get league
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        return []
    
    # If no round specified, find the latest available round for this tournament
    if round_num is None:
        from sqlalchemy import func
        latest_round = db.query(func.max(PlayerScore.round)).filter(
            PlayerScore.tournament_id == league.tournament_id
        ).scalar()
        round_num = latest_round if latest_round else 4
    
    # Get all teams in league
    teams = db.query(Team).filter(Team.league_id == league_id).all()
    
    standings = []
    
    for team in teams:
        # Calculate team score
        team_score = calculate_team_score(team.id, db, round_num)
        
        # Get team player details
        team_players = (
            db.query(TeamPlayer)
            .filter(TeamPlayer.team_id == team.id)
            .all()
        )
        
        player_scores = []
        for tp in team_players:
            player = tp.player
            score = (
                db.query(PlayerScore)
                .filter(
                    PlayerScore.tournament_id == league.tournament_id,
                    PlayerScore.player_id == tp.player_id,
                    PlayerScore.round == round_num
                )
                .first()
            )
            if score is None:
                score = (
                    db.query(PlayerScore)
                    .filter(
                        PlayerScore.tournament_id == league.tournament_id,
                        PlayerScore.player_id == tp.player_id,
                    )
                    .order_by(PlayerScore.round.desc())
                    .first()
                )

            player_score = score.total_score if (score and score.total_score is not None) else None
            player_scores.append({
                'player_id': str(player.id),
                'name': player.full_name,  # Frontend expects 'name'
                'score': player_score,
                'position': score.position if score else None,
                'made_cut': score.made_cut if score else False
            })
        
        standings.append({
            'team_id': str(team.id),
            'team_name': team.team_name,
            'owner_name': team.user.username if team.user else 'Unknown',  # Frontend expects 'owner_name'
            'total_score': team_score,
            'players': player_scores
        })
    
    # Sort by score (lower is better), teams without scores go to bottom
    standings.sort(key=lambda x: (x['total_score'] is None, x['total_score']))
    
    # Add rank
    for i, standing in enumerate(standings):
        if standing['total_score'] is not None:
            standing['rank'] = i + 1
        else:
            standing['rank'] = None
    
    return standings

