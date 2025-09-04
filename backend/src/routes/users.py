from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.models.user import (
    UserCreate, UserUpdate, UserResponse, UserSummary, UserRole, UserStatus
)
from src.models.company import UserCompanyRole
from src.services.auth_service import get_current_user, require_permissions
from src.services.user_service import UserService
from src.models.user import Permission

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()

# Dependências de autenticação e permissões
def require_user_permission(permission: str):
    """Decorator para verificar permissão específica de usuário"""
    return require_permissions([permission])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user = Depends(require_user_permission(Permission.USER_WRITE))
):
    """Criar um novo usuário"""
    try:
        # Verificar se usuário atual tem permissão para criar usuários na empresa
        if not await user_service.can_manage_company_users(
            current_user, user_data.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para criar usuários nesta empresa"
            )
        
        user = await user_service.create_user(user_data, current_user)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@router.get("/", response_model=List[UserSummary])
async def list_users(
    company_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role_filter: Optional[UserRole] = Query(None),
    status_filter: Optional[UserStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(require_user_permission(Permission.USER_READ))
):
    """Listar usuários com filtros e paginação"""
    try:
        # Se company_id não foi especificado, usar empresa atual do usuário
        if not company_id:
            company_id = current_user.get("company_id")
        
        # Verificar se usuário tem acesso à empresa
        if not await user_service.can_access_company(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar esta empresa"
            )
        
        users = await user_service.list_users(
            company_id=company_id,
            current_user=current_user,
            skip=skip,
            limit=limit,
            role_filter=role_filter,
            status_filter=status_filter,
            search=search
        )
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar usuários: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user = Depends(get_current_user)
):
    """Obter perfil do usuário logado"""
    try:
        user = await user_service.get_user_by_id(current_user["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar perfil: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user = Depends(require_user_permission(Permission.USER_READ))
):
    """Obter usuário por ID"""
    try:
        user = await user_service.get_user_by_id(user_id, current_user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar usuário: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user = Depends(require_user_permission(Permission.USER_WRITE))
):
    """Atualizar usuário"""
    try:
        # Verificar se usuário atual pode editar o usuário alvo
        if not await user_service.can_edit_user(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para editar este usuário"
            )
        
        user = await user_service.update_user(user_id, user_data, current_user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user = Depends(require_user_permission(Permission.USER_DELETE))
):
    """Deletar usuário (soft delete)"""
    try:
        # Verificar se usuário atual pode deletar o usuário alvo
        if not await user_service.can_delete_user(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para deletar este usuário"
            )
        
        success = await user_service.delete_user(user_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar usuário: {str(e)}"
        )

@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: UserStatus,
    current_user = Depends(require_user_permission(Permission.USER_WRITE))
):
    """Atualizar status de um usuário"""
    try:
        # Verificar se usuário atual pode alterar status do usuário alvo
        if not await user_service.can_edit_user(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para alterar status deste usuário"
            )
        
        user = await user_service.update_user_status(user_id, status, current_user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar status do usuário: {str(e)}"
        )

@router.post("/{user_id}/add-to-company")
async def add_user_to_company(
    user_id: str,
    company_id: str,
    role: UserCompanyRole,
    is_primary: bool = False,
    current_user = Depends(require_user_permission(Permission.USER_WRITE))
):
    """Adicionar usuário a uma empresa"""
    try:
        # Verificar se usuário atual pode gerenciar usuários na empresa
        if not await user_service.can_manage_company_users(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para gerenciar usuários nesta empresa"
            )
        
        success = await user_service.add_user_to_company(
            user_id, company_id, role, is_primary, current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao adicionar usuário à empresa"
            )
        
        return {"message": "Usuário adicionado à empresa com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao adicionar usuário à empresa: {str(e)}"
        )

@router.delete("/{user_id}/remove-from-company")
async def remove_user_from_company(
    user_id: str,
    company_id: str,
    current_user = Depends(require_user_permission(Permission.USER_WRITE))
):
    """Remover usuário de uma empresa"""
    try:
        # Verificar se usuário atual pode gerenciar usuários na empresa
        if not await user_service.can_manage_company_users(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para gerenciar usuários nesta empresa"
            )
        
        success = await user_service.remove_user_from_company(
            user_id, company_id, current_user
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao remover usuário da empresa"
            )
        
        return {"message": "Usuário removido da empresa com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao remover usuário da empresa: {str(e)}"
        )

@router.get("/{user_id}/companies")
async def get_user_companies(
    user_id: str,
    current_user = Depends(require_user_permission(Permission.USER_READ))
):
    """Obter empresas de um usuário específico"""
    try:
        # Verificar se usuário atual pode ver informações do usuário alvo
        if not await user_service.can_view_user(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para ver informações deste usuário"
            )
        
        companies = await user_service.get_user_companies(user_id)
        return companies
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar empresas do usuário: {str(e)}"
        )

