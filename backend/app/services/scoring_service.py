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
    round_num: int = 4
) -> Optional[int]:
    """
    Calculate total score for a team in a specific round.
    
    Sums the total_score of all players on the team.
    Returns None if any player is missing scores.
    
    Args:
        team_id: Team UUID
        db: Database session
        round_num: Round number (default: 4 for final)
        
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
    
    # Get all players on this team
    team_players = (
        db.query(TeamPlayer)
        .filter(TeamPlayer.team_id == team_id)
        .all()
    )
    
    if not team_players:
        return None
    
    total_score = 0
    players_with_scores = 0
    
    for tp in team_players:
        # Get player's score for this round
        score = (
            db.query(PlayerScore)
            .filter(
                PlayerScore.tournament_id == tournament_id,
                PlayerScore.player_id == tp.player_id,
                PlayerScore.round == round_num
            )
            .first()
        )
        
        if score and score.total_score is not None:
            total_score += score.total_score
            players_with_scores += 1
    
    # Only return score if all players have scores
    expected_players = len(team_players)
    if players_with_scores < expected_players:
        return None  # Incomplete scores
    
    return total_score


def calculate_league_standings(
    league_id: UUID,
    db: Session,
    round_num: int = 4
) -> List[Dict]:
    """
    Calculate standings for a league.
    
    Returns teams ranked by score (lowest first).
    
    Args:
        league_id: League UUID
        db: Database session
        round_num: Round number (default: 4 for final)
        
    Returns:
        List of team standings with scores
    """
    # Get league
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        return []
    
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
            
            player_scores.append({
                'player_id': str(player.id),
                'player_name': player.full_name,
                'score': score.total_score if score else None,
                'position': score.position if score else None,
                'made_cut': score.made_cut if score else True
            })
        
        standings.append({
            'team_id': str(team.id),
            'team_name': team.team_name,
            'user_id': str(team.user_id),
            'user': team.user.username if team.user else None,
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

