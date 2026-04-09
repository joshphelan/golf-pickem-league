"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # Golf API (RapidAPI)
    GOLF_API_KEY: str
    GOLF_API_BASE_URL: str = "https://live-golf-data.p.rapidapi.com"
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Primary Owner (optional - first user is auto-primary owner)
    PRIMARY_OWNER_EMAIL: Optional[str] = None

    # Email (Resend) - for password reset emails
    # Get API key from resend.com → API Keys. Requires a verified domain.
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM_EMAIL: str = "noreply@localhost"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Scheduler Settings
    ENABLE_AUTO_SYNC: bool = False  # Enable automatic score syncing (default: disabled for dev)
    SYNC_INTERVAL_MINUTES: int = 15  # How often to sync scores (when enabled)

    # Job #1: Tournament Import Settings
    TOURNAMENT_IMPORT_WINDOW_DAYS: int = 365  # How far ahead to import tournaments

    # Job #2: Player Refresh Settings
    PLAYER_REFRESH_WINDOW_DAYS: int = 7  # Refresh players for tournaments starting within this window

    # Job #3: Score Sync Settings
    SCORE_SYNC_PLAYING_HOURS_START: int = 7   # Start hour for syncing (tournament local time)
    SCORE_SYNC_PLAYING_HOURS_END: int = 21    # End hour for syncing (tournament local time)

    # Job #4: Backup Sync Settings
    COMPLETED_SYNC_LOOKBACK_DAYS: int = 7  # How far back to sync completed tournaments
    
    class Config:
        # Look for .env in project root (parent of backend folder)
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not defined in this class


# Global settings instance
settings = Settings()

