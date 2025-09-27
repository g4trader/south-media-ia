# 🚀 Ambiente de Produção - MVP Dashboard Builder

## 📋 Visão Geral

O **MVP Dashboard Builder** é o ambiente de produção do sistema de geração automática de dashboards para campanhas de marketing digital. O sistema está hospedado no **Google Cloud Run** e integrado com **Vercel** para deploy automático.

## 🌐 URLs de Produção

### Serviços Principais
- **Dashboard Builder**: `https://mvp-dashboard-builder-609095880025.us-central1.run.app`
- **Git Manager**: `https://git-manager-improved-609095880025.us-central1.run.app`
- **Frontend (Vercel)**: `https://dash.iasouth.tech`

### Endpoints Principais
- **Gerador**: `/dash-generator-pro`
- **API de Dados**: `/api/{campaign_key}/data`
- **Geração**: `/api/generate-dashboard`
- **Health Check**: `/health`

## 🏗️ Arquitetura do Sistema

### Componentes Principais

#### 1. **Cloud Run - Dashboard Builder** (`mvp-dashboard-builder`)
- **Função**: Servidor principal da aplicação
- **Tecnologia**: Flask (Python 3.11)
- **Porta**: 8080
- **Recursos**: 1 vCPU, 2GB RAM
- **Timeout**: 300s

#### 2. **Cloud Run - Git Manager** (`git-manager-improved`)
- **Função**: Microserviço para operações Git automáticas
- **Responsabilidade**: Commit, push e sincronização com GitHub
- **Integração**: Cloud Scheduler (execução periódica)

#### 3. **Google Cloud Storage**
- **Bucket Credenciais**: `south-media-credentials`
  - Arquivo: `service-account-key.json`
  - Acesso: Service Account `southmedia@automatizar-452311.iam.gserviceaccount.com`
- **Bucket Backups**: `south-media-backups`
  - Backup completo do sistema
  - Acesso público para download

#### 4. **Vercel (Frontend)**
- **Função**: Interface web e dashboards estáticos
- **Deploy**: Automático via GitHub
- **Domínio**: `dash.iasouth.tech`

## 🔧 Configuração e Deploy

### Variáveis de Ambiente (Cloud Run)

```bash
# Configurações da aplicação
PORT=8080
DEBUG=False

# URLs dos serviços
API_ENDPOINT=https://mvp-dashboard-builder-609095880025.us-central1.run.app
GIT_MANAGER_URL=https://git-manager-improved-609095880025.us-central1.run.app

# Configurações do banco
DATABASE_PATH=/tmp/campaigns.db
```

### Processo de Deploy

#### 1. **Dashboard Builder**
```bash
# Build e deploy
gcloud builds submit --tag gcr.io/automatizar-452311/mvp-dashboard-builder
gcloud run deploy mvp-dashboard-builder \
  --image gcr.io/automatizar-452311/mvp-dashboard-builder \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

#### 2. **Git Manager**
```bash
# Deploy do microserviço
gcloud run deploy git-manager-improved \
  --image gcr.io/automatizar-452311/git-manager-improved \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 3
```

## 📊 Funcionalidades Principais

### 1. **Gerador de Dashboards**
- **Endpoint**: `/dash-generator-pro`
- **Funcionalidades**:
  - Interface web para criação de dashboards
  - Suporte a múltiplos canais (YouTube, LinkedIn, Netflix, etc.)
  - Seleção de KPI (CPV, CPM, CPC, CPA)
  - Integração com Google Sheets

### 2. **API de Dados**
- **Endpoint**: `/api/{campaign_key}/data`
- **Funcionalidades**:
  - Extração automática de dados do Google Sheets
  - Cálculo de métricas em tempo real
  - Suporte a diferentes tipos de campanha

### 3. **Templates Dinâmicos**
- **CPV Template**: `dash_generic_template.html`
- **CPM Template**: `dash_remarketing_cpm_template.html`
- **Personalização**: Baseada no canal e KPI selecionado

### 4. **Sistema de Backup Automático**
- **Localização**: `gs://south-media-backups`
- **Frequência**: Manual (via comando)
- **Conteúdo**: Dashboards + Bancos de dados

