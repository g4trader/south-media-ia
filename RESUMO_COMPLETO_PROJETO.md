# 📊 RESUMO COMPLETO DO PROJETO - South Media IA

## 🎯 INFORMAÇÕES ESSENCIAIS

### **Projeto Correto:**
- **Nome**: `south-media-ia`
- **GCP Project ID**: `automatizar-452311`
- **Project Number**: `609095880025`
- **Repositório**: https://github.com/g4trader/south-media-ia

### **❌ O QUE NÃO É:**
- ~~`south-media-444117`~~ (projeto errado que causou confusão)
- ~~Outros projetos GCP~~

## 🌐 AMBIENTES E URLS

### **PRODUÇÃO**
- **Service**: `gen-dashboard-ia`
- **URL**: https://gen-dashboard-ia-609095880025.us-central1.run.app
- **Dataset BigQuery**: `south_media_dashboards`
- **Firestore Collections**: `campaigns`, `dashboards`

### **STAGING**
- **Service**: `stg-gen-dashboard-ia`
- **URL**: https://stg-gen-dashboard-ia-609095880025.us-central1.run.app
- **Dataset BigQuery**: `south_media_dashboards_staging`
- **Firestore Collections**: `campaigns_staging`, `dashboards_staging`

### **HOMOLOGAÇÃO (HML)**
- **Service**: `hml-gen-dashboard-ia`
- **URL**: https://hml-gen-dashboard-ia-609095880025.us-central1.run.app
- **Dataset BigQuery**: `south_media_dashboards_hml`
- **Firestore Collections**: `campaigns_hml`, `dashboards_hml`

## 🔐 AUTENTICAÇÃO

### **Conta Ativa:**
- **Email**: `g4trader.news@gmail.com`
- **Tem acesso**: ✅ Sim ao projeto `automatizar-452311`

### **Service Account Disponível:**
- **Email**: `southmedia@automatizar-452311.iam.gserviceaccount.com`
- **Projeto**: `automatizar-452311`

## 🏗️ ARQUITETURA DO SISTEMA

### **Arquivos Principais:**
```
cloud_run_mvp.py                    # API Flask principal
bigquery_firestore_manager.py      # Gerenciamento de persistência
real_google_sheets_extractor.py    # Extração de dados do Google Sheets
local_extractor.py                  # Extração local (desenvolvimento)
```

### **Templates de Dashboard:**
```
static/dash_generic_template.html           # Template CPV
static/dash_remarketing_cpm_template.html   # Template CPM
static/dash_generic_cpe_template.html       # Template CPE (novo!)
static/dash_sonho.html                      # Dashboard multicanal estático
```

### **Persistência de Dados:**
- **BigQuery**: Armazenamento de dados estruturados
  - Tabelas: `campaigns`, `dashboards`
  - Schema automático com validação
  
- **Firestore**: Metadados e consultas rápidas
  - Collections por ambiente
  - Documentos com metadata completa

### **Configuração por Ambiente:**
```python
# Definido em bigquery_firestore_manager.py
if ENVIRONMENT == "staging":
    dataset_id = "south_media_dashboards_staging"
    campaigns_collection = "campaigns_staging"
    dashboards_collection = "dashboards_staging"
elif ENVIRONMENT == "hml":
    dataset_id = "south_media_dashboards_hml"
    campaigns_collection = "campaigns_hml"
    dashboards_collection = "dashboards_hml"
else:  # production
    dataset_id = "south_media_dashboards"
    campaigns_collection = "campaigns"
    dashboards_collection = "dashboards"
```

## 📋 O QUE FIZEMOS ONTEM (13/10/2025)

### **1. Implementação do KPI CPE (Custo por Escuta)**
✅ **Criado**: `static/dash_generic_cpe_template.html`
✅ **Modificado**: 
- `cloud_run_mvp.py` - seleção automática de template
- `real_google_sheets_extractor.py` - insights dinâmicos
- `local_extractor.py` - insights dinâmicos
- Adicionado atributo `kpi` em `CampaignConfig`

