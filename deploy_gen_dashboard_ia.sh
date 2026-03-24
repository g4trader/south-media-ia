#!/bin/bash

# Script de Deploy para Ambiente de Produção
# Service: gen-dashboard-ia
# Environment: production

set -e

echo "🚀 DEPLOY PRODUÇÃO - GEN-DASHBOARD-IA"
echo "=========================================="
echo "⚠️  AMBIENTE DE PRODUÇÃO - Deploy após validação completa"
echo ""

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="gen-dashboard-ia"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📊 Configurações do Produção:"
echo "  Projeto: ${PROJECT_ID}"
echo "  Serviço: ${SERVICE_NAME}"
echo "  Região: ${REGION}"
echo "  Imagem: ${IMAGE_NAME}"
echo ""

# Verificar arquivos necessários
echo "🔍 Verificando arquivos necessários..."
REQUIRED_FILES=(
    "cloud_run_mvp.py"
    "bigquery_firestore_manager.py"
    "templates_client_admin.py"
    "real_google_sheets_extractor.py"
    "google_sheets_service.py"
    "config.py"
    "gunicorn.conf.py"
    "date_normalizer.py"
    "requirements.txt"
    "Dockerfile"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo não encontrado: $file"
        exit 1
    fi
done
echo "✅ Todos os arquivos necessários estão presentes."

# Verificar templates com filtros
echo "🔍 Verificando templates com filtros..."
TEMPLATE_FILES=(
    "static/dash_generic_template.html"
    "static/dash_remarketing_cpm_template.html"
)

for file in "${TEMPLATE_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Template não encontrado: $file"
        exit 1
    fi
done
echo "✅ Templates com filtros estão presentes."

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project ${PROJECT_ID}

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    bigquery.googleapis.com \
    firestore.googleapis.com \
    sheets.googleapis.com \
    >/dev/null 2>&1 || true

# Build da imagem
echo "🏗️ Construindo imagem para produção..."
gcloud builds submit --tag ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir imagem"
    exit 1
fi

echo "✅ Imagem construída com sucesso!"

# Deploy no Cloud Run
echo "🚀 Fazendo deploy para Cloud Run (PRODUÇÃO)..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},ENVIRONMENT=production" \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 80 \
    --port 8080

if [ $? -ne 0 ]; then
    echo "❌ Erro no deploy"
    exit 1
fi

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --format 'value(status.url)')

echo ""
echo "✅ DEPLOY PRODUÇÃO CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo "🌐 URL do Serviço Produção: ${SERVICE_URL}"
echo ""

# Aguardar serviço ficar disponível
echo "⏳ Aguardando serviço produção ficar disponível..."
sleep 15

# Health check
echo "🏥 Testando health check..."
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health" || echo "failed")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Health check passou!"
else
    echo "⚠️  Health check falhou. Verifique os logs:"
    echo "   gcloud run services logs read ${SERVICE_NAME} --limit=50"
fi

# Teste Selenium: validar dashboard operacional (ex.: FPS YouTube)
echo ""
echo "🧪 Teste Selenium - dashboard operacional..."
if BASE_URL="${SERVICE_URL}" python3 selenium_test_dashboard.py 2>/dev/null; then
    echo "✅ Teste Selenium passou!"
else
    echo "⚠️  Teste Selenium falhou. Execute manualmente: BASE_URL=${SERVICE_URL} python3 selenium_test_dashboard.py"
fi

echo ""
echo "📋 Endpoints Disponíveis (PRODUÇÃO):"
echo "  🏠 Home: ${SERVICE_URL}/"
echo "  🏥 Health: ${SERVICE_URL}/health"
echo "  📊 Persistência: ${SERVICE_URL}/persistence-status"
echo "  🎯 Gerador: ${SERVICE_URL}/api/generate-dashboard"
echo "  📋 Campanhas: ${SERVICE_URL}/api/campaigns"
echo "  📊 Dashboards: ${SERVICE_URL}/api/dashboards"
echo "  📋 Lista: ${SERVICE_URL}/dashboards-list"
echo ""

echo "🎉 GEN-DASHBOARD-IA V2.0 está rodando em PRODUÇÃO!"
echo "🔬 Sistema com filtros interativos e persistência definitiva"
echo ""

echo "📊 Configurações do Produção:"
echo "  - Memória: 4GB (máxima performance)"
echo "  - CPU: 2 vCPU (melhor performance)"
echo "  - Max Instances: 10 (alta disponibilidade)"
echo "  - Timeout: 3600s (1h - operações longas)"
echo "  - Environment: production"
echo ""

echo "🔍 Monitoramento:"
echo "  - Logs: gcloud run services logs tail ${SERVICE_NAME}"
echo "  - Console: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}"
echo ""
