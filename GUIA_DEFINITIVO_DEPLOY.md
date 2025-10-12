# 📘 GUIA DEFINITIVO: DEPLOY E MANUTENÇÃO DO SISTEMA DE DASHBOARDS

## 🎯 VISÃO GERAL DO SISTEMA

### Arquitetura
- **Frontend**: HTML/CSS/JavaScript com Chart.js
- **Backend**: Python/Flask (Cloud Run)
- **Persistência**: BigQuery (analytics) + Firestore (metadados rápidos)
- **Geração**: Dinâmica via API (`/api/dashboard/{campaign_key}`)

### Ambientes
1. **PRODUÇÃO** - Ambiente estável para usuários finais
2. **STAGING** - Ambiente de testes e validação
3. **HML** - Ambiente de homologação

---

## 🏗️ ESTRUTURA DE AMBIENTES

### Isolamento de Dados

| Ambiente | URL | BigQuery Dataset | Firestore Collections | ENVIRONMENT Var |
|----------|-----|------------------|----------------------|-----------------|
| **Produção** | `gen-dashboard-ia` | `south_media_dashboards` | `campaigns`, `dashboards` | `production` |
| **Staging** | `stg-gen-dashboard-ia` | `south_media_dashboards_staging` | `campaigns_staging`, `dashboards_staging` | `staging` |
| **HML** | `hml-gen-dashboard-ia` | `south_media_dashboards_hml` | `campaigns_hml`, `dashboards_hml` | `hml` |

### ⚠️ REGRA DE OURO:
**NUNCA** compartilhe dados entre ambientes! Cada ambiente tem seu próprio dataset BigQuery e coleções Firestore.

---

## 📝 ARQUIVOS PRINCIPAIS

### Código Core
- `cloud_run_mvp.py` - Aplicação Flask principal
- `bigquery_firestore_manager.py` - Gerenciador de persistência (respeita ENVIRONMENT)
- `real_google_sheets_extractor.py` - Extrator de dados do Google Sheets
- `google_sheets_service.py` - Serviço de autenticação Google Sheets
- `date_normalizer.py` - Normalização de datas
- `config.py` - Configurações gerais
- `gunicorn.conf.py` - Configuração do servidor

### Templates HTML
- `static/dash_generic_template.html` - Template para KPI CPV
- `static/dash_remarketing_cpm_template.html` - Template para KPI CPM

**⚠️ IMPORTANTE:** Ambos os templates têm filtros implementados e devem ser mantidos sincronizados.

### Scripts de Deploy
- `deploy_gen_dashboard_ia.sh` - Deploy em PRODUÇÃO
- `deploy_stg_gen_dashboard_ia.sh` - Deploy em STAGING
- `deploy_hml_gen_dashboard_ia.sh` - Deploy em HML
- `deploy_production_complete.sh` - Deploy completo automatizado (produção)

### Scripts de Manutenção
- `clean_and_recreate_production.py` - Limpar e recriar produção
- `clean_and_recreate_hml.py` - Limpar e recriar HML
- `backup_production_data.py` - Backup completo
- `check_all_environments.py` - Verificar todos os ambientes

### Dados
- `dashboards.csv` - Lista mestra de dashboards (31 dashboards)

---

## 🚀 PROCESSO DE DEPLOY COMPLETO

### OPÇÃO 1: Deploy Automatizado (RECOMENDADO)

Para produção:
```bash
./deploy_production_complete.sh
```

**O que faz:**
1. ✅ Backup automático dos dados atuais
2. ✅ Limpeza do ambiente (BigQuery + Firestore)
3. ✅ Build e deploy do código atualizado
4. ✅ Recriação de todos os dashboards do CSV
5. ✅ Correção automática de metadados
6. ✅ Relatório completo

**Tempo estimado:** 5-7 minutos

---

### OPÇÃO 2: Deploy Manual (Passo a Passo)

#### PASSO 1: Backup de Segurança (SEMPRE!)

```bash
python3 backup_production_data.py
```

**Verifica:**
- ✅ Diretório `production_backup_[timestamp]/` criado
- ✅ Arquivos JSON de BigQuery e Firestore salvos
- ✅ Metadados do backup registrados

