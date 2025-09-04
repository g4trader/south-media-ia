from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
import os

from src.config import settings
from src.services.scheduler_service import celery_app

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    
    # Startup
    logger.info("🚀 Iniciando South Media IA API...")
    
    try:
        # Verificar configurações
        logger.info(f"📋 Configurações carregadas:")
        logger.info(f"   - Nome da App: {settings.app_name}")
        logger.info(f"   - Versão: {settings.app_version}")
        logger.info(f"   - Debug: {settings.debug}")
        logger.info(f"   - Redis URL: {settings.redis_url}")
        logger.info(f"   - Database: PostgreSQL")
        
        # Verificar conectividade com Redis
        try:
            from redis import Redis
            redis_client = Redis.from_url(settings.redis_url)
            redis_client.ping()
            logger.info("✅ Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️  Redis não disponível: {e}")
            logger.info("   Importações automáticas serão desabilitadas")
        
        # Verificar credenciais do Google
        if settings.google_application_credentials:
            if os.path.exists(settings.google_application_credentials):
                logger.info("✅ Credenciais do Google Cloud configuradas")
            else:
                logger.warning("⚠️  Arquivo de credenciais do Google não encontrado")
        else:
            logger.info("ℹ️  Credenciais do Google Cloud não configuradas")
        
        # Verificar credenciais do Google Sheets
        if settings.google_sheets_credentials_file:
            if os.path.exists(settings.google_sheets_credentials_file):
                logger.info("✅ Credenciais do Google Sheets configuradas")
            else:
                logger.warning("⚠️  Arquivo de credenciais do Google Sheets não encontrado")
        else:
            logger.info("ℹ️  Credenciais do Google Sheets não configuradas")
        
        logger.info("✅ Aplicação iniciada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando South Media IA API...")
    
    try:
        # Parar worker do Celery se estiver rodando
        try:
            celery_app.control.shutdown()
            logger.info("✅ Worker do Celery encerrado")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao encerrar Celery: {e}")
        
        logger.info("✅ Aplicação encerrada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro no encerramento: {e}")

def create_startup_events():
    """Criar eventos de inicialização para a aplicação"""
    return {
        "startup": [
            "Verificar conectividade com Redis",
            "Verificar credenciais do Google Cloud",
            "Verificar credenciais do Google Sheets",
            "Inicializar serviços de dashboard",
            "Configurar agendamento de importações"
        ],
        "shutdown": [
            "Encerrar worker do Celery",
            "Salvar estado da aplicação",
            "Fechar conexões de banco de dados"
        ]
    }

def get_system_status():
    """Obter status atual do sistema"""
    try:
        status = {
            "status": "operational",
            "services": {
                "api": "operational",
                "redis": "unknown",
                "bigquery": "unknown",
                "google_sheets": "unknown",
                "celery": "unknown"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Verificar Redis
        try:
            from redis import Redis
            redis_client = Redis.from_url(settings.redis_url)
            redis_client.ping()
            status["services"]["redis"] = "operational"
        except Exception:
            status["services"]["redis"] = "unavailable"
        
        # Verificar BigQuery
        if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
            status["services"]["bigquery"] = "configured"
        else:
            status["services"]["bigquery"] = "not_configured"
        
        # Verificar Google Sheets
        if settings.google_sheets_credentials_file and os.path.exists(settings.google_sheets_credentials_file):
            status["services"]["google_sheets"] = "configured"
        else:
            status["services"]["google_sheets"] = "not_configured"
        
        # Verificar Celery
        try:
            celery_app.control.inspect().active()
            status["services"]["celery"] = "operational"
        except Exception:
            status["services"]["celery"] = "unavailable"
        
        # Determinar status geral
        if any(service == "unavailable" for service in status["services"].values()):
            status["status"] = "degraded"
        
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

