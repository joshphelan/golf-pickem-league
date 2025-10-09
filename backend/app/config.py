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
    
    class Config:
        # Look for .env in project root (parent of backend folder)
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not defined in this class


# Global settings instance
settings = Settings()