✅ **Labels Adaptados**:
- VC → Escutas
- CPV → CPE
- VC Contratadas → Escutas Contratadas
- VC Entregue → Escutas Entregues
- Quartis de Vídeo → Quartis de Escuta

### **2. Restauração de Funcionalidades Perdidas**
✅ **Quartis de Vídeo**: Re-implementado na aba Visão Geral
✅ **Coluna Criativo**: Re-implementada na tabela diária
✅ **Filtros**: Recálculo correto de todas as métricas

### **3. Filtro de Dashboards de Teste**
✅ **Implementado**: Filtro automático em `/dashboards-list`
✅ **Lógica**: Oculta dashboards com `client.startswith('teste')`
✅ **Resultado**: Apenas dashboards de produção aparecem

### **4. Limpeza e Recriação do Staging**
✅ **Limpo**: BigQuery dataset e Firestore collections
✅ **Recriado**: 31 dashboards do `dashboards.csv`
✅ **Distribuição**: 14 CPV + 17 CPM

## 🚀 PROCESSO DE DEPLOY

### **Para STAGING:**
```bash
cd /Users/lucianoterres/Documents/GitHub/south-media-ia
gcloud config set project automatizar-452311
gcloud run deploy stg-gen-dashboard-ia \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=staging
```

### **Para PRODUÇÃO:**
```bash
gcloud run deploy gen-dashboard-ia \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production
```

### **Para HML:**
```bash
gcloud run deploy hml-gen-dashboard-ia \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=hml
```

## 🧹 PROCESSO DE LIMPEZA E RECRIAÇÃO

### **Script Completo:**
```python
from google.cloud import bigquery, firestore
import pandas as pd
import requests

PROJECT_ID = "automatizar-452311"
DATASET_ID = "south_media_dashboards_staging"  # ou _hml, ou sem sufixo para prod
STAGING_URL = "https://stg-gen-dashboard-ia-609095880025.us-central1.run.app"

# 1. LIMPAR BigQuery
bq_client = bigquery.Client(project=PROJECT_ID)
bq_client.delete_dataset(f"{PROJECT_ID}.{DATASET_ID}", 
                         delete_contents=True, not_found_ok=True)

# 2. LIMPAR Firestore
db = firestore.Client(project=PROJECT_ID)
for collection in ["campaigns_staging", "dashboards_staging"]:
    for doc in db.collection(collection).stream():
        doc.reference.delete()

# 3. CRIAR Infraestrutura
dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
dataset.location = "US"
bq_client.create_dataset(dataset, exists_ok=True)

# Schema campaigns
campaigns_schema = [
    bigquery.SchemaField("campaign_key", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("client", "STRING"),
    bigquery.SchemaField("campaign_name", "STRING"),
    bigquery.SchemaField("sheet_id", "STRING"),
    bigquery.SchemaField("channel", "STRING"),
    bigquery.SchemaField("kpi", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
]

# Schema dashboards
dashboards_schema = [
    bigquery.SchemaField("dashboard_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("campaign_key", "STRING"),
    bigquery.SchemaField("dashboard_name", "STRING"),
    bigquery.SchemaField("dashboard_url", "STRING"),
    bigquery.SchemaField("file_path", "STRING"),  # IMPORTANTE!
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]

# Criar tabelas
table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.campaigns", 
                       schema=campaigns_schema)
bq_client.create_table(table, exists_ok=True)

table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.dashboards", 
                       schema=dashboards_schema)
bq_client.create_table(table, exists_ok=True)

# 4. RECRIAR Dashboards do CSV
df = pd.read_csv('dashboards.csv')

for _, row in df.iterrows():
    payload = {
        "campaign_key": f"{row['cliente']}_{row['campanha']}".lower()
                        .replace(' ', '_').replace('-', '_'),
        "client": row['cliente'],
        "campaign_name": row['campanha'],
        "sheet_id": row['planilha'].split('/d/')[1].split('/')[0] 
                    if '/d/' in row['planilha'] else row['planilha'],
        "channel": row['canal'],
        "kpi": row['kpi'].upper()
    }
    
    response = requests.post(f"{STAGING_URL}/api/generate-dashboard", 
                            json=payload, timeout=120)
```

