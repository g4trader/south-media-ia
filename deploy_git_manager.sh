#!/bin/bash

# Deploy Git Manager Microservice para Cloud Run
echo "🚀 DEPLOY GIT MANAGER MICROSERVICE PARA CLOUD RUN"
echo "================================================"

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="git-manager"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/git-manager"

echo "📊 Configurações:"
echo "  Projeto: $PROJECT_ID"
echo "  Serviço: $SERVICE_NAME"
echo "  Região: $REGION"
echo "  Imagem: $IMAGE_NAME"
echo ""

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Construir e fazer deploy
echo "🏗️ Construindo e fazendo deploy..."
gcloud builds submit \
    --tag $IMAGE_NAME \
    .

# Deploy para Cloud Run
echo "🚀 Fazendo deploy para Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 5 \
    --timeout 300 \
    --set-env-vars GITHUB_TOKEN=$GITHUB_TOKEN \
    --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================="
echo "🌐 URL do Serviço: $SERVICE_URL"
echo ""
echo "📋 Endpoints Disponíveis:"
echo "  🏥 Health: $SERVICE_URL/health"
echo "  📊 Status: $SERVICE_URL/status"
echo "  🔄 Process: $SERVICE_URL/process"
echo "  💪 Force Commit: $SERVICE_URL/force-commit"
echo ""
echo "🧪 Teste o microserviço:"
echo "  curl $SERVICE_URL/health"
echo "  curl $SERVICE_URL/status"
echo "  curl -X POST $SERVICE_URL/process"
echo ""
echo "🎉 Git Manager Microservice está rodando na nuvem!"
