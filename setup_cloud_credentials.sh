#!/bin/bash

# Script para configurar credenciais no Google Cloud Run
# Execute: ./setup_cloud_credentials.sh

set -e

echo "🔐 CONFIGURAÇÃO DE CREDENCIAIS NO CLOUD RUN"
echo "==========================================="

# Verificar se arquivo credentials.json existe
if [ ! -f "credentials/credentials.json" ]; then
    echo "❌ Arquivo credentials/credentials.json não encontrado"
    echo "📋 Siga estes passos:"
    echo "1. Acesse: https://console.cloud.google.com/"
    echo "2. Vá em APIs & Services > Credentials"
    echo "3. Crie credenciais OAuth 2.0 (Desktop Application)"
    echo "4. Baixe o arquivo JSON"
    echo "5. Coloque em: credentials/credentials.json"
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
echo ""

# Criar Secret Manager secret para credentials
echo "🔐 Criando secret para credenciais..."
SECRET_NAME="dashboard-automation-credentials"

# Criar secret se não existir
gcloud secrets create $SECRET_NAME --data-file=credentials/credentials.json 2>/dev/null || \
    gcloud secrets versions add $SECRET_NAME --data-file=credentials/credentials.json

echo "✅ Secret criado/atualizado: $SECRET_NAME"

# Obter SERVICE_URL
SERVICE_URL=$(gcloud run services describe dashboard-automation --region=us-central1 --format="value(status.url)" 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo "⚠️ Serviço Cloud Run não encontrado"
    echo "Execute primeiro: ./deploy.sh"
    exit 1
fi

echo "🌐 Serviço: $SERVICE_URL"

# Atualizar serviço Cloud Run com secret
echo "🔄 Atualizando serviço Cloud Run com credenciais..."

gcloud run services update dashboard-automation \
    --region=us-central1 \
    --set-secrets="GOOGLE_CREDENTIALS_FILE=$SECRET_NAME:latest" \
    --set-env-vars="AUTOMATION_MODE=scheduler,LOG_LEVEL=INFO,BACKUP_ENABLED=true"

echo ""
echo "✅ CONFIGURAÇÃO DE CREDENCIAIS CONCLUÍDA!"
echo "=========================================="
echo "🔐 Credenciais configuradas via Secret Manager"
echo "🌐 Serviço atualizado: $SERVICE_URL"
echo ""
echo "🧪 Para testar:"
echo "  curl $SERVICE_URL/health"
echo "  curl $SERVICE_URL/status"
echo ""
echo "📋 Próximos passos:"
echo "1. Verificar se o serviço está funcionando"
echo "2. Testar trigger manual: curl -X POST $SERVICE_URL/trigger"
echo "3. Verificar logs no Cloud Console"
echo ""
echo "🔍 Para monitorar:"
echo "  gcloud run logs read dashboard-automation --region=us-central1 --limit=50"
