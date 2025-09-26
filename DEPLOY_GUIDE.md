# 🚀 Guia de Deploy - MVP Dashboard Builder

## 📋 Visão Geral

Este guia mostra como fazer deploy do MVP Dashboard Builder para o Google Cloud Run, mantendo todas as funcionalidades desenvolvidas localmente.

## ✅ Funcionalidades do MVP

- ✅ **Gerador de Dashboards** - Interface web e API
- ✅ **Cards de Totalizadores** - 12 métricas principais na aba "Por Canal"
- ✅ **Loading Modal Real** - Progresso baseado em processos reais
- ✅ **Extração de Dados** - Google Sheets em tempo real
- ✅ **Tipo de Criativo** - Campo corrigido e funcionando
- ✅ **Formatação Brasileira** - R$, %, números
- ✅ **Layout Responsivo** - Desktop e mobile

## 🛠️ Pré-requisitos

### 1. Google Cloud SDK
```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Verificar instalação
gcloud --version
```

### 2. Configuração do Projeto
```bash
# Configurar projeto (substitua pelo seu PROJECT_ID)
export PROJECT_ID="automatizar-452311"
gcloud config set project $PROJECT_ID

# Autenticar
gcloud auth login
gcloud auth application-default login
```

### 3. APIs Necessárias
```bash
# Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 🚀 Deploy Automático

### Opção 1: Script Automático (Recomendado)
```bash
# Executar script de deploy
./deploy_mvp.sh
```

### Opção 2: Deploy Manual

#### 1. Build da Imagem
```bash
# Configurar variáveis
PROJECT_ID="automatizar-452311"
SERVICE_NAME="mvp-dashboard-builder"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build e push da imagem
gcloud builds submit --tag $IMAGE_NAME
```

#### 2. Deploy para Cloud Run
```bash
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80
```

## 🔧 Configurações Específicas

### Service Account
O Cloud Run usa automaticamente as credenciais do Google Cloud:
- ✅ **Service Account**: `southmedia@automatizar-452311.iam.gserviceaccount.com`
- ✅ **Permissões**: Editor no projeto
- ✅ **Google Sheets API**: Habilitada automaticamente

### Variáveis de Ambiente
```bash
# Configurar variáveis (opcional)
gcloud run services update $SERVICE_NAME \
    --set-env-vars="DEBUG=False,PROJECT_ID=$PROJECT_ID"
```

### Persistência de Dados
- ✅ **SQLite**: Armazenado em `/tmp` (temporário)
- ✅ **Cache**: Dados em memória entre requests
- ✅ **Planilhas**: Sempre dados frescos do Google Sheets

## 📊 Testando o Deploy

### 1. Health Check
```bash
curl https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/health
```

### 2. Interface Web
Acesse: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/test-generator`

### 3. API Test
```bash
curl -X POST https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{
    "campaign_key": "teste_mvp",
    "client": "Cliente Teste",
    "campaign_name": "Campanha MVP",
    "sheet_id": "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8",
    "channel": "Video Programática"
  }'
```

## 🌐 URLs do Serviço

Após o deploy, você terá:

- **🏠 Home**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/`
- **🎯 Gerador**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/test-generator`
- **📊 API**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/api/generate-dashboard`
- **📋 Lista**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/api/list-campaigns`
- **🏥 Health**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app/health`

## 🔄 Updates e Manutenção

### Fazer Update
```bash
# Simplesmente executar o deploy novamente
./deploy_mvp.sh
```

### Logs
```bash
# Ver logs em tempo real
gcloud run services logs tail $SERVICE_NAME --region us-central1

# Ver logs históricos
gcloud run services logs read $SERVICE_NAME --region us-central1
```

### Monitoramento
```bash
# Ver métricas
gcloud run services describe $SERVICE_NAME --region us-central1
```

## 💰 Custos

### Cloud Run
- ✅ **Billing por uso**: Paga apenas quando usado
- ✅ **CPU**: R$ 0,024 por vCPU-hora
- ✅ **Memória**: R$ 0,0025 por GB-hora
- ✅ **Requests**: R$ 0,40 por milhão

### Estimativa
Para uso moderado (1000 requests/dia):
- **Custo mensal**: ~R$ 5-15
- **Custo anual**: ~R$ 60-180

## 🎯 Próximos Passos

### Melhorias Futuras
1. **Cloud SQL**: Para persistência permanente
2. **Cloud Storage**: Para arquivos estáticos
3. **Domain Mapping**: URL customizada
4. **SSL Custom**: Certificado próprio
5. **CI/CD**: Deploy automático via GitHub

### Escalabilidade
- ✅ **Auto-scaling**: 0 a 10 instâncias
- ✅ **Cold Start**: ~2-3 segundos
- ✅ **Warm Instances**: <500ms response time

## 🆘 Troubleshooting

### Problemas Comuns

#### 1. Erro de Permissão
```bash
# Verificar permissões
gcloud projects get-iam-policy $PROJECT_ID
```

#### 2. Service Account
```bash
# Verificar service account
gcloud iam service-accounts list
```

#### 3. APIs não habilitadas
```bash
# Verificar APIs
gcloud services list --enabled
```

#### 4. Logs de Erro
```bash
# Ver logs detalhados
gcloud run services logs read $SERVICE_NAME --region us-central1 --limit=50
```

## ✅ Checklist de Deploy

- [ ] Google Cloud SDK instalado
- [ ] Projeto configurado
- [ ] APIs habilitadas
- [ ] Service Account com permissões
- [ ] Arquivos do MVP presentes
- [ ] Deploy executado
- [ ] Health check funcionando
- [ ] Interface web acessível
- [ ] API testada
- [ ] Dashboard gerado com sucesso

## 🎉 Conclusão

O MVP Dashboard Builder está pronto para produção no Google Cloud Run!

**URL do Serviço**: `https://mvp-dashboard-builder-[PROJECT_ID]-uc.a.run.app`

**Funcionalidades Ativas**:
- ✅ Gerador de dashboards
- ✅ Cards de totalizadores
- ✅ Loading modal real
- ✅ Dados em tempo real
- ✅ Interface responsiva
- ✅ Formatação brasileira

**Custo Estimado**: R$ 5-15/mês para uso moderado

**Escalabilidade**: 0-10 instâncias automáticas
