from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"    # Administrador do sistema (pode gerenciar todas as empresas)
    COMPANY_ADMIN = "company_admin" # Administrador de uma empresa específica
    MANAGER = "manager"            # Gerente
    ANALYST = "analyst"            # Analista
    VIEWER = "viewer"              # Visualizador

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.PENDING
    
    # Informações pessoais
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    
    # Configurações do usuário
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"
    notifications_enabled: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    company_id: str  # Empresa principal do usuário
    role: UserRole = UserRole.VIEWER  # Role padrão mais restritivo

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    company_id: str
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    company_id: Optional[str] = None  # Para usuários com múltiplas empresas

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    current_company_id: str  # Empresa atualmente ativa
    available_companies: List[str] = []  # Lista de empresas disponíveis para o usuário

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class CompanySwitch(BaseModel):
    company_id: str

# Permissões específicas por recurso
class Permission(str, Enum):
    # Empresas
    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"
    
    # Usuários
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Campanhas
    CAMPAIGN_READ = "campaign:read"
    CAMPAIGN_WRITE = "campaign:write"
    CAMPAIGN_DELETE = "campaign:delete"
    
    # Dashboards
    DASHBOARD_READ = "dashboard:read"
    DASHBOARD_WRITE = "dashboard:write"
    DASHBOARD_DELETE = "dashboard:delete"
    
    # Relatórios
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    REPORT_DELETE = "report:delete"
    
    # Configurações
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"

# Mapeamento de roles para permissões padrão
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [perm.value for perm in Permission],
    UserRole.COMPANY_ADMIN: [
        Permission.COMPANY_READ.value,
        Permission.USER_READ.value, Permission.USER_WRITE.value,
        Permission.CAMPAIGN_READ.value, Permission.CAMPAIGN_WRITE.value,
        Permission.DASHBOARD_READ.value, Permission.DASHBOARD_WRITE.value,
        Permission.REPORT_READ.value, Permission.REPORT_WRITE.value,
        Permission.SETTINGS_READ.value, Permission.SETTINGS_WRITE.value
    ],
    UserRole.MANAGER: [
        Permission.COMPANY_READ.value,
        Permission.USER_READ.value,
        Permission.CAMPAIGN_READ.value, Permission.CAMPAIGN_WRITE.value,
        Permission.DASHBOARD_READ.value, Permission.DASHBOARD_WRITE.value,
        Permission.REPORT_READ.value, Permission.REPORT_WRITE.value,
        Permission.SETTINGS_READ.value
    ],
    UserRole.ANALYST: [
        Permission.COMPANY_READ.value,
        Permission.CAMPAIGN_READ.value, Permission.CAMPAIGN_WRITE.value,
        Permission.DASHBOARD_READ.value,
        Permission.REPORT_READ.value, Permission.REPORT_WRITE.value
    ],
    UserRole.VIEWER: [
        Permission.COMPANY_READ.value,
        Permission.CAMPAIGN_READ.value,
        Permission.DASHBOARD_READ.value,
        Permission.REPORT_READ.value
    ]
}
