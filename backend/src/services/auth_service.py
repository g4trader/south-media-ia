from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import settings
from src.models.user import UserRole, UserStatus, Permission, ROLE_PERMISSIONS
from src.models.company import UserCompanyRole
from src.services.company_service import CompanyService
from src.core.database import get_db
from src.models.database_models import User
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.company_service = CompanyService()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token with company context"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, email: str, password: str, company_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email, password and optional company context"""
        try:
            # Buscar usuário no PostgreSQL
            db = next(get_db())
            try:
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    return None
                
                # Verificar senha (assumindo que está armazenada como hash)
                if not self.verify_password(password, user.hashed_password or ""):
                    return None
                
                # Verificar status do usuário
                if user.status != UserStatus.ACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User account is not active"
                    )
                
                # Verificar acesso à empresa se especificada
                if company_id:
                    user_companies = await self.company_service.get_user_companies(user.id)
                    company_ids = [c["id"] for c in user_companies]
                    if company_id not in company_ids:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not have access to this company"
                        )
                
                # Retornar dados do usuário
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "status": user.status,
                    "company_id": company_id or "default"
                }
                
            finally:
                db.close()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return None
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token with company context"""
        try:
            token = credentials.credentials
            payload = self.verify_token(token)
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            
            # Buscar dados atualizados do usuário no PostgreSQL
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found"
                    )
                
                # Retornar dados atualizados do usuário
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "status": user.status,
                    "company_id": payload.get("company_id"),
                    "available_companies": payload.get("available_companies", []),
                    "permissions": payload.get("permissions", [])
                }
                
            finally:
                db.close()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter usuário atual: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    async def check_permissions(self, user: Dict[str, Any], required_permissions: List[str]) -> bool:
        """Check if user has all required permissions"""
        try:
            user_role = user.get("role")
            if not user_role:
                return False
            
            # Super admin tem todas as permissões
            if user_role == UserRole.SUPER_ADMIN:
                return True
            
            # Obter permissões do role
            role_permissions = ROLE_PERMISSIONS.get(user_role, [])
            
            # Verificar se usuário tem todas as permissões necessárias
            for permission in required_permissions:
                if permission not in role_permissions:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissões: {e}")
            return False
    
    async def check_company_access(self, user: Dict[str, Any], company_id: str) -> bool:
        """Check if user has access to a specific company"""
        try:
            user_role = user.get("role")
            
            # Super admin tem acesso a todas as empresas
            if user_role == UserRole.SUPER_ADMIN:
                return True
            
            # Verificar se usuário tem acesso à empresa
            user_companies = await self.company_service.get_user_companies(user["id"])
            company_ids = [c.id for c in user_companies]
            
            return company_id in company_ids
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso à empresa: {e}")
            return False
    
    async def get_user_companies_for_token(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all companies a user has access to for token generation"""
        try:
            user_companies = await self.company_service.get_user_companies(user_id)
            
            companies_data = []
            for uc in user_companies:
                companies_data.append({
                    "id": uc.id,
                    "name": uc.name,
                    "company_type": uc.company_type,
                    "is_primary": uc.is_primary if hasattr(uc, 'is_primary') else False
                })
            
            return companies_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas do usuário: {e}")
            return []
    
    def create_company_context_token(
        self, 
        user_data: Dict[str, Any], 
        company_id: str,
        available_companies: List[Dict[str, Any]]
    ) -> str:
        """Create JWT token with company context"""
        token_data = {
            "sub": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "company_id": company_id,
            "available_companies": [c["id"] for c in available_companies],
            "permissions": ROLE_PERMISSIONS.get(user_data["role"], [])
        }
        
        return self.create_access_token(token_data)
    
    def require_role(self, allowed_roles: List[UserRole]):
        """Dependency to check if user has one of the allowed roles"""
        async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
            user_role = current_user.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role permissions"
                )
            return current_user
        return role_checker

# Instância global do serviço de autenticação
auth_service = AuthService()

# Funções auxiliares para dependências
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    try:
        auth_service = AuthService()
        return await auth_service.get_current_user(credentials)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou expiradas",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def check_permissions(current_user: Dict[str, Any], required_permissions: List[str]) -> bool:
    """Check if user has required permissions"""
    auth_service = AuthService()
    return await auth_service.check_permissions(current_user, required_permissions)

def require_permissions(required_permissions: List[str]):
    """Dependency to check user permissions"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        has_permission = await check_permissions(current_user, required_permissions)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_checker

# Função para verificar permissão de leitura de dashboards
async def can_read_dashboards(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to check if user can read dashboards"""
    # Verificar se usuário tem permissão para ler dashboards
    has_permission = await auth_service.check_permissions(current_user, ["dashboard:read"])
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to read dashboards"
        )
    return current_user

# Função para verificar roles específicos
def require_role(allowed_roles: List[UserRole]):
    """Dependency to check if user has one of the allowed roles"""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )
        return current_user
    return role_checker

async def require_company_access(company_id: str):
    """Dependency to check company access"""
    async def company_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        auth_service = AuthService()
        has_access = await auth_service.check_company_access(current_user, company_id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
        return current_user
    return company_checker