**⚠️ NUNCA pule este passo em produção!**

---

#### PASSO 2: Limpar e Recriar Dashboards

**Para PRODUÇÃO:**
```bash
python3 clean_and_recreate_production.py
```

**Para STAGING:**
```bash
python3 clean_staging_data.py
python3 automate_dashboard_creation.py  # URL staging
python3 fix_dashboard_metadata_from_csv.py
python3 fix_remaining_dashboards.py
```

**Para HML:**
```bash
python3 clean_and_recreate_hml.py
```

---

#### PASSO 3: Deploy do Código

**Para PRODUÇÃO:**
```bash
./deploy_gen_dashboard_ia.sh
```

**Para STAGING:**
```bash
./deploy_stg_gen_dashboard_ia.sh
```

**Para HML:**
```bash
./deploy_hml_gen_dashboard_ia.sh
```

**Aguarde:** 30-60 segundos para estabilização

---

#### PASSO 4: Verificar Tráfego do Cloud Run

**⚠️ IMPORTANTE:** Após o deploy, verificar se o tráfego foi direcionado para a nova revisão:

```bash
# Verificar revisão atual
gcloud run services describe gen-dashboard-ia --region=us-central1 --format="value(status.traffic[0].revisionName)"

# Se necessário, direcionar tráfego manualmente
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=gen-dashboard-ia-[NOVA_REVISAO]=100 \
  --region=us-central1
```

**Substitua `[NOVA_REVISAO]` pela revisão criada no deploy.**

---

#### PASSO 5: Validação Pós-Deploy

```bash
python3 check_all_environments.py
```

**Verifica:**
- ✅ Persistência ativa (BigQuery + Firestore)
- ✅ Contagem correta de dashboards (31)
- ✅ Todos os endpoints respondendo

---

## 📊 ADICIONANDO NOVOS DASHBOARDS

### 1. Atualizar o CSV

Edite `dashboards.csv` e adicione a nova linha:

```csv
cliente,campanha,planilha,canal,kpi
novo_cliente,Nova Campanha,https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA,canal,cpm
```

**Colunas:**
- `cliente` - Nome do cliente (ex: copacol, senai)
- `campanha` - Nome da campanha
- `planilha` - URL completa da planilha Google Sheets
- `canal` - Canal de veiculação (ex: youtube, netflix, linkedin)
- `kpi` - Métrica principal: `cpm` ou `cpv` (minúsculo no CSV)

---

### 2. Gerar Dashboard

**Opção A: Via Interface Web**
1. Acesse: `https://[ambiente]/dash-generator-pro`
2. Preencha o formulário
3. Clique em "Gerar Dashboard"

**Opção B: Via API**
```bash
curl -X POST https://[ambiente]/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{
    "campaign_key": "cliente_campanha",
    "client": "Cliente",
    "campaign_name": "Nome da Campanha",
    "sheet_id": "ID_DA_PLANILHA",
    "channel": "canal",
    "kpi": "CPM"
  }'
```

**Opção C: Recriar Todos do CSV (Recomendado)**
```bash
# Limpar e recriar todos os dashboards
python3 clean_and_recreate_production.py
```

---

## 🔧 TROUBLESHOOTING

### Problema: Dashboard mostra "N/A" nos metadados

**Causa:** Metadados não foram salvos no Firestore

**Solução:**
```bash
python3 fix_production_metadata.py
python3 fix_remaining_production_dashboards.py
```

---

### Problema: Listagem mostra número errado de dashboards

**Causa:** Cloud Run direcionando tráfego para revisão antiga

**Solução:**
```bash
# Listar revisões
gcloud run revisions list --service=gen-dashboard-ia --region=us-central1

# Direcionar para revisão mais recente
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=[REVISAO_MAIS_RECENTE]=100 \
  --region=us-central1
```

---

### Problema: Filtros não funcionam no dashboard

**Causa:** Template HTML desatualizado

**Verificar:**
1. Template correto está sendo usado? (CPV vs CPM)
2. Templates têm o código de filtros?
3. `applyDateFilter()` está implementado?

**Solução:**
1. Verificar `static/dash_generic_template.html` (CPV)
2. Verificar `static/dash_remarketing_cpm_template.html` (CPM)
3. Fazer deploy novamente se templates foram atualizados

