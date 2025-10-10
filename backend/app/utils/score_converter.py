"""Utility to convert golf API score strings to integers."""


def parse_golf_score(score_str: str) -> int:
    """
    Convert golf score string from API to integer.
    
    API returns scores as strings like:
    - "-12" -> -12
    - "+3" -> 3
    - "E" -> 0 (even par)
    - "WD" -> None (withdrawn)
    - "CUT" -> None (missed cut)
    
    Args:
        score_str: Score string from API
        
    Returns:
        Integer score, or None if not a valid score
    """
    if not score_str or not isinstance(score_str, str):
        return None
    
    score_str = score_str.strip().upper()
    
    # Handle special cases
    if score_str in ['E', 'EVEN']:
        return 0
    
    if score_str in ['WD', 'WITHDRAWN', 'CUT', 'MDF', 'DQ', 'DNS']:
        return None
    
    # Parse numeric scores
    try:
        # Remove any non-digit characters except +/- at start
        score_str = score_str.replace(' ', '')
        return int(score_str)
    except ValueError:
        # If conversion fails, return None
        return None


def parse_strokes(strokes) -> int:
    """
    Parse total strokes from API response.
    
    API may return as:
    - Integer: 272
    - String: "272"
    - Dict: {"$numberInt": "272"}
    
    Args:
        strokes: Strokes value from API
        
    Returns:
        Integer strokes, or None if invalid
    """
    if strokes is None:
        return None
    
    # Handle dict format (MongoDB export)
    if isinstance(strokes, dict):
        if '$numberInt' in strokes:
            try:
                return int(strokes['$numberInt'])
            except (ValueError, TypeError):
                return None
        return None
    
    # Handle string or int
    try:
        return int(strokes)
    except (ValueError, TypeError):
        return None

