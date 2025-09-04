from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from src.models.company import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanySummary,
    CompanyStatus, CompanyType
)
from src.models.user import UserRole, Permission
from src.services.auth_service import get_current_user, require_permissions
from src.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])
company_service = CompanyService()

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user = Depends(require_permissions([Permission.COMPANY_WRITE]))
):
    """Criar uma nova empresa"""
    try:
        company = await company_service.create_company(company_data, current_user["id"])
        return company
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar empresa: {str(e)}"
        )

@router.get("/", response_model=List[CompanySummary])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[CompanyStatus] = Query(None),
    company_type: Optional[CompanyType] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(require_permissions([Permission.COMPANY_READ]))
):
    """Listar empresas com filtros e paginação"""
    try:
        companies = await company_service.list_companies(
            current_user=current_user,
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            company_type=company_type,
            search=search
        )
        return companies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar empresas: {str(e)}"
        )

@router.get("/my-companies", response_model=List[CompanySummary])
async def get_my_companies(
    current_user = Depends(get_current_user)
):
    """Listar empresas do usuário logado"""
    try:
        companies = await company_service.get_user_companies(current_user.id)
        return companies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar empresas do usuário: {str(e)}"
        )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    current_user = Depends(require_permissions([Permission.COMPANY_READ]))
):
    """Obter detalhes de uma empresa específica"""
    try:
        company = await company_service.get_company(company_id, current_user)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar empresa: {str(e)}"
        )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    current_user = Depends(require_permissions([Permission.COMPANY_WRITE]))
):
    """Atualizar uma empresa"""
    try:
        company = await company_service.update_company(company_id, company_data, current_user)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar empresa: {str(e)}"
        )

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    current_user = Depends(require_permissions([Permission.COMPANY_DELETE]))
):
    """Deletar uma empresa (soft delete)"""
    try:
        success = await company_service.delete_company(company_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar empresa: {str(e)}"
        )

@router.patch("/{company_id}/status", response_model=CompanyResponse)
async def update_company_status(
    company_id: str,
    status: CompanyStatus,
    current_user = Depends(require_permissions([Permission.COMPANY_WRITE]))
):
    """Atualizar status de uma empresa"""
    try:
        company = await company_service.update_company_status(company_id, status, current_user)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar status da empresa: {str(e)}"
        )

@router.get("/{company_id}/users")
async def get_company_users(
    company_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_permissions([Permission.USER_READ]))
):
    """Listar usuários de uma empresa específica"""
    try:
        users = await company_service.get_company_users(
            company_id, 
            current_user, 
            skip=skip, 
            limit=limit
        )
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar usuários da empresa: {str(e)}"
        )

@router.get("/{company_id}/campaigns")
async def get_company_campaigns(
    company_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_permissions([Permission.CAMPAIGN_READ]))
):
    """Listar campanhas de uma empresa específica"""
    try:
        campaigns = await company_service.get_company_campaigns(
            company_id, 
            current_user, 
            skip=skip, 
            limit=limit
        )
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar campanhas da empresa: {str(e)}"
        )

@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: str,
    current_user = Depends(require_permissions([Permission.COMPANY_READ]))
):
    """Obter estatísticas de uma empresa"""
    try:
        stats = await company_service.get_company_stats(company_id, current_user)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar estatísticas da empresa: {str(e)}"
        )