---

### Problema: Dashboard não carrega dados

**Causa 1:** Planilha Google Sheets não acessível
**Solução:** Verificar permissões da planilha (deve ser "Anyone with link can view")

**Causa 2:** ID da planilha errado
**Solução:** Verificar URL no CSV

**Causa 3:** Dados não processados
**Solução:** Regenerar o dashboard

---

### Problema: "Campanha não encontrada"

**Causa:** Dashboard não existe no Firestore

**Solução:**
```bash
# Regenerar dashboard específico
curl -X POST https://[ambiente]/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{"campaign_key": "...", ...}'
```

---

## 🔄 ROLLBACK (Se necessário)

### Opção 1: Reverter Cloud Run para Revisão Anterior

```bash
# Listar revisões disponíveis
gcloud run revisions list --service=gen-dashboard-ia --region=us-central1

# Reverter para revisão específica
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=[REVISAO_ANTERIOR]=100 \
  --region=us-central1
```

**Exemplo:**
```bash
# Reverter para revisão 00023 (última estável)
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=gen-dashboard-ia-00023-ts9=100 \
  --region=us-central1
```

---

### Opção 2: Restaurar Backup

```bash
# 1. Identificar backup
ls -lt production_backup_*/

# 2. Usar script de restauração (se disponível)
python3 restore_backup_to_production.py

# 3. OU restaurar manualmente via console do GCP
```

---

## 🧪 VALIDAÇÃO DE DEPLOY

### Checklist Pós-Deploy

Use este checklist após QUALQUER deploy:

- [ ] **Persistência OK**
  ```bash
  curl https://[ambiente]/persistence-status
  # Deve retornar campaigns_count: 31, dashboards_count: 31
  ```

- [ ] **Listagem Mostra 31 Dashboards**
  ```bash
  # Acesse: https://[ambiente]/dashboards-list
  # Deve mostrar "31 Total de Dashboards"
  ```

- [ ] **Dashboards Carregam Dados**
  ```bash
  # Teste 3-5 dashboards aleatórios
  curl https://[ambiente]/api/dashboard/[campaign_key]
  # Deve retornar HTML completo com dados
  ```

- [ ] **Filtros Funcionam**
  - Abra um dashboard CPV no browser
  - Teste filtros: Todos, 30 dias, 7 dias, Hoje
  - Verifique que métricas recalculam
  - Teste aba "Por Canal" com filtros
  
  - Abra um dashboard CPM no browser
  - Repita os mesmos testes

- [ ] **Metadados Corretos**
  - Todos os dashboards têm Cliente, Campanha, Canal, KPI
  - Nenhum dashboard mostra "N/A"

- [ ] **Sem Erros nos Logs**
  ```bash
  gcloud run logs tail gen-dashboard-ia --region=us-central1
  # Não deve ter erros críticos
  ```

---

## 🎓 LIÇÕES APRENDIDAS

### 1. **SEMPRE Faça Backup Antes de Deploy em Produção**

```bash
python3 backup_production_data.py
```

Salvou o projeto múltiplas vezes quando precisamos reverter mudanças.

---

### 2. **Verificar Direcionamento de Tráfego do Cloud Run**

Após deploy, o Cloud Run pode criar uma nova revisão mas **não direcionar o tráfego** automaticamente.

**Sempre verificar:**
```bash
gcloud run services describe gen-dashboard-ia --region=us-central1 --format="value(status.traffic[0].revisionName)"
```

Se a revisão não for a mais recente, atualizar manualmente.

---

### 3. **Metadados Devem Ser Salvos Junto com Dashboard**

O método `save_dashboard()` em `bigquery_firestore_manager.py` **DEVE** receber e salvar:
- `client`
- `campaign_name`
- `channel`
- `kpi`

**Código correto:**
```python
bq_fs_manager.save_dashboard(
    dashboard_id=dashboard_id,
    campaign_key=campaign_key,
    dashboard_name=dashboard_name_full,
    dashboard_url=result['dashboard_url'],
    file_path=result['dashboard_url'],
    client=client,          # ← ESSENCIAL
    campaign_name=campaign_name,  # ← ESSENCIAL
    channel=channel,        # ← ESSENCIAL
    kpi=kpi                # ← ESSENCIAL
)
```

