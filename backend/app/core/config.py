"""
Configuration Settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # App Settings
    app_name: str = "Voice Agent API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    database_url: Optional[str] = os.getenv("DATABASE_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

