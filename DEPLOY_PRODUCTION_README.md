# 🚀 GUIA COMPLETO: DEPLOY EM PRODUÇÃO

## 📋 PRÉ-REQUISITOS

### ✅ Arquivos Atualizados:
- [x] `cloud_run_mvp.py` - Com todas as correções de filtros e endpoints
- [x] `bigquery_firestore_manager.py` - Com suporte a ambientes (production/staging/hml)
- [x] `dashboards.csv` - Com os 31 dashboards corretos (sem duplicatas)
- [x] Templates HTML - Com filtros funcionando (CPV e CPM)
- [x] Scripts de deploy - `deploy_gen_dashboard_ia.sh` e `deploy_production_complete.sh`

### 🔧 Configurações de Ambiente:

**PRODUÇÃO:**
- `ENVIRONMENT=production`
- Dataset BigQuery: `south_media_dashboards`
- Firestore Collections: `campaigns`, `dashboards`
- URL: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

**STAGING:**
- `ENVIRONMENT=staging`
- Dataset BigQuery: `south_media_dashboards_staging`
- Firestore Collections: `campaigns_staging`, `dashboards_staging`
- URL: https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app

---

## 🎯 OPÇÃO 1: DEPLOY COMPLETO AUTOMATIZADO (RECOMENDADO)

Este script faz **TODO O PROCESSO** automaticamente:

```bash
./deploy_production_complete.sh
```

### O que o script faz:

1. **🔄 Backup Automático**
   - Cria backup completo de BigQuery e Firestore de produção
   - Salva em diretório `production_backup_[timestamp]`

2. **🧹 Limpeza de Dados**
   - Remove todos os dados de produção (BigQuery + Firestore)
   - Prepara ambiente para novos dashboards

3. **🏗️ Deploy do Código**
   - Faz build da imagem Docker
   - Deploy no Cloud Run com configurações de produção
   - Aguarda serviço estabilizar

4. **📊 Recriação dos Dashboards**
   - Lê o arquivo `dashboards.csv`
   - Gera todos os 31 dashboards via API
   - Relatório completo de sucesso/falhas

### ⏱️ Tempo Estimado: ~5-7 minutos

---

## 🎯 OPÇÃO 2: DEPLOY MANUAL (PASSO A PASSO)

Se preferir fazer manualmente ou verificar cada etapa:

### PASSO 1: Backup de Segurança

```bash
python3 backup_production_data.py
```

**Verifica:**
- Backup salvo em `production_backup_[timestamp]/`
- Arquivos JSON criados para BigQuery e Firestore

---

### PASSO 2: Limpar Dados de Produção

```bash
python3 clean_production_data.py
```

**Verifica:**
- BigQuery: 0 campaigns, 0 dashboards
- Firestore: 0 documentos em `campaigns` e `dashboards`

---

### PASSO 3: Deploy do Código

```bash
./deploy_gen_dashboard_ia.sh
```

**Verifica:**
- Build bem-sucedido
- Cloud Run deployment OK
- Health check passando

**Aguarde:** 30 segundos para estabilização

---

### PASSO 4: Recriar Dashboards

```bash
python3 automate_production_dashboards.py
```

**Verifica:**
- 31/31 dashboards criados
- Taxa de sucesso: 100%
- Nenhum erro na API

---

## 🔍 VALIDAÇÃO PÓS-DEPLOY

### 1. Verificar Persistência

```bash
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status
```

**Esperado:**
```json
{
  "persistence_status": {
    "campaigns_count": 31,
    "dashboards_count": 31,
    "bigquery_available": true,
    "firestore_available": true
  }
}
```

---

### 2. Verificar Listagem

Acesse: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list

**Esperado:**
- 31 dashboards listados
- Todos com metadados corretos (Cliente, Campanha, Canal, KPI)
- Nenhum dashboard com "N/A"

---

### 3. Testar Dashboards Aleatórios

**Teste 3-5 dashboards diferentes:**

