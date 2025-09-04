from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer
from src.models.user import (
    UserCreate, UserResponse, UserLogin, Token, PasswordChange, 
    PasswordReset, PasswordResetConfirm, UserRole, UserStatus, CompanySwitch
)
from src.models.company import CompanySummary
from src.services.auth_service import AuthService, get_current_user
from src.services.company_service import CompanyService
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()
company_service = CompanyService()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login do usuário com contexto de empresa"""
    try:
        # Autenticar usuário
        user_data = await auth_service.authenticate_user(
            email=user_credentials.email,
            password=user_credentials.password,
            company_id=user_credentials.company_id
        )
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Determinar empresa ativa
        current_company_id = user_credentials.company_id or user_data.get("company_id")
        
        # Obter todas as empresas do usuário
        user_companies = await auth_service.get_user_companies_for_token(user_data["id"])
        
        if not user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem acesso a nenhuma empresa"
            )
        
        # Se não foi especificada empresa, usar a primeira disponível
        if not current_company_id:
            current_company_id = user_companies[0]["id"]
        
        # Verificar se usuário tem acesso à empresa especificada
        if current_company_id not in [c["id"] for c in user_companies]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não tem acesso a esta empresa"
            )
        
        # Criar token com contexto da empresa
        access_token = auth_service.create_company_context_token(
            user_data, current_company_id, user_companies
        )
        
        # Criar resposta do usuário
        user_response = UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            status=user_data["status"],
            timezone="America/Sao_Paulo",
            language="pt-BR",
            notifications_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            current_company_id=current_company_id,
            available_companies=[c["id"] for c in user_companies]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no servidor: {str(e)}"
        )

@router.post("/switch-company")
async def switch_company(
    company_switch: CompanySwitch,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Trocar empresa ativa para o usuário"""
    try:
        # Verificar se usuário tem acesso à empresa
        has_access = await auth_service.check_company_access(current_user, company_switch.company_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a esta empresa"
            )
        
        # Obter empresas disponíveis
        user_companies = await auth_service.get_user_companies_for_token(current_user["sub"])
        
        # Criar novo token com nova empresa
        new_token = auth_service.create_company_context_token(
            current_user, company_switch.company_id, user_companies
        )
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "current_company_id": company_switch.company_id,
            "message": "Empresa alterada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao trocar empresa: {str(e)}"
        )

@router.get("/me/companies", response_model=List[CompanySummary])
async def get_my_companies(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter empresas disponíveis para o usuário logado"""
    try:
        company_service = CompanyService()
        companies = await company_service.get_user_companies(current_user["sub"])
        return companies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar empresas: {str(e)}"
        )

@router.get("/profile")
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obter perfil do usuário logado"""
    try:
        # TODO: Implementar busca completa do usuário no BigQuery
        # Por enquanto, retornando dados do token
        
        profile = {
            "id": current_user["sub"],
            "email": current_user["email"],
            "role": current_user["role"],
            "company_id": current_user.get("company_id"),
            "permissions": current_user.get("permissions", []),
            "available_companies": current_user.get("available_companies", [])
        }
        
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar perfil: {str(e)}"
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Registrar novo usuário"""
    try:
        # TODO: Implementar registro real no BigQuery
        # Por enquanto, apenas validação básica
        
        # Verificar se email já existe
        # TODO: Implementar verificação de email único
        
        # Gerar ID único
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Criar usuário
        user = UserResponse(
            id=user_id,
            **user_data.dict(exclude={'password'}),
            created_at=now,
            updated_at=now
        )
        
        # TODO: Salvar no BigQuery
        # TODO: Criar relacionamento User-Company
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar usuário: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Alterar senha do usuário logado"""
    try:
        # TODO: Implementar alteração de senha real
        # Por enquanto, apenas validação básica
        
        # Verificar senha atual
        # TODO: Implementar verificação de senha atual
        
        # Hash da nova senha
        new_hashed_password = auth_service.get_password_hash(password_data.new_password)
        
        # TODO: Atualizar senha no BigQuery
        
        return {"message": "Senha alterada com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        )

@router.post("/forgot-password")
async def forgot_password(password_data: PasswordReset):
    """Solicitar redefinição de senha"""
    try:
        # TODO: Implementar sistema de redefinição de senha
        # Por enquanto, apenas validação básica
        
        # Verificar se email existe
        # TODO: Implementar verificação de email
        
        # Gerar token de redefinição
        # TODO: Implementar geração de token
        
        # Enviar email
        # TODO: Implementar envio de email
        
        return {"message": "Email de redefinição enviado com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar solicitação: {str(e)}"
        )

@router.post("/reset-password")
async def reset_password(password_data: PasswordResetConfirm):
    """Redefinir senha com token"""
    try:
        # TODO: Implementar redefinição de senha real
        # Por enquanto, apenas validação básica
        
        # Verificar token
        # TODO: Implementar verificação de token
        
        # Hash da nova senha
        new_hashed_password = auth_service.get_password_hash(password_data.new_password)
        
        # TODO: Atualizar senha no BigQuery
        
        return {"message": "Senha redefinida com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao redefinir senha: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Logout do usuário"""
    # Em JWT, o logout é feito no frontend removendo o token
    # Aqui podemos implementar blacklist de tokens se necessário
    return {"message": "Logout realizado com sucesso"}

@router.get("/validate-token")
async def validate_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Validar token atual"""
    try:
        return {
            "valid": True,
            "user": {
                "id": current_user["sub"],
                "email": current_user["email"],
                "role": current_user["role"],
                "company_id": current_user.get("company_id")
            }
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}


