# 🚀 Guia de Deploy - Sistema Gerador de Dashboards

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Configuração Inicial](#configuração-inicial)
4. [Deploy por Ambiente](#deploy-por-ambiente)
5. [Processo Detalhado](#processo-detalhado)
6. [Verificação Pós-Deploy](#verificação-pós-deploy)
7. [Rollback](#rollback)
8. [Troubleshooting](#troubleshooting)
9. [Checklist de Deploy](#checklist-de-deploy)

---

## 🎯 Visão Geral

Este guia detalha o processo completo de deploy do Sistema Gerador de Dashboards nos três ambientes disponíveis:

- **🧪 Staging (STG)** - Desenvolvimento e testes
- **🔬 Homologação (HML)** - Validação final
- **🚀 Produção (PRD)** - Ambiente de produção

---

## ✅ Pré-requisitos

### 1. Software Necessário

```bash
# Google Cloud SDK
gcloud version
# Deve estar instalado e atualizado

# Git
git --version

# Python 3.11 (para testes locais)
python3 --version
```

### 2. Autenticação GCP

```bash
# Login no GCP
gcloud auth login

# Configurar projeto
gcloud config set project automatizar-452311

# Verificar autenticação
gcloud auth list
```

### 3. Permissões Necessárias

Sua conta GCP deve ter:
- ✅ **Cloud Run Admin**
- ✅ **Cloud Build Editor**
- ✅ **Container Registry Service Agent**
- ✅ **BigQuery Admin**
- ✅ **Cloud Datastore User**
- ✅ **Service Account User**

### 4. Verificar APIs Habilitadas

```bash
# APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable sheets.googleapis.com
```

---

## ⚙️ Configuração Inicial

### 1. Clonar Repositório

```bash
cd ~/Documents/GitHub
git clone [REPO_URL] south-media-ia
cd south-media-ia
```

### 2. Verificar Arquivos Necessários

```bash
# Arquivos principais
ls -la cloud_run_mvp.py
ls -la bigquery_firestore_manager.py
ls -la real_google_sheets_extractor.py
ls -la Dockerfile
ls -la requirements.txt

# Templates
ls -la static/dash_generic_template.html
ls -la static/dash_remarketing_cpm_template.html

# Scripts de deploy
ls -la deploy_stg_gen_dashboard_ia.sh
ls -la deploy_hml_gen_dashboard_ia.sh
ls -la deploy_gen_dashboard_ia.sh
```

### 3. Dar Permissões aos Scripts

```bash
chmod +x deploy_stg_gen_dashboard_ia.sh
chmod +x deploy_hml_gen_dashboard_ia.sh
chmod +x deploy_gen_dashboard_ia.sh
```

---

## 🌍 Deploy por Ambiente

### 🧪 Staging (STG)

**Quando usar:**
- Desenvolvimento de novas funcionalidades
- Testes de bugs e correções
- Validação inicial de alterações

**Deploy:**

```bash
./deploy_stg_gen_dashboard_ia.sh
```

**Configurações:**
- Service: `stg-gen-dashboard-ia`
- Environment: `staging`
- Memória: 1GB
- CPU: 1 vCPU
- Max Instances: 3
- Timeout: 300s (5 min)

**URL:** https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Persistência:**
- BigQuery: `staging_campaigns`, `staging_campaign_metrics`
- Firestore: `campaigns_staging`, `dashboards_staging`

---

### 🔬 Homologação (HML)

**Quando usar:**
- Validação final antes de produção
- Testes com stakeholders
- Demonstrações para clientes
- Testes de carga

**Deploy:**

```bash
./deploy_hml_gen_dashboard_ia.sh
```

**Configurações:**
- Service: `hml-gen-dashboard-ia`
- Environment: `hml`
- Memória: 2GB
- CPU: 2 vCPU
- Max Instances: 5
- Timeout: 1800s (30 min)

**URL:** https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Persistência:**
- BigQuery: `hml_campaigns`, `hml_campaign_metrics`
- Firestore: `campaigns_hml`, `dashboards_hml`

---

### 🚀 Produção (PRD)

**Quando usar:**
- Deploy de versões estáveis
- Após validação completa em HML
- Com aprovação dos stakeholders

**Deploy:**

```bash
./deploy_gen_dashboard_ia.sh
```

**Configurações:**
- Service: `gen-dashboard-ia`
- Environment: `production`
- Memória: 4GB
- CPU: 2 vCPU
- Max Instances: 10
- Timeout: 3600s (1h)

**URL:** https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**Persistência:**
- BigQuery: `campaigns`, `campaign_metrics`
- Firestore: `campaigns`, `dashboards`

---

## 🔄 Processo Detalhado

### Fase 1: Preparação (1-2 min)

```bash
# 1. Verificar branch
git branch
# Deve estar na branch correta (main para produção)

# 2. Puxar últimas alterações
git pull origin main

# 3. Verificar status
git status
# Não deve ter alterações não commitadas
```

### Fase 2: Build da Imagem (2-3 min)

O script automaticamente:

1. **Valida arquivos necessários**
   ```
   ✅ cloud_run_mvp.py
   ✅ bigquery_firestore_manager.py
   ✅ real_google_sheets_extractor.py
   ✅ Dockerfile
   ✅ requirements.txt
   ```

2. **Configura projeto GCP**
   ```bash
   gcloud config set project automatizar-452311
   ```

3. **Habilita APIs necessárias**
   ```
   ✅ run.googleapis.com
   ✅ cloudbuild.googleapis.com
   ✅ bigquery.googleapis.com
   ✅ firestore.googleapis.com
   ```

4. **Inicia Cloud Build**
   ```bash
   gcloud builds submit --tag gcr.io/automatizar-452311/[SERVICE_NAME]
   ```

**O que acontece no Cloud Build:**

```dockerfile
# 1. Base image
FROM python:3.11-slim

# 2. Instala dependências do sistema
RUN apt-get update && apt-get install -y git curl

# 3. Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia arquivos da aplicação
COPY cloud_run_mvp.py .
COPY bigquery_firestore_manager.py .
COPY real_google_sheets_extractor.py .
COPY google_sheets_service.py .
COPY config.py .
COPY gunicorn.conf.py .
COPY date_normalizer.py .
COPY static/ ./static/

# 5. Configura usuário não-root
RUN useradd --create-home --shell /bin/bash app
USER app

# 6. Expõe porta 8080
EXPOSE 8080

# 7. Define comando de inicialização
CMD ["gunicorn", "--config", "gunicorn.conf.py", "cloud_run_mvp:app"]
```

### Fase 3: Deploy no Cloud Run (1-2 min)

O script executa:

```bash
gcloud run deploy [SERVICE_NAME] \
  --image gcr.io/automatizar-452311/[SERVICE_NAME]:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=automatizar-452311,ENVIRONMENT=[ENV]" \
  --memory [MEMORY] \
  --cpu [CPU] \
  --timeout [TIMEOUT] \
  --max-instances [MAX] \
    --concurrency 80
```

**Variáveis de Ambiente Configuradas:**

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `PROJECT_ID` | ID do projeto GCP | `automatizar-452311` |
| `ENVIRONMENT` | Ambiente de execução | `staging`, `hml`, `production` |

**Recursos Alocados por Ambiente:**

| Ambiente | Memória | CPU | Max Instances | Timeout |
|----------|---------|-----|---------------|---------|
| Staging | 1GB | 1 | 3 | 5 min |
| Homologação | 2GB | 2 | 5 | 30 min |
| Produção | 4GB | 2 | 10 | 1h |

### Fase 4: Verificação (30s)

O script automaticamente verifica:

1. **Health Check**
   ```bash
   curl https://[SERVICE_URL]/health
   # Espera: {"status": "healthy", "timestamp": "..."}
   ```

2. **Endpoints Principais**
   ```bash
   # Home
   curl https://[SERVICE_URL]/
   
   # Persistence Status
   curl https://[SERVICE_URL]/persistence-status
   
   # Campaigns
   curl https://[SERVICE_URL]/api/campaigns
   ```

---

## ✅ Verificação Pós-Deploy

### 1. Verificação Automática (feita pelo script)

```bash
# Health check
✅ Health check passou!

# Endpoints disponíveis
📋 Endpoints Disponíveis:
  🏠 Home: https://[SERVICE_URL]/
  🏥 Health: https://[SERVICE_URL]/health
  📊 Persistência: https://[SERVICE_URL]/persistence-status
  🎯 Gerador: https://[SERVICE_URL]/api/generate-dashboard
  📋 Campanhas: https://[SERVICE_URL]/api/campaigns
  📊 Dashboards: https://[SERVICE_URL]/api/dashboards
```

### 2. Verificação Manual

#### A. Testar Interface Web

```bash
# Abrir no navegador
open https://[SERVICE_URL]/dash-generator-pro
```

**Verificar:**
- ✅ Página carrega corretamente
- ✅ Formulário está funcional
- ✅ Badge de persistência mostra "BigQuery + Firestore"

#### B. Testar Geração de Dashboard

```bash
curl -X POST https://[SERVICE_URL]/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{
    "campaign_key": "teste_pos_deploy",
    "client": "Teste Deploy",
    "campaign_name": "Validação Pós-Deploy",
    "sheet_id": "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8",
    "kpi": "CPV"
  }'
```

**Resposta Esperada:**
```json
{
  "success": true,
  "message": "Dashboard gerado com sucesso!",
  "campaign_key": "teste_pos_deploy",
  "dashboard_url": "/api/dashboard/teste_pos_deploy",
  "dashboard_url_full": "https://[SERVICE_URL]/api/dashboard/teste_pos_deploy"
}
```

#### C. Testar Dashboard Gerado

```bash
# Abrir dashboard no navegador
open https://[SERVICE_URL]/api/dashboard/teste_pos_deploy
```

**Verificar:**
- ✅ Dashboard carrega
- ✅ Dados são exibidos
- ✅ Gráficos renderizam
- ✅ Filtros funcionam
  - Clicar em "7 dias"
  - Verificar que dados atualizam
  - Verificar que gráficos atualizam
- ✅ Abas funcionam (Visão Geral, Por Canal, Por Data)

#### D. Testar Listagem de Dashboards

```bash
# Abrir listagem no navegador
open https://[SERVICE_URL]/dashboards-list
```

**Verificar:**
- ✅ Lista carrega
- ✅ Dashboard recém-criado aparece
- ✅ Filtros funcionam (cliente, canal, KPI)
- ✅ Busca funciona
- ✅ Links para dashboards funcionam

#### E. Verificar Persistência

```bash
# Status de persistência
curl https://[SERVICE_URL]/persistence-status
```

**Resposta Esperada:**
```json
{
  "status": "active",
  "type": "BigQuery + Firestore",
  "environment": "[staging|hml|production]",
  "bigquery_datasets": {
    "campaigns": "[ENV]_campaigns",
    "metrics": "[ENV]_campaign_metrics"
  },
  "firestore_collections": {
    "campaigns": "campaigns_[ENV]",
    "dashboards": "dashboards_[ENV]"
  },
  "campaign_count": 1,
  "dashboard_count": 1
}
```

### 3. Verificação de Logs

```bash
# Ver logs em tempo real
gcloud run services logs tail [SERVICE_NAME] --limit=50

# Verificar erros
gcloud run services logs read [SERVICE_NAME] --severity=ERROR
```

**Logs Esperados:**
```
✅ Servidor Flask iniciado
✅ Persistência BigQuery + Firestore ativa
✅ Environment: [staging|hml|production]
✅ Servidor rodando na porta 8080
```

---

## ⏪ Rollback

Se algo der errado, você pode fazer rollback para a versão anterior.

### Método 1: Via Script (Rápido)

```bash
# Listar revisões disponíveis
gcloud run revisions list --service=[SERVICE_NAME] --limit=5

# Output:
# REVISION                         SERVICE           DEPLOYED                 DEPLOYED BY
# service-00036-x5s               service           2025-10-11 03:41:06      user@domain.com
# service-00035-a2b               service           2025-10-10 15:20:30      user@domain.com
# service-00034-c3d               service           2025-10-09 10:15:00      user@domain.com

# Fazer rollback para revisão anterior
gcloud run services update-traffic [SERVICE_NAME] \
  --to-revisions=[SERVICE-00035-a2b]=100 \
  --region=us-central1
```

### Método 2: Via Console GCP

1. Acesse [Cloud Run Console](https://console.cloud.google.com/run)
2. Selecione o serviço
3. Vá para aba "REVISIONS"
4. Selecione a revisão anterior
5. Clique em "MANAGE TRAFFIC"
6. Mude para 100% na revisão anterior
7. Clique em "SAVE"

### Método 3: Deploy da Versão Anterior

```bash
# Voltar para commit anterior
git log --oneline -5
git checkout [COMMIT_HASH_ANTERIOR]

# Fazer deploy
./deploy_[ENV]_gen_dashboard_ia.sh

# Voltar para branch principal
git checkout main
```

---

## 🔧 Troubleshooting

### Problema 1: Build Falha

**Sintoma:**
```
ERROR: build step 0 "gcr.io/cloud-builders/docker" failed
```

**Possíveis Causas:**
- Erro no Dockerfile
- Dependência faltando em requirements.txt
- Arquivo Python com erro de sintaxe

**Solução:**
```bash
# 1. Verificar sintaxe Python
python3 -m py_compile cloud_run_mvp.py

# 2. Testar Dockerfile localmente (se tiver Docker)
docker build -t test-image .

# 3. Verificar requirements.txt
cat requirements.txt
```

### Problema 2: Deploy Falha

**Sintoma:**
```
ERROR: Deployment failed
```

**Possíveis Causas:**
- Timeout no deploy
- Recursos insuficientes
- Variáveis de ambiente incorretas

**Solução:**
```bash
# 1. Verificar logs do Cloud Run
gcloud run services logs read [SERVICE_NAME] --limit=50

# 2. Verificar configuração do serviço
gcloud run services describe [SERVICE_NAME]

# 3. Tentar deploy com mais recursos
# Editar script e aumentar memória/timeout
```

### Problema 3: Health Check Falha

**Sintoma:**
```
❌ Health check failed!
```

**Possíveis Causas:**
- Aplicação não iniciou
- Erro no código Python
- Dependência faltando

**Solução:**
```bash
# 1. Ver logs detalhados
gcloud run services logs tail [SERVICE_NAME]

# 2. Verificar startup da aplicação
# Procurar por:
# - ModuleNotFoundError
# - ImportError
# - Syntax errors

# 3. Testar localmente
python3 cloud_run_mvp.py
```

### Problema 4: Persistência Não Funciona

**Sintoma:**
```
❌ Erro ao salvar no BigQuery/Firestore
```

**Possíveis Causas:**
- Variável ENVIRONMENT incorreta
- Permissões insuficientes
- Datasets/Collections não existem

**Solução:**
```bash
# 1. Verificar variável de ambiente
gcloud run services describe [SERVICE_NAME] \
  --format='value(spec.template.spec.containers[0].env)'

# 2. Verificar permissões da service account
gcloud projects get-iam-policy automatizar-452311 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount"

# 3. Criar datasets/collections se necessário
# Ver DOCUMENTACAO_SISTEMA.md seção "Persistência de Dados"
```

### Problema 5: Timeout em Requisições

**Sintoma:**
```
Error 504: Deadline Exceeded
```

**Possíveis Causas:**
- Timeout muito curto
- Operação muito demorada
- Planilha muito grande

**Solução:**
```bash
# 1. Aumentar timeout no script de deploy
# Editar deploy_[ENV]_gen_dashboard_ia.sh
# Alterar --timeout para valor maior

# 2. Re-deploy
./deploy_[ENV]_gen_dashboard_ia.sh

# 3. Otimizar código se necessário
# - Adicionar cache
# - Processar dados em batches
# - Limitar quantidade de dados processados
```

---

## ✅ Checklist de Deploy

### Pré-Deploy

- [ ] Código commitado no Git
- [ ] Branch correta (main para produção)
- [ ] Testes locais passando
- [ ] Documentação atualizada
- [ ] Aprovação dos stakeholders (para produção)

### Durante Deploy

- [ ] Executar script de deploy correto
- [ ] Monitorar logs do Cloud Build
- [ ] Verificar que build completa com sucesso
- [ ] Verificar que deploy completa com sucesso
- [ ] Aguardar health check passar

### Pós-Deploy

- [ ] Interface web carrega
- [ ] Gerar dashboard de teste
- [ ] Verificar dashboard funciona
- [ ] Testar todos os filtros
- [ ] Verificar listagem de dashboards
- [ ] Confirmar persistência de dados
- [ ] Verificar logs sem erros
- [ ] Notificar equipe sobre deploy
- [ ] Documentar qualquer problema

### Rollback (se necessário)

- [ ] Identificar problema
- [ ] Decidir fazer rollback
- [ ] Executar rollback
- [ ] Verificar que versão anterior funciona
- [ ] Investigar causa do problema
- [ ] Corrigir problema
- [ ] Fazer novo deploy quando pronto

---

## 📊 Fluxo Recomendado de Deploy

```
┌─────────────────┐
│  Desenvolvimento │
│   (Local/STG)    │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Deploy STG    │
│  Testes Iniciais │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Deploy HML    │
│ Validação Final  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Deploy PRD    │
│    Produção     │
└─────────────────┘
```

### Timing Recomendado

| Ambiente | Quando Deploy | Frequência |
|----------|--------------|------------|
| **Staging** | A cada feature/bugfix | Várias vezes ao dia |
| **Homologação** | Quando STG está estável | 1-2x por semana |
| **Produção** | Após validação em HML | 1x por semana ou quinzenal |

---

## 🎯 Melhores Práticas

### 1. Sempre Testar em STG Primeiro

Nunca faça deploy direto em produção sem testar em staging.

### 2. Usar HML para Validação Final

Homologação deve ser idêntico à produção em configuração.

### 3. Deploy em Horários de Baixo Uso

Para produção, prefira:
- Madrugada
- Finais de semana
- Horários com poucos usuários ativos

### 4. Monitorar Pós-Deploy

Após deploy, monitore por pelo menos 30 minutos:
- Logs
- Métricas de performance
- Relatórios de erro

### 5. Comunicar Deploy

Antes de deploy em produção:
- Notificar equipe
- Avisar stakeholders
- Preparar mensagem de status

### 6. Documentar Mudanças

Sempre documentar:
- O que foi alterado
- Por que foi alterado
- Como testar as alterações

---

## 📞 Suporte

### Em caso de problemas durante deploy:

1. **Não entrar em pânico** 🧘
2. **Capturar logs** do erro
3. **Tentar rollback** se necessário
4. **Consultar troubleshooting** acima
5. **Contactar desenvolvedor** se necessário

### Informações para reportar problemas:

- Ambiente (STG/HML/PRD)
- Horário do deploy
- Logs completos do erro
- Passos para reproduzir
- Comportamento esperado vs. observado

---

## 📝 Histórico de Deploys

Manter registro de deploys realizados:

| Data | Ambiente | Versão | Responsável | Status | Observações |
|------|----------|--------|-------------|--------|-------------|
| 2025-10-11 | STG | v2.0.1 | Luciano | ✅ | Deploy inicial pós-refactoring |
| 2025-10-11 | HML | v2.0.1 | Luciano | 🔄 | Em progresso |
| ... | ... | ... | ... | ... | ... |

---

**Última Atualização:** Outubro 2025
**Versão do Guia:** 1.0
**Responsável:** Luciano Torres