from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENCY = "agency"
    CLIENT = "client"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    agency_id: Optional[str] = None  # Para clientes, referência à agência
    client_id: Optional[str] = None  # Para usuários da agência, referência ao cliente

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    agency_id: Optional[str] = None
    client_id: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    agency_id: Optional[str] = None
    client_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AgencyBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: EmailStr
    contact_phone: Optional[str] = None

class AgencyCreate(AgencyBase):
    pass

class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None

class AgencyResponse(AgencyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    
    class Config:
        from_attributes = True

class ClientBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    industry: Optional[str] = None

class ClientCreate(ClientBase):
    agency_id: str

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    industry: Optional[str] = None

class ClientResponse(ClientBase):
    id: str
    agency_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    
    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    resource: str  # 'campaign', 'dashboard', 'reports'
    action: str    # 'read', 'write', 'delete'
    user_id: str

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
