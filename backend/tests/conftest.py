"""
Configuração de testes para South Media IA
Inclui fixtures para pytest e configurações de teste
"""

import pytest
import asyncio
import os
import sys
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.config import settings
from src.models.user import UserRole, UserStatus, Permission
from src.models.company import CompanyStatus, CompanyType
from src.models.campaign import CampaignType, CampaignStatus

# Configurações de teste
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/1"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configurar ambiente de teste"""
    # Carregar arquivo .env.test
    from dotenv import load_dotenv
    load_dotenv(".env.test")
    
    # Forçar ambiente de teste
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    # Importar e criar tabelas
    from src.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Limpar
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Criar loop de eventos para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_client():
    """Cliente de teste FastAPI"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def test_database():
    """Banco de dados de teste"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Criar tabelas
    # TODO: Implementar criação de tabelas de teste
    
    yield engine
    
    # Limpar banco
    engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="session")
def test_session(test_database):
    """Sessão de banco de dados para testes"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_database)
    session = TestingSessionLocal()
    yield session
    session.close()

# Fixtures para dados de teste

@pytest.fixture
def mock_company_data() -> Dict[str, Any]:
    """Dados mock para empresa de teste"""
    return {
        "id": "test-company-001",
        "name": "Empresa de Teste LTDA",
        "description": "Empresa para testes automatizados",
        "status": CompanyStatus.ACTIVE,
        "company_type": CompanyType.CLIENT,
        "industry": "Tecnologia",
        "website": "https://teste.com.br",
        "email": "contato@teste.com.br",
        "phone": "+55 11 99999-9999",
        "address": {
            "street": "Rua de Teste, 123",
            "city": "São Paulo",
            "state": "SP",
            "postal_code": "01234-567",
            "country": "Brasil"
        },
        "tax_id": "12.345.678/0001-90",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_user_data() -> Dict[str, Any]:
    """Dados mock para usuário de teste"""
    return {
        "id": "test-user-001",
        "username": "testuser",
        "email": "test@teste.com.br",
        "full_name": "Usuário de Teste",
        "role": UserRole.COMPANY_ADMIN,
        "status": UserStatus.ACTIVE,
        "company_id": "test-company-001",
        "permissions": [
            Permission.COMPANY_READ,
            Permission.COMPANY_WRITE,
            Permission.USER_READ,
            Permission.USER_WRITE,
            Permission.CAMPAIGN_READ,
            Permission.CAMPAIGN_WRITE,
            Permission.DASHBOARD_READ,
            Permission.DASHBOARD_WRITE
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_campaign_data() -> Dict[str, Any]:
    """Dados mock para campanha de teste"""
    return {
        "id": "test-campaign-001",
        "name": "Campanha de Teste Q1 2024",
        "company_id": "test-company-001",
        "campaign_type": CampaignType.VIDEO,
        "status": CampaignStatus.ACTIVE,
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=90),
        "google_sheets_url": "https://docs.google.com/spreadsheets/d/test123",
        "spreadsheet_id": "test123",
        "sheet_name": "Dados",
        "dashboard_template": "video_template",
        "strategies": "Estratégia de teste para campanha de vídeo",
        "contract_scope": "1000 completions",
        "unit_cost": "CPV R$ 0.15",
        "total_budget": 1500.0,
        "spent_budget": 750.0,
        "channels": ["YouTube", "Google Display Video"],
        "platforms": ["Google"],
        "description": "Campanha de teste para validação do sistema",
        "objectives": ["Awareness", "Consideration"],
        "target_audience": "Jovens 18-35 interessados em tecnologia",
        "kpis": ["CTR", "CPV", "Completion Rate"],
        "refresh_frequency": "daily",
        "auto_import": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_notification_data() -> Dict[str, Any]:
    """Dados mock para notificação de teste"""
    return {
        "id": "test-notification-001",
        "title": "Teste de Notificação",
        "message": "Esta é uma notificação de teste para validação do sistema",
        "notification_type": "campaign_alert",
        "priority": "medium",
        "company_id": "test-company-001",
        "campaign_id": "test-campaign-001",
        "channels": ["email"],
        "immediate": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_alert_data() -> Dict[str, Any]:
    """Dados mock para alerta de teste"""
    return {
        "id": "test-alert-001",
        "name": "Alerta de Teste CTR",
        "description": "Alerta para monitorar CTR abaixo do esperado",
        "company_id": "test-company-001",
        "alert_type": "ctr_anomaly",
        "severity": "warning",
        "trigger_type": "threshold",
        "metric_name": "ctr",
        "condition": "less_than",
        "threshold_value": 2.0,
        "frequency": "every_hour",
        "lookback_period": "24h",
        "cooldown_period": "1h",
        "campaign_id": "test-campaign-001",
        "notification_channels": ["email"],
        "machine_learning_enabled": True,
        "trend_analysis_enabled": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_integration_data() -> Dict[str, Any]:
    """Dados mock para integração de teste"""
    return {
        "id": "test-integration-001",
        "name": "Google Ads Test",
        "description": "Integração de teste com Google Ads",
        "company_id": "test-company-001",
        "integration_type": "google_ads",
        "authentication_type": "oauth2",
        "base_url": "https://googleads.googleapis.com",
        "api_version": "v14",
        "endpoint_urls": {
            "campaigns": "/v14/customers/{customer_id}/googleAds:search",
            "metrics": "/v14/customers/{customer_id}/googleAds:search"
        },
        "credentials": {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token"
        },
        "data_sync_frequency": "every_hour",
        "sync_enabled": True,
        "is_active": True,
        "is_test_mode": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# Fixtures para autenticação

@pytest.fixture
def mock_auth_headers(mock_user_data) -> Dict[str, str]:
    """Headers de autenticação mock"""
    return {
        "Authorization": f"Bearer test-jwt-token-{mock_user_data['id']}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def mock_current_user(mock_user_data) -> Dict[str, Any]:
    """Usuário atual mock para testes"""
    return {
        "id": mock_user_data["id"],
        "username": mock_user_data["username"],
        "email": mock_user_data["email"],
        "full_name": mock_user_data["full_name"],
        "role": mock_user_data["role"],
        "status": mock_user_data["status"],
        "company_id": mock_user_data["company_id"],
        "permissions": mock_user_data["permissions"],
        "current_company_id": mock_user_data["company_id"],
        "available_companies": [mock_user_data["company_id"]]
    }

# Fixtures para mocking de serviços

@pytest.fixture
def mock_company_service():
    """Mock do CompanyService"""
    with patch('src.services.company_service.CompanyService') as mock:
        service = mock.return_value
        service.get_company.return_value = mock_company_data()
        service.list_companies.return_value = [mock_company_data()]
        service.create_company.return_value = mock_company_data()
        service.update_company.return_value = mock_company_data()
        service.delete_company.return_value = True
        yield service

@pytest.fixture
def mock_user_service():
    """Mock do UserService"""
    with patch('src.services.user_service.UserService') as mock:
        service = mock.return_value
        service.get_user.return_value = mock_user_data()
        service.list_company_users.return_value = [mock_user_data()]
        service.create_user.return_value = mock_user_data()
        service.update_user.return_value = mock_user_data()
        service.delete_user.return_value = True
        yield service

@pytest.fixture
def mock_campaign_service():
    """Mock do CampaignService"""
    with patch('src.services.campaign_service.CampaignService') as mock:
        service = mock.return_value
        service.get_campaign.return_value = mock_campaign_data()
        service.list_campaigns.return_value = [mock_campaign_data()]
        service.create_campaign.return_value = mock_campaign_data()
        service.update_campaign.return_value = mock_campaign_data()
        service.delete_campaign.return_value = True
        service.get_campaign_performance.return_value = {
            "total_impressions": 50000,
            "total_clicks": 2500,
            "avg_ctr": 5.0,
            "avg_cpm": 12.0,
            "avg_cpc": 0.60
        }
        yield service

@pytest.fixture
def mock_notification_service():
    """Mock do NotificationService"""
    with patch('src.services.notification_service.NotificationService') as mock:
        service = mock.return_value
        service.create_notification.return_value = mock_notification_data()
        service.send_notification.return_value = True
        yield service

@pytest.fixture
def mock_alert_service():
    """Mock do AlertService"""
    with patch('src.services.alert_service.AlertService') as mock:
        service = mock.return_value
        service.create_alert.return_value = mock_alert_data()
        service.check_alerts.return_value = []
        yield service

@pytest.fixture
def mock_dashboard_service():
    """Mock do DashboardService"""
    with patch('src.services.dashboard_service.DashboardService') as mock:
        service = mock.return_value
        service.generate_campaign_dashboard.return_value = {
            "dashboard_id": "test-dashboard-001",
            "campaign_id": "test-campaign-001",
            "widgets": [],
            "layout": {"type": "grid", "columns": 12, "rows": 6},
            "generated_at": datetime.utcnow()
        }
        service.generate_company_dashboard.return_value = {
            "dashboard_id": "test-dashboard-002",
            "company_id": "test-company-001",
            "widgets": [],
            "layout": {"type": "grid", "columns": 12, "rows": 8},
            "generated_at": datetime.utcnow()
        }
        yield service

# Fixtures para dados de teste em massa

@pytest.fixture
def mock_companies_bulk() -> list:
    """Lista de empresas para testes em massa"""
    companies = []
    for i in range(10):
        companies.append({
            "id": f"test-company-{i:03d}",
            "name": f"Empresa de Teste {i:03d} LTDA",
            "description": f"Empresa de teste número {i:03d}",
            "status": CompanyStatus.ACTIVE,
            "company_type": CompanyType.CLIENT,
            "industry": "Tecnologia",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    return companies

@pytest.fixture
def mock_campaigns_bulk() -> list:
    """Lista de campanhas para testes em massa"""
    campaigns = []
    campaign_types = [CampaignType.VIDEO, CampaignType.SOCIAL, CampaignType.DISPLAY]
    statuses = [CampaignStatus.ACTIVE, CampaignStatus.PAUSED, CampaignStatus.DRAFT]
    
    for i in range(20):
        campaigns.append({
            "id": f"test-campaign-{i:03d}",
            "name": f"Campanha de Teste {i:03d}",
            "company_id": f"test-company-{(i % 10):03d}",
            "campaign_type": campaign_types[i % len(campaign_types)],
            "status": statuses[i % len(statuses)],
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=90),
            "total_budget": 1000.0 + (i * 100),
            "spent_budget": (1000.0 + (i * 100)) * 0.6,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    return campaigns

@pytest.fixture
def mock_users_bulk() -> list:
    """Lista de usuários para testes em massa"""
    users = []
    roles = [UserRole.MANAGER, UserRole.ANALYST, UserRole.VIEWER]
    
    for i in range(15):
        users.append({
            "id": f"test-user-{i:03d}",
            "username": f"testuser{i:03d}",
            "email": f"test{i:03d}@teste.com.br",
            "full_name": f"Usuário de Teste {i:03d}",
            "role": roles[i % len(roles)],
            "status": UserStatus.ACTIVE,
            "company_id": f"test-company-{(i % 10):03d}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    return users

# Configurações de teste

def pytest_configure(config):
    """Configuração do pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "selenium: marks tests as selenium tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modificar itens de coleta de testes"""
    for item in items:
        # Marcar testes de integração
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Marcar testes E2E
        if "test_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Marcar testes Selenium
        if "test_selenium" in item.nodeid:
            item.add_marker(pytest.mark.selenium)
        
        # Marcar testes lentos
        if "test_bulk" in item.nodeid or "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)

