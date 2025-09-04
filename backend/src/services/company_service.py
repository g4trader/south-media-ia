"""
Serviço de empresas usando PostgreSQL
"""
from typing import List, Optional, Dict, Any
from src.models.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanySummary, CompanyType, CompanyStatus
from src.services.database_service import DatabaseService
from src.core.logging import logger
from datetime import datetime

class CompanyService:
    """Serviço para operações relacionadas a empresas"""
    
    def __init__(self):
        self.database_service = DatabaseService()
    
    async def create_company(self, company_data: CompanyCreate, user_id: str) -> CompanyResponse:
        """Criar nova empresa"""
        try:
            # Criar empresa no banco
            company = await self.database_service.create_company(company_data.dict())
            
            # Criar relacionamento usuário-empresa (usuário criador como admin)
            await self.database_service.create_user_company_relationship(
                user_id=user_id,
                company_id=company.id,
                role="admin",
                is_primary=True
            )
            
            # Converter para CompanyResponse
            return CompanyResponse(
                id=company.id,
                name=company.name,
                description=company.description,
                status=company.status,
                company_type=company.company_type,
                contact_email=company.contact_email,
                contact_phone=company.contact_phone,
                website=company.website,
                address={
                    "street": company.address_street,
                    "city": company.address_city,
                    "state": company.address_state,
                    "postal_code": company.address_postal_code,
                    "country": company.address_country
                },
                tax_id=company.tax_id,
                industry=company.industry,
                created_at=company.created_at,
                updated_at=company.updated_at
            )
        except Exception as e:
            logger.error(f"Erro ao criar empresa: {e}")
            raise
    
    async def get_company(self, company_id: str) -> Optional[CompanyResponse]:
        """Obter empresa por ID"""
        try:
            company = await self.database_service.get_company_by_id(company_id)
            if not company:
                    return None
            
            return CompanyResponse(
                id=company.id,
                name=company.name,
                description=company.description,
                status=company.status,
                company_type=company.company_type,
                contact_email=company.contact_email,
                contact_phone=company.contact_phone,
                website=company.website,
                address={
                    "street": company.address_street,
                    "city": company.address_city,
                    "state": company.address_state,
                    "postal_code": company.address_postal_code,
                    "country": company.address_country
                },
                tax_id=company.tax_id,
                industry=company.industry,
                created_at=company.created_at,
                updated_at=company.updated_at
            )
        except Exception as e:
            logger.error(f"Erro ao buscar empresa: {e}")
            raise
    
    async def list_companies(self, filters: Optional[Dict[str, Any]] = None) -> List[CompanyResponse]:
        """Listar empresas com filtros opcionais"""
        try:
            companies = await self.database_service.list_companies(filters)
            return [
                CompanyResponse(
                    id=company.id,
                    name=company.name,
                    description=company.description,
                    status=company.status,
                    company_type=company.company_type,
                    contact_email=company.contact_email,
                    contact_phone=company.contact_phone,
                    website=company.website,
                    address={
                        "street": company.address_street,
                        "city": company.address_city,
                        "state": company.address_state,
                        "postal_code": company.address_postal_code,
                        "country": company.address_country
                    },
                    tax_id=company.tax_id,
                    industry=company.industry,
                    created_at=company.created_at,
                    updated_at=company.updated_at
                )
                for company in companies
            ]
        except Exception as e:
            logger.error(f"Erro ao listar empresas: {e}")
            raise
    
    async def update_company(self, company_id: str, company_data: CompanyUpdate) -> Optional[CompanyResponse]:
        """Atualizar empresa"""
        try:
            # Buscar empresa existente
            company = await self.database_service.get_company_by_id(company_id)
            if not company:
                return None
            
            # Atualizar campos
            update_data = company_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            
            # Salvar no banco
            db = next(self.database_service.get_db())
            try:
                db.commit()
                db.refresh(company)
            finally:
                db.close()
            
            # Retornar empresa atualizada
            return await self.get_company(company_id)
        except Exception as e:
            logger.error(f"Erro ao atualizar empresa: {e}")
            raise
    
    async def delete_company(self, company_id: str) -> bool:
        """Deletar empresa"""
        try:
            # Buscar empresa
            company = await self.database_service.get_company_by_id(company_id)
            if not company:
                return False
            
            # Deletar do banco
            db = next(self.database_service.get_db())
            try:
                db.delete(company)
                db.commit()
            return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Erro ao deletar empresa: {e}")
            raise
    
    async def get_user_companies(self, user_id: str) -> List[CompanySummary]:
        """Obter empresas de um usuário"""
        try:
            companies_data = await self.database_service.get_user_companies(user_id)
            return [
                CompanySummary(
                    id=company["id"],
                    name=company["name"],
                    company_type=company["company_type"],
                    status=CompanyStatus.ACTIVE,  # Assumindo que empresas relacionadas estão ativas
                    contact_email=None,  # Não disponível no relacionamento
                    created_at=datetime.utcnow()  # Placeholder
                )
                for company in companies_data
            ]
        except Exception as e:
            logger.error(f"Erro ao buscar empresas do usuário: {e}")
            raise
    
    async def check_user_company_access(self, user_id: str, company_id: str) -> bool:
        """Verificar se usuário tem acesso à empresa"""
        try:
            return await self.database_service.check_user_company_access(user_id, company_id)
        except Exception as e:
            logger.error(f"Erro ao verificar acesso do usuário à empresa: {e}")
            return False

