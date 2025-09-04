"""
Serviço de banco de dados PostgreSQL
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from src.core.database import get_db
from src.models.database_models import User, Company, UserCompany, Campaign
from src.models.user import UserRole, UserStatus
from src.models.company import CompanyType, CompanyStatus
from src.models.campaign import CampaignType, CampaignStatus
import uuid
from datetime import datetime

class DatabaseService:
    """Serviço para operações no banco de dados"""
    
    def __init__(self):
        pass
    
    # ===== OPERAÇÕES DE USUÁRIO =====
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Criar novo usuário"""
        db = next(get_db())
        try:
            user = User(
                id=str(uuid.uuid4()),
                email=user_data["email"],
                full_name=user_data["full_name"],
                username=user_data.get("username"),
                role=user_data.get("role", UserRole.VIEWER),
                status=user_data.get("status", UserStatus.PENDING),
                phone=user_data.get("phone"),
                position=user_data.get("position"),
                department=user_data.get("department"),
                timezone=user_data.get("timezone", "America/Sao_Paulo"),
                language=user_data.get("language", "pt-BR"),
                notifications_enabled=user_data.get("notifications_enabled", True)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        db = next(get_db())
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuário por ID"""
        db = next(get_db())
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """Atualizar usuário"""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()
    
    # ===== OPERAÇÕES DE EMPRESA =====
    
    async def create_company(self, company_data: Dict[str, Any]) -> Company:
        """Criar nova empresa"""
        db = next(get_db())
        try:
            company = Company(
                id=str(uuid.uuid4()),
                name=company_data["name"],
                description=company_data.get("description"),
                status=company_data.get("status", CompanyStatus.ACTIVE),
                company_type=company_data.get("company_type", CompanyType.CLIENT),
                contact_email=company_data.get("contact_email"),
                contact_phone=company_data.get("contact_phone"),
                website=company_data.get("website"),
                address_street=company_data.get("address", {}).get("street"),
                address_city=company_data.get("address", {}).get("city"),
                address_state=company_data.get("address", {}).get("state"),
                address_postal_code=company_data.get("address", {}).get("postal_code"),
                address_country=company_data.get("address", {}).get("country"),
                tax_id=company_data.get("tax_id"),
                industry=company_data.get("industry")
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            return company
        finally:
            db.close()
    
    async def get_company_by_id(self, company_id: str) -> Optional[Company]:
        """Buscar empresa por ID"""
        db = next(get_db())
        try:
            return db.query(Company).filter(Company.id == company_id).first()
        finally:
            db.close()
    
    async def list_companies(self, filters: Optional[Dict[str, Any]] = None) -> List[Company]:
        """Listar empresas com filtros opcionais"""
        db = next(get_db())
        try:
            query = db.query(Company)
            if filters:
                if filters.get("status"):
                    query = query.filter(Company.status == filters["status"])
                if filters.get("company_type"):
                    query = query.filter(Company.company_type == filters["company_type"])
                if filters.get("industry"):
                    query = query.filter(Company.industry == filters["industry"])
            return query.all()
        finally:
            db.close()
    
    # ===== OPERAÇÕES DE RELACIONAMENTO USUÁRIO-EMPRESA =====
    
    async def create_user_company_relationship(self, user_id: str, company_id: str, role: str, is_primary: bool = False) -> UserCompany:
        """Criar relacionamento entre usuário e empresa"""
        db = next(get_db())
        try:
            # Se for primário, remover outros relacionamentos primários do usuário
            if is_primary:
                db.query(UserCompany).filter(
                    and_(UserCompany.user_id == user_id, UserCompany.is_primary == True)
                ).update({"is_primary": False})
            
            user_company = UserCompany(
                id=str(uuid.uuid4()),
                user_id=user_id,
                company_id=company_id,
                role=role,
                is_primary=is_primary
            )
            db.add(user_company)
            db.commit()
            db.refresh(user_company)
            return user_company
        finally:
            db.close()
    
    async def get_user_companies(self, user_id: str) -> List[Dict[str, Any]]:
        """Obter empresas de um usuário"""
        db = next(get_db())
        try:
            user_companies = db.query(UserCompany).filter(UserCompany.user_id == user_id).all()
            companies = []
            for uc in user_companies:
                company = db.query(Company).filter(Company.id == uc.company_id).first()
                if company:
                    companies.append({
                        "id": company.id,
                        "name": company.name,
                        "company_type": company.company_type.value,
                        "is_primary": uc.is_primary,
                        "role": uc.role
                    })
            return companies
        finally:
            db.close()
    
    async def check_user_company_access(self, user_id: str, company_id: str) -> bool:
        """Verificar se usuário tem acesso à empresa"""
        db = next(get_db())
        try:
            user_company = db.query(UserCompany).filter(
                and_(UserCompany.user_id == user_id, UserCompany.company_id == company_id)
            ).first()
            return user_company is not None
        finally:
            db.close()
    
    # ===== OPERAÇÕES DE CAMPANHA =====
    
    async def create_campaign(self, campaign_data: Dict[str, Any], user_id: str) -> Campaign:
        """Criar nova campanha"""
        db = next(get_db())
        try:
            campaign = Campaign(
                id=str(uuid.uuid4()),
                name=campaign_data["name"],
                company_id=campaign_data["company_id"],
                campaign_type=campaign_data["campaign_type"],
                status=campaign_data.get("status", CampaignStatus.DRAFT),
                start_date=campaign_data.get("start_date"),
                end_date=campaign_data.get("end_date"),
                total_budget=campaign_data.get("total_budget"),
                spent_budget=campaign_data.get("spent_budget", 0),
                unit_cost=campaign_data.get("unit_cost"),
                google_sheets_url=campaign_data.get("google_sheets_url"),
                spreadsheet_id=campaign_data.get("spreadsheet_id"),
                sheet_name=campaign_data.get("sheet_name"),
                dashboard_template=campaign_data.get("dashboard_template"),
                strategies=campaign_data.get("strategies"),
                contract_scope=campaign_data.get("contract_scope"),
                channels=str(campaign_data.get("channels", [])),
                platforms=str(campaign_data.get("platforms", [])),
                description=campaign_data.get("description"),
                objectives=str(campaign_data.get("objectives", [])),
                target_audience=campaign_data.get("target_audience"),
                kpis=str(campaign_data.get("kpis", [])),
                refresh_frequency=campaign_data.get("refresh_frequency"),
                auto_import=campaign_data.get("auto_import", True)
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            return campaign
        finally:
            db.close()
    
    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """Buscar campanha por ID"""
        db = next(get_db())
        try:
            return db.query(Campaign).filter(Campaign.id == campaign_id).first()
        finally:
            db.close()
    
    async def list_campaigns(self, company_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Campaign]:
        """Listar campanhas com filtros opcionais"""
        db = next(get_db())
        try:
            query = db.query(Campaign)
            if company_id:
                query = query.filter(Campaign.company_id == company_id)
            if filters:
                if filters.get("status"):
                    query = query.filter(Campaign.status == filters["status"])
                if filters.get("campaign_type"):
                    query = query.filter(Campaign.campaign_type == filters["campaign_type"])
            return query.all()
        finally:
            db.close()