---

### 4. **Endpoint `/dashboards-list` Deve Usar Manager Correto**

**ERRADO:**
```python
# Hardcoded - sempre usa produção
firestore_client.collection('dashboards').stream()
```

**CORRETO:**
```python
# Usa a coleção correta do ambiente
bq_fs_manager.fs_client.collection(bq_fs_manager.dashboards_collection).stream()
```

---

### 5. **Campaign Keys: Normalização de Caracteres**

Campaign keys são gerados removendo:
- Espaços → `_`
- Caracteres especiais (acentos, til, hífen no meio do nome)
- Apenas alfanuméricos e `_`, `-`

**Exemplos:**
- `Linkedin Sponsored - vídeo` → `senai_linkedin_sponsored_video` (automação remove hífen e acento)
- `Sabão em pó` → `sonho_sabao_em_po` (remove til e acento)

**⚠️ Isso pode causar discrepâncias!** Use scripts de correção manual quando necessário.

---

### 6. **CSV É a Fonte da Verdade**

O arquivo `dashboards.csv` deve sempre conter:
- **Todos** os dashboards que devem existir
- **Sem duplicatas**
- **Dados corretos** (cliente, campanha, planilha, canal, kpi)

**Antes de adicionar nova linha:**
1. Verificar se não há duplicata
2. Validar URL da planilha
3. Confirmar KPI correto (cpm ou cpv)

---

### 7. **Testar em Staging ANTES de Produção**

**SEMPRE siga este fluxo:**

```
1. Desenvolvimento Local
   ↓
2. Deploy em STAGING
   ↓
3. Testes completos em STAGING
   ↓
4. (Opcional) Deploy em HML
   ↓
5. Testes de aceitação em HML
   ↓
6. Deploy em PRODUÇÃO
   ↓
7. Validação em PRODUÇÃO
```

**NUNCA** pule o staging!

---

## 📋 PROCEDIMENTOS PADRÃO

### Procedimento 1: Deploy de Correção de Bug

**Cenário:** Corrigir um bug no código (ex: filtro não funciona)

**Passos:**
1. Fazer correção no código local
2. Testar localmente (se possível)
3. Deploy em staging:
   ```bash
   ./deploy_stg_gen_dashboard_ia.sh
   ```
4. Testar correção em staging
5. Se OK, deploy em produção:
   ```bash
   ./deploy_gen_dashboard_ia.sh
   ```
6. Verificar tráfego direcionado para nova revisão
7. Validar correção em produção

**Tempo:** ~15-20 minutos

---

### Procedimento 2: Adicionar Novo Dashboard

**Cenário:** Cliente solicita novo dashboard

**Passos:**
1. Obter dados da planilha Google Sheets (URL)
2. Adicionar linha no `dashboards.csv`:
   ```csv
   cliente,campanha,URL_planilha,canal,kpi
   ```
3. Gerar dashboard em staging:
   ```bash
   curl -X POST https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/generate-dashboard \
     -H 'Content-Type: application/json' \
     -d '{"campaign_key": "...", "client": "...", ...}'
   ```
4. Testar dashboard em staging
5. Se OK, gerar em produção:
   ```bash
   curl -X POST https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/generate-dashboard \
     -H 'Content-Type: application/json' \
     -d '{"campaign_key": "...", "client": "...", ...}'
   ```

**Tempo:** ~5 minutos

---

### Procedimento 3: Recriar Todos os Dashboards

**Cenário:** Grande atualização ou correção estrutural

**Passos:**
1. **BACKUP OBRIGATÓRIO:**
   ```bash
   python3 backup_production_data.py
   ```

2. Atualizar `dashboards.csv` se necessário

3. Limpar e recriar staging (teste primeiro):
   ```bash
   python3 clean_staging_data.py
   python3 automate_dashboard_creation.py
   ```

4. Validar staging completamente

5. Limpar e recriar produção:
   ```bash
   python3 clean_and_recreate_production.py
   ```

6. Validar produção

**Tempo:** ~10-15 minutos

