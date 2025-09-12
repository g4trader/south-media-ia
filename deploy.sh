#!/bin/bash

# Script de deploy para Google Cloud Run
# Execute: ./deploy.sh

set -e

echo "🚀 DEPLOY DA AUTOMAÇÃO DO DASHBOARD PARA CLOUD RUN"
echo "=================================================="

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI não encontrado"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar se está logado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Não está logado no Google Cloud"
    echo "Execute: gcloud auth login"
    exit 1
fi

# Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID não configurado"
    echo "Execute: gcloud config set project SEU_PROJECT_ID"
    exit 1
fi

echo "📋 Projeto: $PROJECT_ID"
echo "📍 Região: us-central1"
echo ""

# Habilitar APIs necessárias
echo "🔧 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable sheets.googleapis.com

# Fazer build e deploy
echo "🏗️ Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/dashboard-automation

# Deploy para Cloud Run
echo "🚀 Deployando para Cloud Run..."
gcloud run deploy dashboard-automation \
    --image gcr.io/$PROJECT_ID/dashboard-automation \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars AUTOMATION_MODE=scheduler

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe dashboard-automation --region=us-central1 --format="value(status.url)")

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "🌐 URL do serviço: $SERVICE_URL"
echo ""

# Configurar Cloud Scheduler
echo "⏰ Configurando Cloud Scheduler..."

# Atualizar scheduler.yaml com URL real
sed "s|https://dashboard-automation-xxxxx-uc.a.run.app/trigger|$SERVICE_URL/trigger|g" scheduler.yaml > scheduler_updated.yaml

# Criar job do scheduler
gcloud scheduler jobs create http dashboard-automation-scheduler \
    --schedule="0 */3 * * *" \
    --uri="$SERVICE_URL/trigger" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"triggered_by":"cloud_scheduler"}' \
    --time-zone="America/Sao_Paulo" \
    --description="Executa automação do dashboard a cada 3 horas" \
    || echo "⚠️ Scheduler pode já existir, tentando atualizar..."

# Atualizar se já existir
gcloud scheduler jobs update http dashboard-automation-scheduler \
    --schedule="0 */3 * * *" \
    --uri="$SERVICE_URL/trigger" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"triggered_by":"cloud_scheduler"}' \
    --time-zone="America/Sao_Paulo" \
    --description="Executa automação do dashboard a cada 3 horas" \
    || true

echo ""
echo "🎉 CONFIGURAÇÃO COMPLETA!"
echo "========================="
echo "✅ Serviço Cloud Run: $SERVICE_URL"
echo "✅ Cloud Scheduler configurado para executar a cada 3 horas"
echo ""
echo "🔗 Endpoints disponíveis:"
echo "  - Health: $SERVICE_URL/health"
echo "  - Status: $SERVICE_URL/status"
echo "  - Logs: $SERVICE_URL/logs"
echo "  - Trigger manual: $SERVICE_URL/trigger (POST)"
echo ""
echo "📋 Para configurar credenciais:"
echo "  1. Acesse o Cloud Console"
echo "  2. Vá em Cloud Run > dashboard-automation"
echo "  3. Edite e adicione as variáveis de ambiente necessárias"
echo "  4. Faça upload do arquivo credentials.json"
echo ""
echo "🧪 Para testar:"
echo "  curl $SERVICE_URL/health"
echo "  curl -X POST $SERVICE_URL/trigger"