## ⚠️ PONTOS CRÍTICOS APRENDIDOS HOJE

### **1. Schema do BigQuery DEVE incluir `file_path`**
```python
dashboards_schema = [
    # ...
    bigquery.SchemaField("file_path", "STRING"),  # ❗ ESSENCIAL
    # ...
]
```
**Sem isso**: Erro `no such field: file_path` e dados não são salvos!

### **2. Dataset deve ser RECRIADO após deletar**
- Deletar dataset → Criar dataset → Criar tabelas → Recriar dashboards
- **NÃO** pular nenhuma etapa!

### **3. Firestore limpa rápido, mas precisa de batch**
```python
batch = db.batch()
count = 0
for doc in collection.stream():
    batch.delete(doc.reference)
    count += 1
    if count >= 500:  # Commit em lotes
        batch.commit()
        batch = db.batch()
        count = 0
if count > 0:
    batch.commit()
```

### **4. Dashboards vs Listagem**
- **Dashboards criados**: 31 (via API)
- **Firestore pode ter**: menos documentos (se houver erro de salvamento)
- **Listagem web**: lê do Firestore (pode mostrar menos que 31)
- **Solução**: Sempre verificar logs e recriar faltantes

## 📊 DASHBOARDS DO PROJETO

### **Arquivo Fonte:**
`dashboards.csv` - 31 dashboards

### **Distribuição:**
- **CPV (14)**: Campanhas de vídeo com Complete Views
- **CPM (17)**: Campanhas de impressão e remarketing
- **CPE (0)**: Novo KPI, ainda sem campanhas em produção

### **Clientes:**
- Senai: 4 dashboards
- Copacol: 11 dashboards
- Sebrae PR: 4 dashboards
- Unimed: 1 dashboard
- Iquine: 1 dashboard
- Sesi: 4 dashboards
- Sonho: 6 dashboards

## 🔍 COMANDOS ÚTEIS DE VERIFICAÇÃO

### **Ver Dashboards em Firestore:**
```python
from google.cloud import firestore
db = firestore.Client(project="automatizar-452311")
dashboards = list(db.collection("dashboards_staging").stream())
print(f"Total: {len(dashboards)}")
```

### **Ver Dados em BigQuery:**
```python
from google.cloud import bigquery
client = bigquery.Client(project="automatizar-452311")
query = "SELECT COUNT(*) as total FROM `automatizar-452311.south_media_dashboards_staging.dashboards`"
result = list(client.query(query).result())[0].total
print(f"Total: {result}")
```

### **Ver Listagem Web:**
```bash
curl -s "https://stg-gen-dashboard-ia-609095880025.us-central1.run.app/dashboards-list" | grep -o '<div class="dashboard-card"' | wc -l
```

### **Ver Logs do Cloud Run:**
```bash
gcloud run services logs read stg-gen-dashboard-ia \
  --region=us-central1 \
  --project=automatizar-452311 \
  --limit=50
```

## ✅ STATUS ATUAL (14/10/2025 - 11:00)

### **STAGING:**
- ✅ Limpo e recriado
- ✅ 31/31 dashboards funcionando
- ✅ BigQuery e Firestore sincronizados
- ✅ Filtro de teste ativo

### **PRODUÇÃO:**
- ⚠️  Não mexer sem autorização!
- ℹ️  Deploy pendente das melhorias CPE

### **HML:**
- ℹ️  Sincronizado com staging
- ℹ️  Pronto para testes

## 🎯 LIÇÕES APRENDIDAS

1. **SEMPRE verificar projeto correto** antes de qualquer comando
2. **SEMPRE criar schema completo** no BigQuery (incluindo file_path)
3. **SEMPRE verificar logs** após criação de dashboards
4. **SEMPRE fazer backup** antes de limpar dados
5. **NUNCA assumir** que dados foram salvos sem verificar
6. **Staging é para testar** - produção só com autorização!

---

**Atualizado**: 2025-10-14 11:30  
**Status**: ✅ Staging 100% funcional com 31 dashboards
