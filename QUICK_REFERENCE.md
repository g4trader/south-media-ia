# ⚡ REFERÊNCIA RÁPIDA - COMANDOS ESSENCIAIS

## 🚀 DEPLOY RÁPIDO

### Deploy Completo em Produção (Automatizado)
```bash
./deploy_production_complete.sh
# Faz: Backup → Limpeza → Deploy → Recriação de dashboards
# Tempo: ~5-7 minutos
```

### Deploy Apenas do Código
```bash
# Produção
./deploy_gen_dashboard_ia.sh

# Staging
./deploy_stg_gen_dashboard_ia.sh

# HML
./deploy_hml_gen_dashboard_ia.sh
```

---

## 🧹 LIMPEZA E RECRIAÇÃO

### Recriar Todos os Dashboards
```bash
# Produção (com backup automático)
python3 clean_and_recreate_production.py

# HML
python3 clean_and_recreate_hml.py

# Staging
python3 clean_staging_data.py
python3 automate_dashboard_creation.py
```

---

## 🔍 VERIFICAÇÃO RÁPIDA

### Status de Todos os Ambientes
```bash
python3 check_all_environments.py
```

### Status Individual
```bash
curl https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status        # Produção
curl https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status    # Staging
curl https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/persistence-status    # HML
```

---

## 💾 BACKUP

### Fazer Backup
```bash
python3 backup_production_data.py
# Cria: production_backup_[timestamp]/
```

### Restaurar Backup em Staging
```bash
python3 restore_backup_to_staging.py
```

---

## 🔧 CORREÇÕES RÁPIDAS

### Corrigir Metadados (N/A nos dashboards)
```bash
# Produção
python3 fix_production_metadata.py
python3 fix_remaining_production_dashboards.py

# Staging
python3 fix_dashboard_metadata_from_csv.py
python3 fix_remaining_dashboards.py
```

### Regenerar Dashboard Específico
```bash
curl -X POST https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{"campaign_key": "cliente_campanha", "client": "Cliente", "campaign_name": "Campanha", "sheet_id": "ID", "channel": "canal", "kpi": "CPM"}'
```

---

## 🔄 ROLLBACK

### Reverter Cloud Run
```bash
# Listar revisões
gcloud run revisions list --service=gen-dashboard-ia --region=us-central1 --limit=10

# Reverter para revisão específica
gcloud run services update-traffic gen-dashboard-ia \
  --to-revisions=gen-dashboard-ia-00023-ts9=100 \
  --region=us-central1
```

---

## 📊 MONITORAMENTO

### Ver Logs em Tempo Real
```bash
gcloud run logs tail gen-dashboard-ia --region=us-central1
```

### Buscar Erros
```bash
gcloud run logs read gen-dashboard-ia --region=us-central1 --filter="severity=ERROR" --limit=50
```

---

## 🌐 URLs PRINCIPAIS

### Produção
- 🏠 Home: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/
- 📋 Lista: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list
- 🎯 Gerador: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dash-generator-pro

### Staging
- 🏠 Home: https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/
- 📋 Lista: https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list
- 🎯 Gerador: https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dash-generator-pro

### HML
- 🏠 Home: https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/
- 📋 Lista: https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list
- 🎯 Gerador: https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dash-generator-pro

---

## 📂 CONFIGURAÇÕES DE AMBIENTE

### Datasets BigQuery
- Produção: `south_media_dashboards`
- Staging: `south_media_dashboards_staging`
- HML: `south_media_dashboards_hml`

### Coleções Firestore
- Produção: `campaigns`, `dashboards`
- Staging: `campaigns_staging`, `dashboards_staging`
- HML: `campaigns_hml`, `dashboards_hml`

---

## 🎯 FLUXO DE TRABALHO IDEAL

```
1. Mudança no código/CSV
   ↓
2. Deploy em STAGING
   ↓
3. Testes em STAGING
   ↓
4. Se OK → Deploy em PRODUÇÃO
   ↓
5. Validação em PRODUÇÃO
```

---

## ⚠️ PROBLEMAS COMUNS E SOLUÇÕES RÁPIDAS

| Problema | Solução Rápida |
|----------|---------------|
| Dashboard com "N/A" | `python3 fix_production_metadata.py` |
| Listagem mostra número errado | Verificar tráfego Cloud Run |
| Dashboard não carrega | Regenerar via API |
| Filtros não funcionam | Verificar template correto (CPV vs CPM) |
| Persistência indisponível | Verificar service account permissions |

---

## 📞 EM CASO DE DÚVIDA

1. Consultar `GUIA_DEFINITIVO_DEPLOY.md` (documentação completa)
2. Verificar logs do Cloud Run
3. Testar em staging primeiro
4. Fazer backup antes de mudanças grandes

---

**🎉 Sistema estável com 31 dashboards em 3 ambientes!**

