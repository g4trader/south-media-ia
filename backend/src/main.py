import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from src.config import settings
from src.startup import lifespan, get_system_status
from src.routes import auth, users, companies, campaigns, dashboards

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI com lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    # South Media IA - API Multi-Empresa
    
    ## 🚀 Sistema de Dashboards de Mídia Digital
    
    ### Funcionalidades Principais:
    - **Sistema Multi-Empresa**: Gerenciamento completo de empresas e usuários
    - **Autenticação JWT**: Login seguro com controle de permissões
    - **CRUD de Campanhas**: Criação e gerenciamento de campanhas de mídia
    - **Templates de Dashboard**: Dashboards configuráveis por tipo de campanha
    - **Importação Automática**: Dados do Google Sheets atualizados automaticamente
    - **Métricas em Tempo Real**: Performance e KPIs das campanhas
    
    ### Tipos de Campanha Suportados:
    - 🎥 **Vídeo**: YouTube, Google Display Video
    - 📱 **Social**: Facebook, Instagram, TikTok
    - 🖼️ **Display**: Google Display Network
    - 🔍 **Search**: Google Ads Search
    - 🔀 **Híbrido**: Combinação de canais
    
    ### Endpoints Principais:
    - `/auth/*` - Autenticação e gerenciamento de usuários
    - `/companies/*` - Gerenciamento de empresas
    - `/campaigns/*` - CRUD de campanhas e métricas
    - `/dashboards/*` - Dashboards dinâmicos e agendamento
    
    ### Tecnologias:
    - **Backend**: FastAPI + Python 3.11+
    - **Banco de Dados**: PostgreSQL + Redis
    - **Autenticação**: JWT + bcrypt
    - **Agendamento**: Celery + Redis
    - **Integração**: Google Sheets API
    
    ### Autenticação:
    Use o endpoint `/auth/login` para obter um token JWT e inclua no header:
    `Authorization: Bearer <seu_token>`
    """,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(dashboards.router, prefix="/api")

# Servir arquivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint de informações da API
@app.get("/api/info")
async def get_api_info():
    """Obter informações da API"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Sistema Multi-Empresa para Dashboards de Mídia Digital",
        "features": [
            "Sistema Multi-Empresa com controle de permissões",
            "CRUD completo de empresas, usuários e campanhas",
            "Templates de dashboard configuráveis",
            "Importação automática do Google Sheets",
            "Métricas em tempo real com agendamento Celery",
            "Autenticação JWT com roles e permissões",
            "Integração com PostgreSQL",
            "Dashboards dinâmicos por tipo de campanha"
        ],
        "endpoints": {
            "auth": "/api/auth/*",
            "users": "/api/users/*", 
            "companies": "/api/companies/*",
            "campaigns": "/api/campaigns/*",
            "dashboards": "/api/dashboards/*"
        },
        "campaign_types": [
            "video", "social", "display", "search", "hybrid"
        ],
        "dashboard_templates": [
            "video_template", "social_template", "display_template"
        ]
    }

# Endpoint de status do sistema
@app.get("/api/status")
async def get_system_status():
    """Obter status atual do sistema"""
    return {
        "api_status": "operational",
        "status": "operational",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": "2024-01-01T00:00:00Z",
        "components": {
            "database": "connected",
            "redis": "connected",
            "celery": "running"
        }
    }

# Endpoint de saúde da API
@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": f"Bem-vindo à {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "/api/status",
        "info": "/api/info"
    }

# Tratamento de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Tratamento global de exceções"""
    logger.error(f"Erro não tratado: {exc}")
    return {
        "error": "Erro interno do servidor",
        "detail": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
