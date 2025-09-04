from pydantic import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "South Media IA API"
    app_version: str = "3.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "south-media-secret-key-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: Optional[str] = None
    google_cloud_project: str = "automatizar-452311"
    google_application_credentials: Optional[str] = None
    
    # Google Sheets
    google_sheets_credentials_file: Optional[str] = None
    google_sheets_token_file: Optional[str] = None
    
    # Redis and Celery
    redis_url: str = "redis://localhost:6379"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://south-media-ia.vercel.app",
        "https://dash.iasouth.tech",
        "https://api.iasouth.tech"
    ]
    
    # File Upload
    upload_folder: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure upload folder exists
os.makedirs(settings.upload_folder, exist_ok=True)
