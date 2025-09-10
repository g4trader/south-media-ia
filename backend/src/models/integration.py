from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json

class IntegrationType(str, Enum):
    """Tipos de integração disponíveis"""
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    INSTAGRAM_ADS = "instagram_ads"
    TIKTOK_ADS = "tiktok_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TWITTER_ADS = "twitter_ads"
    GOOGLE_ANALYTICS = "google_analytics"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    GOOGLE_SHEETS = "google_sheets"
    GOOGLE_BIGQUERY = "google_bigquery"
    CUSTOM_API = "custom_api"
    WEBHOOK = "webhook"

class IntegrationStatus(str, Enum):
    """Status da integração"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    MAINTENANCE = "maintenance"

class AuthenticationType(str, Enum):
    """Tipos de autenticação"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"
    USERNAME_PASSWORD = "username_password"
    TOKEN = "token"
    CUSTOM = "custom"

class DataSyncFrequency(str, Enum):
    """Frequência de sincronização de dados"""
    REAL_TIME = "real_time"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_HOUR = "every_hour"
    EVERY_4_HOURS = "every_4_hours"
    DAILY = "daily"
    WEEKLY = "weekly"
    ON_DEMAND = "on_demand"

class IntegrationBase(BaseModel):
    """Modelo base para integrações externas"""
    name: str = Field(..., min_length=3, max_length=200, description="Nome da integração")
    description: Optional[str] = Field(None, description="Descrição da integração")
    company_id: str = Field(..., description="ID da empresa")
    
    # Configuração da integração
    integration_type: IntegrationType = Field(..., description="Tipo da integração")
    authentication_type: AuthenticationType = Field(..., description="Tipo de autenticação")
    
    # Configurações de conexão
    base_url: Optional[HttpUrl] = Field(None, description="URL base da API")
    api_version: Optional[str] = Field(None, description="Versão da API")
    endpoint_urls: Dict[str, str] = Field(default={}, description="URLs dos endpoints")
    
    # Configurações de autenticação
    credentials: Dict[str, Any] = Field(default={}, description="Credenciais de autenticação")
    auth_headers: Dict[str, str] = Field(default={}, description="Headers de autenticação")
    auth_params: Dict[str, Any] = Field(default={}, description="Parâmetros de autenticação")
    
    # Configurações de dados
    data_sync_frequency: DataSyncFrequency = Field(default=DataSyncFrequency.EVERY_HOUR, description="Frequência de sincronização")
    sync_enabled: bool = Field(default=True, description="Se a sincronização está habilitada")
    last_sync: Optional[datetime] = Field(None, description="Última sincronização")
    next_sync: Optional[datetime] = Field(None, description="Próxima sincronização")
    
    # Configurações de campanha
    campaign_mapping: Dict[str, str] = Field(default={}, description="Mapeamento de campanhas")
    metric_mapping: Dict[str, str] = Field(default={}, description="Mapeamento de métricas")
    
    # Configurações avançadas
    retry_enabled: bool = Field(default=True, description="Se deve tentar novamente em caso de falha")
    max_retries: int = Field(default=3, description="Número máximo de tentativas")
    retry_delay: int = Field(default=300, description="Delay entre tentativas (segundos)")
    timeout: int = Field(default=30, description="Timeout da requisição (segundos)")
    
    # Configurações de cache
    cache_enabled: bool = Field(default=True, description="Se deve usar cache")
    cache_ttl: int = Field(default=3600, description="TTL do cache (segundos)")
    
    # Status
    is_active: bool = Field(default=True, description="Se a integração está ativa")
    is_test_mode: bool = Field(default=False, description="Se está em modo de teste")

class IntegrationCreate(IntegrationBase):
    pass

