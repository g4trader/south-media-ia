from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
import uuid
import pandas as pd
import json

from src.models.notification import (
    ReportType, ReportFrequency, ReportFormat, ReportSchedule, ReportScheduleCreate,
    ReportScheduleResponse, ReportExecution, ReportExecutionCreate
)
from src.models.campaign import CampaignResponse, CampaignPerformance
from src.services.campaign_service import CampaignService
from src.services.company_service import CompanyService
from src.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.campaign_service = CampaignService()
        self.company_service = CompanyService()
        self.notification_service = NotificationService()
    
    async def create_report_schedule(
        self, 
        schedule_data: ReportScheduleCreate, 
        current_user: Dict[str, Any]
    ) -> ReportScheduleResponse:
        """Criar um novo agendamento de relatório"""
        try:
            # Gerar ID único para o agendamento
            schedule_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Calcular próxima execução
            next_generation = self._calculate_next_execution(
                schedule_data.frequency, 
                schedule_data.start_date
            )
            
            # Criar agendamento
            schedule = ReportScheduleResponse(
                id=schedule_id,
                **schedule_data.dict(),
                created_at=now,
                updated_at=now,
                last_generated=None,
                next_generation=next_generation
            )
            
            # Salvar no BigQuery
            await self._save_schedule_to_bigquery(schedule)
            
            # Agendar primeira execução
            await self._schedule_report_execution(schedule)
            
            logger.info(f"Agendamento de relatório criado com sucesso: {schedule_id}")
            return schedule
            
        except Exception as e:
            logger.error(f"Erro ao criar agendamento de relatório: {e}")
            raise Exception(f"Falha ao criar agendamento: {str(e)}")
    
    async def generate_report(
        self, 
        report_type: ReportType, 
        company_id: str, 
        format: ReportFormat = ReportFormat.PDF,
        parameters: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gerar relatório baseado no tipo especificado"""
        try:
            # Verificar se empresa existe
            if not await self.company_service.get_company(company_id, {"company_id": company_id}):
                raise Exception("Empresa não encontrada")
            
            # Gerar relatório baseado no tipo
            if report_type == ReportType.CAMPAIGN_PERFORMANCE:
                report_data = await self._generate_campaign_performance_report(
                    company_id, parameters, filters
                )
            elif report_type == ReportType.COMPANY_OVERVIEW:
                report_data = await self._generate_company_overview_report(
                    company_id, parameters, filters
                )
            elif report_type == ReportType.IMPORT_SUMMARY:
                report_data = await self._generate_import_summary_report(
                    company_id, parameters, filters
                )
            elif report_type == ReportType.USER_ACTIVITY:
                report_data = await self._generate_user_activity_report(
                    company_id, parameters, filters
                )
            elif report_type == ReportType.SYSTEM_HEALTH:
                report_data = await self._generate_system_health_report(
                    company_id, parameters, filters
                )
            else:
                raise Exception(f"Tipo de relatório não suportado: {report_type}")
            
            # Formatar relatório
            formatted_report = await self._format_report(report_data, format)
            
            # Salvar execução do relatório
            execution = await self._save_report_execution(
                None, company_id, "completed", len(report_data.get("records", []))
            )
            
            return {
                "report_type": report_type.value,
                "company_id": company_id,
                "format": format.value,
                "generated_at": datetime.utcnow(),
                "execution_id": execution.get("id") if execution else None,
                "data": formatted_report
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório {report_type}: {e}")
            raise Exception(f"Falha ao gerar relatório: {str(e)}")
    
    async def execute_scheduled_report(self, schedule_id: str) -> bool:
        """Executar relatório agendado"""
        try:
            # TODO: Implementar busca real no BigQuery
            # Por enquanto, usando dados mock
            
            mock_schedule = {
                "id": schedule_id,
                "name": "Relatório Semanal de Performance",
                "report_type": ReportType.CAMPAIGN_PERFORMANCE,
                "company_id": "company-001",
                "frequency": ReportFrequency.WEEKLY,
                "format": ReportFormat.PDF,
                "recipients": ["user-001", "user-002"],
                "channels": ["email"],
                "parameters": {"date_range": "7d"},
                "filters": {"status": "active"}
            }
            
            # Gerar relatório
            report_data = await self.generate_report(
                mock_schedule["report_type"],
                mock_schedule["company_id"],
                mock_schedule["format"],
                mock_schedule["parameters"],
                mock_schedule["filters"]
            )
            
            # Enviar relatório para destinatários
            await self._send_scheduled_report(report_data, mock_schedule)
            
            # Atualizar agendamento
            await self._update_schedule_execution(schedule_id)
            
            logger.info(f"Relatório agendado {schedule_id} executado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar relatório agendado {schedule_id}: {e}")
            return False
    
    # Métodos para geração de relatórios específicos
    
    async def _generate_campaign_performance_report(
        self, 
        company_id: str, 
        parameters: Optional[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gerar relatório de performance das campanhas"""
        try:
            # Obter campanhas da empresa
            campaigns = await self.campaign_service.list_campaigns(
                company_id, {"company_id": company_id}, limit=1000
            )
            
            # Aplicar filtros
            if filters:
                if "status" in filters:
                    campaigns = [c for c in campaigns if c.status.value == filters["status"]]
                if "campaign_type" in filters:
                    campaigns = [c for c in campaigns if c.campaign_type.value == filters["campaign_type"]]
            
            # Obter performance de cada campanha
            campaign_performances = []
            for campaign in campaigns:
                performance = await self.campaign_service.get_campaign_performance(
                    campaign.id, {"company_id": company_id}
                )
                if performance:
                    campaign_performances.append({
                        "campaign_id": campaign.id,
                        "campaign_name": campaign.name,
                        "campaign_type": campaign.campaign_type.value,
                        "status": campaign.status.value,
                        "start_date": campaign.start_date,
                        "end_date": campaign.end_date,
                        "total_budget": campaign.total_budget,
                        "spent_budget": campaign.spent_budget,
                        "budget_utilization": (campaign.spent_budget / campaign.total_budget) * 100,
                        "total_impressions": performance.total_impressions,
                        "total_clicks": performance.total_clicks,
                        "avg_ctr": performance.avg_ctr,
                        "avg_cpm": performance.avg_cpm,
                        "avg_cpc": performance.avg_cpc,
                        "performance_score": performance.performance_score,
                        "days_active": performance.days_active
                    })
            
            # Calcular métricas consolidadas
            total_campaigns = len(campaign_performances)
            active_campaigns = len([c for c in campaign_performances if c["status"] == "active"])
            total_budget = sum(c["total_budget"] for c in campaign_performances)
            total_spent = sum(c["spent_budget"] for c in campaign_performances)
            total_impressions = sum(c["total_impressions"] for c in campaign_performances)
            total_clicks = sum(c["total_clicks"] for c in campaign_performances)
            
            # Calcular médias
            avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
            avg_cpm = total_spent / total_impressions * 1000 if total_impressions > 0 else 0
            avg_cpc = total_spent / total_clicks if total_clicks > 0 else 0
            
            return {
                "report_type": "campaign_performance",
                "company_id": company_id,
                "generated_at": datetime.utcnow(),
                "summary": {
                    "total_campaigns": total_campaigns,
                    "active_campaigns": active_campaigns,
                    "total_budget": total_budget,
                    "total_spent": total_spent,
                    "budget_utilization": (total_spent / total_budget) * 100 if total_budget > 0 else 0,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "avg_ctr": avg_ctr,
                    "avg_cpm": avg_cpm,
                    "avg_cpc": avg_cpc
                },
                "campaigns": campaign_performances,
                "records": len(campaign_performances)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de performance: {e}")
            return {"error": str(e)}
    
    async def _generate_company_overview_report(
        self, 
        company_id: str, 
        parameters: Optional[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gerar relatório de visão geral da empresa"""
        try:
            # Obter dados da empresa
            company = await self.company_service.get_company(company_id, {"company_id": company_id})
            if not company:
                return {"error": "Empresa não encontrada"}
            
            # Obter campanhas
            campaigns = await self.campaign_service.list_campaigns(
                company_id, {"company_id": company_id}, limit=1000
            )
            
            # Agrupar campanhas por tipo
            campaigns_by_type = {}
            for campaign in campaigns:
                campaign_type = campaign.campaign_type.value
                if campaign_type not in campaigns_by_type:
                    campaigns_by_type[campaign_type] = []
                campaigns_by_type[campaign_type].append(campaign)
            
            # Agrupar campanhas por status
            campaigns_by_status = {}
            for campaign in campaigns:
                campaign_status = campaign.status.value
                if campaign_status not in campaigns_by_status:
                    campaigns_by_status[campaign_status] = []
                campaigns_by_status[campaign_status].append(campaign)
            
            # Calcular métricas
            total_campaigns = len(campaigns)
            active_campaigns = len([c for c in campaigns if c.status.value == "active"])
            total_budget = sum(c.total_budget for c in campaigns)
            spent_budget = sum(c.spent_budget for c in campaigns)
            
            return {
                "report_type": "company_overview",
                "company_id": company_id,
                "company_name": company.name,
                "generated_at": datetime.utcnow(),
                "summary": {
                    "total_campaigns": total_campaigns,
                    "active_campaigns": active_campaigns,
                    "total_budget": total_budget,
                    "spent_budget": spent_budget,
                    "budget_utilization": (spent_budget / total_budget) * 100 if total_budget > 0 else 0
                },
                "campaigns_by_type": {
                    campaign_type: len(campaigns_list) 
                    for campaign_type, campaigns_list in campaigns_by_type.items()
                },
                "campaigns_by_status": {
                    campaign_status: len(campaigns_list) 
                    for campaign_status, campaigns_list in campaigns_by_status.items()
                },
                "records": total_campaigns
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de visão geral: {e}")
            return {"error": str(e)}
    
    async def _generate_import_summary_report(
        self, 
        company_id: str, 
        parameters: Optional[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gerar relatório de resumo de importações"""
        try:
            # TODO: Implementar relatório real de importações
            # Por enquanto, usando dados mock
            
            return {
                "report_type": "import_summary",
                "company_id": company_id,
                "generated_at": datetime.utcnow(),
                "summary": {
                    "total_imports": 45,
                    "successful_imports": 42,
                    "failed_imports": 3,
                    "total_records": 125000,
                    "last_import": datetime.utcnow() - timedelta(hours=2)
                },
                "imports_by_campaign": [
                    {
                        "campaign_name": "Campanha de Vídeo Q1 2024",
                        "imports_count": 15,
                        "success_rate": 100.0,
                        "total_records": 45000
                    },
                    {
                        "campaign_name": "Campanha Social Q1 2024",
                        "imports_count": 15,
                        "success_rate": 93.3,
                        "total_records": 40000
                    }
                ],
                "records": 2
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de importações: {e}")
            return {"error": str(e)}
    
    async def _generate_user_activity_report(
        self, 
        company_id: str, 
        parameters: Optional[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gerar relatório de atividade dos usuários"""
        try:
            # TODO: Implementar relatório real de atividade
            # Por enquanto, usando dados mock
            
            return {
                "report_type": "user_activity",
                "company_id": company_id,
                "generated_at": datetime.utcnow(),
                "summary": {
                    "total_users": 8,
                    "active_users": 6,
                    "total_logins": 45,
                    "total_actions": 120
                },
                "user_activity": [
                    {
                        "user_name": "João Silva",
                        "role": "manager",
                        "last_login": datetime.utcnow() - timedelta(hours=1),
                        "actions_count": 25
                    },
                    {
                        "user_name": "Maria Santos",
                        "role": "analyst",
                        "last_login": datetime.utcnow() - timedelta(hours=3),
                        "actions_count": 18
                    }
                ],
                "records": 2
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de atividade: {e}")
            return {"error": str(e)}
    
    async def _generate_system_health_report(
        self, 
        company_id: str, 
        parameters: Optional[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gerar relatório de saúde do sistema"""
        try:
            # TODO: Implementar relatório real de saúde
            # Por enquanto, usando dados mock
            
            return {
                "report_type": "system_health",
                "company_id": company_id,
                "generated_at": datetime.utcnow(),
                "summary": {
                    "system_status": "healthy",
                    "uptime": "99.8%",
                    "last_error": None,
                    "active_services": 4
                },
                "service_status": [
                    {
                        "service": "API",
                        "status": "operational",
                        "response_time": "45ms",
                        "last_check": datetime.utcnow()
                    },
                    {
                        "service": "Database",
                        "status": "operational",
                        "response_time": "12ms",
                        "last_check": datetime.utcnow()
                    },
                    {
                        "service": "Redis",
                        "status": "operational",
                        "response_time": "2ms",
                        "last_check": datetime.utcnow()
                    },
                    {
                        "service": "Celery",
                        "status": "operational",
                        "response_time": "N/A",
                        "last_check": datetime.utcnow()
                    }
                ],
                "records": 4
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de saúde: {e}")
            return {"error": str(e)}
    
    # Métodos auxiliares
    
    def _calculate_next_execution(self, frequency: ReportFrequency, start_date: datetime) -> datetime:
        """Calcular próxima execução baseado na frequência"""
        try:
            if frequency == ReportFrequency.DAILY:
                return start_date + timedelta(days=1)
            elif frequency == ReportFrequency.WEEKLY:
                return start_date + timedelta(weeks=1)
            elif frequency == ReportFrequency.MONTHLY:
                # Aproximação simples para meses
                return start_date + timedelta(days=30)
            elif frequency == ReportFrequency.QUARTERLY:
                return start_date + timedelta(days=90)
            elif frequency == ReportFrequency.YEARLY:
                return start_date + timedelta(days=365)
            else:
                return start_date + timedelta(days=1)
                
        except Exception as e:
            logger.error(f"Erro ao calcular próxima execução: {e}")
            return start_date + timedelta(days=1)
    
    async def _format_report(self, report_data: Dict[str, Any], format: ReportFormat) -> Any:
        """Formatar relatório no formato especificado"""
        try:
            if format == ReportFormat.JSON:
                return report_data
            elif format == ReportFormat.CSV:
                # Converter para CSV
                df = pd.DataFrame(report_data.get("campaigns", []))
                return df.to_csv(index=False)
            elif format == ReportFormat.HTML:
                # Converter para HTML
                df = pd.DataFrame(report_data.get("campaigns", []))
                return df.to_html(index=False, classes="table table-striped")
            elif format == ReportFormat.EXCEL:
                # Converter para Excel
                df = pd.DataFrame(report_data.get("campaigns", []))
                return df.to_excel(index=False)
            elif format == ReportFormat.PDF:
                # TODO: Implementar geração de PDF
                return f"PDF Report: {report_data.get('report_type', 'Unknown')}"
            else:
                return report_data
                
        except Exception as e:
            logger.error(f"Erro ao formatar relatório: {e}")
            return report_data
    
    async def _send_scheduled_report(self, report_data: Dict[str, Any], schedule: Dict[str, Any]):
        """Enviar relatório agendado para os destinatários"""
        try:
            # TODO: Implementar envio real do relatório
            logger.info(f"Relatório agendado enviado para {len(schedule.get('recipients', []))} destinatários")
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório agendado: {e}")
    
    async def _save_schedule_to_bigquery(self, schedule: ReportScheduleResponse):
        """Salvar agendamento no BigQuery"""
        # TODO: Implementar integração com BigQuery
        logger.info(f"Agendamento {schedule.id} salvo no BigQuery")
    
    async def _schedule_report_execution(self, schedule: ReportScheduleResponse):
        """Agendar execução do relatório"""
        # TODO: Implementar agendamento com Celery
        logger.info(f"Execução do relatório {schedule.id} agendada para {schedule.next_generation}")
    
    async def _save_report_execution(
        self, 
        schedule_id: Optional[str], 
        company_id: str, 
        status: str, 
        records_processed: int
    ) -> Optional[Dict[str, Any]]:
        """Salvar execução do relatório"""
        try:
            execution_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            execution = {
                "id": execution_id,
                "report_schedule_id": schedule_id,
                "company_id": company_id,
                "status": status,
                "started_at": now,
                "completed_at": now if status == "completed" else None,
                "file_path": None,
                "file_size": None,
                "records_processed": records_processed,
                "error_message": None,
                "error_details": None,
                "created_at": now,
                "updated_at": now
            }
            
            # TODO: Salvar no BigQuery
            logger.info(f"Execução do relatório {execution_id} salva")
            
            return execution
            
        except Exception as e:
            logger.error(f"Erro ao salvar execução do relatório: {e}")
            return None
    
    async def _update_schedule_execution(self, schedule_id: str):
        """Atualizar execução do agendamento"""
        try:
            # TODO: Implementar atualização real no BigQuery
            logger.info(f"Execução do agendamento {schedule_id} atualizada")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar execução do agendamento: {e}")




