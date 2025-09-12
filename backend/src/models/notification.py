from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Tipos de notificação disponíveis"""
    IMPORT_SUCCESS = "import_success"
    IMPORT_FAILURE = "import_failure"
    CAMPAIGN_ALERT = "campaign_alert"
    PERFORMANCE_UPDATE = "performance_update"
    SYSTEM_ALERT = "system_alert"
    USER_ACTION = "user_action"
    SCHEDULED_REPORT = "scheduled_report"

class NotificationPriority(str, Enum):
    """Prioridades de notificação"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    """Status da notificação"""
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"

class NotificationChannel(str, Enum):
    """Canais de notificação"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PUSH = "push"

class NotificationBase(BaseModel):
    """Modelo base para notificações"""
    title: str = Field(..., min_length=5, max_length=200, description="Título da notificação")
    message: str = Field(..., min_length=10, max_length=1000, description="Mensagem da notificação")
    notification_type: NotificationType = Field(..., description="Tipo da notificação")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridade da notificação")
    
    # Destinatários
    company_id: str = Field(..., description="ID da empresa")
    user_ids: Optional[List[str]] = Field(None, description="IDs específicos de usuários")
    role_filter: Optional[str] = Field(None, description="Filtrar por role específico")
    
    # Metadados
    campaign_id: Optional[str] = Field(None, description="ID da campanha relacionada")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais da notificação")
    
    # Configurações de entrega
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL], description="Canais de entrega")
    immediate: bool = Field(default=False, description="Enviar imediatamente")
    scheduled_at: Optional[datetime] = Field(None, description="Data/hora agendada para envio")
    
    # Configurações de repetição
    repeat: bool = Field(default=False, description="Repetir notificação")
    repeat_interval: Optional[str] = Field(None, description="Intervalo de repetição (daily, weekly, monthly)")
    repeat_until: Optional[datetime] = Field(None, description="Parar repetição em")

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    """Modelo para atualização de notificações"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    message: Optional[str] = Field(None, min_length=10, max_length=1000)
    priority: Optional[NotificationPriority] = None
    status: Optional[NotificationStatus] = None
    channels: Optional[List[NotificationChannel]] = None
    immediate: Optional[bool] = None
    scheduled_at: Optional[datetime] = None
    repeat: Optional[bool] = None
    repeat_interval: Optional[str] = None
    repeat_until: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    """Modelo de resposta para notificações"""
    id: str
    status: NotificationStatus
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationSummary(BaseModel):
    """Resumo de notificação para listagem"""
    id: str
    title: str
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    company_id: str
    campaign_id: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None

# Modelos para templates de notificação

class NotificationTemplate(BaseModel):
    """Template para notificações reutilizáveis"""
    name: str = Field(..., min_length=3, max_length=100, description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    company_id: Optional[str] = Field(None, description="ID da empresa (None = global)")
    
    # Conteúdo do template
    title_template: str = Field(..., description="Template do título com variáveis")
    message_template: str = Field(..., description="Template da mensagem com variáveis")
    
    # Configurações padrão
    notification_type: NotificationType = Field(..., description="Tipo padrão da notificação")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridade padrão")
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL], description="Canais padrão")
    
    # Variáveis disponíveis
    available_variables: List[str] = Field(default=[], description="Lista de variáveis disponíveis no template")
    
    # Status
    is_active: bool = Field(default=True, description="Se o template está ativo")
    is_default: bool = Field(default=False, description="Se é o template padrão")

class NotificationTemplateCreate(NotificationTemplate):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    channels: Optional[List[NotificationChannel]] = None
    available_variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplate):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para configurações de notificação

class NotificationSettings(BaseModel):
    """Configurações de notificação por usuário/empresa"""
    user_id: str = Field(..., description="ID do usuário")
    company_id: str = Field(..., description="ID da empresa")
    
    # Preferências de canal
    email_enabled: bool = Field(default=True, description="Notificações por email")
    webhook_enabled: bool = Field(default=False, description="Notificações por webhook")
    slack_enabled: bool = Field(default=False, description="Notificações por Slack")
    teams_enabled: bool = Field(default=False, description="Notificações por Teams")
    sms_enabled: bool = Field(default=False, description="Notificações por SMS")
    push_enabled: bool = Field(default=False, description="Notificações push")
    
    # Configurações de webhook
    webhook_url: Optional[str] = Field(None, description="URL do webhook")
    webhook_headers: Optional[Dict[str, str]] = Field(None, description="Headers do webhook")
    
    # Configurações de Slack
    slack_webhook_url: Optional[str] = Field(None, description="URL do webhook do Slack")
    slack_channel: Optional[str] = Field(None, description="Canal do Slack")
    
    # Configurações de Teams
    teams_webhook_url: Optional[str] = Field(None, description="URL do webhook do Teams")
    
    # Filtros de notificação
    min_priority: NotificationPriority = Field(default=NotificationPriority.LOW, description="Prioridade mínima para receber")
    notification_types: List[NotificationType] = Field(default=[], description="Tipos de notificação para receber (vazio = todos)")
    
    # Configurações de agendamento
    quiet_hours_start: Optional[str] = Field(None, description="Início das horas silenciosas (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Fim das horas silenciosas (HH:MM)")
    timezone: str = Field(default="America/Sao_Paulo", description="Fuso horário do usuário")

class NotificationSettingsCreate(NotificationSettings):
    pass

class NotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    slack_enabled: Optional[bool] = None
    teams_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    webhook_headers: Optional[Dict[str, str]] = None
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    min_priority: Optional[NotificationPriority] = None
    notification_types: Optional[List[NotificationType]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class NotificationSettingsResponse(NotificationSettings):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para histórico de notificações

class NotificationDelivery(BaseModel):
    """Registro de entrega de notificação"""
    notification_id: str = Field(..., description="ID da notificação")
    user_id: str = Field(..., description="ID do usuário")
    channel: NotificationChannel = Field(..., description="Canal de entrega")
    
    # Status da entrega
    status: str = Field(..., description="Status da entrega (sent, failed, pending)")
    sent_at: Optional[datetime] = Field(None, description="Data/hora do envio")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se falhou")
    
    # Metadados da entrega
    delivery_attempts: int = Field(default=1, description="Número de tentativas de entrega")
    max_attempts: int = Field(default=3, description="Número máximo de tentativas")
    next_retry: Optional[datetime] = Field(None, description="Próxima tentativa de reenvio")

class NotificationDeliveryCreate(NotificationDelivery):
    pass

class NotificationDeliveryResponse(NotificationDelivery):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para relatórios

class ReportType(str, Enum):
    """Tipos de relatório disponíveis"""
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    COMPANY_OVERVIEW = "company_overview"
    IMPORT_SUMMARY = "import_summary"
    USER_ACTIVITY = "user_activity"
    SYSTEM_HEALTH = "system_health"
    CUSTOM = "custom"

class ReportFrequency(str, Enum):
    """Frequências de relatório"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class ReportFormat(str, Enum):
    """Formatos de relatório"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"

class ReportSchedule(BaseModel):
    """Agendamento de relatórios"""
    name: str = Field(..., min_length=3, max_length=100, description="Nome do relatório")
    description: Optional[str] = Field(None, description="Descrição do relatório")
    company_id: str = Field(..., description="ID da empresa")
    
    # Configuração do relatório
    report_type: ReportType = Field(..., description="Tipo do relatório")
    frequency: ReportFrequency = Field(..., description="Frequência de geração")
    format: ReportFormat = Field(default=ReportFormat.PDF, description="Formato do relatório")
    
    # Configurações de agendamento
    is_active: bool = Field(default=True, description="Se o agendamento está ativo")
    start_date: datetime = Field(..., description="Data de início do agendamento")
    end_date: Optional[datetime] = Field(None, description="Data de fim do agendamento")
    
    # Configurações de entrega
    recipients: List[str] = Field(..., description="IDs dos usuários que receberão o relatório")
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL], description="Canais de entrega")
    
    # Configurações específicas do relatório
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parâmetros específicos do relatório")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados ao relatório")

class ReportScheduleCreate(ReportSchedule):
    pass

class ReportScheduleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    report_type: Optional[ReportType] = None
    frequency: Optional[ReportFrequency] = None
    format: Optional[ReportFormat] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    recipients: Optional[List[str]] = None
    channels: Optional[List[NotificationChannel]] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class ReportScheduleResponse(ReportSchedule):
    id: str
    created_at: datetime
    updated_at: datetime
    last_generated: Optional[datetime] = None
    next_generation: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReportExecution(BaseModel):
    """Execução de um relatório"""
    report_schedule_id: str = Field(..., description="ID do agendamento do relatório")
    company_id: str = Field(..., description="ID da empresa")
    
    # Status da execução
    status: str = Field(..., description="Status da execução (running, completed, failed)")
    started_at: datetime = Field(..., description="Data/hora de início")
    completed_at: Optional[datetime] = Field(None, description="Data/hora de conclusão")
    
    # Resultados
    file_path: Optional[str] = Field(None, description="Caminho do arquivo gerado")
    file_size: Optional[int] = Field(None, description="Tamanho do arquivo em bytes")
    records_processed: Optional[int] = Field(None, description="Número de registros processados")
    
    # Erros
    error_message: Optional[str] = Field(None, description="Mensagem de erro se falhou")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes do erro")

class ReportExecutionCreate(ReportExecution):
    pass

class ReportExecutionResponse(ReportExecution):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True




