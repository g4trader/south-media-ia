"""
Modelos do banco de dados usando SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
from src.models.user import UserRole, UserStatus
from src.models.company import CompanyType, CompanyStatus
from src.models.campaign import CampaignType, CampaignStatus

class User(Base):
    """Modelo de usuário no banco de dados"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING)
    
    # Informações pessoais
    phone = Column(String)
    position = Column(String)
    department = Column(String)
    
    # Configurações
    timezone = Column(String, default="America/Sao_Paulo")
    language = Column(String, default="pt-BR")
    notifications_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relacionamentos
    user_companies = relationship("UserCompany", back_populates="user")

class Company(Base):
    """Modelo de empresa no banco de dados"""
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(CompanyStatus), default=CompanyStatus.ACTIVE)
    company_type = Column(SQLEnum(CompanyType), default=CompanyType.CLIENT)
    
    # Informações de contato
    contact_email = Column(String)
    contact_phone = Column(String)
    website = Column(String)
    
    # Endereço
    address_street = Column(String)
    address_city = Column(String)
    address_state = Column(String)
    address_postal_code = Column(String)
    address_country = Column(String)
    
    # Informações fiscais
    tax_id = Column(String)
    industry = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user_companies = relationship("UserCompany", back_populates="company")

class UserCompany(Base):
    """Relacionamento entre usuário e empresa"""
    __tablename__ = "user_companies"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    role = Column(String, nullable=False)  # admin, manager, analyst, viewer
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="user_companies")
    company = relationship("Company", back_populates="user_companies")

class Campaign(Base):
    """Modelo de campanha no banco de dados"""
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    campaign_type = Column(SQLEnum(CampaignType), nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Datas
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Orçamento
    total_budget = Column(Integer)
    spent_budget = Column(Integer, default=0)
    unit_cost = Column(String)
    
    # Configurações
    google_sheets_url = Column(String)
    spreadsheet_id = Column(String)
    sheet_name = Column(String)
    dashboard_template = Column(String)
    
    # Estratégia
    strategies = Column(Text)
    contract_scope = Column(String)
    channels = Column(Text)  # JSON string
    platforms = Column(Text)  # JSON string
    description = Column(Text)
    objectives = Column(Text)  # JSON string
    target_audience = Column(Text)
    kpis = Column(Text)  # JSON string
    refresh_frequency = Column(String)
    auto_import = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    company = relationship("Company")
