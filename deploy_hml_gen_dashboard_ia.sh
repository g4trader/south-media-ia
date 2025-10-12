#!/bin/bash

# Script de Deploy para Ambiente de Homologação
# Service: hml-gen-dashboard-ia
# Environment: hml

set -e

echo "🚀 DEPLOY HOMOLOGAÇÃO - HML-GEN-DASHBOARD-IA"
echo "=========================================="
echo "🔬 Ambiente de validação final antes de produção"
echo ""

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="hml-gen-dashboard-ia"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📊 Configurações do Homologação:"
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
echo "🏗️ Construindo imagem para homologação..."
gcloud builds submit --tag ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir imagem"
    exit 1
fi

echo "✅ Imagem construída com sucesso!"

# Deploy no Cloud Run
echo "🚀 Fazendo deploy para Cloud Run (HOMOLOGAÇÃO)..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},ENVIRONMENT=hml" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 1800 \
    --max-instances 5 \
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
echo "✅ DEPLOY HOMOLOGAÇÃO CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo "🌐 URL do Serviço Homologação: ${SERVICE_URL}"
echo ""

# Aguardar serviço ficar disponível
echo "⏳ Aguardando serviço homologação ficar disponível..."
sleep 10

# Health check
echo "🏥 Testando health check..."
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health" || echo "failed")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Health check passou!"
else
    echo "⚠️  Health check falhou. Verifique os logs:"
    echo "   gcloud run services logs read ${SERVICE_NAME} --limit=50"
fi

echo ""
echo "📋 Endpoints Disponíveis (HOMOLOGAÇÃO):"
echo "  🏠 Home: ${SERVICE_URL}/"
echo "  🏥 Health: ${SERVICE_URL}/health"
echo "  📊 Persistência: ${SERVICE_URL}/persistence-status"
echo "  🎯 Gerador: ${SERVICE_URL}/api/generate-dashboard"
echo "  📋 Campanhas: ${SERVICE_URL}/api/campaigns"
echo "  📊 Dashboards: ${SERVICE_URL}/api/dashboards"
echo "  📋 Lista: ${SERVICE_URL}/dashboards-list"
echo ""

echo "🧪 Teste o gerador (HOMOLOGAÇÃO):"
echo "  curl -X POST ${SERVICE_URL}/api/generate-dashboard \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"campaign_key\": \"teste_hml\", \"client\": \"Teste HML\", \"campaign_name\": \"Campanha HML\", \"sheet_id\": \"1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8\"}'"
echo ""

echo "🎉 HML-GEN-DASHBOARD-IA está rodando no ambiente de homologação!"
echo "🔬 Valide todas as funcionalidades antes do deploy em produção"
echo ""

echo "📊 Configurações do Homologação:"
echo "  - Memória: 2GB (melhor performance que staging)"
echo "  - CPU: 2 vCPU (melhor performance que staging)"
echo "  - Max Instances: 5 (mais que staging, menos que produção)"
echo "  - Timeout: 1800s (30 min - adequado para validação)"
echo "  - Environment: hml"
echo ""

echo "🔄 Para fazer deploy em produção após validação:"
echo "  ./deploy_gen_dashboard_ia.sh"
echo ""

echo "📝 Checklist de Validação:"
echo "  [ ] Testar interface web"
echo "  [ ] Gerar dashboard de teste"
echo "  [ ] Verificar filtros funcionam"
echo "  [ ] Testar listagem de dashboards"
echo "  [ ] Confirmar persistência de dados"
echo "  [ ] Validar com stakeholders"
echo "  [ ] Aprovar para produção"
echo ""
