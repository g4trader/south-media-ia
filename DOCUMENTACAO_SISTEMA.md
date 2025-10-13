# 📊 Sistema Gerador de Dashboards - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Estrutura de Arquivos](#estrutura-de-arquivos)
5. [Funcionalidades](#funcionalidades)
6. [Persistência de Dados](#persistência-de-dados)
7. [Templates de Dashboard](#templates-de-dashboard)
8. [Sistema de Filtros](#sistema-de-filtros)
9. [Ambientes](#ambientes)
10. [Deploy](#deploy)
11. [Manutenção e Troubleshooting](#manutenção-e-troubleshooting)

---

## 🎯 Visão Geral

Sistema profissional de geração automática de dashboards de campanhas de marketing digital. O sistema extrai dados de planilhas do Google Sheets, processa métricas e gera dashboards interativos com filtros, gráficos e análises detalhadas.

### Principais Características

- ✅ **Geração Automática**: Cria dashboards completos a partir de planilhas Google Sheets
- ✅ **Persistência Definitiva**: Dados salvos em BigQuery + Firestore
- ✅ **Filtros Interativos**: Filtros de período (Hoje, 7 dias, 30 dias, Todos, Personalizado)
- ✅ **Multi-KPI**: Suporte para CPV, CPM, CPC, CPA
- ✅ **Multi-Canal**: Instagram, Facebook, TikTok, YouTube, LinkedIn, Pinterest, Geofence, Programática
- ✅ **Arquitetura Dinâmica**: Dashboards gerados dinamicamente via endpoint `/api/dashboard/{campaign_key}`
- ✅ **Listagem de Dashboards**: Interface para visualizar todos os dashboards criados

---

## 🏗️ Arquitetura do Sistema

### Diagrama de Fluxo

```
┌─────────────────┐
│ Google Sheets   │
│  (Fonte Dados)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Flask API      │◄────►│  BigQuery        │
│  (Backend)      │      │  (Campanhas +    │
└────────┬────────┘      │   Métricas)      │
         │               └──────────────────┘
         │
         ▼               ┌──────────────────┐
┌─────────────────┐     │  Firestore       │
│ Template Engine │◄────►│  (Dashboards)    │
│ (Jinja2)        │     └──────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard HTML │
│  + JavaScript   │
│  + CSS          │
└─────────────────┘
```

### Componentes Principais

1. **Backend (Flask)**
   - API REST para geração de dashboards
   - Extração de dados do Google Sheets
   - Processamento de métricas
   - Gerenciamento de persistência

2. **Persistência (BigQuery + Firestore)**
   - BigQuery: Armazena campanhas e métricas
   - Firestore: Armazena metadados dos dashboards

3. **Frontend (HTML + JavaScript)**
   - Templates dinâmicos com Jinja2
   - Filtros interativos em JavaScript
   - Gráficos com Chart.js
   - Design responsivo

---

## 🛠️ Tecnologias Utilizadas

### Backend

- **Python 3.11**
- **Flask 2.3.3** - Framework web
- **Gunicorn 21.2.0** - Servidor WSGI para produção
- **Google Cloud SDK** - Integração com GCP

### Google Cloud Platform

- **Cloud Run** - Hosting serverless
- **BigQuery** - Data warehouse para campanhas e métricas
- **Firestore** - Banco NoSQL para metadados
- **Cloud Build** - CI/CD para builds de imagens Docker
- **Container Registry (GCR)** - Registry de imagens Docker

### APIs Google

- **Google Sheets API** - Extração de dados
- **Google Auth** - Autenticação e autorização

### Frontend

- **HTML5 + CSS3** - Estrutura e estilização
- **JavaScript ES6+** - Lógica client-side
- **Chart.js** - Visualização de dados
- **Jinja2** - Template engine

### Processamento de Dados

- **Pandas 2.1.3** - Manipulação de dados
- **NumPy 1.25.2** - Operações numéricas

---

## 📁 Estrutura de Arquivos

```
south-media-ia/
├── cloud_run_mvp.py                    # 🎯 Aplicação Flask principal
├── bigquery_firestore_manager.py       # 💾 Gerenciador de persistência
├── real_google_sheets_extractor.py     # 📊 Extrator de dados do Sheets
├── google_sheets_service.py            # 🔐 Serviço de autenticação Sheets
├── date_normalizer.py                  # 📅 Normalizador de datas
├── config.py                           # ⚙️  Configurações do sistema
├── gunicorn.conf.py                    # 🚀 Configurações do Gunicorn
├── requirements.txt                    # 📦 Dependências Python
├── Dockerfile                          # 🐳 Definição da imagem Docker
├── .env                                # 🔑 Variáveis de ambiente (local)
│
├── deploy/                             # 📂 Scripts de deploy
│   ├── deploy_stg_gen_dashboard_ia.sh  # 🧪 Deploy staging
│   ├── deploy_hml_gen_dashboard_ia.sh  # 🔬 Deploy homologação
│   └── deploy_gen_dashboard_ia.sh      # 🚀 Deploy produção
│
├── static/                             # 📂 Templates de dashboards
│   ├── dash_generic_template.html      # 📄 Template CPV (padrão)
│   ├── dash_remarketing_cpm_template.html  # 📄 Template CPM
│   └── [outros templates estáticos]
│
├── scripts/                            # 📂 Scripts utilitários
│   ├── clean_staging_direct.py         # 🧹 Limpeza de dados staging
│   └── [outros scripts]
│
└── docs/                               # 📂 Documentação
    ├── DOCUMENTACAO_SISTEMA.md         # 📚 Este arquivo
    └── DEPLOY_GUIDE.md                 # 📖 Guia de deploy
```

---

## ⚙️ Funcionalidades

### 1. Geração de Dashboards

**Endpoint:** `POST /api/generate-dashboard`

**Request:**
```json
{
  "campaign_key": "cliente_campanha_canal",
  "client": "Nome do Cliente",
  "campaign_name": "Nome da Campanha",
  "sheet_id": "ID_DA_PLANILHA_GOOGLE_SHEETS",
  "kpi": "CPV"  // Opcional: CPV, CPM, CPC, CPA
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dashboard gerado com sucesso!",
  "campaign_key": "cliente_campanha_canal",
  "dashboard_url": "/api/dashboard/cliente_campanha_canal",
  "dashboard_url_full": "https://[SERVICE_URL]/api/dashboard/cliente_campanha_canal"
}
```

### 2. Visualização de Dashboard

**Endpoint:** `GET /api/dashboard/{campaign_key}`

Retorna HTML dinâmico do dashboard com:
- Dados da campanha
- Métricas consolidadas
- Gráficos interativos
- Filtros de período
- Tabelas detalhadas

### 3. Listagem de Dashboards

**Endpoint:** `GET /dashboards-list`

Interface web que exibe todos os dashboards criados com:
- Filtros por cliente, canal, KPI
- Busca por texto
- Cards informativos
- Links diretos para dashboards

### 4. APIs de Dados

#### Obter dados de campanha
```
GET /api/{campaign_key}/data
```

#### Listar todas as campanhas
```
GET /api/campaigns
```

#### Listar todos os dashboards
```
GET /api/dashboards
```

#### Status de persistência
```
GET /persistence-status
```

---

## 💾 Persistência de Dados

### BigQuery

**Datasets por Ambiente:**
- **Staging:** `staging_campaigns`, `staging_campaign_metrics`
- **Homologação:** `hml_campaigns`, `hml_campaign_metrics`
- **Produção:** `campaigns`, `campaign_metrics`

**Schema - Tabela `campaigns`:**
```sql
- campaign_key: STRING (PK)
- client: STRING
- campaign_name: STRING
- channel: STRING
- kpi: STRING
- sheet_id: STRING
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

**Schema - Tabela `campaign_metrics`:**
```sql
- campaign_key: STRING (FK)
- date: DATE
- creative: STRING
- impressions: INTEGER
- clicks: INTEGER
- views: INTEGER
- spend: FLOAT
- conversions: INTEGER
- metric_date: TIMESTAMP
```

### Firestore

**Collections por Ambiente:**
- **Staging:** `campaigns_staging`, `dashboards_staging`
- **Homologação:** `campaigns_hml`, `dashboards_hml`
- **Produção:** `campaigns`, `dashboards`

**Document Structure - `campaigns`:**
```javascript
{
  campaign_key: string,
  client: string,
  campaign_name: string,
  channel: string,
  kpi: string,
  sheet_id: string,
  created_at: timestamp,
  updated_at: timestamp
}
```

**Document Structure - `dashboards`:**
```javascript
{
  dashboard_id: string,
  campaign_key: string,
  dashboard_name: string,
  dashboard_url: string,
  template_used: string,
  created_at: timestamp,
  updated_at: timestamp
}
```

---

## 📄 Templates de Dashboard

### Template CPV (Padrão)

**Arquivo:** `static/dash_generic_template.html`

**KPIs Principais:**
- Visualizações (Views)
- CPV (Custo por Visualização)
- CTR (Click-Through Rate)
- Investimento Total

**Uso:** CPV, CPC, CPA

### Template CPM

**Arquivo:** `static/dash_remarketing_cpm_template.html`

**KPIs Principais:**
- Impressões
- CPM (Custo por Mil Impressões)
- CTR
- Investimento Total

**Uso:** CPM, Campanhas de Remarketing

### Seleção Automática

O sistema seleciona automaticamente o template baseado no KPI:

```python
if kpi == 'CPM':
    template_file = 'static/dash_remarketing_cpm_template.html'
else:  # CPV, CPC, CPA
    template_file = 'static/dash_generic_template.html'
```

---

## 🎛️ Sistema de Filtros

### Filtros Disponíveis

1. **Hoje** - Dados do dia atual
2. **7 dias** - Últimos 7 dias
3. **30 dias** - Últimos 30 dias
4. **Todos** - Todo o período disponível (padrão)
5. **Personalizado** - Seleção de datas customizada

### Funcionamento

#### 1. Armazenamento de Dados

```javascript
class DashboardLoader {
  constructor() {
    this.originalData = null;  // Dados completos
    this.filteredData = null;  // Dados filtrados
    this.currentStartDate = null;
    this.currentEndDate = null;
  }
}
```

#### 2. Aplicação de Filtros

```javascript
async applyDateFilter(startDate = null, endDate = null) {
  // Filtra daily_data
  const filtered = this.originalData.daily_data.filter(item => {
    const itemDate = new Date(item.data);
    return itemDate >= startDate && itemDate <= endDate;
  });
  
  // Recalcula métricas
  this.recalculateMetrics();
  this.recalculateChannelMetrics();
  
  // Re-renderiza dashboard
  await this.renderDashboard(this.filteredData);
}
```

#### 3. Recálculo de Métricas

- **Métricas Gerais:** Soma de investimento, visualizações, cliques, impressões
- **Métricas Calculadas:** CPV, CPM, CPC, CTR
- **Métricas por Canal:** Agrupamento por creative/channel

#### 4. Atualização Visual

- Tabelas de resumo
- Gráficos (Chart.js)
- Tabelas detalhadas por canal
- Tabela de entrega diária

---

## 🌍 Ambientes

### Staging (STG)

**URL:** https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Propósito:** Testes de desenvolvimento e validação de novas funcionalidades

**Configurações:**
- Memória: 1GB
- CPU: 1 vCPU
- Max Instances: 3
- Timeout: 300s (5 min)
- Environment: `staging`

**Persistência:**
- BigQuery: `staging_campaigns`, `staging_campaign_metrics`
- Firestore: `campaigns_staging`, `dashboards_staging`

### Homologação (HML)

**URL:** https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Propósito:** Validação final antes de produção, testes com stakeholders

**Configurações:**
- Memória: 2GB
- CPU: 2 vCPU
- Max Instances: 5
- Timeout: 1800s (30 min)
- Environment: `hml`

**Persistência:**
- BigQuery: `hml_campaigns`, `hml_campaign_metrics`
- Firestore: `campaigns_hml`, `dashboards_hml`

### Produção (PRD)

**URL:** https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Propósito:** Ambiente de produção para uso real

**Configurações:**
- Memória: 4GB
- CPU: 2 vCPU
- Max Instances: 10
- Timeout: 3600s (1h)
- Environment: `production`

**Persistência:**
- BigQuery: `campaigns`, `campaign_metrics`
- Firestore: `campaigns`, `dashboards`

---

## 🚀 Deploy

### Pré-requisitos

1. **Google Cloud SDK** instalado e configurado
2. **Docker** instalado (opcional, Cloud Build faz o build)
3. **Credenciais GCP** configuradas
4. **Permissões** adequadas no projeto GCP

### Variáveis de Ambiente

**Staging:**
```bash
export PROJECT_ID=automatizar-452311
export ENVIRONMENT=staging
```

**Homologação:**
```bash
export PROJECT_ID=automatizar-452311
export ENVIRONMENT=hml
```

**Produção:**
```bash
export PROJECT_ID=automatizar-452311
export ENVIRONMENT=production
```

### Scripts de Deploy

#### 1. Deploy Staging

```bash
./deploy_stg_gen_dashboard_ia.sh
```

#### 2. Deploy Homologação

```bash
./deploy_hml_gen_dashboard_ia.sh
```

#### 3. Deploy Produção

```bash
./deploy_gen_dashboard_ia.sh
```

### Processo de Deploy

1. **Verificação de Arquivos**
   - Valida presença de arquivos necessários
   - Verifica templates com filtros

2. **Configuração do Projeto**
   - Define projeto GCP
   - Habilita APIs necessárias

3. **Build da Imagem**
   - Cloud Build cria imagem Docker
   - Push para Google Container Registry

4. **Deploy no Cloud Run**
   - Cria/atualiza serviço
   - Configura variáveis de ambiente
   - Define recursos (CPU, memória)
   - Configura timeout e concurrency

5. **Verificação**
   - Health check
   - Teste de endpoints

### Rollback

Se necessário fazer rollback para versão anterior:

```bash
# Listar revisões
gcloud run revisions list --service=gen-dashboard-ia

# Fazer rollback para revisão específica
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=gen-dashboard-ia-00035-x5s=100
```

---

## 🔧 Manutenção e Troubleshooting

### Logs

#### Visualizar logs em tempo real

```bash
# Staging
gcloud run services logs tail stg-gen-dashboard-ia

# Homologação
gcloud run services logs tail hml-gen-dashboard-ia

# Produção
gcloud run services logs tail gen-dashboard-ia
```

#### Filtrar logs por severidade

```bash
gcloud run services logs read gen-dashboard-ia \
  --severity=ERROR \
  --limit=50
```

### Limpeza de Dados

#### Limpar dados de staging

```bash
python3 clean_staging_direct.py
```

#### Limpar dados de homologação

Criar script similar adaptando para `hml_*` collections/datasets

### Problemas Comuns

#### 1. Dashboard retorna 404

**Causa:** Dashboard não existe no Firestore

**Solução:**
- Verificar se campaign_key está correto
- Regenerar dashboard via API

#### 2. Filtros não funcionam

**Causa:** JavaScript não carregado ou erro de execução

**Solução:**
- Abrir console do navegador (F12)
- Verificar erros JavaScript
- Validar que `window.dashboard` está definido

#### 3. Erro ao extrair dados do Sheets

**Causa:** Credenciais inválidas ou planilha sem permissão

**Solução:**
- Verificar credenciais no Secret Manager
- Garantir que planilha tem permissão pública ou compartilhada com service account

#### 4. Timeout no deploy

**Causa:** Build muito demorado ou timeout de deploy

**Solução:**
- Aumentar timeout no script de deploy
- Otimizar Dockerfile (usar cache)

#### 5. Dados não persistindo

**Causa:** BigQuery/Firestore não configurado ou sem permissões

**Solução:**
- Verificar variável `ENVIRONMENT`
- Validar permissões da service account
- Checar status: `GET /persistence-status`

### Monitoramento

#### Métricas do Cloud Run

```bash
# Abrir console de métricas
gcloud run services describe gen-dashboard-ia --format=yaml
```

#### Alertas Recomendados

1. **Latência > 5s** - Investigar performance
2. **Taxa de Erro > 5%** - Investigar erros
3. **Uso de Memória > 80%** - Considerar aumento
4. **Timeout de Requisições** - Aumentar timeout ou otimizar código

---

## 📞 Suporte

### Contatos

- **Desenvolvedor:** Luciano Torres
- **Projeto GCP:** `automatizar-452311`

### Recursos

- [Documentação Flask](https://flask.palletsprojects.com/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)
- [Firestore Docs](https://cloud.google.com/firestore/docs)

---

## 📝 Changelog

### v2.0 - Arquitetura Dinâmica (Atual)

- ✅ Dashboards dinâmicos via `/api/dashboard/{campaign_key}`
- ✅ Persistência definitiva (BigQuery + Firestore)
- ✅ Filtros interativos em todos os templates
- ✅ Sistema de ambientes (staging, hml, produção)
- ✅ Listagem de dashboards
- ✅ Correção de exibição de canais (sem fallbacks incorretos)

### v1.0 - MVP Inicial

- Geração de dashboards estáticos em `/static`
- Persistência em SQLite + GCS
- Templates básicos
- Deploy manual

---

## 🎯 Roadmap

### Próximas Implementações

1. **Dashboard de Administração**
   - Gerenciar dashboards existentes
   - Editar campanhas
   - Visualizar métricas do sistema

2. **Notificações**
   - Email ao finalizar geração de dashboard
   - Alertas de performance de campanhas

3. **Exportação de Relatórios**
   - PDF com dados do dashboard
   - Excel com dados brutos

4. **API de Integração**
   - Webhooks para notificações
   - API REST completa para integração com outros sistemas

5. **Machine Learning**
   - Previsão de performance
   - Recomendações de otimização

---

**Última Atualização:** Outubro 2025
**Versão do Sistema:** 2.0
**Ambiente:** Multi-ambiente (staging, hml, produção)
