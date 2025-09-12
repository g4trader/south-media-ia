# 🚀 DEPLOY NO GOOGLE CLOUD RUN

Guia completo para fazer deploy da automação do dashboard no Google Cloud Run.

## 📋 PRÉ-REQUISITOS

### 1. Google Cloud CLI
```bash
# Instalar Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Fazer login
gcloud auth login

# Configurar projeto
gcloud config set project SEU_PROJECT_ID
```

### 2. Credenciais Google Sheets
- Arquivo `credentials/credentials.json` configurado
- Planilhas compartilhadas com a conta de serviço

### 3. APIs Habilitadas
```bash
# APIs necessárias (serão habilitadas automaticamente pelo deploy.sh)
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable sheets.googleapis.com
```

---

## 🚀 DEPLOY AUTOMÁTICO

### **Linux/Mac:**
```bash
./deploy.sh
```

### **Windows:**
```cmd
deploy.bat
```

### **Manual:**
```bash
# 1. Build da imagem
gcloud builds submit --tag gcr.io/$PROJECT_ID/dashboard-automation

# 2. Deploy para Cloud Run
gcloud run deploy dashboard-automation \
    --image gcr.io/$PROJECT_ID/dashboard-automation \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10

# 3. Configurar Scheduler
gcloud scheduler jobs create http dashboard-automation-scheduler \
    --schedule="0 */3 * * *" \
    --uri="https://dashboard-automation-xxxxx-uc.a.run.app/trigger" \
    --http-method=POST \
    --time-zone="America/Sao_Paulo"
```

---

## 🔐 CONFIGURAÇÃO DE CREDENCIAIS

### **Automática:**
```bash
./setup_cloud_credentials.sh
```

### **Manual:**
```bash
# 1. Criar secret
gcloud secrets create dashboard-automation-credentials \
    --data-file=credentials/credentials.json

# 2. Atualizar serviço
gcloud run services update dashboard-automation \
    --region=us-central1 \
    --set-secrets="GOOGLE_CREDENTIALS_FILE=dashboard-automation-credentials:latest"
```

---

## 🌐 ENDPOINTS DA API

Após o deploy, sua automação estará disponível em:
```
https://dashboard-automation-xxxxx-uc.a.run.app
```

### **Endpoints Disponíveis:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Health check |
| `/status` | GET | Status da automação |
| `/trigger` | POST | Disparar atualização manual |
| `/logs` | GET | Logs recentes |
| `/config` | GET | Configuração atual |

### **Exemplos de Uso:**

```bash
# Health check
curl https://dashboard-automation-xxxxx-uc.a.run.app/health

# Ver status
curl https://dashboard-automation-xxxxx-uc.a.run.app/status

# Disparar atualização manual
curl -X POST https://dashboard-automation-xxxxx-uc.a.run.app/trigger

# Ver logs
curl https://dashboard-automation-xxxxx-uc.a.run.app/logs
```

---

## ⏰ AGENDAMENTO AUTOMÁTICO

### **Cloud Scheduler Configurado:**
- **Frequência**: A cada 3 horas
- **Timezone**: America/Sao_Paulo
- **Endpoint**: `/trigger`
- **Retry**: 3 tentativas

### **Verificar Scheduler:**
```bash
# Listar jobs
gcloud scheduler jobs list

# Ver detalhes
gcloud scheduler jobs describe dashboard-automation-scheduler

# Executar manualmente
gcloud scheduler jobs run dashboard-automation-scheduler
```

---

## 📊 MONITORAMENTO

### **Cloud Console:**
1. Acesse: https://console.cloud.google.com/
2. Vá em **Cloud Run** > **dashboard-automation**
3. Monitore métricas, logs e execuções

### **Logs via CLI:**
```bash
# Logs em tempo real
gcloud run logs tail dashboard-automation --region=us-central1

# Logs recentes
gcloud run logs read dashboard-automation --region=us-central1 --limit=50

# Filtrar por erro
gcloud run logs read dashboard-automation --region=us-central1 --filter="severity>=ERROR"
```

### **Métricas:**
```bash
# Ver métricas
gcloud run services describe dashboard-automation --region=us-central1
```

---

## 🔧 CONFIGURAÇÕES AVANÇADAS

