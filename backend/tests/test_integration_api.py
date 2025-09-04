"""
Testes de integração para API do sistema South Media IA
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.main import app
from src.models.user import UserRole, UserStatus, Permission
from src.models.company import CompanyStatus, CompanyType
from src.models.campaign import CampaignType, CampaignStatus


class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""
    
    def test_login_success(self, test_client: TestClient, mock_user_data):
        """Testar login bem-sucedido"""
        with patch('src.services.auth_service.AuthService.authenticate_user') as mock_auth, \
             patch('src.services.auth_service.AuthService.get_user_companies_for_token') as mock_get_companies, \
             patch('src.services.auth_service.AuthService.create_company_context_token') as mock_create_token:
            
            # Mock do authenticate_user
            mock_auth.return_value = {
                "id": mock_user_data["id"],
                "email": mock_user_data["email"],
                "role": mock_user_data["role"].value,  # Usar .value para o enum
                "status": mock_user_data["status"].value,  # Usar .value para o enum
                "company_id": mock_user_data["company_id"],
                "permissions": mock_user_data["permissions"]
            }
            
            # Mock do get_user_companies_for_token
            mock_get_companies.return_value = [
                {
                    "id": "test-company-001",
                    "name": "Empresa de Teste",
                    "role": "admin"
                }
            ]
            
            # Mock do create_company_context_token
            mock_create_token.return_value = "test-jwt-token"
            
            response = test_client.post("/api/auth/login", json={
                "email": "test@teste.com.br",
                "password": "testpassword123",
                "company_id": "test-company-001"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_client: TestClient):
        """Testar login com credenciais inválidas"""
        with patch('src.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            response = test_client.post("/api/auth/login", json={
                "username": "invaliduser",
                "password": "wrongpassword",
                "company_id": "test-company-001"
            })
            
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert "Invalid credentials" in data["detail"]
    
    def test_login_missing_fields(self, test_client: TestClient):
        """Testar login com campos faltando"""
        response = test_client.post("/api/auth/login", json={
            "username": "testuser"
            # password e company_id faltando
        })
        
        assert response.status_code == 422
    
    def test_switch_company_success(self, test_client: TestClient, mock_auth_headers):
        """Testar troca de empresa bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.auth_service.AuthService.create_company_context_token') as mock_create_token:
                mock_create_token.return_value = "new-jwt-token"
                
                response = test_client.post("/api/auth/switch-company", json={
                    "company_id": "test-company-002"
                }, headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["access_token"] == "new-jwt-token"
    
    def test_switch_company_unauthorized(self, test_client: TestClient):
        """Testar troca de empresa sem autenticação"""
        response = test_client.post("/api/auth/switch-company", json={
            "company_id": "test-company-002"
        })
        
        assert response.status_code == 401
    
    def test_me_companies_success(self, test_client: TestClient, mock_auth_headers):
        """Testar listagem de empresas do usuário"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.auth_service.AuthService.get_user_companies_for_token') as mock_get_companies:
                mock_get_companies.return_value = [
                    {"id": "company-001", "name": "Empresa 1"},
                    {"id": "company-002", "name": "Empresa 2"}
                ]
                
                response = test_client.get("/api/auth/me/companies", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["id"] == "company-001"
                assert data[1]["id"] == "company-002"


class TestCompanyEndpoints:
    """Testes para endpoints de empresa"""
    
    def test_create_company_success(self, test_client: TestClient, mock_auth_headers, mock_company_data):
        """Testar criação de empresa bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_WRITE]
            }
            
            with patch('src.services.company_service.CompanyService.create_company') as mock_create:
                mock_create.return_value = mock_company_data
                
                company_data = {
                    "name": "Nova Empresa LTDA",
                    "description": "Nova empresa para testes",
                    "status": CompanyStatus.ACTIVE,
                    "company_type": CompanyType.CLIENT,
                    "industry": "Tecnologia",
                    "website": "https://novaempresa.com.br",
                    "email": "contato@novaempresa.com.br",
                    "phone": "+55 11 88888-8888",
                    "address": {
                        "street": "Rua Nova, 456",
                        "city": "São Paulo",
                        "state": "SP",
                        "postal_code": "04567-890",
                        "country": "Brasil"
                    },
                    "tax_id": "98.765.432/0001-10"
                }
                
                response = test_client.post("/api/companies/", json=company_data, headers=mock_auth_headers)
                
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "Nova Empresa LTDA"
                assert data["status"] == CompanyStatus.ACTIVE
    
    def test_create_company_insufficient_permissions(self, test_client: TestClient, mock_auth_headers):
        """Testar criação de empresa sem permissões suficientes"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]  # Apenas leitura
            }
            
            company_data = {
                "name": "Nova Empresa LTDA",
                "description": "Nova empresa para testes",
                "status": CompanyStatus.ACTIVE,
                "company_type": CompanyType.CLIENT,
                "industry": "Tecnologia"
            }
            
            response = test_client.post("/api/companies/", json=company_data, headers=mock_auth_headers)
            
            assert response.status_code == 403
    
    def test_list_companies_success(self, test_client: TestClient, mock_auth_headers):
        """Testar listagem de empresas bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.company_service.CompanyService.list_companies') as mock_list:
                mock_list.return_value = [
                    {"id": "company-001", "name": "Empresa 1", "status": CompanyStatus.ACTIVE},
                    {"id": "company-002", "name": "Empresa 2", "status": CompanyStatus.ACTIVE}
                ]
                
                response = test_client.get("/api/companies/", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["name"] == "Empresa 1"
                assert data[1]["name"] == "Empresa 2"
    
    def test_get_company_success(self, test_client: TestClient, mock_auth_headers, mock_company_data):
        """Testar obtenção de empresa específica bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.company_service.CompanyService.get_company') as mock_get:
                mock_get.return_value = mock_company_data
                
                response = test_client.get("/api/companies/test-company-001", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "test-company-001"
                assert data["name"] == "Empresa de Teste LTDA"
    
    def test_get_company_not_found(self, test_client: TestClient, mock_auth_headers):
        """Testar obtenção de empresa inexistente"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.company_service.CompanyService.get_company') as mock_get:
                mock_get.return_value = None
                
                response = test_client.get("/api/companies/non-existent", headers=mock_auth_headers)
                
                assert response.status_code == 404
    
    def test_update_company_success(self, test_client: TestClient, mock_auth_headers, mock_company_data):
        """Testar atualização de empresa bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_WRITE]
            }
            
            with patch('src.services.company_service.CompanyService.update_company') as mock_update:
                updated_data = mock_company_data.copy()
                updated_data["name"] = "Empresa Atualizada LTDA"
                mock_update.return_value = updated_data
                
                update_data = {
                    "name": "Empresa Atualizada LTDA",
                    "description": "Descrição atualizada"
                }
                
                response = test_client.put("/api/companies/test-company-001", json=update_data, headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Empresa Atualizada LTDA"
    
    def test_delete_company_success(self, test_client: TestClient, mock_auth_headers):
        """Testar exclusão de empresa bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_WRITE]
            }
            
            with patch('src.services.company_service.CompanyService.delete_company') as mock_delete:
                mock_delete.return_value = True
                
                response = test_client.delete("/api/companies/test-company-001", headers=mock_auth_headers)
                
                assert response.status_code == 204