class IntegrationUpdate(BaseModel):
    """Modelo para atualização de integrações"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    authentication_type: Optional[AuthenticationType] = None
    base_url: Optional[HttpUrl] = None
    api_version: Optional[str] = None
    endpoint_urls: Optional[Dict[str, str]] = None
    credentials: Optional[Dict[str, Any]] = None
    auth_headers: Optional[Dict[str, str]] = None
    auth_params: Optional[Dict[str, Any]] = None
    data_sync_frequency: Optional[DataSyncFrequency] = None
    sync_enabled: Optional[bool] = None
    campaign_mapping: Optional[Dict[str, str]] = None
    metric_mapping: Optional[Dict[str, str]] = None
    retry_enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[int] = None
    timeout: Optional[int] = None
    cache_enabled: Optional[bool] = None
    cache_ttl: Optional[int] = None
    is_active: Optional[bool] = None
    is_test_mode: Optional[bool] = None

class IntegrationResponse(IntegrationBase):
    """Modelo de resposta para integrações"""
    id: str
    status: IntegrationStatus = Field(default=IntegrationStatus.INACTIVE)
    created_at: datetime
    updated_at: datetime
    last_connection_test: Optional[datetime] = None
    connection_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Taxa de sucesso da conexão")
    total_sync_attempts: int = Field(default=0, description="Total de tentativas de sincronização")
    successful_syncs: int = Field(default=0, description="Sincronizações bem-sucedidas")
    failed_syncs: int = Field(default=0, description="Sincronizações falharam")
    
    class Config:
        from_attributes = True

class IntegrationSummary(BaseModel):
    """Resumo de integração para listagem"""
    id: str
    name: str
    integration_type: IntegrationType
    status: IntegrationStatus
    company_id: str
    is_active: bool
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    connection_success_rate: float
    created_at: datetime

# Modelos para dados sincronizados

class SyncJob(BaseModel):
    """Trabalho de sincronização de dados"""
    integration_id: str = Field(..., description="ID da integração")
    company_id: str = Field(..., description="ID da empresa")
    
    # Configuração do job
    job_type: str = Field(..., description="Tipo do job (full_sync, incremental, real_time)")
    data_types: List[str] = Field(..., description="Tipos de dados a sincronizar")
    
    # Status do job
    status: str = Field(..., description="Status do job (pending, running, completed, failed)")
    started_at: Optional[datetime] = Field(None, description="Data/hora de início")
    completed_at: Optional[datetime] = Field(None, description="Data/hora de conclusão")
    
    # Resultados
    records_processed: int = Field(default=0, description="Registros processados")
    records_created: int = Field(default=0, description="Registros criados")
    records_updated: int = Field(default=0, description="Registros atualizados")
    records_deleted: int = Field(default=0, description="Registros deletados")
    
    # Erros
    error_count: int = Field(default=0, description="Número de erros")
    error_messages: List[str] = Field(default=[], description="Mensagens de erro")
    
    # Metadados
    source_data_hash: Optional[str] = Field(None, description="Hash dos dados de origem")
    target_data_hash: Optional[str] = Field(None, description="Hash dos dados de destino")

class SyncJobCreate(SyncJob):
    pass

class SyncJobResponse(SyncJob):
    """Modelo de resposta para jobs de sincronização"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para dados específicos de cada plataforma

class GoogleAdsData(BaseModel):
    """Dados específicos do Google Ads"""
    account_id: str = Field(..., description="ID da conta do Google Ads")
    customer_id: str = Field(..., description="ID do cliente")
    
    # Métricas de campanha
    campaigns: List[Dict[str, Any]] = Field(default=[], description="Dados das campanhas")
    ad_groups: List[Dict[str, Any]] = Field(default=[], description="Dados dos grupos de anúncios")
    keywords: List[Dict[str, Any]] = Field(default=[], description="Dados das palavras-chave")
    
    # Métricas de performance
    impressions: int = Field(default=0, description="Impressões")
    clicks: int = Field(default=0, description="Cliques")
    cost: float = Field(default=0.0, description="Custo")
    conversions: int = Field(default=0, description="Conversões")
    conversion_value: float = Field(default=0.0, description="Valor das conversões")
    
    # Métricas de qualidade
    quality_score: Optional[float] = Field(None, description="Quality Score")
    avg_position: Optional[float] = Field(None, description="Posição média")
    search_impression_share: Optional[float] = Field(None, description="Share de impressões")