```bash
# Exemplo 1: CPV (Netflix)
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/dashboard/copacol_video_de_30s_campanha_institicional_netflix

# Exemplo 2: CPM (LinkedIn)
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/dashboard/senai_linkedin_sponsored_display

# Exemplo 3: CPV (YouTube)
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/dashboard/copacol_campanha_institucional_de_video_de_30s_em_youtube
```

**Verifique no browser:**
- Dashboard carrega completamente
- Dados aparecem nas tabelas
- Filtros funcionam (Todos, 30 dias, 7 dias, Hoje)
- Aba "Por Canal" funciona com filtros

---

### 4. Testar Filtros (Manual no Browser)

**Para cada template (CPV e CPM):**

1. **Filtro "Todos"**: Mostra todos os dados
2. **Filtro "30 dias"**: Filtra últimos 30 dias
3. **Filtro "7 dias"**: Filtra últimos 7 dias
4. **Filtro "Hoje"**: 
   - Se há dados de hoje: mostra
   - Se não há dados: mostra "Nenhum dado disponível"

5. **Aba "Por Canal"**: Filtros aplicam corretamente

---

## 🚨 ROLLBACK (Se necessário)

Se algo der errado, você pode reverter:

### Opção 1: Reverter Cloud Run para Revisão Anterior

```bash
# Listar revisões
gcloud run revisions list --service=gen-dashboard-ia --region=us-central1

# Reverter para revisão específica
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=[REVISION_NAME]=100 \
  --region=us-central1
```

---

### Opção 2: Restaurar Backup

```bash
# Usar o script de restauração (se criado)
python3 restore_backup_to_production.py
```

**OU manualmente:**

1. Restaurar BigQuery:
```bash
# Para cada tabela no backup
bq load --source_format=NEWLINE_DELIMITED_JSON \
  south_media_dashboards.campaigns \
  production_backup_[timestamp]/bq_south_media_dashboards_campaigns.json
```

2. Restaurar Firestore:
```python
# Usar script Python para restaurar coleções
```

---

## 📊 MONITORAMENTO CONTÍNUO

### Métricas Importantes:

1. **Taxa de Sucesso de Geração**: 100%
2. **Dashboards Ativos**: 31
3. **Tempo de Resposta**: < 5s
4. **Erros de API**: 0

### Logs:

```bash
# Ver logs em tempo real
gcloud run logs tail gen-dashboard-ia --region=us-central1

# Buscar erros
gcloud run logs read gen-dashboard-ia --region=us-central1 --filter="severity=ERROR"
```

---

## 🔧 TROUBLESHOOTING

### Problema: Dashboards com "N/A"

**Causa:** Metadados não salvos no Firestore

**Solução:**
```bash
python3 fix_remaining_dashboards.py
```

---

### Problema: Filtros não funcionam

**Causa:** Template HTML não atualizado

**Solução:**
1. Verificar se os templates corretos foram incluídos no deploy
2. Redesenhar se necessário

---

### Problema: Dashboard não encontrado

**Causa:** Dashboard não foi gerado ou nome incorreto

**Solução:**
```bash
# Regenerar dashboard específico
curl -X POST https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{"campaign_key": "...", "client": "...", "campaign_name": "...", "sheet_id": "...", "channel": "...", "kpi": "..."}'
```

---

## 📝 CHECKLIST FINAL

Antes de considerar o deploy completo:

- [ ] Backup de produção realizado com sucesso
- [ ] Deploy do código concluído sem erros
- [ ] 31 dashboards criados (100%)
- [ ] Listagem mostrando 31 dashboards
- [ ] Testados 3+ dashboards aleatórios
- [ ] Filtros funcionando em CPV e CPM
- [ ] Aba "Por Canal" funcionando
- [ ] Sem erros no Cloud Run logs
- [ ] Persistence status OK (31/31)

---

## 🎉 SUCESSO!

Se todos os itens acima estão ✅, o deploy foi concluído com sucesso!

**URLs de Produção:**
- 🏠 Home: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/
- 📋 Lista: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list
- 📊 API: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/campaigns
- 🏥 Health: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/health

---

## 📞 SUPORTE

Em caso de dúvidas ou problemas:
1. Verificar logs do Cloud Run
2. Verificar este README
3. Verificar scripts de troubleshooting na pasta raiz

