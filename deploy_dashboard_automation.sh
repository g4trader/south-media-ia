#!/bin/bash

# Script para deploy do serviço dashboard-automation no Cloud Run

set -e  # Exit on any error

PROJECT_ID="automatizar-452311"
SERVICE_NAME="dashboard-automation"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Iniciando deploy do Dashboard Automation..."
echo "📊 Projeto: $PROJECT_ID"
echo "🌍 Região: $REGION"
echo "🔧 Serviço: $SERVICE_NAME"

# Verificar se gcloud está configurado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo "❌ Gcloud não está autenticado. Execute: gcloud auth login"
    exit 1
fi

# Definir projeto
gcloud config set project $PROJECT_ID

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile.dashboard-automation" ]; then
    echo "❌ Dockerfile.dashboard-automation não encontrado!"
    exit 1
fi

echo "📦 Fazendo build da imagem..."
# Build da imagem
gcloud builds submit \
    --tag $IMAGE_NAME:latest \
    --file Dockerfile.dashboard-automation \
    --timeout 1200s

echo "🚀 Fazendo deploy no Cloud Run..."
# Deploy no Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 540s \
    --max-instances 5 \
    --concurrency 10 \
    --service-account 609095880025-compute@developer.gserviceaccount.com

echo "✅ Deploy concluído com sucesso!"

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🌐 URL do serviço: $SERVICE_URL"

# Testar health check
echo "🔍 Testando health check..."
sleep 5
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passou!"
else
    echo "⚠️ Health check falhou. Verifique os logs:"
    echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
fi

echo ""
echo "📋 Endpoints disponíveis:"
echo "  🏥 Health: $SERVICE_URL/health"
echo "  📊 Status: $SERVICE_URL/status"
echo "  🚀 Trigger: $SERVICE_URL/trigger (POST)"
echo "  📋 Logs: $SERVICE_URL/logs"
echo ""

