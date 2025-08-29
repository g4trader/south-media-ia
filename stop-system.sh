#!/bin/bash

# South Media IA - Sistema Stop Script
# Este script para todos os serviços do sistema

echo "🛑 Parando South Media IA - Sistema Completo"

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

# Function to check if a process is running
is_process_running() {
    ps -p $1 > /dev/null 2>&1
}

# Stop Frontend
echo "⚛️  Parando Frontend..."
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if is_process_running $FRONTEND_PID; then
        kill $FRONTEND_PID
        print_status "Frontend parado (PID: $FRONTEND_PID)"
    else
        print_warning "Frontend já estava parado"
    fi
    rm .frontend.pid
else
    print_warning "PID do Frontend não encontrado"
fi

# Stop Backend API
echo "🚀 Parando Backend API..."
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if is_process_running $BACKEND_PID; then
        kill $BACKEND_PID
        print_status "Backend API parado (PID: $BACKEND_PID)"
    else
        print_warning "Backend API já estava parado"
    fi
    rm .backend.pid
else
    print_warning "PID do Backend não encontrado"
fi

# Stop Celery processes
echo "🐛 Parando Celery Worker..."
pkill -f "celery worker" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Celery Worker parado"
else
    print_warning "Celery Worker já estava parado"
fi

echo "⏰ Parando Celery Beat..."
pkill -f "celery beat" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Celery Beat parado"
else
    print_warning "Celery Beat já estava parado"
fi

# Stop Redis (optional - comment out if you want to keep Redis running)
echo "🔴 Parando Redis..."
redis-cli shutdown 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Redis parado"
else
    print_warning "Redis já estava parado ou não foi possível parar"
fi

# Kill any remaining processes on our ports
echo "🧹 Limpando processos nas portas..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

print_status "Sistema parado com sucesso!"

echo ""
echo "📊 Status dos Serviços:"
echo "   Frontend (3000): $(lsof -i :3000 >/dev/null 2>&1 && echo "🟢 Rodando" || echo "🔴 Parado")"
echo "   Backend (8080): $(lsof -i :8080 >/dev/null 2>&1 && echo "🟢 Rodando" || echo "🔴 Parado")"
echo "   Redis (6379): $(lsof -i :6379 >/dev/null 2>&1 && echo "🟢 Rodando" || echo "🔴 Parado")"
echo ""
echo "🚀 Para reiniciar o sistema, execute: ./start-system.sh"