class FacebookAdsData(BaseModel):
    """Dados específicos do Facebook Ads"""
    ad_account_id: str = Field(..., description="ID da conta de anúncios")
    business_id: str = Field(..., description="ID do negócio")
    
    # Métricas de campanha
    campaigns: List[Dict[str, Any]] = Field(default=[], description="Dados das campanhas")
    ad_sets: List[Dict[str, Any]] = Field(default=[], description="Dados dos conjuntos de anúncios")
    ads: List[Dict[str, Any]] = Field(default=[], description="Dados dos anúncios")
    
    # Métricas de performance
    impressions: int = Field(default=0, description="Impressões")
    reach: int = Field(default=0, description="Alcance")
    clicks: int = Field(default=0, description="Cliques")
    spend: float = Field(default=0.0, description="Gasto")
    actions: List[Dict[str, Any]] = Field(default=[], description="Ações realizadas")
    
    # Métricas de engajamento
    likes: int = Field(default=0, description="Curtidas")
    shares: int = Field(default=0, description="Compartilhamentos")
    comments: int = Field(default=0, description="Comentários")
    video_views: int = Field(default=0, description="Visualizações de vídeo")

class GoogleAnalyticsData(BaseModel):
    """Dados específicos do Google Analytics"""
    property_id: str = Field(..., description="ID da propriedade")
    view_id: str = Field(..., description="ID da visualização")
    
    # Métricas de tráfego
    sessions: int = Field(default=0, description="Sessões")
    users: int = Field(default=0, description="Usuários")
    pageviews: int = Field(default=0, description="Visualizações de página")
    bounce_rate: float = Field(default=0.0, description="Taxa de rejeição")
    avg_session_duration: float = Field(default=0.0, description="Duração média da sessão")
    
    # Métricas de conversão
    goal_completions: int = Field(default=0, description="Conclusões de objetivo")
    goal_value: float = Field(default=0.0, description="Valor dos objetivos")
    ecommerce_transactions: int = Field(default=0, description="Transações de e-commerce")
    ecommerce_revenue: float = Field(default=0.0, description="Receita de e-commerce")
    
    # Dados demográficos
    demographics: Dict[str, Any] = Field(default={}, description="Dados demográficos")
    interests: Dict[str, Any] = Field(default={}, description="Interesses")
    geography: Dict[str, Any] = Field(default={}, description="Geografia")

class TikTokAdsData(BaseModel):
    """Dados específicos do TikTok Ads"""
    advertiser_id: str = Field(..., description="ID do anunciante")
    app_id: Optional[str] = Field(None, description="ID do aplicativo")
    
    # Métricas de campanha
    campaigns: List[Dict[str, Any]] = Field(default=[], description="Dados das campanhas")
    ad_groups: List[Dict[str, Any]] = Field(default=[], description="Dados dos grupos de anúncios")
    ads: List[Dict[str, Any]] = Field(default=[], description="Dados dos anúncios")
    
    # Métricas de performance
    impressions: int = Field(default=0, description="Impressões")
    clicks: int = Field(default=0, description="Cliques")
    spend: float = Field(default=0.0, description="Gasto")
    conversions: int = Field(default=0, description="Conversões")
    
    # Métricas específicas do TikTok
    video_views: int = Field(default=0, description="Visualizações de vídeo")
    video_watched_2s: int = Field(default=0, description="Vídeo assistido por 2s")
    video_watched_6s: int = Field(default=0, description="Vídeo assistido por 6s")
    video_watched_15s: int = Field(default=0, description="Vídeo assistido por 15s")
    
    # Métricas de engajamento
    likes: int = Field(default=0, description="Curtidas")
    shares: int = Field(default=0, description="Compartilhamentos")
    comments: int = Field(default=0, description="Comentários")
    profile_visits: int = Field(default=0, description="Visitas ao perfil")

# Modelos para configurações de API

