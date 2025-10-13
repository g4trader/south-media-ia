#!/bin/bash

# Script para deploy em ambiente de teste
# Cria um ambiente separado para testar a correção de datas

set -e

echo "🚀 DEPLOY EM AMBIENTE DE TESTE - CORREÇÃO DE DATAS"
echo "=================================================="

# Configurações do ambiente de teste
PROJECT_ID=${PROJECT_ID:-"automatizar-452311"}
SERVICE_NAME="dashboard-builder-test"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
BUILD_ID=$(date +%Y%m%d-%H%M%S)

echo "📊 Configurações do ambiente de teste:"
echo "  Projeto: $PROJECT_ID"
echo "  Serviço: $SERVICE_NAME"
echo "  Região: $REGION"
echo "  Imagem: $IMAGE_NAME:$BUILD_ID"
echo ""

# Verificar se gcloud está configurado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK não encontrado. Instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "real_google_sheets_extractor.py" ]; then
    echo "❌ Arquivo real_google_sheets_extractor.py não encontrado. Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar se a correção foi aplicada
if ! grep -q "date_normalizer" real_google_sheets_extractor.py; then
    echo "❌ Correção de datas não aplicada no real_google_sheets_extractor.py"
    echo "   Execute primeiro: python3 apply_date_fix.py"
    exit 1
fi

echo "✅ Correção de datas detectada no código"

# Verificar se o arquivo date_normalizer.py existe
if [ ! -f "date_normalizer.py" ]; then
    echo "❌ Arquivo date_normalizer.py não encontrado"
    exit 1
fi

echo "✅ Arquivo date_normalizer.py encontrado"

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build da imagem com correção
echo "🏗️ Construindo imagem com correção de datas..."
gcloud builds submit --tag $IMAGE_NAME:$BUILD_ID

echo "🚀 Fazendo deploy para ambiente de teste..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:$BUILD_ID \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --concurrency 80 \
    --timeout 300s \
    --set-env-vars ENVIRONMENT=test,LOG_LEVEL=info,GUNICORN_WORKERS=1

# Obter URL do serviço de teste
TEST_URL=$(gcloud run services describe $SERVICE_NAME --project=$PROJECT_ID --platform=managed --region=$REGION --format='value(status.url)')

echo ""
echo "✅ DEPLOY EM AMBIENTE DE TESTE CONCLUÍDO!"
echo "=========================================="
echo "🌐 URL do ambiente de teste: $TEST_URL"
echo "📊 Imagem: $IMAGE_NAME:$BUILD_ID"
echo ""
echo "🧪 PRÓXIMOS PASSOS:"
echo "1. Testar endpoints no ambiente de teste"
echo "2. Validar correção de datas"
echo "3. Se tudo estiver OK, fazer deploy em produção"
echo ""
echo "📋 COMANDOS PARA TESTE:"
echo "curl \"$TEST_URL/health\""
echo "curl \"$TEST_URL/api/copacol_semana_do_pescado_youtube/data\""
echo ""
echo "⚠️  IMPORTANTE: Este é um ambiente de TESTE separado da produção"
echo "   A produção continua funcionando normalmente até a validação"
