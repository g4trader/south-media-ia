#!/bin/bash
set -e

echo "🚀 Deploying South Media Backend to Google Cloud Run..."

# Configurações do projeto
PROJECT_ID="automatizar-452311"
REGION="us-central1"
SERVICE_NAME="south-media-ia-backend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Verificar se gcloud está configurado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ gcloud não está autenticado. Execute: gcloud auth login"
    exit 1
fi

# Definir projeto
echo "📋 Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔧 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Navegar para o diretório backend
cd backend

# Build e deploy usando Cloud Build
echo "🏗️ Iniciando build e deploy..."
gcloud builds submit --config=cloudbuild.yaml --project=$PROJECT_ID

# Verificar se o deploy foi bem-sucedido
echo "✅ Verificando deploy..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

if [ -n "$SERVICE_URL" ]; then
    echo "🎉 Deploy concluído com sucesso!"
    echo "📍 URL do serviço: $SERVICE_URL"
    echo "🔗 Endpoint da API: $SERVICE_URL/api/dashboard/data"
    
    # Testar endpoint
    echo "🧪 Testando endpoint..."
    if curl -f -s "$SERVICE_URL/health" > /dev/null; then
        echo "✅ Health check passou!"
    else
        echo "⚠️ Health check falhou, mas o serviço pode estar funcionando"
    fi
    
    # Atualizar variável de ambiente no frontend
    echo "🔄 Atualizando configuração do frontend..."
    cd ../frontend
    if [ -f ".env" ]; then
        sed -i.bak "s|REACT_APP_API_URL=.*|REACT_APP_API_URL=$SERVICE_URL|" .env
    else
        echo "REACT_APP_API_URL=$SERVICE_URL" > .env
    fi
    echo "✅ Frontend configurado para usar: $SERVICE_URL"
    
else
    echo "❌ Deploy falhou!"
    exit 1
fi

echo ""
echo "🎯 Próximos passos:"
echo "1. Configure as credenciais do Google Sheets no Cloud Run"
echo "2. Teste a integração: $SERVICE_URL/api/dashboard/data"
echo "3. Faça deploy do frontend atualizado"
echo ""
echo "📚 Documentação: GOOGLE_SHEETS_INTEGRATION.md"
