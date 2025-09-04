"""
Testes unitários para modelos do sistema South Media IA
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.user import (
    UserRole, UserStatus, Permission, UserBase, UserCreate, UserUpdate,
    UserResponse, UserSummary
)
from src.models.company import (
    CompanyStatus, CompanyType, CompanyBase, CompanyCreate, CompanyUpdate,
    CompanyResponse, CompanySummary, UserCompanyRole, UserCompany
)
from src.models.campaign import (
    CampaignType, CampaignStatus, CampaignBase, CampaignCreate, CampaignUpdate,
    CampaignResponse, CampaignSummary, CampaignPerformance
)
from src.models.notification import (
    NotificationType, NotificationPriority, NotificationStatus, NotificationChannel,
    NotificationBase, NotificationCreate, NotificationResponse
)
from src.models.alert import (
    AlertType, AlertSeverity, AlertStatus, AlertTrigger, AlertCondition,
    AlertFrequency, AlertBase, AlertCreate, AlertResponse
)
from src.models.integration import (
    IntegrationType, IntegrationStatus, AuthenticationType, DataSyncFrequency,
    IntegrationBase, IntegrationCreate, IntegrationResponse
)


class TestUserModels:
    """Testes para modelos de usuário"""
    
    def test_user_role_enum(self):
        """Testar enum de roles de usuário"""
        assert UserRole.SUPER_ADMIN == "super_admin"
        assert UserRole.COMPANY_ADMIN == "company_admin"
        assert UserRole.MANAGER == "manager"
        assert UserRole.ANALYST == "analyst"
        assert UserRole.VIEWER == "viewer"
    
    def test_user_status_enum(self):
        """Testar enum de status de usuário"""
        assert UserStatus.ACTIVE == "active"
        assert UserStatus.INACTIVE == "inactive"
        assert UserStatus.SUSPENDED == "suspended"
        assert UserStatus.PENDING == "pending"
    
    def test_permission_enum(self):
        """Testar enum de permissões"""
        assert Permission.COMPANY_READ == "company:read"
        assert Permission.COMPANY_WRITE == "company:write"
        assert Permission.USER_READ == "user:read"
        assert Permission.USER_WRITE == "user:write"
        assert Permission.CAMPAIGN_READ == "campaign:read"
        assert Permission.CAMPAIGN_WRITE == "campaign:write"
        assert Permission.DASHBOARD_READ == "dashboard:read"
        assert Permission.DASHBOARD_WRITE == "dashboard:write"
    
    def test_user_base_validation(self):
        """Testar validação do modelo base de usuário"""
        # Dados válidos
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Usuário de Teste",
            "role": UserRole.MANAGER,
            "status": UserStatus.ACTIVE,
            "company_id": "company-001"
        }
        
        user = UserBase(**valid_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.MANAGER
    
    def test_user_base_validation_errors(self):
        """Testar erros de validação no modelo base de usuário"""
        # Username muito curto
        with pytest.raises(ValidationError):
            UserBase(
                username="ab",
                email="test@example.com",
                full_name="Usuário de Teste",
                role=UserRole.MANAGER,
                status=UserStatus.ACTIVE,
                company_id="company-001"
            )
        
        # Email inválido
        with pytest.raises(ValidationError):
            UserBase(
                username="testuser",
                email="invalid-email",
                full_name="Usuário de Teste",
                role=UserRole.MANAGER,
                status=UserStatus.ACTIVE,
                company_id="company-001"
            )
    
    def test_user_create_validation(self):
        """Testar validação do modelo de criação de usuário"""
        valid_data = {
            "username": "newuser",
            "email": "new@example.com",
            "full_name": "Novo Usuário",
            "password": "securepassword123",
            "role": UserRole.ANALYST,
            "company_id": "company-001"
        }
        
        user_create = UserCreate(**valid_data)
        assert user_create.username == "newuser"
        assert user_create.password == "securepassword123"
    
    def test_user_update_validation(self):
        """Testar validação do modelo de atualização de usuário"""
        # Todos os campos opcionais
        user_update = UserUpdate()
        assert user_update.username is None
        assert user_update.email is None
        
        # Apenas alguns campos
        user_update = UserUpdate(username="updateduser", email="updated@example.com")
        assert user_update.username == "updateduser"
        assert user_update.email == "updated@example.com"
        assert user_update.full_name is None


class TestCompanyModels:
    """Testes para modelos de empresa"""
    
    def test_company_status_enum(self):
        """Testar enum de status de empresa"""
        assert CompanyStatus.ACTIVE == "active"
        assert CompanyStatus.INACTIVE == "inactive"
        assert CompanyStatus.SUSPENDED == "suspended"
        assert CompanyStatus.PENDING == "pending"
    
    def test_company_type_enum(self):
        """Testar enum de tipo de empresa"""
        assert CompanyType.CLIENT == "client"
        assert CompanyType.AGENCY == "agency"
        assert CompanyType.PARTNER == "partner"
    
    def test_company_base_validation(self):
        """Testar validação do modelo base de empresa"""
        valid_data = {
            "name": "Empresa de Teste LTDA",
            "description": "Empresa para testes",
            "status": CompanyStatus.ACTIVE,
            "company_type": CompanyType.CLIENT,
            "industry": "Tecnologia",
            "contact_email": "contato@teste.com.br",
            "contact_phone": "+55 11 99999-9999",
            "address": "Rua de Teste, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234-567",
            "country": "Brasil"
        }
        
        company = CompanyBase(**valid_data)
        assert company.name == "Empresa de Teste LTDA"
        assert company.status == CompanyStatus.ACTIVE
        assert company.company_type == CompanyType.CLIENT
    
    def test_company_base_validation_errors(self):
        """Testar erros de validação no modelo base de empresa"""
        # Nome muito curto
        with pytest.raises(ValidationError):
            CompanyBase(
                name="A",
                description="Empresa para testes",
                status=CompanyStatus.ACTIVE,
                company_type=CompanyType.CLIENT,
                industry="Tecnologia",
                contact_email="contato@teste.com.br",
                contact_phone="+55 11 99999-9999",
                address="Rua de Teste, 123",
                city="São Paulo",
                state="SP",
                zip_code="01234-567",
                country="Brasil"
            )
        
        # Email inválido
        with pytest.raises(ValidationError):
            CompanyBase(
                name="Empresa de Teste LTDA",
                description="Empresa para testes",
                status=CompanyStatus.ACTIVE,
                company_type=CompanyType.CLIENT,
                industry="Tecnologia",
                contact_email="invalid-email",
                contact_phone="+55 11 99999-9999",
                address="Rua de Teste, 123",
                city="São Paulo",
                state="SP",
                zip_code="01234-567",
                country="Brasil"
            )
    
    def test_company_create_validation(self):
        """Testar validação do modelo de criação de empresa"""
        valid_data = {
            "name": "Nova Empresa LTDA",
            "description": "Nova empresa para testes",
            "status": CompanyStatus.ACTIVE,
            "company_type": CompanyType.CLIENT,
            "industry": "Tecnologia",
            "contact_email": "contato@novaempresa.com.br",
            "contact_phone": "+55 11 88888-8888",
            "address": "Rua Nova, 456",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "04567-890",
            "country": "Brasil"
        }
        
        company_create = CompanyCreate(**valid_data)
        assert company_create.name == "Nova Empresa LTDA"
        assert company_create.status == CompanyStatus.ACTIVE


class TestCampaignModels:
    """Testes para modelos de campanha"""
    
    def test_campaign_type_enum(self):
        """Testar enum de tipo de campanha"""
        assert CampaignType.VIDEO == "video"
        assert CampaignType.SOCIAL == "social"
        assert CampaignType.DISPLAY == "display"
        assert CampaignType.SEARCH == "search"
        assert CampaignType.HYBRID == "hybrid"
    
    def test_campaign_status_enum(self):
        """Testar enum de status de campanha"""
        assert CampaignStatus.DRAFT == "draft"
        assert CampaignStatus.ACTIVE == "active"
        assert CampaignStatus.PAUSED == "paused"
        assert CampaignStatus.COMPLETED == "completed"
        assert CampaignStatus.CANCELLED == "cancelled"
    
    def test_campaign_base_validation(self):
        """Testar validação do modelo base de campanha"""
        valid_data = {
            "name": "Campanha de Teste",
            "company_id": "company-001",
            "campaign_type": CampaignType.VIDEO,
            "status": CampaignStatus.ACTIVE,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "google_sheets_url": "https://docs.google.com/spreadsheets/d/test123",
            "spreadsheet_id": "test123",
            "sheet_name": "Dados",
            "dashboard_template": "video_template",
            "strategies": "Estratégia de teste para campanha",
            "contract_scope": "1000 completions",
            "unit_cost": "CPV R$ 0.15",
            "total_budget": 1500.0,
            "spent_budget": 0.0,
            "channels": ["YouTube"],
            "platforms": ["Google"],
            "description": "Campanha de teste",
            "objectives": ["Awareness"],
            "target_audience": "Jovens 18-35",
            "kpis": ["CTR", "CPV"],
            "refresh_frequency": "daily",
            "auto_import": True
        }
        
        campaign = CampaignBase(**valid_data)
        assert campaign.name == "Campanha de Teste"
        assert campaign.campaign_type == CampaignType.VIDEO
        assert campaign.status == CampaignStatus.ACTIVE
        assert campaign.total_budget == 1500.0
    
    def test_campaign_base_validation_errors(self):
        """Testar erros de validação no modelo base de campanha"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        # Nome muito curto
        with pytest.raises(ValidationError):
            CampaignBase(
                name="A",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=1500.0,
                channels=["YouTube"],
                platforms=["Google"]
            )
        
        # Orçamento zero (deve falhar pois é gt=0, não ge=0)
        with pytest.raises(ValidationError):
            CampaignBase(
                name="Campanha de Teste",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=0.0,
                channels=["YouTube"],
                platforms=["Google"]
            )
    
    def test_campaign_performance_validation(self):
        """Testar validação do modelo de performance de campanha"""
        valid_data = {
            "campaign_id": "campaign-001",
            "campaign_name": "Campanha de Teste",
            "company_id": "company-001",
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
        
        performance = CampaignPerformance(**valid_data)
        assert performance.campaign_id == "campaign-001"
        assert performance.total_impressions == 50000
        assert performance.avg_ctr == 5.0
        assert performance.performance_score == 85.0


class TestNotificationModels:
    """Testes para modelos de notificação"""
    
    def test_notification_type_enum(self):
        """Testar enum de tipo de notificação"""
        assert NotificationType.IMPORT_SUCCESS == "import_success"
        assert NotificationType.IMPORT_FAILURE == "import_failure"
        assert NotificationType.CAMPAIGN_ALERT == "campaign_alert"
        assert NotificationType.PERFORMANCE_UPDATE == "performance_update"
        assert NotificationType.SYSTEM_ALERT == "system_alert"
    
    def test_notification_priority_enum(self):
        """Testar enum de prioridade de notificação"""
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.MEDIUM == "medium"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.CRITICAL == "critical"
    
    def test_notification_status_enum(self):
        """Testar enum de status de notificação"""
        assert NotificationStatus.PENDING == "pending"
        assert NotificationStatus.SENT == "sent"
        assert NotificationStatus.READ == "read"
        assert NotificationStatus.FAILED == "failed"
    
    def test_notification_channel_enum(self):
        """Testar enum de canal de notificação"""
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.WEBHOOK == "webhook"
        assert NotificationChannel.SLACK == "slack"
        assert NotificationChannel.TEAMS == "teams"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.PUSH == "push"
    
    def test_notification_base_validation(self):
        """Testar validação do modelo base de notificação"""
        valid_data = {
            "title": "Título da Notificação",
            "message": "Mensagem da notificação com pelo menos 10 caracteres",
            "notification_type": NotificationType.CAMPAIGN_ALERT,
            "priority": NotificationPriority.MEDIUM,
            "company_id": "company-001",
            "channels": [NotificationChannel.EMAIL],
            "immediate": True
        }
        
        notification = NotificationBase(**valid_data)
        assert notification.title == "Título da Notificação"
        assert notification.notification_type == NotificationType.CAMPAIGN_ALERT
        assert notification.priority == NotificationPriority.MEDIUM
        assert notification.immediate is True


class TestAlertModels:
    """Testes para modelos de alerta"""
    
    def test_alert_type_enum(self):
        """Testar enum de tipo de alerta"""
        assert AlertType.PERFORMANCE_DROP == "performance_drop"
        assert AlertType.BUDGET_OVERSPEND == "budget_overspend"
        assert AlertType.CTR_ANOMALY == "ctr_anomaly"
        assert AlertType.CONVERSION_DROP == "conversion_drop"
        assert AlertType.COST_SPIKE == "cost_spike"
    
    def test_alert_severity_enum(self):
        """Testar enum de severidade de alerta"""
        assert AlertSeverity.INFO == "info"
        assert AlertSeverity.WARNING == "warning"
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.EMERGENCY == "emergency"
    
    def test_alert_trigger_enum(self):
        """Testar enum de gatilho de alerta"""
        assert AlertTrigger.THRESHOLD == "threshold"
        assert AlertTrigger.PERCENTAGE_CHANGE == "percentage_change"
        assert AlertTrigger.ABSOLUTE_CHANGE == "absolute_change"
        assert AlertTrigger.TREND_ANALYSIS == "trend_analysis"
        assert AlertTrigger.MACHINE_LEARNING == "machine_learning"
    
    def test_alert_condition_enum(self):
        """Testar enum de condição de alerta"""
        assert AlertCondition.GREATER_THAN == "greater_than"
        assert AlertCondition.LESS_THAN == "less_than"
        assert AlertCondition.EQUAL_TO == "equal_to"
        assert AlertCondition.BETWEEN == "between"
        assert AlertCondition.OUTSIDE == "outside"
    
    def test_alert_frequency_enum(self):
        """Testar enum de frequência de alerta"""
        assert AlertFrequency.REAL_TIME == "real_time"
        assert AlertFrequency.EVERY_5_MINUTES == "every_5_minutes"
        assert AlertFrequency.EVERY_HOUR == "every_hour"
        assert AlertFrequency.DAILY == "daily"
        assert AlertFrequency.WEEKLY == "weekly"
    
    def test_alert_base_validation(self):
        """Testar validação do modelo base de alerta"""
        valid_data = {
            "name": "Alerta de Teste",
            "description": "Descrição do alerta de teste",
            "company_id": "company-001",
            "alert_type": AlertType.CTR_ANOMALY,
            "severity": AlertSeverity.WARNING,
            "trigger_type": AlertTrigger.THRESHOLD,
            "metric_name": "ctr",
            "condition": AlertCondition.LESS_THAN,
            "threshold_value": 2.0,
            "frequency": AlertFrequency.EVERY_HOUR,
            "lookback_period": "24h",
            "cooldown_period": "1h",
            "notification_channels": [NotificationChannel.EMAIL],
            "machine_learning_enabled": True,
            "trend_analysis_enabled": True,
            "is_active": True
        }
        
        alert = AlertBase(**valid_data)
        assert alert.name == "Alerta de Teste"
        assert alert.alert_type == AlertType.CTR_ANOMALY
        assert alert.severity == AlertSeverity.WARNING
        assert alert.machine_learning_enabled is True


class TestIntegrationModels:
    """Testes para modelos de integração"""
    
    def test_integration_type_enum(self):
        """Testar enum de tipo de integração"""
        assert IntegrationType.GOOGLE_ADS == "google_ads"
        assert IntegrationType.FACEBOOK_ADS == "facebook_ads"
        assert IntegrationType.INSTAGRAM_ADS == "instagram_ads"
        assert IntegrationType.TIKTOK_ADS == "tiktok_ads"
        assert IntegrationType.GOOGLE_ANALYTICS == "google_analytics"
    
    def test_integration_status_enum(self):
        """Testar enum de status de integração"""
        assert IntegrationStatus.ACTIVE == "active"
        assert IntegrationStatus.INACTIVE == "inactive"
        assert IntegrationStatus.ERROR == "error"
        assert IntegrationStatus.CONNECTING == "connecting"
        assert IntegrationStatus.DISCONNECTED == "disconnected"
    
    def test_authentication_type_enum(self):
        """Testar enum de tipo de autenticação"""
        assert AuthenticationType.OAUTH2 == "oauth2"
        assert AuthenticationType.API_KEY == "api_key"
        assert AuthenticationType.SERVICE_ACCOUNT == "service_account"
        assert AuthenticationType.USERNAME_PASSWORD == "username_password"
        assert AuthenticationType.TOKEN == "token"
    
    def test_data_sync_frequency_enum(self):
        """Testar enum de frequência de sincronização"""
        assert DataSyncFrequency.REAL_TIME == "real_time"
        assert DataSyncFrequency.EVERY_5_MINUTES == "every_5_minutes"
        assert DataSyncFrequency.EVERY_HOUR == "every_hour"
        assert DataSyncFrequency.DAILY == "daily"
        assert DataSyncFrequency.WEEKLY == "weekly"
    
    def test_integration_base_validation(self):
        """Testar validação do modelo base de integração"""
        valid_data = {
            "name": "Integração de Teste",
            "description": "Descrição da integração de teste",
            "company_id": "company-001",
            "integration_type": IntegrationType.GOOGLE_ADS,
            "authentication_type": AuthenticationType.OAUTH2,
            "base_url": "https://googleads.googleapis.com",
            "api_version": "v14",
            "endpoint_urls": {
                "campaigns": "/v14/customers/{customer_id}/googleAds:search"
            },
            "credentials": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret"
            },
            "data_sync_frequency": DataSyncFrequency.EVERY_HOUR,
            "sync_enabled": True,
            "retry_enabled": True,
            "max_retries": 3,
            "timeout": 30,
            "cache_enabled": True,
            "cache_ttl": 3600,
            "is_active": True,
            "is_test_mode": True
        }
        
        integration = IntegrationBase(**valid_data)
        assert integration.name == "Integração de Teste"
        assert integration.integration_type == IntegrationType.GOOGLE_ADS
        assert integration.authentication_type == AuthenticationType.OAUTH2
        assert integration.sync_enabled is True
        assert integration.is_test_mode is True


