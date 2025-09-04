"""
Configuração do banco de dados PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.core.config import settings

# Configuração do banco de dados
if settings.environment == "test":
    # Para testes, usar SQLite em memória
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # Para produção/desenvolvimento, usar PostgreSQL
    SQLALCHEMY_DATABASE_URL = settings.database_url or "postgresql://user:password@localhost/south_media_ia"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependency para obter a sessão do banco
def get_db():
    """Obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar todas as tabelas
def create_tables():
    """Criar todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

# Função para remover todas as tabelas
def drop_tables():
    """Remover todas as tabelas do banco de dados"""
    Base.metadata.drop_all(bind=engine)