---

## 🔍 COMANDOS ÚTEIS

### Verificar Status de um Ambiente

```bash
# Produção
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status

# Staging
curl https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status

# HML
curl https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status
```

**Resposta esperada:**
```json
{
  "persistence_status": {
    "bigquery_available": true,
    "firestore_available": true,
    "campaigns_count": 31,
    "dashboards_count": 31
  }
}
```

---

### Ver Logs em Tempo Real

```bash
# Produção
gcloud run logs tail gen-dashboard-ia --region=us-central1

# Staging
gcloud run logs tail stg-gen-dashboard-ia --region=us-central1

# HML
gcloud run logs tail hml-gen-dashboard-ia --region=us-central1
```

---

### Buscar Erros nos Logs

```bash
gcloud run logs read gen-dashboard-ia \
  --region=us-central1 \
  --filter="severity=ERROR" \
  --limit=50
```

---

### Listar Revisões do Cloud Run

```bash
gcloud run revisions list \
  --service=gen-dashboard-ia \
  --region=us-central1 \
  --limit=10
```

---

### Verificar Datasets BigQuery

```bash
# Listar datasets
bq ls --project_id=automatizar-452311

# Contar registros
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `automatizar-452311.south_media_dashboards.dashboards`'
```

---

### Verificar Coleções Firestore

```python
python3 -c "
from google.cloud import firestore
fs = firestore.Client()
count = sum(1 for _ in fs.collection('dashboards').stream())
print(f'Dashboards: {count}')
"
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
south-media-ia/
├── cloud_run_mvp.py                    # App principal
├── bigquery_firestore_manager.py       # Gerenciador de dados
├── real_google_sheets_extractor.py     # Extrator de planilhas
├── google_sheets_service.py            # Serviço Google Sheets
├── config.py                           # Configurações
├── gunicorn.conf.py                    # Config servidor
├── date_normalizer.py                  # Normalização de datas
├── requirements.txt                    # Dependências Python
├── Dockerfile                          # Container Docker
├── dashboards.csv                      # Lista de dashboards (FONTE DA VERDADE)
│
├── deploy_gen_dashboard_ia.sh          # Deploy PRODUÇÃO
├── deploy_stg_gen_dashboard_ia.sh      # Deploy STAGING
├── deploy_hml_gen_dashboard_ia.sh      # Deploy HML
├── deploy_production_complete.sh       # Deploy automatizado
│
├── backup_production_data.py           # Backup completo
├── clean_and_recreate_production.py    # Limpar/recriar produção
├── clean_and_recreate_hml.py           # Limpar/recriar HML
├── clean_staging_data.py               # Limpar staging
├── automate_dashboard_creation.py      # Criar dashboards via API
├── fix_production_metadata.py          # Corrigir metadados
├── fix_remaining_production_dashboards.py  # Correções manuais
├── check_all_environments.py           # Verificar todos ambientes
│
├── static/
│   ├── dash_generic_template.html              # Template CPV
│   └── dash_remarketing_cpm_template.html      # Template CPM
│
├── GUIA_DEFINITIVO_DEPLOY.md          # Este guia
└── DEPLOY_PRODUCTION_README.md        # Guia de deploy
```

---

## 🎯 BOAS PRÁTICAS

### 1. **Sempre Teste em Staging Primeiro**

```bash
# ERRADO - Deploy direto em produção
./deploy_gen_dashboard_ia.sh

# CORRETO - Testar em staging primeiro
./deploy_stg_gen_dashboard_ia.sh
# ... testar ...
./deploy_gen_dashboard_ia.sh
```

---

### 2. **Mantenha CSV Atualizado**

O `dashboards.csv` é a **fonte da verdade**. Sempre que criar/remover dashboard:

1. Atualizar CSV
2. Commitar mudanças no git
3. Recriar ambientes se necessário

---

### 3. **Monitore os Logs Após Deploy**

```bash
# Primeiros 5 minutos após deploy
gcloud run logs tail gen-dashboard-ia --region=us-central1

# Buscar por erros
# Se aparecer "ERROR", investigar imediatamente
```

---

### 4. **Documente Mudanças Grandes**

