from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings managed through environment variables
    """
    # Database
    DATABASE_URL: str = "sqlite:///./google_alerts.db"  # SQLite database file in project root
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Google Alerts API"
    
    # RSS Feed
    RSS_FETCH_INTERVAL: int = 300  # 5 minutes in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()