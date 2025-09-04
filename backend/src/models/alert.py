from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json

class AlertType(str, Enum):
    """Tipos de alerta disponíveis"""
    PERFORMANCE_DROP = "performance_drop"
    BUDGET_OVERSPEND = "budget_overspend"
    CTR_ANOMALY = "ctr_anomaly"
    CONVERSION_DROP = "conversion_drop"
    COST_SPIKE = "cost_spike"
    REACH_DECLINE = "reach_decline"
    ENGAGEMENT_DROP = "engagement_drop"
    QUALITY_SCORE_DROP = "quality_score_drop"
    COMPETITOR_ACTIVITY = "competitor_activity"
    SEASONAL_PATTERN = "seasonal_pattern"
    MACHINE_LEARNING = "machine_learning"
    CUSTOM_THRESHOLD = "custom_threshold"

class AlertSeverity(str, Enum):
    """Níveis de severidade do alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(str, Enum):
    """Status do alerta"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    EXPIRED = "expired"

class AlertTrigger(str, Enum):
    """Tipos de gatilho para alertas"""
    THRESHOLD = "threshold"
    PERCENTAGE_CHANGE = "percentage_change"
    ABSOLUTE_CHANGE = "absolute_change"
    TREND_ANALYSIS = "trend_analysis"
    MACHINE_LEARNING = "machine_learning"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SEASONAL_COMPARISON = "seasonal_comparison"

class AlertCondition(str, Enum):
    """Condições para ativação do alerta"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUAL_TO = "equal_to"
    NOT_EQUAL_TO = "not_equal_to"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    BETWEEN = "between"
    OUTSIDE = "outside"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

class AlertFrequency(str, Enum):
    """Frequência de verificação do alerta"""
    REAL_TIME = "real_time"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_HOUR = "every_hour"
    EVERY_4_HOURS = "every_4_hours"
    DAILY = "daily"
    WEEKLY = "weekly"

class AlertBase(BaseModel):
    """Modelo base para alertas inteligentes"""
    name: str = Field(..., min_length=3, max_length=200, description="Nome do alerta")
    description: Optional[str] = Field(None, description="Descrição detalhada do alerta")
    company_id: str = Field(..., description="ID da empresa")
    
    # Configuração do alerta
    alert_type: AlertType = Field(..., description="Tipo do alerta")
    severity: AlertSeverity = Field(default=AlertSeverity.WARNING, description="Severidade do alerta")
    trigger_type: AlertTrigger = Field(..., description="Tipo de gatilho")
    
    # Condições do alerta
    metric_name: str = Field(..., description="Nome da métrica a ser monitorada")
    condition: AlertCondition = Field(..., description="Condição para ativação")
    threshold_value: Union[float, int, str] = Field(..., description="Valor do limiar")
    threshold_value_secondary: Optional[Union[float, int, str]] = Field(None, description="Valor secundário para ranges")
    
    # Configurações de tempo
    frequency: AlertFrequency = Field(default=AlertFrequency.EVERY_HOUR, description="Frequência de verificação")
    lookback_period: str = Field(default="24h", description="Período de análise (ex: 24h, 7d, 30d)")
    cooldown_period: str = Field(default="1h", description="Período de resfriamento entre alertas")
    
    # Configurações de campanha
    campaign_id: Optional[str] = Field(None, description="ID da campanha específica (None = todas)")
    campaign_type: Optional[str] = Field(None, description="Tipo de campanha para filtrar")
    
    # Configurações de notificação
    notification_channels: List[str] = Field(default=["email"], description="Canais de notificação")
    recipients: List[str] = Field(default=[], description="IDs dos usuários que receberão o alerta")
    role_filter: Optional[str] = Field(None, description="Filtrar por role específico")
    
    # Configurações avançadas
    machine_learning_enabled: bool = Field(default=False, description="Usar ML para detecção de anomalias")
    trend_analysis_enabled: bool = Field(default=False, description="Analisar tendências históricas")
    competitor_analysis_enabled: bool = Field(default=False, description="Analisar atividade de concorrentes")
    seasonal_adjustment_enabled: bool = Field(default=False, description="Ajustar por sazonalidade")
    
    # Parâmetros de ML
    ml_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Limiar de confiança do ML")
    ml_training_data_days: Optional[int] = Field(None, ge=7, description="Dias de dados para treinamento")
    
    # Status
    is_active: bool = Field(default=True, description="Se o alerta está ativo")
    is_template: bool = Field(default=False, description="Se é um template reutilizável")

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    """Modelo para atualização de alertas"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    trigger_type: Optional[AlertTrigger] = None
    metric_name: Optional[str] = None
    condition: Optional[AlertCondition] = None
    threshold_value: Optional[Union[float, int, str]] = None
    threshold_value_secondary: Optional[Union[float, int, str]] = None
    frequency: Optional[AlertFrequency] = None
    lookback_period: Optional[str] = None
    cooldown_period: Optional[str] = None
    campaign_id: Optional[str] = None
    campaign_type: Optional[str] = None
    notification_channels: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    role_filter: Optional[str] = None
    machine_learning_enabled: Optional[bool] = None
    trend_analysis_enabled: Optional[bool] = None
    competitor_analysis_enabled: Optional[bool] = None
    seasonal_adjustment_enabled: Optional[bool] = None
    ml_confidence_threshold: Optional[float] = None
    ml_training_data_days: Optional[int] = None
    is_active: Optional[bool] = None
    is_template: Optional[bool] = None