Para mudanças estruturais (novos campos, novos templates):
1. Criar issue/documento descrevendo mudança
2. Testar extensivamente em staging
3. Validar em HML
4. Deploy gradual em produção
5. Monitorar por 24h

---

### 5. **Mantenha Backups Regulares**

```bash
# Backup semanal automático (adicionar ao cron)
0 2 * * 0 cd /path/to/south-media-ia && python3 backup_production_data.py
```

Manter últimos 4 backups (1 mês).

---

## 🚨 SITUAÇÕES DE EMERGÊNCIA

### Cenário: Produção está fora do ar

**Passos imediatos:**

1. **Verificar revisão atual:**
   ```bash
   gcloud run services describe gen-dashboard-ia --region=us-central1
   ```

2. **Reverter para última revisão estável:**
   ```bash
   gcloud run services update-traffic gen-dashboard-ia \
     --to-revisions=gen-dashboard-ia-00023-ts9=100 \
     --region=us-central1
   ```

3. **Verificar logs:**
   ```bash
   gcloud run logs read gen-dashboard-ia --region=us-central1 --limit=100
   ```

4. **Notificar equipe e investigar causa**

---

### Cenário: Dashboards não carregam dados

**Diagnóstico:**

1. **Verificar persistência:**
   ```bash
   curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status
   ```

2. **Verificar Firestore:**
   ```bash
   python3 check_all_environments.py
   ```

3. **Verificar planilhas Google Sheets:**
   - Planilhas acessíveis?
   - Permissões corretas?

4. **Regenerar dashboards afetados:**
   ```bash
   python3 clean_and_recreate_production.py
   ```

---

### Cenário: Perda de dados após deploy

**Recuperação:**

1. **NÃO ENTRE EM PÂNICO** - Temos backups!

2. **Identificar último backup:**
   ```bash
   ls -lt production_backup_*/
   ```

3. **Reverter Cloud Run:**
   ```bash
   gcloud run services update-traffic gen-dashboard-ia \
     --to-revisions=[ULTIMA_REVISAO_ESTAVEL]=100 \
     --region=us-central1
   ```

4. **Restaurar dados do backup:**
   ```bash
   python3 restore_backup_to_production.py
   # OU restaurar manualmente via console GCP
   ```

5. **Validar restauração:**
   ```bash
   python3 check_all_environments.py
   ```

---

## 🔐 SEGURANÇA E PERMISSÕES

### Service Account

Cada serviço Cloud Run usa service account com permissões:
- BigQuery Data Editor
- Firestore User
- Cloud Storage Object Viewer (para Google Sheets API)

**Verificar permissões:**
```bash
gcloud projects get-iam-policy automatizar-452311
```

---

### Variáveis de Ambiente Sensíveis

**Não commitar:**
- Chaves de API
- Tokens de acesso
- Credenciais de serviço

**Usar:**
- Cloud Run environment variables
- Secret Manager (para dados muito sensíveis)

---

## 📊 MONITORAMENTO CONTÍNUO

### Métricas Importantes

1. **Taxa de Sucesso de Geração:** > 95%
2. **Tempo de Resposta da API:** < 5s
3. **Erros HTTP 5xx:** < 1%
4. **Uptime:** > 99.9%

### Alertas Recomendados

Configure alertas no Google Cloud Console:
- Erro rate > 5% (15 min)
- Latência > 10s (5 min)
- Instâncias falhando
- Uso de memória > 90%

---

## 🎓 CONCEITOS TÉCNICOS

### Por que BigQuery + Firestore?

**BigQuery:**
- ✅ Ótimo para analytics e queries complexas
- ✅ Escalável para milhões de registros
- ❌ Lento para leituras individuais (100-500ms)
- ❌ Mais caro para muitas leituras pequenas

**Firestore:**
- ✅ Extremamente rápido para leituras (10-50ms)
- ✅ Barato para leituras frequentes
- ✅ Ideal para metadados e cache
- ❌ Não ideal para analytics complexos

**Combinação:**
- BigQuery: Armazena TODOS os dados (histórico completo)
- Firestore: Metadados rápidos para listagem e cache

---

### Templates Dinâmicos vs Estáticos

