from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CampaignType(str, Enum):
    VIDEO = "video"
    DISPLAY = "display"
    SOCIAL = "social"
    SEARCH = "search"
    HYBRID = "hybrid"

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"

class CampaignBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Nome da campanha")
    company_id: str = Field(..., description="ID da empresa proprietária da campanha")
    campaign_type: CampaignType = Field(..., description="Tipo da campanha")
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, description="Status atual da campanha")
    
    # Período da campanha
    start_date: datetime = Field(..., description="Data de início da campanha")
    end_date: datetime = Field(..., description="Data de término da campanha")
    
    # URL da planilha Google Sheets
    google_sheets_url: HttpUrl = Field(..., description="URL da planilha do Google Sheets para atualização de dados")
    spreadsheet_id: str = Field(..., description="ID da planilha do Google Sheets")
    sheet_name: str = Field(..., description="Nome da aba da planilha")
    
    # Template de dashboard
    dashboard_template: str = Field(..., description="Template de dashboard a ser usado para esta campanha")
    
    # Estratégias da campanha
    strategies: str = Field(..., min_length=10, description="Descrição das estratégias utilizadas na campanha")
    
    # Detalhes do contrato
    contract_scope: str = Field(..., description="Escopo do contrato (completions para video, impressions para display)")
    unit_cost: str = Field(..., description="Custo unitário (CPV para video, CPM para display)")
    total_budget: float = Field(..., gt=0, description="Orçamento total da campanha")
    spent_budget: float = Field(default=0, ge=0, description="Orçamento já gasto")
    
    # Canais e plataformas
    channels: List[str] = Field(default=[], description="Canais de mídia utilizados")
    platforms: List[str] = Field(default=[], description="Plataformas (Google, Facebook, TikTok, etc.)")
    
    # Metadados adicionais
    description: Optional[str] = Field(None, description="Descrição detalhada da campanha")
    objectives: Optional[List[str]] = Field(None, description="Objetivos da campanha")
    target_audience: Optional[str] = Field(None, description="Público-alvo")
    kpis: Optional[List[str]] = Field(None, description="Indicadores-chave de performance")
    
    # Configurações de atualização
    refresh_frequency: str = Field(default="daily", description="Frequência de atualização dos dados (daily, weekly, monthly)")
    auto_import: bool = Field(default=True, description="Se deve importar dados automaticamente")
    last_data_update: Optional[datetime] = Field(None, description="Última atualização dos dados")
    
    @validator('end_date')
    @classmethod
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    campaign_type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    google_sheets_url: Optional[HttpUrl] = None
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    dashboard_template: Optional[str] = None
    strategies: Optional[str] = Field(None, min_length=10)
    total_budget: Optional[float] = Field(None, gt=0)
    spent_budget: Optional[float] = Field(None, ge=0)
    channels: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    description: Optional[str] = None
    objectives: Optional[List[str]] = None
    target_audience: Optional[str] = None
    kpis: Optional[List[str]] = None
    refresh_frequency: Optional[str] = None
    auto_import: Optional[bool] = None

class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CampaignSummary(BaseModel):
    id: str
    name: str
    company_id: str
    campaign_type: CampaignType
    status: CampaignStatus
    start_date: datetime
    end_date: datetime
    dashboard_template: str
    total_budget: float
    spent_budget: float
    channels: List[str]
    platforms: List[str]
    last_data_update: Optional[datetime] = None

# Métricas de campanha (genéricas)
class CampaignMetrics(BaseModel):
    date: datetime
    campaign_id: str
    
    # Métricas básicas
    impressions: int = Field(default=0, description="Número de impressões")
    clicks: int = Field(default=0, description="Número de cliques")
    ctr: float = Field(default=0.0, description="Click-through rate")
    cpm: float = Field(default=0.0, description="Custo por mil impressões")
    cpc: float = Field(default=0.0, description="Custo por clique")
    investment: float = Field(default=0.0, description="Investimento realizado")
    
    # Métricas específicas por tipo
    video_metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas específicas para campanhas de vídeo")
    social_metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas específicas para campanhas sociais")
    search_metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas específicas para campanhas de busca")
    
    # Metadados
    creative: Optional[str] = Field(None, description="Criativo utilizado")
    placement: Optional[str] = Field(None, description="Posicionamento")
    device: Optional[str] = Field(None, description="Dispositivo")
    location: Optional[str] = Field(None, description="Localização")

