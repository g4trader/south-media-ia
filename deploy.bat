@echo off
echo ================================================
echo   DEPLOY DA AUTOMACAO DO DASHBOARD PARA CLOUD RUN
echo ================================================

REM Verificar se gcloud está instalado
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Google Cloud CLI não encontrado
    echo Instale em: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Verificar se está logado
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr . >nul
if %errorlevel% neq 0 (
    echo ❌ Não está logado no Google Cloud
    echo Execute: gcloud auth login
    pause
    exit /b 1
)

REM Obter PROJECT_ID
for /f "delims=" %%i in ('gcloud config get-value project') do set PROJECT_ID=%%i
if "%PROJECT_ID%"=="" (
    echo ❌ PROJECT_ID não configurado
    echo Execute: gcloud config set project SEU_PROJECT_ID
    pause
    exit /b 1
)

echo 📋 Projeto: %PROJECT_ID%
echo 📍 Região: us-central1
echo.

REM Habilitar APIs necessárias
echo 🔧 Habilitando APIs necessárias...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable sheets.googleapis.com

REM Fazer build e deploy
echo 🏗️ Fazendo build da imagem...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/dashboard-automation

REM Deploy para Cloud Run
echo 🚀 Deployando para Cloud Run...
gcloud run deploy dashboard-automation ^
    --image gcr.io/%PROJECT_ID%/dashboard-automation ^
    --region us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 3600 ^
    --max-instances 10 ^
    --set-env-vars AUTOMATION_MODE=scheduler

REM Obter URL do serviço
for /f "delims=" %%i in ('gcloud run services describe dashboard-automation --region=us-central1 --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ✅ DEPLOY CONCLUÍDO!
echo 🌐 URL do serviço: %SERVICE_URL%
echo.

REM Configurar Cloud Scheduler
echo ⏰ Configurando Cloud Scheduler...

REM Criar job do scheduler
gcloud scheduler jobs create http dashboard-automation-scheduler ^
    --schedule="0 */3 * * *" ^
    --uri="%SERVICE_URL%/trigger" ^
    --http-method=POST ^
    --headers="Content-Type=application/json" ^
    --message-body="{\"triggered_by\":\"cloud_scheduler\"}" ^
    --time-zone="America/Sao_Paulo" ^
    --description="Executa automação do dashboard a cada 3 horas" 2>nul

if %errorlevel% neq 0 (
    echo Atualizando scheduler existente...
    gcloud scheduler jobs update http dashboard-automation-scheduler ^
        --schedule="0 */3 * * *" ^
        --uri="%SERVICE_URL%/trigger" ^
        --http-method=POST ^
        --headers="Content-Type=application/json" ^
        --message-body="{\"triggered_by\":\"cloud_scheduler\"}" ^
        --time-zone="America/Sao_Paulo" ^
        --description="Executa automação do dashboard a cada 3 horas"
)

echo.
echo 🎉 CONFIGURAÇÃO COMPLETA!
echo =========================
echo ✅ Serviço Cloud Run: %SERVICE_URL%
echo ✅ Cloud Scheduler configurado para executar a cada 3 horas
echo.
echo 🔗 Endpoints disponíveis:
echo   - Health: %SERVICE_URL%/health
echo   - Status: %SERVICE_URL%/status
echo   - Logs: %SERVICE_URL%/logs
echo   - Trigger manual: %SERVICE_URL%/trigger (POST)
echo.
echo 📋 Para configurar credenciais:
echo   1. Acesse o Cloud Console
echo   2. Vá em Cloud Run ^> dashboard-automation
echo   3. Edite e adicione as variáveis de ambiente necessárias
echo   4. Faça upload do arquivo credentials.json
echo.
echo 🧪 Para testar:
echo   curl %SERVICE_URL%/health
echo   curl -X POST %SERVICE_URL%/trigger

pause
