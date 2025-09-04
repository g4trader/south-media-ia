#!/bin/bash

# South Media IA - Sistema Completo Startup Script
# Este script inicializa todo o sistema operacional

echo "🚀 Iniciando South Media IA - Sistema Completo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Verificando pré-requisitos..."

if ! command_exists node; then
    print_error "Node.js não encontrado. Execute ./quick-start.sh primeiro."
    exit 1
fi

if ! command_exists python3; then
    print_error "Python 3 não encontrado. Execute ./quick-start.sh primeiro."
    exit 1
fi

if ! command_exists redis-server; then
    print_warning "Redis não encontrado. Instalando..."
    if command_exists brew; then
        brew install redis
    else
        print_error "Redis não pode ser instalado automaticamente. Instale manualmente."
        exit 1
    fi
fi

print_status "Pré-requisitos verificados"

# Create necessary directories
echo "📁 Criando diretórios necessários..."
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p frontend/build

print_status "Diretórios criados"

# Setup Backend
echo "🐍 Configurando Backend..."

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Activate virtual environment
print_info "Ativando ambiente virtual..."
source venv/bin/activate

# Install dependencies
print_info "Instalando dependências Python..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Criando arquivo de configuração..."
    cat > .env << EOF
# Backend Environment Variables
SECRET_KEY=south-media-secret-key-2024
GOOGLE_CLOUD_PROJECT=automatizar-452311
BIGQUERY_DATASET=south_media_dashboard
FLASK_ENV=development
PORT=8080

# Redis Configuration
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=
GOOGLE_SHEETS_TOKEN_FILE=

# Debug Mode
DEBUG=true
EOF
fi

cd ..

# Setup Frontend
echo "⚛️  Configurando Frontend..."

cd frontend

# Install dependencies
print_info "Instalando dependências Node.js..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_info "Criando arquivo de configuração do frontend..."
    cat > .env.local << EOF
# Frontend Environment Variables
REACT_APP_API_URL=http://localhost:8080/api
REACT_APP_VERCEL_TOKEN=5w8zipRxMJnLEET9OMESteB7
REACT_APP_GITHUB_TOKEN=REPLACED_TOKEN

# Development settings
REACT_APP_ENV=development
REACT_APP_DEBUG=true
EOF
fi

cd ..

# Start Redis
echo "🔴 Iniciando Redis..."
if ! port_in_use 6379; then
    redis-server --daemonize yes
    print_status "Redis iniciado"
else
    print_warning "Redis já está rodando na porta 6379"
fi

# Start Celery Worker (Backend)
echo "🐛 Iniciando Celery Worker..."
cd backend
source venv/bin/activate

# Start Celery worker in background
celery -A src.tasks worker --loglevel=info --detach
print_status "Celery Worker iniciado"

# Start Celery Beat (Scheduler)
echo "⏰ Iniciando Celery Beat..."
celery -A src.tasks beat --loglevel=info --detach
print_status "Celery Beat iniciado"

cd ..

# Start Backend API
echo "🚀 Iniciando Backend API..."
cd backend
source venv/bin/activate

# Start FastAPI server in background
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload --log-level info &
BACKEND_PID=$!
print_status "Backend API iniciado (PID: $BACKEND_PID)"

cd ..

# Start Frontend
echo "⚛️  Iniciando Frontend..."
cd frontend

# Start React development server in background
npm start &
FRONTEND_PID=$!
print_status "Frontend iniciado (PID: $FRONTEND_PID)"

cd ..

# Wait a moment for services to start
echo "⏳ Aguardando serviços iniciarem..."
sleep 5

# Check if services are running
echo "🔍 Verificando status dos serviços..."

if port_in_use 8080; then
    print_status "Backend API rodando em http://localhost:8080"
else
    print_error "Backend API não está rodando"
fi

if port_in_use 3000; then
    print_status "Frontend rodando em http://localhost:3000"
else
    print_error "Frontend não está rodando"
fi

if port_in_use 6379; then
    print_status "Redis rodando na porta 6379"
else
    print_error "Redis não está rodando"
fi

# Save PIDs for later cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 Sistema South Media IA iniciado com sucesso!"
echo ""
echo "📊 URLs de Acesso:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo "   Health Check: http://localhost:8080/health"
echo ""
echo "🔐 Credenciais de Teste:"
echo "   Admin: admin@southmedia.com / admin123"
echo "   Agency: agency@southmedia.com / agency123"
echo "   Client: client@example.com / client123"
echo ""
echo "🛑 Para parar o sistema, execute: ./stop-system.sh"
echo "📝 Para ver logs, execute: ./logs.sh"
echo ""

# Function to handle cleanup on script exit
cleanup() {
    echo ""
    print_info "Parando serviços..."
    
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # Stop Celery processes
    pkill -f "celery worker" 2>/dev/null
    pkill -f "celery beat" 2>/dev/null
    
    print_status "Sistema parado"
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
echo "🔄 Sistema rodando... Pressione Ctrl+C para parar"
wait