class CampaignMetricsCreate(CampaignMetrics):
    pass

class CampaignMetricsResponse(CampaignMetrics):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Configuração de importação do Google Sheets
class SheetsIntegration(BaseModel):
    campaign_id: str
    spreadsheet_id: str
    sheet_name: str
    range_name: Optional[str] = Field(None, description="Range específico da planilha")
    
    # Mapeamento de colunas
    column_mapping: Dict[str, str] = Field(default={}, description="Mapeia colunas do sheet para campos do sistema")
    
    # Configurações de importação
    update_frequency: str = Field(default="daily", description="Frequência de atualização (daily, weekly, monthly)")
    last_updated: Optional[datetime] = Field(None, description="Última atualização")
    auto_import: bool = Field(default=True, description="Importação automática")
    
    # Configurações de validação
    required_columns: List[str] = Field(default=[], description="Colunas obrigatórias")
    date_format: str = Field(default="%Y-%m-%d", description="Formato da data")
    number_format: str = Field(default="en_US", description="Formato dos números")

class SheetsIntegrationCreate(SheetsIntegration):
    pass

class SheetsIntegrationUpdate(BaseModel):
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    range_name: Optional[str] = None
    column_mapping: Optional[Dict[str, str]] = None
    update_frequency: Optional[str] = None
    auto_import: Optional[bool] = None
    required_columns: Optional[List[str]] = None
    date_format: Optional[str] = None
    number_format: Optional[str] = None

class SheetsIntegrationResponse(SheetsIntegration):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Template de dashboard
class DashboardTemplate(BaseModel):
    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    company_id: Optional[str] = Field(None, description="ID da empresa (None = template global)")
    
    # Configuração do layout
    layout_type: str = Field(default="grid", description="Tipo de layout (grid, flexbox, masonry)")
    columns: int = Field(default=12, description="Número de colunas")
    rows: int = Field(default=8, description="Número de linhas")
    
    # Widgets disponíveis
    available_widgets: List[str] = Field(default=[], description="Lista de widgets disponíveis")
    
    # Configurações padrão
    default_charts: List[Dict[str, Any]] = Field(default=[], description="Gráficos padrão")
    default_filters: List[Dict[str, Any]] = Field(default=[], description="Filtros padrão")
    
    # Status
    is_active: bool = Field(default=True, description="Se o template está ativo")
    is_default: bool = Field(default=False, description="Se é o template padrão")

class DashboardTemplateCreate(DashboardTemplate):
    pass

class DashboardTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout_type: Optional[str] = None
    columns: Optional[int] = None
    rows: Optional[int] = None
    available_widgets: Optional[List[str]] = None
    default_charts: Optional[List[Dict[str, Any]]] = None
    default_filters: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class DashboardTemplateResponse(DashboardTemplate):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Resumo de performance da campanha
class CampaignPerformance(BaseModel):
    campaign_id: str
    campaign_name: str
    company_id: str
    
    # Métricas de performance
    total_impressions: int = 0
    total_clicks: int = 0
    total_investment: float = 0.0
    avg_ctr: float = 0.0
    avg_cpm: float = 0.0
    avg_cpc: float = 0.0
    
    # Métricas específicas por tipo
    video_completion_rate: Optional[float] = None
    social_engagement_rate: Optional[float] = None
    search_quality_score: Optional[float] = None
    
    # Status e progresso
    days_active: int = 0
    budget_utilization: float = 0.0  # Porcentagem do orçamento utilizado
    performance_score: float = 0.0  # Score geral de performance
    
    # Última atualização
    last_metrics_update: Optional[datetime] = None