**Sistema ANTIGO (Estático):**
- Gerava arquivos HTML em `/static/`
- Problema: Arquivos acumulavam, difícil manutenção

**Sistema ATUAL (Dinâmico):**
- Templates genéricos em `/static/`
- API injeta dados: `/api/dashboard/{campaign_key}`
- Vantagens:
  - ✅ 1 template para múltiplos dashboards
  - ✅ Fácil atualizar todos os dashboards
  - ✅ Não acumula arquivos

---

### Filtros de Data

**Implementação:**
- JavaScript puro (sem dependências externas)
- Filtra array `daily_data` por data
- Recalcula métricas (CTR, conversões, custos)
- Atualiza tabelas e gráficos
- Funciona em ambas as abas (Visão Geral e Por Canal)

**Filtros disponíveis:**
- **Todos:** Mostra todo o período
- **30 dias:** Últimos 30 dias
- **7 dias:** Últimos 7 dias
- **Hoje:** Apenas dados de hoje (mostra "Nenhum dado" se vazio)

---

## 🎁 SCRIPTS ÚTEIS CRIADOS

### Backup e Restauração
- `backup_production_data.py` - Backup completo
- `restore_backup_to_staging.py` - Restaurar backup em staging
- `restore_backup_to_production.py` - Restaurar backup em produção (criar se necessário)

### Limpeza
- `clean_staging_data.py` - Limpar staging
- `clean_production_data.py` - Limpar produção (criado dinamicamente)
- `clean_and_recreate_production.py` - Limpar e recriar produção
- `clean_and_recreate_hml.py` - Limpar e recriar HML

### Automação
- `automate_dashboard_creation.py` - Criar dashboards automaticamente
- `deploy_production_complete.sh` - Deploy completo automatizado

### Correção de Metadados
- `fix_production_metadata.py` - Corrigir metadados (primeira passada)
- `fix_remaining_production_dashboards.py` - Correções manuais (segunda passada)
- `fix_dashboard_metadata_from_csv.py` - Corrigir de staging

### Verificação e Debug
- `check_all_environments.py` - Verificar todos os ambientes
- `compare_csv_with_firestore.py` - Comparar CSV com Firestore
- `verify_and_regenerate_dashboards.py` - Verificar e regenerar
- `debug_dashboards_firestore.py` - Debug de Firestore
- `verify_staging_datasets.py` - Verificar isolamento de staging

---

## 📞 CONTATOS E RECURSOS

### Documentação Oficial
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [BigQuery](https://cloud.google.com/bigquery/docs)
- [Firestore](https://cloud.google.com/firestore/docs)
- [Chart.js](https://www.chartjs.org/docs/)

### URLs dos Serviços
- **Produção:** https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app
- **Staging:** https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app
- **HML:** https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

### Console GCP
- **Cloud Run:** https://console.cloud.google.com/run?project=automatizar-452311
- **BigQuery:** https://console.cloud.google.com/bigquery?project=automatizar-452311
- **Firestore:** https://console.cloud.google.com/firestore?project=automatizar-452311

---

## ✅ CHECKLIST FINAL ANTES DE DEPLOY EM PRODUÇÃO

- [ ] Código testado em staging
- [ ] Filtros testados (CPV e CPM templates)
- [ ] CSV atualizado e sem duplicatas
- [ ] Backup de produção realizado
- [ ] Equipe notificada sobre deploy
- [ ] Janela de manutenção definida (se necessário)
- [ ] Plano de rollback preparado
- [ ] Logs monitorados durante deploy
- [ ] Validação pós-deploy completa
- [ ] Documentação atualizada

---

## 🎉 CONCLUSÃO

Este sistema agora tem:

✅ **3 ambientes completamente isolados**
✅ **31 dashboards funcionais em cada ambiente**
✅ **Filtros interativos funcionando**
✅ **Persistência robusta (BigQuery + Firestore)**
✅ **Deploy automatizado e seguro**
✅ **Backup e rollback prontos**
✅ **Documentação completa**

**Próximos deploys serão muito mais rápidos e seguros seguindo este guia!** 🚀

---

**Última atualização:** 2025-10-11
**Versão:** 2.0
**Status:** ✅ Produção Estável com 31 Dashboards

