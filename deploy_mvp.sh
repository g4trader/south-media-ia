#!/bin/bash

# Script de Deploy para MVP Dashboard Builder
# Google Cloud Run - Versão Melhorada

set -e

echo "🚀 DEPLOY MVP DASHBOARD BUILDER PARA CLOUD RUN"
echo "=============================================="

# Configurações
PROJECT_ID=${PROJECT_ID:-"automatizar-452311"}
SERVICE_NAME="mvp-dashboard-builder"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📊 Configurações:"
echo "  Projeto: $PROJECT_ID"
echo "  Serviço: $SERVICE_NAME"
echo "  Região: $REGION"
echo "  Imagem: $IMAGE_NAME"
echo ""

# Verificar se gcloud está configurado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK não encontrado. Instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "cloud_run_mvp.py" ]; then
    echo "❌ Arquivo cloud_run_mvp.py não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar se os arquivos necessários existem
echo "🔍 Verificando arquivos necessários..."
required_files=("cloud_run_mvp.py" "requirements.txt" "Dockerfile" "gunicorn.conf.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo $file não encontrado."
        exit 1
    fi
done
echo "✅ Todos os arquivos necessários estão presentes."

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build e Deploy
echo "🏗️ Construindo e fazendo deploy..."
gcloud builds submit --tag $IMAGE_NAME

echo "🚀 Fazendo deploy para Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================="
echo "🌐 URL do Serviço: $SERVICE_URL"
echo ""

# Aguardar o serviço ficar disponível
echo "⏳ Aguardando serviço ficar disponível..."
sleep 30

# Testar health check
echo "🏥 Testando health check..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo "✅ Health check passou!"
else
    echo "⚠️ Health check falhou. Verifique os logs:"
    echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50 --format=\"table(timestamp,severity,textPayload)\""
fi

echo ""
echo "📋 Endpoints Disponíveis:"
echo "  🏠 Home: $SERVICE_URL/"
echo "  🏥 Health: $SERVICE_URL/health"
echo "  🎯 Gerador: $SERVICE_URL/dash-generator-pro"
echo "  📊 API: $SERVICE_URL/api/generate-dashboard"
echo ""
echo "🧪 Teste o gerador:"
echo "  curl -X POST $SERVICE_URL/api/generate-dashboard \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"campaign_key\": \"teste\", \"client\": \"Teste\", \"campaign_name\": \"Campanha Teste\", \"sheet_id\": \"1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8\"}'"
echo ""
echo "🎉 MVP Dashboard Builder está rodando na nuvem!"

