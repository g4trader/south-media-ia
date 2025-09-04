"""
Serviço de agendamento usando PostgreSQL
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from celery import Celery
from src.models.campaign import CampaignResponse, CampaignType
from src.services.campaign_service import CampaignService
from src.services.database_service import DatabaseService
from src.core.config import settings

logger = logging.getLogger(__name__)

# Configuração do Celery
celery_app = Celery(
    'south_media_scheduler',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['src.services.scheduler_service']
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

class SchedulerService:
    def __init__(self):
        self.campaign_service = CampaignService()
        self.database_service = DatabaseService()
    
    async def schedule_campaign_imports(self):
        """Agendar importações automáticas para todas as campanhas ativas"""
        try:
            # Buscar todas as campanhas ativas
            campaigns = await self._get_active_campaigns()
            
            for campaign in campaigns:
                await self._schedule_campaign_import(campaign)
            
            logger.info(f"Importações agendadas para {len(campaigns)} campanhas")
            
        except Exception as e:
            logger.error(f"Erro ao agendar importações: {e}")
    
    async def _get_active_campaigns(self) -> List[CampaignResponse]:
        """Obter todas as campanhas ativas que precisam de importação automática"""
        try:
            # Buscar campanhas ativas no PostgreSQL
            campaigns = await self.database_service.list_campaigns(
                company_id=None,  # Todas as empresas
                filters={"status": "active", "auto_import": True}
            )
            
            # Filtrar apenas campanhas com importação automática
            active_campaigns = [
                c for c in campaigns 
                if c.auto_import and c.refresh_frequency
            ]
            
            return active_campaigns
            
        except Exception as e:
            logger.error(f"Erro ao buscar campanhas ativas: {e}")
            return []
    
    async def _schedule_campaign_import(self, campaign: CampaignResponse):
        """Agendar importação para uma campanha específica"""
        try:
            # Determinar quando executar baseado na frequência
            schedule_time = self._calculate_next_import_time(campaign)
            
            if schedule_time:
                # Agendar tarefa no Celery
                self.celery_app.send_task(
                    'import_campaign_data',
                    args=[campaign.id],
                    eta=schedule_time
                )
                
                logger.info(f"Importação agendada para campanha {campaign.id} em {schedule_time}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar importação para campanha {campaign.id}: {e}")
    
    def _calculate_next_import_time(self, campaign: CampaignResponse) -> Optional[datetime]:
        """Calcular próxima execução baseado na frequência"""
        try:
            frequency = campaign.refresh_frequency.lower()
            now = datetime.utcnow()
            
            if frequency == "hourly":
                return now + timedelta(hours=1)
            elif frequency == "daily":
                return now + timedelta(days=1)
            elif frequency == "weekly":
                return now + timedelta(weeks=1)
            elif frequency == "monthly":
                return now + timedelta(days=30)
            else:
                logger.warning(f"Frequência não reconhecida: {frequency}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao calcular tempo de importação: {e}")
            return None
    
    async def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Obter lista de tarefas agendadas"""
        try:
            # Buscar tarefas ativas no Celery
            active_tasks = self.celery_app.control.inspect().active()
            
            scheduled_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    scheduled_tasks.append({
                        "task_id": task["id"],
                        "name": task["name"],
                        "worker": worker,
                        "started": task.get("time_start", 0),
                        "args": task.get("args", [])
                    })
            
            return scheduled_tasks
            
        except Exception as e:
            logger.error(f"Erro ao buscar tarefas agendadas: {e}")
            return []
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancelar uma tarefa agendada"""
        try:
            # Revogar tarefa no Celery
            self.celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"Tarefa {task_id} cancelada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao cancelar tarefa {task_id}: {e}")
            return False
