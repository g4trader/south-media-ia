from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from src.models.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignSummary,
    CampaignType, CampaignStatus, CampaignMetrics, CampaignMetricsCreate,
    CampaignPerformance, DashboardTemplate, DashboardTemplateCreate,
    DashboardTemplateUpdate, DashboardTemplateResponse
)
from src.models.user import Permission
from src.services.auth_service import get_current_user, require_permissions
from src.services.campaign_service import CampaignService
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])
campaign_service = CampaignService()

# Dependências de autenticação e permissões
def require_campaign_permission(permission: str):
    """Decorator para verificar permissão específica de campanha"""
    return require_permissions([permission])

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_WRITE))
):
    """Criar uma nova campanha"""
    try:
        # Verificar se usuário tem acesso à empresa da campanha
        if not await campaign_service.can_access_company(
            current_user, campaign_data.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para criar campanhas nesta empresa"
            )
        
        # Validar datas da campanha
        if campaign_data.start_date >= campaign_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de início deve ser anterior à data de término"
            )
        
        # TODO: Implementar validação de planilha quando sheets_service estiver disponível
        # Por enquanto, aceitar qualquer spreadsheet_id e sheet_name
        
        campaign = await campaign_service.create_campaign(campaign_data, current_user)
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar campanha: {str(e)}"
        )

@router.get("/", response_model=List[CampaignSummary])
async def list_campaigns(
    company_id: Optional[str] = Query(None),
    campaign_type: Optional[CampaignType] = Query(None),
    status_filter: Optional[CampaignStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    dashboard_template: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_READ))
):
    """Listar campanhas com filtros e paginação"""
    try:
        # Se company_id não foi especificado, usar empresa atual do usuário
        if not company_id:
            company_id = current_user.get("company_id")
        
        # Verificar se usuário tem acesso à empresa
        if not await campaign_service.can_access_company(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar esta empresa"
            )
        
        campaigns = await campaign_service.list_campaigns(
            company_id=company_id,
            current_user=current_user,
            skip=skip,
            limit=limit,
            campaign_type=campaign_type,
            status_filter=status_filter,
            start_date=start_date,
            end_date=end_date,
            dashboard_template=dashboard_template,
            search=search
        )
        
        return campaigns
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar campanhas: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_READ))
):
    """Obter detalhes de uma campanha específica"""
    try:
        campaign = await campaign_service.get_campaign(campaign_id, current_user)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar campanha: {str(e)}"
        )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_WRITE))
):
    """Atualizar uma campanha"""
    try:
        # Verificar se campanha existe e usuário tem permissão
        existing_campaign = await campaign_service.get_campaign(campaign_id, current_user)
        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        # Se estiver alterando datas, validar
        if campaign_data.start_date or campaign_data.end_date:
            start_date = campaign_data.start_date or existing_campaign.start_date
            end_date = campaign_data.end_date or existing_campaign.end_date
            if start_date >= end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data de início deve ser anterior à data de término"
                )
        
        # TODO: Implementar validação de planilha quando sheets_service estiver disponível
        # Por enquanto, aceitar qualquer spreadsheet_id e sheet_name
        
        campaign = await campaign_service.update_campaign(campaign_id, campaign_data, current_user)
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar campanha: {str(e)}"
        )

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_DELETE))
):
    """Deletar uma campanha (soft delete)"""
    try:
        success = await campaign_service.delete_campaign(campaign_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar campanha: {str(e)}"
        )

@router.patch("/{campaign_id}/status", response_model=CampaignResponse)
async def update_campaign_status(
    campaign_id: str,
    status: CampaignStatus,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_WRITE))
):
    """Atualizar status de uma campanha"""
    try:
        campaign = await campaign_service.update_campaign_status(campaign_id, status, current_user)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar status da campanha: {str(e)}"
        )

