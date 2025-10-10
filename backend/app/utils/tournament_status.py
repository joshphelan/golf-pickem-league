"""Utilities for tournament status management."""
from datetime import datetime, date
from typing import Optional


def determine_tournament_status(
    start_date: Optional[date],
    end_date: Optional[date],
    current_status: str = 'upcoming'
) -> str:
    """
    Auto-detect tournament status based on dates.
    
    Logic:
    - If today < start_date: "upcoming"
    - If start_date <= today <= end_date: "active"
    - If today > end_date: "completed"
    - If dates missing: keep current status
    
    Args:
        start_date: Tournament start date
        end_date: Tournament end date
        current_status: Current status (fallback if dates missing)
        
    Returns:
        Status string: 'upcoming', 'active', or 'completed'
    """
    if not start_date or not end_date:
        # Can't determine without dates, keep current
        return current_status
    
    today = datetime.now().date()
    
    if today < start_date:
        return 'upcoming'
    elif start_date <= today <= end_date:
        return 'active'
    else:
        return 'completed'


def should_sync_tournament(
    tournament_status: str,
    enable_sync: bool = False
) -> bool:
    """
    Determine if tournament should be synced.
    
    Simple logic for now:
    - Only sync if auto-sync enabled
    - Only sync if tournament is active
    
    Future: Can add timezone-aware hour filtering here.
    
    Args:
        tournament_status: Tournament status ('upcoming', 'active', 'completed')
        enable_sync: Whether auto-sync is enabled (from config)
        
    Returns:
        True if should sync, False otherwise
    """
    if not enable_sync:
        return False
    
    return tournament_status == 'active'

