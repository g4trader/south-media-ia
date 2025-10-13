#!/bin/bash

# Setup Local PostgreSQL para Desenvolvimento
# Alternativa gratuita ao Cloud SQL durante desenvolvimento

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐘 SETUP LOCAL POSTGRESQL PARA DESENVOLVIMENTO${NC}"
echo "=================================================="
echo ""

# Verificar se PostgreSQL está instalado
if command -v psql &> /dev/null; then
    echo -e "✅ ${GREEN}PostgreSQL já está instalado${NC}"
    psql --version
else
    echo -e "${YELLOW}📦 Instalando PostgreSQL...${NC}"
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql@14
            brew services start postgresql@14
        else
            echo -e "${RED}❌ Homebrew não encontrado. Instale PostgreSQL manualmente.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    else
        echo -e "${RED}❌ Sistema operacional não suportado automaticamente.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}🔧 Configuração do Banco Local:${NC}"
echo "-------------------------------"

# Criar usuário e banco para desenvolvimento
DB_USER="dev_user"
DB_NAME="south_media_dev"
DB_PASSWORD="dev_password_123"

# Verificar se o banco já existe
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "✅ ${GREEN}Banco '$DB_NAME' já existe${NC}"
else
    echo -e "📝 ${YELLOW}Criando banco de desenvolvimento...${NC}"
    
    # Criar usuário (ignorar erro se já existir)
    sudo -u postgres createuser --createdb --login $DB_USER 2>/dev/null || true
    
    # Definir senha
    sudo -u postgres psql -c "ALTER USER $DB_USER PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
    
    # Criar banco
    sudo -u postgres createdb -O $DB_USER $DB_NAME 2>/dev/null || true
    
    echo -e "✅ ${GREEN}Banco criado com sucesso${NC}"
fi

echo ""
echo -e "${BLUE}📋 Informações de Conexão:${NC}"
echo "---------------------------"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""

echo -e "${BLUE}🔗 String de Conexão:${NC}"
echo "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

echo -e "${BLUE}🧪 Comandos Úteis:${NC}"
echo "-------------------"
echo "Conectar: psql -h localhost -U $DB_USER -d $DB_NAME"
echo "Listar DBs: psql -l"
echo "Sair: \\q"
echo ""

echo -e "${GREEN}💡 Dica: Use este banco local para desenvolvimento e Cloud SQL apenas para produção${NC}"
echo ""