### **Recursos do Container:**
```bash
gcloud run services update dashboard-automation \
    --region=us-central1 \
    --memory=4Gi \
    --cpu=4 \
    --max-instances=20 \
    --timeout=3600
```

### **Variáveis de Ambiente:**
```bash
gcloud run services update dashboard-automation \
    --region=us-central1 \
    --set-env-vars="LOG_LEVEL=DEBUG,NOTIFICATION_ENABLED=true"
```

### **Secrets:**
```bash
# Adicionar secret
gcloud secrets create my-secret --data-file=file.txt

# Usar secret no serviço
gcloud run services update dashboard-automation \
    --region=us-central1 \
    --set-secrets="MY_SECRET=my-secret:latest"
```

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### **Erro: "Permission denied"**
```bash
# Verificar permissões
gcloud auth list
gcloud config get-value project

# Fazer login novamente
gcloud auth login
```

### **Erro: "Service not found"**
```bash
# Verificar se serviço existe
gcloud run services list --region=us-central1

# Fazer deploy novamente
./deploy.sh
```

### **Erro: "Credentials not found"**
```bash
# Configurar credenciais
./setup_cloud_credentials.sh

# Ou manualmente
gcloud run services update dashboard-automation \
    --region=us-central1 \
    --set-secrets="GOOGLE_CREDENTIALS_FILE=dashboard-automation-credentials:latest"
```

### **Erro: "Scheduler not found"**
```bash
# Recriar scheduler
gcloud scheduler jobs delete dashboard-automation-scheduler

# Recriar com URL correta
SERVICE_URL=$(gcloud run services describe dashboard-automation --region=us-central1 --format="value(status.url)")
gcloud scheduler jobs create http dashboard-automation-scheduler \
    --schedule="0 */3 * * *" \
    --uri="$SERVICE_URL/trigger" \
    --http-method=POST \
    --time-zone="America/Sao_Paulo"
```

---

## 📈 OTIMIZAÇÕES

### **Performance:**
- **Memory**: 2Gi (pode aumentar se necessário)
- **CPU**: 2 (pode aumentar se necessário)
- **Timeout**: 3600s (1 hora)
- **Max Instances**: 10

### **Custos:**
- **Execução**: Apenas quando necessário
- **Cold Start**: ~5-10 segundos
- **Custo**: Baseado em CPU/Memory/Requests

### **Escalabilidade:**
- **Auto-scaling**: 0 a 10 instâncias
- **Concorrência**: 1000 requests por instância
- **Load Balancing**: Automático

---

## 🔄 ATUALIZAÇÕES

### **Redeploy:**
```bash
# Deploy automático
./deploy.sh

# Ou manual
gcloud builds submit --tag gcr.io/$PROJECT_ID/dashboard-automation
gcloud run deploy dashboard-automation \
    --image gcr.io/$PROJECT_ID/dashboard-automation \
    --region=us-central1
```

### **Rollback:**
```bash
# Ver revisões
gcloud run revisions list --service=dashboard-automation --region=us-central1

# Fazer rollback
gcloud run services update-traffic dashboard-automation \
    --region=us-central1 \
    --to-revisions=REVISION_NAME=100
```

---

## 📞 SUPORTE

### **Logs Úteis:**
```bash
# Logs de automação
gcloud run logs read dashboard-automation --region=us-central1 --filter="textPayload:\"automação\""

# Logs de erro
gcloud run logs read dashboard-automation --region=us-central1 --filter="severity>=ERROR"

# Logs de scheduler
gcloud scheduler jobs describe dashboard-automation-scheduler
```

### **Comandos de Diagnóstico:**
```bash
# Status do serviço
gcloud run services describe dashboard-automation --region=us-central1

# Status do scheduler
gcloud scheduler jobs describe dashboard-automation-scheduler

# Teste de conectividade
curl https://dashboard-automation-xxxxx-uc.a.run.app/health
```

---

## 🎉 PRONTO!

Após seguir todos os passos:

1. ✅ **Serviço Cloud Run** funcionando
2. ✅ **Cloud Scheduler** configurado (a cada 3h)
3. ✅ **Credenciais** configuradas
4. ✅ **API endpoints** disponíveis
5. ✅ **Monitoramento** ativo

**🚀 Sua automação estará rodando na nuvem, atualizando o dashboard automaticamente a cada 3 horas!**