class TestCampaignEndpoints:
    """Testes para endpoints de campanha"""
    
    def test_create_campaign_success(self, test_client: TestClient, mock_auth_headers, mock_campaign_data):
        """Testar criação de campanha bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_WRITE]
            }
            
            with patch('src.services.campaign_service.CampaignService.create_campaign') as mock_create:
                mock_create.return_value = mock_campaign_data
                
                campaign_data = {
                    "name": "Nova Campanha de Teste",
                    "company_id": "test-company-001",
                    "campaign_type": CampaignType.VIDEO,
                    "status": CampaignStatus.DRAFT,
                    "start_date": datetime.utcnow().isoformat(),
                    "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    "google_sheets_url": "https://docs.google.com/spreadsheets/d/new123",
                    "spreadsheet_id": "new123",
                    "sheet_name": "Dados",
                    "dashboard_template": "video_template",
                    "strategies": "Estratégia da nova campanha",
                    "contract_scope": "2000 completions",
                    "unit_cost": "CPV R$ 0.20",
                    "total_budget": 2000.0,
                    "channels": ["YouTube", "Google Display Video"],
                    "platforms": ["Google"]
                }
                
                response = test_client.post("/api/campaigns/", json=campaign_data, headers=mock_auth_headers)
                
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "Nova Campanha de Teste"
                assert data["campaign_type"] == CampaignType.VIDEO
    
    def test_create_campaign_insufficient_permissions(self, test_client: TestClient, mock_auth_headers):
        """Testar criação de campanha sem permissões suficientes"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_READ]  # Apenas leitura
            }
            
            campaign_data = {
                "name": "Nova Campanha de Teste",
                "company_id": "test-company-001",
                "campaign_type": CampaignType.VIDEO,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "google_sheets_url": "https://docs.google.com/spreadsheets/d/new123",
                "spreadsheet_id": "new123",
                "sheet_name": "Dados",
                "dashboard_template": "video_template",
                "strategies": "Estratégia da nova campanha",
                "contract_scope": "2000 completions",
                "unit_cost": "CPV R$ 0.20",
                "total_budget": 2000.0,
                "channels": ["YouTube"],
                "platforms": ["Google"]
            }
            
            response = test_client.post("/api/campaigns/", json=campaign_data, headers=mock_auth_headers)
            
            assert response.status_code == 403
    
    def test_list_campaigns_success(self, test_client: TestClient, mock_auth_headers):
        """Testar listagem de campanhas bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_READ]
            }
            
            with patch('src.services.campaign_service.CampaignService.list_campaigns') as mock_list:
                mock_list.return_value = [
                    {
                        "id": "campaign-001",
                        "name": "Campanha 1",
                        "campaign_type": CampaignType.VIDEO,
                        "status": CampaignStatus.ACTIVE,
                        "company_id": "test-company-001"
                    },
                    {
                        "id": "campaign-002",
                        "name": "Campanha 2",
                        "campaign_type": CampaignType.SOCIAL,
                        "status": CampaignStatus.PAUSED,
                        "company_id": "test-company-001"
                    }
                ]
                
                response = test_client.get("/api/campaigns/", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["name"] == "Campanha 1"
                assert data[1]["name"] == "Campanha 2"
    
    def test_list_campaigns_with_filters(self, test_client: TestClient, mock_auth_headers):
        """Testar listagem de campanhas com filtros"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_READ]
            }
            
            with patch('src.services.campaign_service.CampaignService.list_campaigns') as mock_list:
                mock_list.return_value = [
                    {
                        "id": "campaign-001",
                        "name": "Campanha de Vídeo",
                        "campaign_type": CampaignType.VIDEO,
                        "status": CampaignStatus.ACTIVE,
                        "company_id": "test-company-001"
                    }
                ]
                
                response = test_client.get(
                    "/api/campaigns/?campaign_type=video&status=active",
                    headers=mock_auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["campaign_type"] == CampaignType.VIDEO
                assert data[0]["status"] == CampaignStatus.ACTIVE
    
    def test_get_campaign_success(self, test_client: TestClient, mock_auth_headers, mock_campaign_data):
        """Testar obtenção de campanha específica bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_READ]
            }
            
            with patch('src.services.campaign_service.CampaignService.get_campaign') as mock_get:
                mock_get.return_value = mock_campaign_data
                
                response = test_client.get("/api/campaigns/test-campaign-001", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "test-campaign-001"
                assert data["name"] == "Campanha de Teste Q1 2024"
    
    def test_get_campaign_performance_success(self, test_client: TestClient, mock_auth_headers):
        """Testar obtenção de performance de campanha bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_READ]
            }
            
            with patch('src.services.campaign_service.CampaignService.get_campaign_performance') as mock_get_perf:
                mock_get_perf.return_value = {
                    "campaign_id": "test-campaign-001",
                    "campaign_name": "Campanha de Teste",
                    "company_id": "test-company-001",
                    "total_impressions": 50000,
                    "total_clicks": 2500,
                    "total_investment": 1500.0,
                    "avg_ctr": 5.0,
                    "avg_cpm": 12.0,
                    "avg_cpc": 0.60,
                    "days_active": 30,
                    "budget_utilization": 50.0,
                    "performance_score": 85.0
                }
                
                response = test_client.get("/api/campaigns/test-campaign-001/performance", headers=mock_auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["campaign_id"] == "test-campaign-001"
                assert data["total_impressions"] == 50000
                assert data["avg_ctr"] == 5.0
    
    def test_update_campaign_status_success(self, test_client: TestClient, mock_auth_headers):
        """Testar atualização de status de campanha bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.CAMPAIGN_WRITE]
            }
            
            with patch('src.services.campaign_service.CampaignService.update_campaign_status') as mock_update:
                mock_update.return_value = {
                    "id": "test-campaign-001",
                    "name": "Campanha de Teste",
                    "status": CampaignStatus.PAUSED
                }
                
                response = test_client.patch(
                    "/api/campaigns/test-campaign-001/status",
                    json={"status": CampaignStatus.PAUSED},
                    headers=mock_auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == CampaignStatus.PAUSED


class TestDashboardEndpoints:
    """Testes para endpoints de dashboard"""
    
    def test_get_campaign_dashboard_success(self, test_client: TestClient, mock_auth_headers):
        """Testar obtenção de dashboard de campanha bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.DASHBOARD_READ]
            }
            
            with patch('src.services.dashboard_service.DashboardService.generate_campaign_dashboard') as mock_generate:
                mock_generate.return_value = {
                    "dashboard_id": "dashboard-001",
                    "campaign_id": "test-campaign-001",
                    "widgets": [
                        {"type": "metric", "title": "Impressões", "value": 50000},
                        {"type": "metric", "title": "Cliques", "value": 2500}
                    ],
                    "layout": {"type": "grid", "columns": 12, "rows": 6},
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                response = test_client.get(
                    "/api/dashboards/campaign/test-campaign-001?date_range=30d",
                    headers=mock_auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["campaign_id"] == "test-campaign-001"
                assert len(data["widgets"]) == 2
                assert data["layout"]["type"] == "grid"
    
    def test_get_company_dashboard_success(self, test_client: TestClient, mock_auth_headers):
        """Testar obtenção de dashboard de empresa bem-sucedida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.DASHBOARD_READ]
            }
            
            with patch('src.services.dashboard_service.DashboardService.generate_company_dashboard') as mock_generate:
                mock_generate.return_value = {
                    "dashboard_id": "dashboard-002",
                    "company_id": "test-company-001",
                    "widgets": [
                        {"type": "summary", "title": "Total de Campanhas", "value": 5},
                        {"type": "chart", "title": "Performance por Tipo", "data": []}
                    ],
                    "layout": {"type": "grid", "columns": 12, "rows": 8},
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                response = test_client.get(
                    "/api/dashboards/company/test-company-001?date_range=30d",
                    headers=mock_auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["company_id"] == "test-company-001"
                assert len(data["widgets"]) == 2
                assert data["layout"]["type"] == "grid"


class TestAPIInfoEndpoints:
    """Testes para endpoints de informação da API"""
    
    def test_api_info_endpoint(self, test_client: TestClient):
        """Testar endpoint de informações da API"""
        response = test_client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "features" in data
        assert "endpoints" in data
        assert "campaign_types" in data
        assert "dashboard_templates" in data
    
    def test_api_status_endpoint(self, test_client: TestClient):
        """Testar endpoint de status da API"""
        response = test_client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_status" in data
        assert "redis_status" in data
        assert "bigquery_status" in data
        assert "google_sheets_status" in data
        assert "celery_status" in data
    
    def test_health_check_endpoint(self, test_client: TestClient):
        """Testar endpoint de verificação de saúde"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self, test_client: TestClient):
        """Testar endpoint raiz"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "status" in data
        assert "info" in data


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_404_not_found(self, test_client: TestClient):
        """Testar resposta 404 para endpoint inexistente"""
        response = test_client.get("/api/non-existent-endpoint")
        
        assert response.status_code == 404
    
    def test_422_validation_error(self, test_client: TestClient):
        """Testar resposta 422 para dados inválidos"""
        response = test_client.post("/api/auth/login", json={
            "username": "testuser"
            # Campos obrigatórios faltando
        })
        
        assert response.status_code == 422
    
    def test_500_internal_server_error(self, test_client: TestClient, mock_auth_headers):
        """Testar resposta 500 para erro interno"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Erro interno do servidor")
            
            response = test_client.get("/api/companies/", headers=mock_auth_headers)
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Erro interno do servidor" in data["detail"]


class TestAuthenticationMiddleware:
    """Testes para middleware de autenticação"""
    
    def test_protected_endpoint_without_auth(self, test_client: TestClient):
        """Testar endpoint protegido sem autenticação"""
        response = test_client.get("/api/companies/")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, test_client: TestClient):
        """Testar endpoint protegido com token inválido"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.get("/api/companies/", headers=headers)
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_auth(self, test_client: TestClient, mock_auth_headers):
        """Testar endpoint protegido com autenticação válida"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]
            }
            
            with patch('src.services.company_service.CompanyService.list_companies') as mock_list:
                mock_list.return_value = []
                
                response = test_client.get("/api/companies/", headers=mock_auth_headers)
                
                assert response.status_code == 200