@router.get("/{campaign_id}/performance", response_model=CampaignPerformance)
async def get_campaign_performance(
    campaign_id: str,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_READ))
):
    """Obter performance de uma campanha"""
    try:
        performance = await campaign_service.get_campaign_performance(campaign_id, current_user)
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar performance da campanha: {str(e)}"
        )

@router.get("/{campaign_id}/metrics")
async def get_campaign_metrics(
    campaign_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_READ))
):
    """Obter métricas de uma campanha com filtros de data"""
    try:
        metrics = await campaign_service.get_campaign_metrics(
            campaign_id, 
            current_user, 
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar métricas da campanha: {str(e)}"
        )

@router.post("/{campaign_id}/import-data")
async def import_campaign_data(
    campaign_id: str,
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_WRITE))
):
    """Importar dados da campanha do Google Sheets"""
    try:
        # Verificar se campanha existe
        campaign = await campaign_service.get_campaign(campaign_id, current_user)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        # Importar dados do Google Sheets
        imported_data = await campaign_service.import_data_from_sheets(campaign_id, current_user)
        
        return {
            "message": "Dados importados com sucesso",
            "records_imported": imported_data.get("records_imported", 0),
            "last_update": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao importar dados: {str(e)}"
        )

@router.post("/{campaign_id}/upload-metrics")
async def upload_campaign_metrics(
    campaign_id: str,
    file: UploadFile = File(...),
    current_user = Depends(require_campaign_permission(Permission.CAMPAIGN_WRITE))
):
    """Upload de métricas de campanha via arquivo CSV"""
    try:
        # Verificar se campanha existe
        campaign = await campaign_service.get_campaign(campaign_id, current_user)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campanha não encontrada"
            )
        
        # Validar tipo de arquivo
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos CSV são aceitos"
            )
        
        # Processar upload
        result = await campaign_service.upload_metrics_file(
            campaign_id, file, current_user
        )
        
        return {
            "message": "Arquivo processado com sucesso",
            "records_processed": result.get("records_processed", 0),
            "errors": result.get("errors", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )

# Rotas para templates de dashboard

@router.post("/templates", response_model=DashboardTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard_template(
    template_data: DashboardTemplateCreate,
    current_user = Depends(require_campaign_permission(Permission.DASHBOARD_WRITE))
):
    """Criar um novo template de dashboard"""
    try:
        template = await campaign_service.create_dashboard_template(template_data, current_user)
        return template
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar template: {str(e)}"
        )

@router.get("/templates", response_model=List[DashboardTemplateResponse])
async def list_dashboard_templates(
    company_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user = Depends(require_campaign_permission(Permission.DASHBOARD_READ))
):
    """Listar templates de dashboard disponíveis"""
    try:
        templates = await campaign_service.list_dashboard_templates(
            company_id=company_id,
            is_active=is_active,
            current_user=current_user
        )
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar templates: {str(e)}"
        )

@router.get("/templates/{template_id}", response_model=DashboardTemplateResponse)
async def get_dashboard_template(
    template_id: str,
    current_user = Depends(require_campaign_permission(Permission.DASHBOARD_READ))
):
    """Obter detalhes de um template de dashboard"""
    try:
        template = await campaign_service.get_dashboard_template(template_id, current_user)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template não encontrado"
            )
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar template: {str(e)}"
        )

@router.put("/templates/{template_id}", response_model=DashboardTemplateResponse)
async def update_dashboard_template(
    template_id: str,
    template_data: DashboardTemplateUpdate,
    current_user = Depends(require_campaign_permission(Permission.DASHBOARD_WRITE))
):
    """Atualizar um template de dashboard"""
    try:
        template = await campaign_service.update_dashboard_template(
            template_id, template_data, current_user
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template não encontrado"
            )
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar template: {str(e)}"
        )

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard_template(
    template_id: str,
    current_user = Depends(require_campaign_permission(Permission.DASHBOARD_DELETE))
):
    """Deletar um template de dashboard"""
    try:
        success = await campaign_service.delete_dashboard_template(template_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template não encontrado"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar template: {str(e)}"
        )
