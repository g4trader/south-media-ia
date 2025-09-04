from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class CompanyType(str, Enum):
    AGENCY = "agency"           # Agência de marketing
    CLIENT = "client"           # Cliente final
    PARTNER = "partner"         # Parceiro

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    business_name: Optional[str] = None  # Razão social
    cnpj: Optional[str] = None  # CNPJ da empresa
    description: Optional[str] = None
    industry: Optional[str] = None
    company_type: CompanyType = CompanyType.CLIENT
    
    # Contato principal
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_person: Optional[str] = None
    
    # Endereço
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Brasil"
    zip_code: Optional[str] = None
    
    # Configurações da empresa
    timezone: str = "America/Sao_Paulo"
    currency: str = "BRL"
    language: str = "pt-BR"
    
    # Configurações de dashboard
    dashboard_theme: str = "default"
    default_date_range: str = "30d"  # 7d, 30d, 90d, 1y
    
    # Status
    status: CompanyStatus = CompanyStatus.ACTIVE

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    business_name: Optional[str] = None
    cnpj: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    company_type: Optional[CompanyType] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    dashboard_theme: Optional[str] = None
    default_date_range: Optional[str] = None
    status: Optional[CompanyStatus] = None

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CompanySummary(BaseModel):
    id: str
    name: str
    company_type: CompanyType
    status: CompanyStatus
    contact_email: Optional[str] = None
    created_at: datetime

# Relacionamento User-Company
class UserCompanyRole(str, Enum):
    OWNER = "owner"           # Proprietário da empresa
    ADMIN = "admin"           # Administrador da empresa
    MANAGER = "manager"       # Gerente
    ANALYST = "analyst"       # Analista
    VIEWER = "viewer"         # Visualizador

class UserCompany(BaseModel):
    user_id: str
    company_id: str
    role: UserCompanyRole
    is_primary: bool = False  # Empresa principal do usuário
    permissions: List[str] = []  # Permissões específicas
    created_at: datetime
    updated_at: datetime

class UserCompanyCreate(BaseModel):
    user_id: str
    company_id: str
    role: UserCompanyRole
    is_primary: bool = False
    permissions: List[str] = []

class UserCompanyUpdate(BaseModel):
    role: Optional[UserCompanyRole] = None
    is_primary: Optional[bool] = None
    permissions: Optional[List[str]] = None

class UserCompanyResponse(UserCompany):
    pass

