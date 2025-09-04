"""
Serviço de campanhas usando PostgreSQL
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from src.models.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignSummary,
    CampaignType, CampaignStatus
)
from src.services.database_service import DatabaseService
from src.services.company_service import CompanyService
from src.core.logging import logger
import uuid

class CampaignService:
    """Serviço para operações relacionadas a campanhas"""
    
    def __init__(self):
        self.database_service = DatabaseService()
        self.company_service = CompanyService()
    
    async def create_campaign(self, campaign_data: CampaignCreate, user_id: str) -> CampaignResponse:
        """Criar nova campanha"""
        try:
            # Verificar se usuário tem acesso à empresa
            if not await self.company_service.check_user_company_access(user_id, campaign_data.company_id):
                raise Exception("Usuário não tem acesso à empresa")
            
            # Criar campanha no banco
            campaign = await self.database_service.create_campaign(campaign_data.dict(), user_id)
            
            # Converter para CampaignResponse
            return CampaignResponse(
                id=campaign.id,
                name=campaign.name,
                company_id=campaign.company_id,
                campaign_type=campaign.campaign_type,
                status=campaign.status,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                total_budget=campaign.total_budget,
                spent_budget=campaign.spent_budget,
                unit_cost=campaign.unit_cost,
                google_sheets_url=campaign.google_sheets_url,
                spreadsheet_id=campaign.spreadsheet_id,
                sheet_name=campaign.sheet_name,
                dashboard_template=campaign.dashboard_template,
                strategies=campaign.strategies,
                contract_scope=campaign.contract_scope,
                channels=eval(campaign.channels) if campaign.channels else [],
                platforms=eval(campaign.platforms) if campaign.platforms else [],
                description=campaign.description,
                objectives=eval(campaign.objectives) if campaign.objectives else [],
                target_audience=campaign.target_audience,
                kpis=eval(campaign.kpis) if campaign.kpis else [],
                refresh_frequency=campaign.refresh_frequency,
                auto_import=campaign.auto_import,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {e}")
            raise Exception(f"Falha ao criar campanha: {str(e)}")
    
    async def get_campaign(self, campaign_id: str, current_user: Dict[str, Any]) -> Optional[CampaignResponse]:
        """Obter campanha por ID com verificação de permissão"""
        try:
            # Buscar campanha no PostgreSQL
            campaign = await self.database_service.get_campaign_by_id(campaign_id)
            if not campaign:
                return None
            
            # Verificar se usuário tem acesso à empresa da campanha
            if not await self.company_service.check_user_company_access(current_user["id"], campaign.company_id):
                return None
            
            # Converter para CampaignResponse
            return CampaignResponse(
                id=campaign.id,
                name=campaign.name,
                company_id=campaign.company_id,
                campaign_type=campaign.campaign_type,
                status=campaign.status,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                total_budget=campaign.total_budget,
                spent_budget=campaign.spent_budget,
                unit_cost=campaign.unit_cost,
                google_sheets_url=campaign.google_sheets_url,
                spreadsheet_id=campaign.spreadsheet_id,
                sheet_name=campaign.sheet_name,
                dashboard_template=campaign.dashboard_template,
                strategies=campaign.strategies,
                contract_scope=campaign.contract_scope,
                channels=eval(campaign.channels) if campaign.channels else [],
                platforms=eval(campaign.platforms) if campaign.platforms else [],
                description=campaign.description,
                objectives=eval(campaign.objectives) if campaign.objectives else [],
                target_audience=campaign.target_audience,
                kpis=eval(campaign.kpis) if campaign.kpis else [],
                refresh_frequency=campaign.refresh_frequency,
                auto_import=campaign.auto_import,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar campanha {campaign_id}: {e}")
            return None
    
    async def list_campaigns(
        self,
        company_id: str,
        current_user: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        campaign_type: Optional[CampaignType] = None,
        status_filter: Optional[CampaignStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        dashboard_template: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[CampaignSummary]:
        """Listar campanhas de uma empresa com filtros"""
        try:
            # Verificar se usuário tem acesso à empresa
            if not await self.company_service.check_user_company_access(current_user["id"], company_id):
                return []
            
            # Buscar campanhas no PostgreSQL
            campaigns = await self.database_service.list_campaigns(company_id, {
                "campaign_type": campaign_type,
                "status": status_filter
            })
            
            # Converter para CampaignSummary
            campaign_summaries = []
            for campaign in campaigns:
                campaign_summaries.append(CampaignSummary(
                    id=campaign.id,
                    name=campaign.name,
                    company_id=campaign.company_id,
                    campaign_type=campaign.campaign_type,
                    status=campaign.status,
                    start_date=campaign.start_date,
                    end_date=campaign.end_date,
                    dashboard_template=campaign.dashboard_template,
                    total_budget=campaign.total_budget,
                    spent_budget=campaign.spent_budget,
                    channels=eval(campaign.channels) if campaign.channels else [],
                    platforms=eval(campaign.platforms) if campaign.platforms else [],
                    last_data_update=campaign.updated_at
                ))
            
            return campaign_summaries
            
        except Exception as e:
            logger.error(f"Erro ao listar campanhas: {e}")
            return []
    
    async def update_campaign(self, campaign_id: str, campaign_data: CampaignUpdate, current_user: Dict[str, Any]) -> Optional[CampaignResponse]:
        """Atualizar campanha existente"""
        try:
            # Verificar se campanha existe e usuário tem acesso
            existing_campaign = await self.get_campaign(campaign_id, current_user)
            if not existing_campaign:
                return None
            
            # Atualizar no banco
            updated_campaign = await self.database_service.update_campaign(campaign_id, campaign_data.dict(exclude_unset=True))
            if not updated_campaign:
                return None
            
            # Retornar campanha atualizada
            return await self.get_campaign(campaign_id, current_user)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar campanha {campaign_id}: {e}")
            return None
    
    async def delete_campaign(self, campaign_id: str, current_user: Dict[str, Any]) -> bool:
        """Deletar campanha"""
        try:
            # Verificar se campanha existe e usuário tem acesso
            existing_campaign = await self.get_campaign(campaign_id, current_user)
            if not existing_campaign:
                return False
            
            # Deletar do banco
            return await self.database_service.delete_campaign(campaign_id)
            
        except Exception as e:
            logger.error(f"Erro ao deletar campanha {campaign_id}: {e}")
            return False
