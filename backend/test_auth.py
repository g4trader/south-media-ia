#!/usr/bin/env python3
"""
Script de teste para autenticação PostgreSQL
"""
import asyncio
import os
from src.core.database import create_tables, get_db
from src.models.database_models import User
from src.services.auth_service import AuthService
from src.models.user import UserRole, UserStatus
import uuid

async def test_auth():
    # Configurar ambiente de teste
    os.environ["ENVIRONMENT"] = "test"
    
    # Criar tabelas
    create_tables()
    print("✅ Tabelas criadas com sucesso!")
    
    # Criar usuário de teste
    db = next(get_db())
    try:
        # Verificar se usuário já existe
        existing_user = db.query(User).filter(User.email == 'admin@southmedia.com').first()
        if not existing_user:
            # Criar usuário admin
            auth_service = AuthService()
            hashed_password = auth_service.get_password_hash('admin123')
            
            user = User(
                id=str(uuid.uuid4()),
                email='admin@southmedia.com',
                full_name='Super Admin',
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                username='admin',
                hashed_password=hashed_password
            )
            db.add(user)
            db.commit()
            print("✅ Usuário admin criado com sucesso!")
            print(f"   Email: admin@southmedia.com")
            print(f"   Senha: admin123")
        else:
            print("ℹ️  Usuário admin já existe")
    finally:
        db.close()
    
    # Testar autenticação
    auth_service = AuthService()
    result = await auth_service.authenticate_user('admin@southmedia.com', 'admin123')
    print("✅ Resultado da autenticação:", result is not None)
    if result:
        print("   Usuário:", result['full_name'])
        print("   Role:", result['role'])
        print("   Status:", result['status'])
        print("   ID:", result['id'])
    else:
        print("❌ Falha na autenticação")

if __name__ == "__main__":
    asyncio.run(test_auth())
