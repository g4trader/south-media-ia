#!/bin/bash

# Configurar Cloud Scheduler para Git Manager
echo "⏰ CONFIGURANDO CLOUD SCHEDULER PARA GIT MANAGER"
echo "==============================================="

# Configurações
PROJECT_ID="automatizar-452311"
SERVICE_NAME="git-manager"
REGION="us-central1"
JOB_NAME="git-manager-process"
SERVICE_URL="https://git-manager-609095880025.us-central1.run.app"

echo "📊 Configurações:"
echo "  Projeto: $PROJECT_ID"
echo "  Serviço: $SERVICE_NAME"
echo "  Região: $REGION"
echo "  Job: $JOB_NAME"
echo "  URL: $SERVICE_URL"
echo ""

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs..."
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable run.googleapis.com

# Criar job do Cloud Scheduler
echo "⏰ Criando job do Cloud Scheduler..."
gcloud scheduler jobs create http $JOB_NAME \
    --location=$REGION \
    --schedule="*/2 * * * *" \
    --uri="$SERVICE_URL/process" \
    --http-method=GET \
    --time-zone="America/Sao_Paulo" \
    --description="Processar arquivos novos no Git Manager a cada 2 minutos" \
    --max-retry-attempts=3 \
    --max-retry-duration=300s \
    --min-backoff=10s \
    --max-backoff=60s

echo ""
echo "✅ CLOUD SCHEDULER CONFIGURADO COM SUCESSO!"
echo "==========================================="
echo "⏰ Job: $JOB_NAME"
echo "🔄 Frequência: A cada 2 minutos"
echo "🌐 URL: $SERVICE_URL/process"
echo "⏰ Timezone: America/Sao_Paulo"
echo ""
echo "📋 Comandos úteis:"
echo "  📊 Listar jobs: gcloud scheduler jobs list"
echo "  ▶️ Executar job: gcloud scheduler jobs run $JOB_NAME"
echo "  ⏸️ Pausar job: gcloud scheduler jobs pause $JOB_NAME"
echo "  ▶️ Retomar job: gcloud scheduler jobs resume $JOB_NAME"
echo "  🗑️ Deletar job: gcloud scheduler jobs delete $JOB_NAME"
echo ""
echo "🎉 Cloud Scheduler está configurado e funcionando!"
