# Importar todos os modelos
from .user import (
    UserRole, UserStatus, Permission, UserBase, UserCreate, UserUpdate, 
    UserResponse, UserSummary, PasswordChange, PasswordReset,
    PasswordResetConfirm
)

from .company import (
    CompanyStatus, CompanyType, CompanyBase, CompanyCreate, CompanyUpdate,
    CompanyResponse, CompanySummary, UserCompanyRole, 
    UserCompany, UserCompanyCreate, UserCompanyUpdate, UserCompanyResponse
)

from .campaign import (
    CampaignType, CampaignStatus, CampaignBase, CampaignCreate, CampaignUpdate,
    CampaignResponse, CampaignSummary, CampaignMetrics, CampaignMetricsCreate,
    CampaignMetricsResponse, CampaignPerformance, DashboardTemplate,
    DashboardTemplateCreate, DashboardTemplateUpdate, DashboardTemplateResponse,
    SheetsIntegration, SheetsIntegrationCreate, SheetsIntegrationUpdate,
    SheetsIntegrationResponse
)

from .notification import (
    NotificationType, NotificationPriority, NotificationStatus, NotificationChannel,
    NotificationBase, NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSummary, NotificationTemplate, NotificationTemplateCreate,
    NotificationTemplateUpdate, NotificationTemplateResponse, NotificationSettings,
    NotificationSettingsCreate, NotificationSettingsUpdate, NotificationSettingsResponse,
    NotificationDelivery, NotificationDeliveryCreate, NotificationDeliveryResponse,
    ReportType, ReportFrequency, ReportFormat, ReportSchedule, ReportScheduleCreate,
    ReportScheduleUpdate, ReportScheduleResponse, ReportExecution, ReportExecutionCreate,
    ReportExecutionResponse
)

from .alert import (
    AlertType, AlertSeverity, AlertStatus, AlertTrigger, AlertCondition, AlertFrequency,
    AlertBase, AlertCreate, AlertUpdate, AlertResponse, AlertSummary, AlertInstance,
    AlertInstanceCreate, AlertInstanceResponse, MLModelConfig, TrendAnalysis,
    CompetitorAnalysis, AlertRule, AlertRuleCreate, AlertRuleResponse,
    AlertStatistics, AlertStatisticsResponse
)

from .integration import (
    IntegrationType, IntegrationStatus, AuthenticationType, DataSyncFrequency,
    IntegrationBase, IntegrationCreate, IntegrationUpdate, IntegrationResponse,
    IntegrationSummary, SyncJob, SyncJobCreate, SyncJobResponse, GoogleAdsData,
    FacebookAdsData, GoogleAnalyticsData, TikTokAdsData, APIConfig, APIConfigCreate,
    APIConfigResponse, IntegrationLog, IntegrationLogCreate, IntegrationLogResponse,
    WebhookConfig, WebhookConfigCreate, WebhookConfigResponse
)

# Exportar todos os modelos
__all__ = [
    # User models
    "UserRole", "UserStatus", "Permission", "UserBase", "UserCreate", "UserUpdate",
    "UserResponse", "UserSummary", "UserCompanyRole", "UserCompany", "UserCompanyCreate",
    "UserCompanyUpdate", "UserCompanyResponse", "PasswordChange", "PasswordReset",
    "PasswordResetConfirm",
    
    # Company models
    "CompanyStatus", "CompanyType", "CompanyBase", "CompanyCreate", "CompanyUpdate",
    "CompanyResponse", "CompanySummary",
    
    # Campaign models
    "CampaignType", "CampaignStatus", "CampaignBase", "CampaignCreate", "CampaignUpdate",
    "CampaignResponse", "CampaignSummary", "CampaignMetrics", "CampaignMetricsCreate",
    "CampaignMetricsResponse", "CampaignPerformance", "DashboardTemplate",
    "DashboardTemplateCreate", "DashboardTemplateUpdate", "DashboardTemplateResponse",
    "SheetsIntegration", "SheetsIntegrationCreate", "SheetsIntegrationUpdate",
    "SheetsIntegrationResponse",
    
    # Notification models
    "NotificationType", "NotificationPriority", "NotificationStatus", "NotificationChannel",
    "NotificationBase", "NotificationCreate", "NotificationUpdate", "NotificationResponse",
    "NotificationSummary", "NotificationTemplate", "NotificationTemplateCreate",
    "NotificationTemplateUpdate", "NotificationTemplateResponse", "NotificationSettings",
    "NotificationSettingsCreate", "NotificationSettingsUpdate", "NotificationSettingsResponse",
    "NotificationDelivery", "NotificationDeliveryCreate", "NotificationDeliveryResponse",
    "ReportType", "ReportFrequency", "ReportFormat", "ReportSchedule", "ReportScheduleCreate",
    "ReportScheduleUpdate", "ReportScheduleResponse", "ReportExecution", "ReportExecutionCreate",
    "ReportExecutionResponse",
    
    # Alert models
    "AlertType", "AlertSeverity", "AlertStatus", "AlertTrigger", "AlertCondition", "AlertFrequency",
    "AlertBase", "AlertCreate", "AlertUpdate", "AlertResponse", "AlertSummary", "AlertInstance",
    "AlertInstanceCreate", "AlertInstanceResponse", "MLModelConfig", "TrendAnalysis",
    "CompetitorAnalysis", "AlertRule", "AlertRuleCreate", "AlertRuleResponse",
    "AlertStatistics", "AlertStatisticsResponse",
    
    # Integration models
    "IntegrationType", "IntegrationStatus", "AuthenticationType", "DataSyncFrequency",
    "IntegrationBase", "IntegrationCreate", "IntegrationUpdate", "IntegrationResponse",
    "IntegrationSummary", "SyncJob", "SyncJobCreate", "SyncJobResponse", "GoogleAdsData",
    "FacebookAdsData", "GoogleAnalyticsData", "TikTokAdsData", "APIConfig", "APIConfigCreate",
    "APIConfigResponse", "IntegrationLog", "IntegrationLogCreate", "IntegrationLogResponse",
    "WebhookConfig", "WebhookConfigCreate", "WebhookConfigResponse"
]