class AlertResponse(AlertBase):
    """Modelo de resposta para alertas"""
    id: str
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = Field(default=0, description="Número de vezes que foi acionado")
    last_checked: Optional[datetime] = None
    next_check: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AlertSummary(BaseModel):
    """Resumo de alerta para listagem"""
    id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    company_id: str
    campaign_id: Optional[str] = None
    metric_name: str
    last_triggered: Optional[datetime] = None
    trigger_count: int
    is_active: bool
    created_at: datetime

# Modelos para instâncias de alerta (quando um alerta é acionado)

class AlertInstance(BaseModel):
    """Instância de um alerta acionado"""
    alert_id: str = Field(..., description="ID do alerta")
    company_id: str = Field(..., description="ID da empresa")
    campaign_id: Optional[str] = Field(None, description="ID da campanha")
    
    # Dados do acionamento
    triggered_at: datetime = Field(..., description="Data/hora do acionamento")
    metric_value: Union[float, int, str] = Field(..., description="Valor atual da métrica")
    threshold_value: Union[float, int, str] = Field(..., description="Valor do limiar")
    deviation_percentage: float = Field(..., description="Percentual de desvio")
    
    # Contexto do alerta
    context_data: Dict[str, Any] = Field(default={}, description="Dados contextuais do alerta")
    historical_data: Optional[List[Dict[str, Any]]] = Field(None, description="Dados históricos para análise")
    ml_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confiança do ML")
    
    # Status da instância
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    acknowledged_by: Optional[str] = Field(None, description="ID do usuário que reconheceu")
    acknowledged_at: Optional[datetime] = Field(None, description="Data/hora do reconhecimento")
    resolved_by: Optional[str] = Field(None, description="ID do usuário que resolveu")
    resolved_at: Optional[datetime] = Field(None, description="Data/hora da resolução")
    resolution_notes: Optional[str] = Field(None, description="Notas sobre a resolução")
    
    # Notificações enviadas
    notifications_sent: List[str] = Field(default=[], description="IDs das notificações enviadas")
    notification_channels: List[str] = Field(default=[], description="Canais de notificação utilizados")

class AlertInstanceCreate(AlertInstance):
    pass