class APIConfig(BaseModel):
    """Configuração de API para integrações"""
    base_url: HttpUrl = Field(..., description="URL base da API")
    api_key: Optional[str] = Field(None, description="Chave da API")
    api_secret: Optional[str] = Field(None, description="Segredo da API")
    
    # Configurações de rate limiting
    rate_limit_requests: int = Field(default=100, description="Número de requisições por período")
    rate_limit_period: int = Field(default=3600, description="Período do rate limit (segundos)")
    
    # Configurações de autenticação
    auth_endpoint: Optional[str] = Field(None, description="Endpoint de autenticação")
    token_endpoint: Optional[str] = Field(None, description="Endpoint de token")
    refresh_endpoint: Optional[str] = Field(None, description="Endpoint de refresh")
    
    # Configurações de headers
    default_headers: Dict[str, str] = Field(default={}, description="Headers padrão")
    auth_headers: Dict[str, str] = Field(default={}, description="Headers de autenticação")
    
    # Configurações de timeout
    connection_timeout: int = Field(default=30, description="Timeout de conexão (segundos)")
    read_timeout: int = Field(default=30, description="Timeout de leitura (segundos)")
    
    # Configurações de retry
    max_retries: int = Field(default=3, description="Número máximo de tentativas")
    retry_delay: int = Field(default=1, description="Delay entre tentativas (segundos)")
    backoff_factor: float = Field(default=2.0, description="Fator de backoff exponencial")

class APIConfigCreate(APIConfig):
    pass

class APIConfigResponse(APIConfig):
    """Modelo de resposta para configurações de API"""
    id: str
    integration_id: str
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = Field(default=0, description="Número de usos")
    
    class Config:
        from_attributes = True

# Modelos para logs de integração

class IntegrationLog(BaseModel):
    """Log de atividades da integração"""
    integration_id: str = Field(..., description="ID da integração")
    company_id: str = Field(..., description="ID da empresa")
    
    # Dados do log
    log_level: str = Field(..., description="Nível do log (info, warning, error, debug)")
    message: str = Field(..., description="Mensagem do log")
    operation: str = Field(..., description="Operação realizada")
    
    # Contexto
    request_data: Optional[Dict[str, Any]] = Field(None, description="Dados da requisição")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Dados da resposta")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do erro")
    
    # Metadados
    execution_time: Optional[float] = Field(None, description="Tempo de execução (segundos)")
    user_id: Optional[str] = Field(None, description="ID do usuário que executou")
    ip_address: Optional[str] = Field(None, description="Endereço IP")

class IntegrationLogCreate(IntegrationLog):
    pass

class IntegrationLogResponse(IntegrationLog):
    """Modelo de resposta para logs de integração"""
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Modelos para webhooks

class WebhookConfig(BaseModel):
    """Configuração de webhook para integrações"""
    name: str = Field(..., description="Nome do webhook")
    description: Optional[str] = Field(None, description="Descrição do webhook")
    company_id: str = Field(..., description="ID da empresa")
    
    # Configuração do webhook
    url: HttpUrl = Field(..., description="URL do webhook")
    method: str = Field(default="POST", description="Método HTTP")
    headers: Dict[str, str] = Field(default={}, description="Headers do webhook")
    
    # Configurações de eventos
    events: List[str] = Field(..., description="Eventos que disparam o webhook")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros para eventos")
    
    # Configurações de segurança
    secret_key: Optional[str] = Field(None, description="Chave secreta para validação")
    signature_header: Optional[str] = Field(None, description="Header da assinatura")
    
    # Configurações de retry
    retry_enabled: bool = Field(default=True, description="Se deve tentar novamente em caso de falha")
    max_retries: int = Field(default=3, description="Número máximo de tentativas")
    retry_delay: int = Field(default=300, description="Delay entre tentativas (segundos)")
    
    # Status
    is_active: bool = Field(default=True, description="Se o webhook está ativo")
    last_triggered: Optional[datetime] = Field(None, description="Última vez que foi acionado")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Taxa de sucesso")

class WebhookConfigCreate(WebhookConfig):
    pass

class WebhookConfigResponse(WebhookConfig):
    """Modelo de resposta para configurações de webhook"""
    id: str
    created_at: datetime
    updated_at: datetime
    trigger_count: int = Field(default=0, description="Número de acionamentos")
    
    class Config:
        from_attributes = True



