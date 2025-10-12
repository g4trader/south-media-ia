#!/bin/bash

# Script de Deploy para STAGING - stg-gen-dashboard-ia
# Ambiente de teste antes do deploy em produção

set -e

echo "🚀 DEPLOY STAGING - STG-GEN-DASHBOARD-IA"
echo "========================================="
echo "🧪 Ambiente de teste com todas as funcionalidades de filtro"
echo ""

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="stg-gen-dashboard-ia"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📊 Configurações do Staging:"
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
if [ ! -f "persistent_server.py" ]; then
    echo "❌ Arquivo persistent_server.py não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar se os arquivos necessários existem
echo "🔍 Verificando arquivos necessários..."
required_files=("persistent_server.py" "persistent_database.py" "requirements.txt" "Dockerfile")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo $file não encontrado."
        exit 1
    fi
done
echo "✅ Todos os arquivos necessários estão presentes."

# Verificar se os templates com filtros estão presentes
echo "🔍 Verificando templates com filtros..."
template_files=("static/dash_copacol_video_de_30s_campanha_institucional_netflix.html" "static/dash_generic_template.html" "static/dash_remarketing_cpm_template.html")
for file in "${template_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Template $file não encontrado."
        exit 1
    fi
done
echo "✅ Templates com filtros estão presentes."

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable firestore.googleapis.com

# Build e Deploy
echo "🏗️ Construindo imagem para staging..."
gcloud builds submit --tag $IMAGE_NAME

echo "🚀 Fazendo deploy para Cloud Run (STAGING)..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 3 \
    --timeout 300 \
    --concurrency 80 \
    --cpu-boost \
    --execution-environment gen2 \
    --set-env-vars "PROJECT_ID=$PROJECT_ID,ENVIRONMENT=staging" \
    --service-account 609095880025-compute@developer.gserviceaccount.com

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "✅ DEPLOY STAGING CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo "🌐 URL do Serviço Staging: $SERVICE_URL"
echo ""

# Aguardar o serviço ficar disponível
echo "⏳ Aguardando serviço staging ficar disponível..."
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
echo "📋 Endpoints Disponíveis (STAGING):"
echo "  🏠 Home: $SERVICE_URL/"
echo "  🏥 Health: $SERVICE_URL/health"
echo "  📊 Persistência: $SERVICE_URL/persistence-status"
echo "  🎯 Gerador: $SERVICE_URL/api/generate-dashboard"
echo "  📋 Campanhas: $SERVICE_URL/api/campaigns"
echo "  📊 Dashboards: $SERVICE_URL/api/dashboards"
echo ""
echo "🧪 Teste o gerador (STAGING):"
echo "  curl -X POST $SERVICE_URL/api/generate-dashboard \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"campaign_key\": \"teste_staging\", \"client\": \"Teste Staging\", \"campaign_name\": \"Campanha Staging\", \"sheet_id\": \"1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8\"}'"
echo ""
echo "🎉 STG-GEN-DASHBOARD-IA está rodando no ambiente de staging!"
echo "🧪 Teste todas as funcionalidades antes do deploy em produção"
echo ""
echo "📊 Configurações do Staging:"
echo "  - Memória: 1GB (economia vs produção)"
echo "  - CPU: 1 vCPU (economia vs produção)"
echo "  - Max Instances: 3 (limite vs produção)"
echo "  - Timeout: 300s (5 min vs 1h produção)"
echo "  - Environment: staging"
echo ""
echo "🔄 Para fazer deploy em produção após testes:"
echo "  ./deploy_gen_dashboard_ia.sh"