class TestModelRelationships:
    """Testes para relacionamentos entre modelos"""
    
    def test_user_company_relationship(self):
        """Testar relacionamento usuário-empresa"""
        now = datetime.utcnow()
        user_company = UserCompany(
            user_id="user-001",
            company_id="company-001",
            role=UserCompanyRole.MANAGER,
            permissions=[Permission.CAMPAIGN_READ.value, Permission.CAMPAIGN_WRITE.value],
            is_primary=True,
            created_at=now,
            updated_at=now
        )
        
        assert user_company.user_id == "user-001"
        assert user_company.company_id == "company-001"
        assert user_company.role == UserCompanyRole.MANAGER
        assert len(user_company.permissions) == 2
    
    def test_campaign_company_relationship(self):
        """Testar relacionamento campanha-empresa"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        campaign = CampaignBase(
            name="Campanha Relacionada",
            company_id="company-001",
            campaign_type=CampaignType.VIDEO,
            status=CampaignStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
            spreadsheet_id="test123",
            sheet_name="Dados",
            dashboard_template="video_template",
            strategies="Estratégia de teste",
            contract_scope="1000 completions",
            unit_cost="CPV R$ 0.15",
            total_budget=1500.0,
            channels=["YouTube"],
            platforms=["Google"]
        )
        
        assert campaign.company_id == "company-001"
        assert campaign.campaign_type == CampaignType.VIDEO


class TestModelValidation:
    """Testes para validação de modelos"""
    
    def test_required_fields_validation(self):
        """Testar validação de campos obrigatórios"""
        # Usuário sem campos obrigatórios
        with pytest.raises(ValidationError):
            UserBase()
        
        # Empresa sem campos obrigatórios
        with pytest.raises(ValidationError):
            CompanyBase()
        
        # Campanha sem campos obrigatórios
        with pytest.raises(ValidationError):
            CampaignBase()
    
    def test_field_constraints_validation(self):
        """Testar validação de restrições de campos"""
        # Username muito longo
        with pytest.raises(ValidationError):
            UserBase(
                username="a" * 51,  # Máximo 50 caracteres
                email="test@example.com",
                full_name="Usuário de Teste",
                role=UserRole.MANAGER,
                status=UserStatus.ACTIVE,
                company_id="company-001"
            )
        
        # Email inválido
        with pytest.raises(ValidationError):
            UserBase(
                username="testuser",
                email="invalid-email-format",
                full_name="Usuário de Teste",
                role=UserRole.MANAGER,
                status=UserStatus.ACTIVE,
                company_id="company-001"
            )
    
    def test_enum_validation(self):
        """Testar validação de enums"""
        # Role inválido
        with pytest.raises(ValidationError):
            UserBase(
                username="testuser",
                email="test@example.com",
                full_name="Usuário de Teste",
                role="invalid_role",
                status=UserStatus.ACTIVE,
                company_id="company-001"
            )
        
        # Status inválido
        with pytest.raises(ValidationError):
            UserBase(
                username="testuser",
                email="test@example.com",
                full_name="Usuário de Teste",
                role=UserRole.MANAGER,
                status="invalid_status",
                company_id="company-001"
            )
    
    def test_url_validation(self):
        """Testar validação de URLs"""
        # Testar URL inválida em uma campanha (que tem campo HttpUrl)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        with pytest.raises(ValidationError):
            CampaignBase(
                name="Campanha de Teste",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="invalid-url",  # URL inválida
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=1500.0,
                channels=["YouTube"],
                platforms=["Google"]
            )
    
    def test_date_validation(self):
        """Testar validação de datas"""
        # Data de fim anterior à data de início
        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=1)  # Data anterior
        
        with pytest.raises(ValidationError):
            CampaignBase(
                name="Campanha de Teste",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=1500.0,
                channels=["YouTube"],
                platforms=["Google"]
            )
    
    def test_numeric_validation(self):
        """Testar validação de campos numéricos"""
        # Orçamento zero (deve falhar pois é gt=0)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        with pytest.raises(ValidationError):
            CampaignBase(
                name="Campanha de Teste",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=0.0,  # Valor zero
                channels=["YouTube"],
                platforms=["Google"]
            )
        
        # Gasto negativo (deve falhar pois é ge=0)
        with pytest.raises(ValidationError):
            CampaignBase(
                name="Campanha de Teste",
                company_id="company-001",
                campaign_type=CampaignType.VIDEO,
                status=CampaignStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                google_sheets_url="https://docs.google.com/spreadsheets/d/test123",
                spreadsheet_id="test123",
                sheet_name="Dados",
                dashboard_template="video_template",
                strategies="Estratégia de teste",
                contract_scope="1000 completions",
                unit_cost="CPV R$ 0.15",
                total_budget=1000.0,
                spent_budget=-100.0,  # Gasto negativo
                channels=["YouTube"],
                platforms=["Google"]
            )

