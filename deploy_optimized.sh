#!/bin/bash

# Script otimizado para build e deploy no Cloud Run
# Inclui otimizações de custo e performance

set -e  # Exit on any error

PROJECT_ID="automatizar-452311"
SERVICE_NAME="dashboard-builder"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Iniciando deploy otimizado do South Media IA Dashboard Builder..."
echo "📊 Projeto: $PROJECT_ID"
echo "🌍 Região: $REGION"

# Verificar se gcloud está configurado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo "❌ Gcloud não está autenticado. Execute: gcloud auth login"
    exit 1
fi

# Definir projeto
gcloud config set project $PROJECT_ID

echo "📦 Fazendo build da imagem otimizada..."
# Build com otimizações
gcloud builds submit \
    --tag $IMAGE_NAME:latest \
    --file Dockerfile.optimized \
    --machine-type E2_HIGHCPU_8 \
    --disk-size 100GB \
    --timeout 1200s \
    --async

echo "⏳ Aguardando build concluir..."
gcloud builds list --limit=1 --format="value(id)" | head -n1 | xargs -I {} gcloud builds log {} --stream

echo "🚀 Fazendo deploy no Cloud Run com configurações otimizadas..."

# Deploy com configurações otimizadas
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --cpu-boost \
    --execution-environment gen2 \
    --min-instances 0 \
    --max-instances 5 \
    --concurrency 80 \
    --cpu-throttling \
    --timeout 300s \
    --service-account dashboard-builder-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=info,GUNICORN_WORKERS=1" \
    --quiet

echo "✅ Deploy concluído com sucesso!"

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🌐 URL do serviço: $SERVICE_URL"

# Testar health check
echo "🔍 Testando health check..."
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passou!"
else
    echo "⚠️ Health check falhou - verificar logs"
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=10 --format="value(textPayload)"
fi

echo "📊 Deploy otimizado concluído!"
echo "💡 Otimizações aplicadas:"
echo "   - Memória reduzida para 512Mi (economia ~50%)"
echo "   - Max instances reduzido para 5 (economia ~50%)"
echo "   - Scale-to-zero habilitado"
echo "   - CPU boost habilitado"
echo "   - Concurrency otimizada para 80"
echo "   - Imagem Docker otimizada (multi-stage build)"