class TestPermissionMiddleware:
    """Testes para middleware de permissões"""
    
    def test_endpoint_with_insufficient_permissions(self, test_client: TestClient, mock_auth_headers):
        """Testar endpoint com permissões insuficientes"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ]  # Apenas leitura
            }
            
            company_data = {
                "name": "Nova Empresa LTDA",
                "description": "Nova empresa para testes",
                "status": CompanyStatus.ACTIVE,
                "company_type": CompanyType.CLIENT,
                "industry": "Tecnologia"
            }
            
            response = test_client.post("/api/companies/", json=company_data, headers=mock_auth_headers)
            
            assert response.status_code == 403
    
    def test_endpoint_with_sufficient_permissions(self, test_client: TestClient, mock_auth_headers):
        """Testar endpoint com permissões suficientes"""
        with patch('src.services.auth_service.AuthService.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-001",
                "username": "testuser",
                "company_id": "test-company-001",
                "permissions": [Permission.COMPANY_READ, Permission.COMPANY_WRITE]
            }
            
            with patch('src.services.company_service.CompanyService.create_company') as mock_create:
                mock_create.return_value = {"id": "new-company", "name": "Nova Empresa"}
                
                company_data = {
                    "name": "Nova Empresa LTDA",
                    "description": "Nova empresa para testes",
                    "status": CompanyStatus.ACTIVE,
                    "company_type": CompanyType.CLIENT,
                    "industry": "Tecnologia"
                }
                
                response = test_client.post("/api/companies/", json=company_data, headers=mock_auth_headers)
                
                assert response.status_code == 201