class AlertInstanceResponse(AlertInstance):
    """Modelo de resposta para instâncias de alerta"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Modelos para análise de ML e tendências

class MLModelConfig(BaseModel):
    """Configuração do modelo de machine learning"""
    model_type: str = Field(..., description="Tipo do modelo (isolation_forest, lof, autoencoder)")
    algorithm: str = Field(..., description="Algoritmo específico")
    parameters: Dict[str, Any] = Field(default={}, description="Parâmetros do modelo")
    
    # Configurações de treinamento
    training_window_days: int = Field(default=30, description="Janela de treinamento em dias")
    retrain_frequency_days: int = Field(default=7, description="Frequência de retreinamento")
    min_data_points: int = Field(default=100, description="Mínimo de pontos para treinamento")
    
    # Configurações de performance
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Limiar de confiança")
    false_positive_rate: float = Field(default=0.05, ge=0.0, le=1.0, description="Taxa de falso positivo aceitável")
    
    # Status do modelo
    is_trained: bool = Field(default=False, description="Se o modelo foi treinado")
    last_trained: Optional[datetime] = Field(None, description="Última data de treinamento")
    training_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Acurácia do treinamento")
    validation_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Acurácia da validação")

class TrendAnalysis(BaseModel):
    """Análise de tendências para alertas"""
    metric_name: str = Field(..., description="Nome da métrica analisada")
    analysis_period: str = Field(..., description="Período de análise")
    
    # Dados da tendência
    trend_direction: str = Field(..., description="Direção da tendência (up, down, stable)")
    trend_strength: float = Field(..., ge=0.0, le=1.0, description="Força da tendência")
    trend_confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da análise")
    
    # Estatísticas
    current_value: Union[float, int] = Field(..., description="Valor atual")
    average_value: Union[float, int] = Field(..., description="Valor médio no período")
    standard_deviation: Union[float, int] = Field(..., description="Desvio padrão")
    min_value: Union[float, int] = Field(..., description="Valor mínimo no período")
    max_value: Union[float, int] = Field(..., description="Valor máximo no período")
    
    # Análise sazonal
    seasonal_pattern: Optional[str] = Field(None, description="Padrão sazonal identificado")
    seasonal_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="Força do padrão sazonal")
    
    # Comparação com períodos anteriores
    previous_period_comparison: Optional[Dict[str, Any]] = Field(None, description="Comparação com período anterior")
    year_over_year_change: Optional[float] = Field(None, description="Mudança ano sobre ano")

class CompetitorAnalysis(BaseModel):
    """Análise de concorrentes para alertas"""
    competitor_name: str = Field(..., description="Nome do concorrente")
    analysis_date: datetime = Field(..., description="Data da análise")
    
    # Métricas do concorrente
    competitor_metrics: Dict[str, Union[float, int, str]] = Field(..., description="Métricas do concorrente")
    market_share: Optional[float] = Field(None, ge=0.0, le=1.0, description="Market share estimado")
    
    # Comparação com nossa empresa
    comparison_metrics: Dict[str, Dict[str, Union[float, int, str]]] = Field(..., description="Métricas comparativas")
    competitive_advantage: Optional[str] = Field(None, description="Vantagem competitiva identificada")
    threat_level: str = Field(..., description="Nível de ameaça (low, medium, high, critical)")
    
    # Análise de campanhas
    active_campaigns: List[Dict[str, Any]] = Field(default=[], description="Campanhas ativas do concorrente")
    estimated_budget: Optional[float] = Field(None, description="Orçamento estimado")
    target_audience: Optional[str] = Field(None, description="Público-alvo identificado")

# Modelos para configurações de alerta

class AlertRule(BaseModel):
    """Regra de alerta com condições complexas"""
    name: str = Field(..., description="Nome da regra")
    description: Optional[str] = Field(None, description="Descrição da regra")
    company_id: str = Field(..., description="ID da empresa")
    
    # Condições da regra
    conditions: List[Dict[str, Any]] = Field(..., description="Lista de condições (AND/OR)")
    logical_operator: str = Field(default="AND", description="Operador lógico entre condições")
    
    # Ações da regra
    actions: List[Dict[str, Any]] = Field(..., description="Ações a serem executadas")
    alert_template_id: Optional[str] = Field(None, description="ID do template de alerta")
    
    # Configurações
    priority: int = Field(default=1, ge=1, le=10, description="Prioridade da regra")
    is_active: bool = Field(default=True, description="Se a regra está ativa")
    execution_order: int = Field(default=1, description="Ordem de execução")

class AlertRuleCreate(AlertRule):
    pass

class AlertRuleResponse(AlertRule):
    """Modelo de resposta para regras de alerta"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = Field(default=0, description="Número de execuções")
    
    class Config:
        from_attributes = True

# Modelos para histórico e estatísticas

class AlertStatistics(BaseModel):
    """Estatísticas de alertas"""
    company_id: str = Field(..., description="ID da empresa")
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    # Contadores
    total_alerts: int = Field(default=0, description="Total de alertas no período")
    active_alerts: int = Field(default=0, description="Alertas ativos")
    resolved_alerts: int = Field(default=0, description="Alertas resolvidos")
    false_positives: int = Field(default=0, description="Falsos positivos")
    
    # Métricas por tipo
    alerts_by_type: Dict[str, int] = Field(default={}, description="Alertas por tipo")
    alerts_by_severity: Dict[str, int] = Field(default={}, description="Alertas por severidade")
    alerts_by_status: Dict[str, int] = Field(default={}, description="Alertas por status")
    
    # Tempo de resposta
    avg_time_to_acknowledge: Optional[float] = Field(None, description="Tempo médio para reconhecimento (minutos)")
    avg_time_to_resolve: Optional[float] = Field(None, description="Tempo médio para resolução (minutos)")
    
    # Performance do ML
    ml_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Acurácia do ML")
    false_positive_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Taxa de falso positivo")

class AlertStatisticsResponse(AlertStatistics):
    """Modelo de resposta para estatísticas de alertas"""
    id: str
    generated_at: datetime
    
    class Config:
        from_attributes = True

