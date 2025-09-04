from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Configurações da aplicação
    app_name: str = "South Media IA API"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Configurações do banco de dados
    database_url: Optional[str] = None
    
    # Configurações do Redis
    redis_url: str = "redis://localhost:6379"
    
    # Configurações do Google Cloud
    google_cloud_project: Optional[str] = None
    google_cloud_credentials: Optional[str] = None
    
    # Configurações do BigQuery (mantido para compatibilidade)
    bigquery_dataset: str = "south_media_dashboard"
    
    # Configurações de autenticação
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configurações de CORS
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Detectar ambiente de teste automaticamente
def get_settings():
    """Obter configurações com detecção automática de ambiente"""
    # Verificar se estamos em ambiente de teste
    if "pytest" in os.sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
        return Settings(environment="test")
    
    # Verificar variáveis de ambiente
    environment = os.getenv("ENVIRONMENT", "development")
    return Settings(environment=environment)

# Instância global das configurações
settings = get_settings()
