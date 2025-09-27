#!/bin/bash
# Script para deploy do Git Manager Melhorado

echo "🚀 Deploy do Git Manager Melhorado"
echo "=================================="

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="git-manager-improved"
REGION="us-central1"

# Build da imagem
echo "📦 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 5 \
    --set-env-vars "GITHUB_TOKEN=$GITHUB_TOKEN"

# Verificar deploy
echo "✅ Verificando deploy..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"

echo "🎉 Deploy concluído!"
echo "URL do serviço: https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app"
