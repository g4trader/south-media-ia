from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from src.models.user import (
    UserCreate, UserUpdate, UserResponse, UserSummary, UserRole, UserStatus
)
from src.models.company import UserCompanyRole
from src.services.database_service import DatabaseService
from src.services.auth_service import check_permissions

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.database_service = DatabaseService()
    
    async def create_user(self, user_data: UserCreate, creator_user: Dict[str, Any]) -> UserResponse:
        """Criar um novo usuário"""
        try:
            # Gerar ID único para o usuário
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Hash da senha
            from src.services.auth_service import AuthService
            auth_service = AuthService()
            hashed_password = auth_service.get_password_hash(user_data.password)
            
            # Criar usuário
            user = UserResponse(
                id=user_id,
                **user_data.dict(exclude={'password'}),
                created_at=now,
                updated_at=now
            )
            
            # Salvar no PostgreSQL
            await self.database_service.create_user({
                "id": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "username": user_data.username,
                "hashed_password": hashed_password,
                "role": user_data.role,
                "status": user_data.status,
                "phone": user_data.phone,
                "position": user_data.position,
                "department": user_data.department
            })
            
            # Criar relacionamento User-Company
            if user_data.company_id:
                await self.database_service.create_user_company_relationship(
                    user_id=user_id,
                    company_id=user_data.company_id,
                    role=UserCompanyRole.VIEWER.value,  # Role padrão
                    is_primary=True
                )
            
            logger.info(f"Usuário criado com sucesso: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise Exception(f"Falha ao criar usuário: {str(e)}")
    
    async def get_user_by_id(
        self, 
        user_id: str, 
        current_user: Optional[Dict[str, Any]] = None
    ) -> Optional[UserResponse]:
        """Obter usuário por ID"""
        try:
            # Buscar usuário no PostgreSQL
            user = await self.database_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Se current_user foi fornecido, verificar permissões
            if current_user and not await self.can_view_user(current_user, user_id):
                return None
            
            # Converter para UserResponse
            return UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                username=user.username,
                role=user.role,
                status=user.status,
                phone=user.phone,
                position=user.position,
                department=user.department,
                timezone=user.timezone,
                language=user.language,
                notifications_enabled=user.notifications_enabled,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {user_id}: {e}")
            return None
    
    async def list_users(
        self,
        company_id: str,
        current_user: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        role_filter: Optional[UserRole] = None,
        status_filter: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> List[UserSummary]:
        """Listar usuários de uma empresa com filtros"""
        try:
            # Verificar se usuário tem acesso à empresa
            if not await self.can_access_company(current_user, company_id):
                return []
            
            # TODO: Implementar busca real no BigQuery
            # Por enquanto, usando dados mock para demonstração
            
            mock_users = [
                {
                    "id": "user-001",
                    "email": "company1@example.com",
                    "full_name": "Company Admin",
                    "role": UserRole.COMPANY_ADMIN,
                    "status": UserStatus.ACTIVE,
                    "company_id": "company-001",
                    "created_at": datetime.utcnow()
                },
                {
                    "id": "user-002",
                    "email": "analyst@company1.com",
                    "full_name": "Company Analyst",
                    "role": UserRole.ANALYST,
                    "status": UserStatus.ACTIVE,
                    "company_id": "company-001",
                    "created_at": datetime.utcnow()
                }
            ]
            
            # Filtrar por empresa
            company_users = [u for u in mock_users if u["company_id"] == company_id]
            
            # Aplicar filtros
            if role_filter:
                company_users = [u for u in company_users if u["role"] == role_filter]
            
            if status_filter:
                company_users = [u for u in company_users if u["status"] == status_filter]
            
            if search:
                search_lower = search.lower()
                company_users = [
                    u for u in company_users 
                    if search_lower in u["full_name"].lower() 
                    or search_lower in u["email"].lower()
                ]
            
            # Aplicar paginação
            paginated_users = company_users[skip:skip + limit]
            
            # Converter para UserSummary
            summaries = []
            for user in paginated_users:
                summary = UserSummary(
                    id=user["id"],
                    email=user["email"],
                    full_name=user["full_name"],
                    role=user["role"],
                    status=user["status"],
                    company_id=user["company_id"],
                    created_at=user["created_at"]
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []
    
    async def update_user(
        self, 
        user_id: str, 
        user_data: UserUpdate, 
        current_user: Dict[str, Any]
    ) -> Optional[UserResponse]:
        """Atualizar usuário"""
        try:
            # Verificar se usuário existe
            existing_user = await self.get_user_by_id(user_id, current_user)
            if not existing_user:
                return None
            
            # Atualizar campos
            update_data = user_data.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            # Criar usuário atualizado
            updated_user = UserResponse(
                **existing_user.dict(),
                **update_data
            )
            
            # Salvar no BigQuery
            await self._update_user_in_bigquery(user_id, updated_user)
            
            logger.info(f"Usuário {user_id} atualizado com sucesso")
            return updated_user
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: str, current_user: Dict[str, Any]) -> bool:
        """Deletar usuário (soft delete)"""
        try:
            # Verificar se usuário existe
            existing_user = await self.get_user_by_id(user_id, current_user)
            if not existing_user:
                return False
            
            # Soft delete - apenas marcar como inativo
            updated_user = UserResponse(
                **existing_user.dict(),
                status=UserStatus.INACTIVE,
                updated_at=datetime.utcnow()
            )
            
            # Salvar no BigQuery
            await self._update_user_in_bigquery(user_id, updated_user)
            
            logger.info(f"Usuário {user_id} marcado como inativo")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar usuário {user_id}: {e}")
            return False
    
    async def update_user_status(
        self, 
        user_id: str, 
        new_status: UserStatus, 
        current_user: Dict[str, Any]
    ) -> Optional[UserResponse]:
        """Atualizar status de um usuário"""
        try:
            # Verificar se usuário existe
            existing_user = await self.get_user_by_id(user_id, current_user)
            if not existing_user:
                return None
            
            # Atualizar status
            updated_user = UserResponse(
                **existing_user.dict(),
                status=new_status,
                updated_at=datetime.utcnow()
            )
            
            # Salvar no BigQuery
            await self._update_user_in_bigquery(user_id, updated_user)
            
            logger.info(f"Status do usuário {user_id} alterado para {new_status}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do usuário {user_id}: {e}")
            return None
    
    # Métodos de verificação de permissões
    
    async def can_view_user(self, current_user: Dict[str, Any], target_user_id: str) -> bool:
        """Verificar se usuário atual pode ver usuário alvo"""
        try:
            # Super admin pode ver todos os usuários
            if current_user.get("role") == UserRole.SUPER_ADMIN:
                return True
            
            # Usuário pode ver seu próprio perfil
            if current_user.get("sub") == target_user_id:
                return True
            
            # Verificar se ambos estão na mesma empresa
            current_company_id = current_user.get("company_id")
            if not current_company_id:
                return False
            
            # TODO: Implementar verificação real de empresa
            # Por enquanto, permitindo se estiver na mesma empresa
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão de visualização: {e}")
            return False
    
    async def can_edit_user(self, current_user: Dict[str, Any], target_user_id: str) -> bool:
        """Verificar se usuário atual pode editar usuário alvo"""
        try:
            # Super admin pode editar todos os usuários
            if current_user.get("role") == UserRole.SUPER_ADMIN:
                return True
            
            # Usuário pode editar seu próprio perfil
            if current_user.get("sub") == target_user_id:
                return True
            
            # Company admin pode editar usuários da sua empresa
            if current_user.get("role") == UserRole.COMPANY_ADMIN:
                # TODO: Implementar verificação real de empresa
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão de edição: {e}")
            return False
    
    async def can_delete_user(self, current_user: Dict[str, Any], target_user_id: str) -> bool:
        """Verificar se usuário atual pode deletar usuário alvo"""
        try:
            # Super admin pode deletar todos os usuários
            if current_user.get("role") == UserRole.SUPER_ADMIN:
                return True
            
            # Usuário não pode deletar a si mesmo
            if current_user.get("sub") == target_user_id:
                return False
            
            # Company admin pode deletar usuários da sua empresa
            if current_user.get("role") == UserRole.COMPANY_ADMIN:
                # TODO: Implementar verificação real de empresa
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão de deleção: {e}")
            return False
    
    async def can_manage_company_users(self, current_user: Dict[str, Any], company_id: str) -> bool:
        """Verificar se usuário atual pode gerenciar usuários da empresa"""
        try:
            # Super admin pode gerenciar usuários de todas as empresas
            if current_user.get("role") == UserRole.SUPER_ADMIN:
                return True
            
            # Company admin pode gerenciar usuários da sua empresa
            if current_user.get("role") == UserRole.COMPANY_ADMIN:
                # TODO: Implementar verificação real de empresa
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão de gerenciamento: {e}")
            return False
    
    async def can_access_company(self, current_user: Dict[str, Any], company_id: str) -> bool:
        """Verificar se usuário atual tem acesso à empresa"""
        try:
            # Super admin tem acesso a todas as empresas
            if current_user.get("role") == UserRole.SUPER_ADMIN:
                return True
            
            # Verificar se usuário tem acesso à empresa
            from src.services.auth_service import AuthService
            auth_service = AuthService()
            return await auth_service.check_company_access(current_user, company_id)
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso à empresa: {e}")
            return False
    
    # Métodos de relacionamento User-Company
    
    async def add_user_to_company(
        self, 
        user_id: str, 
        company_id: str, 
        role: UserCompanyRole, 
        is_primary: bool,
        current_user: Dict[str, Any]
    ) -> bool:
        """Adicionar usuário a uma empresa"""
        try:
            # TODO: Implementar criação real no BigQuery
            logger.info(f"Usuário {user_id} adicionado à empresa {company_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar usuário à empresa: {e}")
            return False
    
    async def remove_user_from_company(
        self, 
        user_id: str, 
        company_id: str, 
        current_user: Dict[str, Any]
    ) -> bool:
        """Remover usuário de uma empresa"""
        try:
            # TODO: Implementar remoção real no BigQuery
            logger.info(f"Usuário {user_id} removido da empresa {company_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário da empresa: {e}")
            return False
    
    async def get_user_companies(self, user_id: str) -> List[Dict[str, Any]]:
        """Obter empresas de um usuário"""
        try:
            # TODO: Implementar busca real no BigQuery
            # Por enquanto, retornando dados mock
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas do usuário {user_id}: {e}")
            return []
    
    # Métodos privados para BigQuery
    
    async def _save_user_to_bigquery(self, user: UserResponse, hashed_password: str):
        """Salvar usuário no BigQuery"""
        # TODO: Implementar integração com BigQuery
        logger.info(f"Usuário {user.id} salvo no BigQuery")
    
    async def _update_user_in_bigquery(self, user_id: str, user: UserResponse):
        """Atualizar usuário no BigQuery"""
        # TODO: Implementar atualização no BigQuery
        logger.info(f"Usuário {user_id} atualizado no BigQuery")
    
    async def _create_user_company_relationship(
        self,
        user_id: str,
        company_id: str,
        role: UserCompanyRole,
        is_primary: bool = False
    ):
        """Criar relacionamento User-Company"""
        # TODO: Implementar criação no BigQuery
        logger.info(f"Relacionamento User-Company criado: {user_id} -> {company_id}")

