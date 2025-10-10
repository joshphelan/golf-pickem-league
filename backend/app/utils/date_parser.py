"""Utility to parse dates from Golf API MongoDB format."""
from datetime import datetime, date
from typing import Optional


def parse_api_date(date_obj) -> Optional[date]:
    """
    Parse date from Golf API response.
    
    API returns dates in MongoDB format:
    {
        "$date": {
            "$numberLong": "1735776000000"  // milliseconds since epoch
        }
    }
    
    Or sometimes just as timestamp integer.
    
    Args:
        date_obj: Date object from API
        
    Returns:
        Python date object, or None if invalid
    """
    if not date_obj:
        return None
    
    try:
        # Handle MongoDB format
        if isinstance(date_obj, dict):
            if '$date' in date_obj:
                inner = date_obj['$date']
                if isinstance(inner, dict) and '$numberLong' in inner:
                    # Convert milliseconds to seconds
                    timestamp_ms = int(inner['$numberLong'])
                    timestamp_s = timestamp_ms / 1000
                    return datetime.fromtimestamp(timestamp_s).date()
                elif isinstance(inner, (int, str)):
                    # Direct timestamp
                    timestamp_ms = int(inner)
                    timestamp_s = timestamp_ms / 1000
                    return datetime.fromtimestamp(timestamp_s).date()
        
        # Handle direct integer timestamp (milliseconds)
        if isinstance(date_obj, (int, str)):
            timestamp_ms = int(date_obj)
            timestamp_s = timestamp_ms / 1000
            return datetime.fromtimestamp(timestamp_s).date()
        
    except (ValueError, TypeError, KeyError):
        pass
    
    return None


def parse_api_dates(api_data: dict) -> tuple[Optional[date], Optional[date]]:
    """
    Parse start and end dates from tournament API response.
    
    Expects api_data['date'] = {
        'start': <date_obj>,
        'end': <date_obj>
    }
    
    Args:
        api_data: Tournament data from API
        
    Returns:
        Tuple of (start_date, end_date), either may be None
    """
    date_info = api_data.get('date', {})
    
    if not isinstance(date_info, dict):
        return None, None
    
    start_date = parse_api_date(date_info.get('start'))
    end_date = parse_api_date(date_info.get('end'))
    
    return start_date, end_date

