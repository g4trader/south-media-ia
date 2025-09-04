from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging
import json

from src.models.campaign import (
    CampaignResponse, CampaignMetrics, CampaignPerformance,
    DashboardTemplate, CampaignType
)
from src.services.campaign_service import CampaignService
from src.services.company_service import CompanyService

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self):
        self.campaign_service = CampaignService()
        self.company_service = CompanyService()
    
    async def generate_campaign_dashboard(
        self, 
        campaign_id: str, 
        current_user: Dict[str, Any],
        date_range: str = "30d",
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gerar dashboard dinâmico para uma campanha específica"""
        try:
            # Verificar se campanha existe
            campaign = await self.campaign_service.get_campaign(campaign_id, current_user)
            if not campaign:
                raise Exception("Campanha não encontrada")
            
            # Obter template de dashboard
            if template_id:
                template = await self.campaign_service.get_dashboard_template(template_id, current_user)
            else:
                template = await self._get_default_template(campaign.dashboard_template)
            
            if not template:
                raise Exception("Template de dashboard não encontrado")
            
            # Calcular período de dados
            start_date, end_date = self._calculate_date_range(date_range)
            
            # Obter métricas da campanha
            metrics = await self.campaign_service.get_campaign_metrics(
                campaign_id, current_user, start_date, end_date
            )
            
            # Obter performance da campanha
            performance = await self.campaign_service.get_campaign_performance(
                campaign_id, current_user
            )
            
            # Gerar widgets do dashboard
            widgets = await self._generate_dashboard_widgets(
                campaign, template, metrics, performance, date_range
            )
            
            # Gerar layout do dashboard
            layout = self._generate_dashboard_layout(template, widgets)
            
            return {
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "layout_type": template.layout_type
                },
                "date_range": date_range,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "layout": layout,
                "widgets": widgets,
                "performance": performance.dict() if performance else None,
                "last_update": datetime.utcnow(),
                "refresh_interval": 300  # 5 minutos
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard da campanha {campaign_id}: {e}")
            raise Exception(f"Falha ao gerar dashboard: {str(e)}")
    
    async def generate_company_dashboard(
        self, 
        company_id: str, 
        current_user: Dict[str, Any],
        date_range: str = "30d"
    ) -> Dict[str, Any]:
        """Gerar dashboard consolidado para uma empresa"""
        try:
            # Verificar se usuário tem acesso à empresa
            if not await self.company_service.get_company(company_id, current_user):
                raise Exception("Empresa não encontrada ou acesso negado")
            
            # Calcular período de dados
            start_date, end_date = self._calculate_date_range(date_range)
            
            # Obter campanhas da empresa
            campaigns = await self.campaign_service.list_campaigns(
                company_id, current_user, limit=1000
            )
            
            # Obter métricas consolidadas
            consolidated_metrics = await self._get_consolidated_metrics(
                company_id, start_date, end_date
            )
            
            # Gerar widgets consolidados
            widgets = await self._generate_company_widgets(
                campaigns, consolidated_metrics, date_range
            )
            
            # Layout padrão para dashboard da empresa
            layout = self._generate_company_layout(widgets)
            
            return {
                "company_id": company_id,
                "date_range": date_range,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "campaigns_count": len(campaigns),
                "layout": layout,
                "widgets": widgets,
                "consolidated_metrics": consolidated_metrics,
                "last_update": datetime.utcnow(),
                "refresh_interval": 600  # 10 minutos
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard da empresa {company_id}: {e}")
            raise Exception(f"Falha ao gerar dashboard da empresa: {str(e)}")
    
    async def _get_default_template(self, template_name: str) -> Optional[DashboardTemplate]:
        """Obter template padrão por nome"""
        try:
            # TODO: Implementar busca real no BigQuery
            # Por enquanto, usando dados mock
            
            default_templates = {
                "video_template": {
                    "id": "template-001",
                    "name": "Template de Vídeo",
                    "description": "Template otimizado para campanhas de vídeo",
                    "company_id": None,
                    "layout_type": "grid",
                    "columns": 12,
                    "rows": 8,
                    "available_widgets": ["video_player", "completion_rate", "engagement_metrics"],
                    "default_charts": [],
                    "default_filters": [],
                    "is_active": True,
                    "is_default": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "social_template": {
                    "id": "template-002",
                    "name": "Template Social",
                    "description": "Template para campanhas sociais",
                    "company_id": None,
                    "layout_type": "grid",
                    "columns": 12,
                    "rows": 6,
                    "available_widgets": ["social_feed", "engagement_rate", "reach_metrics"],
                    "default_charts": [],
                    "default_filters": [],
                    "is_active": True,
                    "is_default": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "display_template": {
                    "id": "template-003",
                    "name": "Template Display",
                    "description": "Template para campanhas de display",
                    "company_id": None,
                    "layout_type": "grid",
                    "columns": 12,
                    "rows": 8,
                    "available_widgets": ["impression_metrics", "click_metrics", "conversion_metrics"],
                    "default_charts": [],
                    "default_filters": [],
                    "is_active": True,
                    "is_default": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            
            template_data = default_templates.get(template_name)
            if template_data:
                from src.models.campaign import DashboardTemplateResponse
                return DashboardTemplateResponse(**template_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar template padrão {template_name}: {e}")
            return None
    
    def _calculate_date_range(self, date_range: str) -> tuple[date, date]:
        """Calcular período de datas baseado no range especificado"""
        try:
            end_date = date.today()
            
            if date_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif date_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif date_range == "90d":
                start_date = end_date - timedelta(days=90)
            elif date_range == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                # Padrão: 30 dias
                start_date = end_date - timedelta(days=30)
            
            return start_date, end_date
            
        except Exception as e:
            logger.error(f"Erro ao calcular período de datas: {e}")
            # Fallback para 30 dias
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            return start_date, end_date
    
    async def _generate_dashboard_widgets(
        self, 
        campaign: CampaignResponse, 
        template: DashboardTemplate, 
        metrics: List[Dict[str, Any]], 
        performance: Optional[CampaignPerformance],
        date_range: str
    ) -> List[Dict[str, Any]]:
        """Gerar widgets específicos para o dashboard da campanha"""
        try:
            widgets = []
            
            # Widget de resumo da campanha
            summary_widget = {
                "id": "campaign_summary",
                "type": "summary_card",
                "title": "Resumo da Campanha",
                "position": {"x": 0, "y": 0, "w": 4, "h": 2},
                "data": {
                    "campaign_name": campaign.name,
                    "campaign_type": campaign.campaign_type.value,
                    "status": campaign.status.value,
                    "total_budget": campaign.total_budget,
                    "spent_budget": campaign.spent_budget,
                    "budget_utilization": (campaign.spent_budget / campaign.total_budget) * 100
                }
            }
            widgets.append(summary_widget)
            
            # Widget de performance
            if performance:
                performance_widget = {
                    "id": "campaign_performance",
                    "type": "performance_metrics",
                    "title": "Métricas de Performance",
                    "position": {"x": 4, "y": 0, "w": 4, "h": 2},
                    "data": {
                        "impressions": performance.total_impressions,
                        "clicks": performance.total_clicks,
                        "ctr": performance.avg_ctr,
                        "cpm": performance.avg_cpm,
                        "cpc": performance.avg_cpc,
                        "performance_score": performance.performance_score
                    }
                }
                widgets.append(performance_widget)
            
            # Widget de gráfico de tendências
            if metrics:
                trends_widget = {
                    "id": "trends_chart",
                    "type": "line_chart",
                    "title": "Tendências de Performance",
                    "position": {"x": 0, "y": 2, "w": 8, "h": 3},
                    "data": {
                        "labels": [m["date"].strftime("%d/%m") for m in metrics],
                        "datasets": [
                            {
                                "label": "Impressões",
                                "data": [m["impressions"] for m in metrics],
                                "borderColor": "#3B82F6",
                                "backgroundColor": "rgba(59, 130, 246, 0.1)"
                            },
                            {
                                "label": "Cliques",
                                "data": [m["clicks"] for m in metrics],
                                "borderColor": "#10B981",
                                "backgroundColor": "rgba(16, 185, 129, 0.1)"
                            }
                        ]
                    }
                }
                widgets.append(trends_widget)
            
            # Widgets específicos por tipo de campanha
            if campaign.campaign_type == CampaignType.VIDEO:
                video_widgets = await self._generate_video_widgets(campaign, metrics, template)
                widgets.extend(video_widgets)
            elif campaign.campaign_type == CampaignType.SOCIAL:
                social_widgets = await self._generate_social_widgets(campaign, metrics, template)
                widgets.extend(social_widgets)
            elif campaign.campaign_type == CampaignType.DISPLAY:
                display_widgets = await self._generate_display_widgets(campaign, metrics, template)
                widgets.extend(display_widgets)
            
            # Widget de configurações
            config_widget = {
                "id": "dashboard_config",
                "type": "config_panel",
                "title": "Configurações",
                "position": {"x": 8, "y": 0, "w": 4, "h": 2},
                "data": {
                    "date_range": date_range,
                    "refresh_interval": 300,
                    "template": template.name,
                    "last_update": datetime.utcnow().isoformat()
                }
            }
            widgets.append(config_widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"Erro ao gerar widgets do dashboard: {e}")
            return []
    
    async def _generate_video_widgets(
        self, 
        campaign: CampaignResponse, 
        metrics: List[Dict[str, Any]], 
        template: DashboardTemplate
    ) -> List[Dict[str, Any]]:
        """Gerar widgets específicos para campanhas de vídeo"""
        try:
            widgets = []
            
            # Widget de taxa de conclusão
            completion_widget = {
                "id": "completion_rate",
                "type": "gauge_chart",
                "title": "Taxa de Conclusão",
                "position": {"x": 8, "y": 2, "w": 4, "h": 2},
                "data": {
                    "value": 75.0,  # TODO: Calcular valor real
                    "max": 100,
                    "label": "%",
                    "color": "#10B981"
                }
            }
            widgets.append(completion_widget)
            
            # Widget de métricas de vídeo
            video_metrics_widget = {
                "id": "video_metrics",
                "type": "metrics_grid",
                "title": "Métricas de Vídeo",
                "position": {"x": 0, "y": 5, "w": 12, "h": 3},
                "data": {
                    "metrics": [
                        {"label": "Inícios de Vídeo", "value": "125,000", "change": "+5.2%"},
                        {"label": "25% Completado", "value": "93,750", "change": "+3.8%"},
                        {"label": "50% Completado", "value": "75,000", "change": "+2.1%"},
                        {"label": "75% Completado", "value": "56,250", "change": "+1.5%"},
                        {"label": "100% Completado", "value": "37,500", "change": "+0.9%"}
                    ]
                }
            }
            widgets.append(video_metrics_widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"Erro ao gerar widgets de vídeo: {e}")
            return []
    
    async def _generate_social_widgets(
        self, 
        campaign: CampaignResponse, 
        metrics: List[Dict[str, Any]], 
        template: DashboardTemplate
    ) -> List[Dict[str, Any]]:
        """Gerar widgets específicos para campanhas sociais"""
        try:
            widgets = []
            
            # Widget de engajamento
            engagement_widget = {
                "id": "engagement_rate",
                "type": "gauge_chart",
                "title": "Taxa de Engajamento",
                "position": {"x": 8, "y": 2, "w": 4, "h": 2},
                "data": {
                    "value": 8.5,  # TODO: Calcular valor real
                    "max": 20,
                    "label": "%",
                    "color": "#F59E0B"
                }
            }
            widgets.append(engagement_widget)
            
            # Widget de métricas sociais
            social_metrics_widget = {
                "id": "social_metrics",
                "type": "metrics_grid",
                "title": "Métricas Sociais",
                "position": {"x": 0, "y": 5, "w": 12, "h": 3},
                "data": {
                    "metrics": [
                        {"label": "Alcance", "value": "2.5M", "change": "+12.3%"},
                        {"label": "Impressões", "value": "8.2M", "change": "+8.7%"},
                        {"label": "Curtidas", "value": "125K", "change": "+15.2%"},
                        {"label": "Comentários", "value": "18K", "change": "+22.1%"},
                        {"label": "Compartilhamentos", "value": "8.5K", "change": "+18.9%"}
                    ]
                }
            }
            widgets.append(social_metrics_widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"Erro ao gerar widgets sociais: {e}")
            return []
    
    async def _generate_display_widgets(
        self, 
        campaign: CampaignResponse, 
        metrics: List[Dict[str, Any]], 
        template: DashboardTemplate
    ) -> List[Dict[str, Any]]:
        """Gerar widgets específicos para campanhas de display"""
        try:
            widgets = []
            
            # Widget de CTR
            ctr_widget = {
                "id": "ctr_gauge",
                "type": "gauge_chart",
                "title": "Click-Through Rate",
                "position": {"x": 8, "y": 2, "w": 4, "h": 2},
                "data": {
                    "value": 2.5,  # TODO: Calcular valor real
                    "max": 10,
                    "label": "%",
                    "color": "#8B5CF6"
                }
            }
            widgets.append(ctr_widget)
            
            # Widget de métricas de display
            display_metrics_widget = {
                "id": "display_metrics",
                "type": "metrics_grid",
                "title": "Métricas de Display",
                "position": {"x": 0, "y": 5, "w": 12, "h": 3},
                "data": {
                    "metrics": [
                        {"label": "Impressões", "value": "5.2M", "change": "+7.8%"},
                        {"label": "Cliques", "value": "130K", "change": "+12.3%"},
                        {"label": "CTR", "value": "2.5%", "change": "+4.2%"},
                        {"label": "CPM", "value": "R$ 2.85", "change": "-1.2%"},
                        {"label": "CPC", "value": "R$ 0.45", "change": "-2.1%"}
                    ]
                }
            }
            widgets.append(display_metrics_widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"Erro ao gerar widgets de display: {e}")
            return []
    
    def _generate_dashboard_layout(self, template: DashboardTemplate, widgets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gerar layout do dashboard baseado no template"""
        try:
            layout = {
                "type": template.layout_type,
                "columns": template.columns,
                "rows": template.rows,
                "widgets": []
            }
            
            # Adicionar widgets ao layout
            for widget in widgets:
                layout["widgets"].append({
                    "id": widget["id"],
                    "position": widget["position"],
                    "type": widget["type"],
                    "title": widget["title"]
                })
            
            return layout
            
        except Exception as e:
            logger.error(f"Erro ao gerar layout do dashboard: {e}")
            return {"type": "grid", "columns": 12, "rows": 8, "widgets": []}
    
    async def _get_consolidated_metrics(
        self, 
        company_id: str, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obter métricas consolidadas da empresa"""
        try:
            # TODO: Implementar busca real no BigQuery
            # Por enquanto, usando dados mock
            
            return {
                "total_campaigns": 5,
                "active_campaigns": 3,
                "total_impressions": 15000000,
                "total_clicks": 750000,
                "total_investment": 250000.0,
                "avg_ctr": 5.0,
                "avg_cpm": 16.67,
                "avg_cpc": 0.33,
                "performance_trend": "+12.5%",
                "budget_utilization": 78.5
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas consolidadas: {e}")
            return {}
    
    async def _generate_company_widgets(
        self, 
        campaigns: List[Any], 
        consolidated_metrics: Dict[str, Any], 
        date_range: str
    ) -> List[Dict[str, Any]]:
        """Gerar widgets para dashboard da empresa"""
        try:
            widgets = []
            
            # Widget de resumo da empresa
            summary_widget = {
                "id": "company_summary",
                "type": "summary_card",
                "title": "Resumo da Empresa",
                "position": {"x": 0, "y": 0, "w": 4, "h": 2},
                "data": {
                    "total_campaigns": consolidated_metrics.get("total_campaigns", 0),
                    "active_campaigns": consolidated_metrics.get("active_campaigns", 0),
                    "total_investment": consolidated_metrics.get("total_investment", 0),
                    "budget_utilization": consolidated_metrics.get("budget_utilization", 0)
                }
            }
            widgets.append(summary_widget)
            
            # Widget de performance consolidada
            performance_widget = {
                "id": "company_performance",
                "type": "performance_metrics",
                "title": "Performance Consolidada",
                "position": {"x": 4, "y": 0, "w": 4, "h": 2},
                "data": {
                    "impressions": consolidated_metrics.get("total_impressions", 0),
                    "clicks": consolidated_metrics.get("total_clicks", 0),
                    "ctr": consolidated_metrics.get("avg_ctr", 0),
                    "cpm": consolidated_metrics.get("avg_cpm", 0),
                    "cpc": consolidated_metrics.get("avg_cpc", 0),
                    "trend": consolidated_metrics.get("performance_trend", "0%")
                }
            }
            widgets.append(performance_widget)
            
            # Widget de campanhas por status
            campaigns_widget = {
                "id": "campaigns_status",
                "type": "pie_chart",
                "title": "Status das Campanhas",
                "position": {"x": 8, "y": 0, "w": 4, "h": 2},
                "data": {
                    "labels": ["Ativas", "Pausadas", "Concluídas", "Rascunho"],
                    "datasets": [{
                        "data": [3, 1, 1, 0],
                        "backgroundColor": ["#10B981", "#F59E0B", "#3B82F6", "#6B7280"]
                    }]
                }
            }
            widgets.append(campaigns_widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"Erro ao gerar widgets da empresa: {e}")
            return []
    
    def _generate_company_layout(self, widgets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gerar layout para dashboard da empresa"""
        try:
            layout = {
                "type": "grid",
                "columns": 12,
                "rows": 6,
                "widgets": []
            }
            
            # Adicionar widgets ao layout
            for widget in widgets:
                layout["widgets"].append({
                    "id": widget["id"],
                    "position": widget["position"],
                    "type": widget["type"],
                    "title": widget["title"]
                })
            
            return layout
            
        except Exception as e:
            logger.error(f"Erro ao gerar layout da empresa: {e}")
            return {"type": "grid", "columns": 12, "rows": 6, "widgets": []}