## 🔐 Segurança e Credenciais

### Service Account
- **Email**: `southmedia@automatizar-452311.iam.gserviceaccount.com`
- **Permissões**: Editor no projeto, acesso ao Google Sheets
- **Localização**: Google Cloud Storage (`south-media-credentials`)

### Autenticação Google Sheets
- **Método**: Service Account JSON
- **Scopes**: `https://www.googleapis.com/auth/spreadsheets.readonly`
- **Fallback**: Application Default Credentials

## 📈 Monitoramento e Logs

### Cloud Logging
```bash
# Logs do Dashboard Builder
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mvp-dashboard-builder" --limit=50

# Logs do Git Manager
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=git-manager-improved" --limit=50
```

### Health Checks
- **Dashboard Builder**: `GET /health`
- **Git Manager**: `GET /health`
- **Frequência**: 30s

## 🗄️ Persistência de Dados

### Banco de Dados SQLite
- **Localização**: `/tmp/campaigns.db` (container)
- **Backup**: Google Cloud Storage
- **Tabelas**:
  - `campaigns`: Configurações das campanhas
  - `dashboard_configs`: Configurações dos dashboards

### Arquivos Estáticos
- **Localização**: `/app/static/` (container)
- **Sincronização**: Git Manager automático
- **Deploy**: Vercel (automático)

## 🔄 Fluxo de Operação

### 1. **Geração de Dashboard**
```
Usuário → Interface Web → API Generate → Extrator Google Sheets → Template HTML → Git Commit → Deploy Vercel
```

### 2. **Acesso a Dados**
```
Dashboard → API Data → Google Sheets → Processamento → JSON Response → Renderização
```

### 3. **Backup e Sincronização**
```
Sistema → Git Manager → GitHub → Vercel → Deploy Automático
```

## 🛠️ Manutenção e Troubleshooting

### Comandos Úteis

#### Verificar Status dos Serviços
```bash
gcloud run services list --region=us-central1
gcloud run services describe mvp-dashboard-builder --region=us-central1
```

#### Verificar Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mvp-dashboard-builder AND severity>=ERROR" --limit=10
```

#### Testar Conectividade
```bash
curl -s https://mvp-dashboard-builder-609095880025.us-central1.run.app/health
curl -s https://mvp-dashboard-builder-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor_spotify/data
```

#### Backup Manual
```bash
# Criar backup local
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
cp static/dash_*.html backup/$(date +%Y%m%d_%H%M%S)/
cp *.db backup/$(date +%Y%m%d_%H%M%S)/

# Upload para GCS
gsutil cp backup/$(date +%Y%m%d_%H%M%S).tar.gz gs://south-media-backups/
```

### Problemas Comuns

#### 1. **Erro de Credenciais Google Sheets**
- **Sintoma**: "GoogleSheetsService não configurado"
- **Solução**: Verificar arquivo no bucket `south-media-credentials`

#### 2. **Dashboard não atualiza no Vercel**
- **Sintoma**: Mudanças não aparecem no frontend
- **Solução**: Verificar Git Manager e logs de commit

#### 3. **API retorna erro 500**
- **Sintoma**: Dashboard não carrega dados
- **Solução**: Verificar logs do Cloud Run e conectividade com Google Sheets

## 📞 Contatos e Suporte

- **Projeto**: `automatizar-452311`
- **Região**: `us-central1`
- **Repositório**: `south-media-ia`
- **Service Account**: `southmedia@automatizar-452311.iam.gserviceaccount.com`

## 📅 Histórico de Versões

### v1.0.0 (27/09/2025)
- ✅ Sistema de geração de dashboards funcional
- ✅ Integração com Google Sheets
- ✅ Templates CPV e CPM
- ✅ Git Manager automático
- ✅ Sistema de backup
- ✅ 52+ dashboards gerados

---

**Última atualização**: 27/09/2025  
**Ambiente**: Produção  
**Status**: ✅ Operacional
