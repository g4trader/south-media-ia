# 📂 ORGANIZAÇÃO DOS SCRIPTS

## ✅ SCRIPTS ESSENCIAIS (Manter)

### Deploy
- `deploy_gen_dashboard_ia.sh` - Deploy produção
- `deploy_stg_gen_dashboard_ia.sh` - Deploy staging
- `deploy_hml_gen_dashboard_ia.sh` - Deploy HML
- `deploy_production_complete.sh` - Deploy completo automatizado

### Manutenção de Produção
- `backup_production_data.py` - Backup completo
- `clean_and_recreate_production.py` - Limpar e recriar produção
- `clean_and_recreate_hml.py` - Limpar e recriar HML
- `automate_dashboard_creation.py` - Criar dashboards via API (staging)

### Verificação
- `check_all_environments.py` - Verificar todos os ambientes

### Correção
- `fix_production_metadata.py` - Corrigir metadados produção
- `fix_remaining_production_dashboards.py` - Correções manuais produção

---

## 🗑️ SCRIPTS TEMPORÁRIOS (Podem ser Removidos)

### Debug e Análise (Usados durante desenvolvimento)
- `debug_dashboards_firestore.py`
- `debug_firestore_check.py`
- `check_production_cleanup.py`
- `compare_csv_with_firestore.py`
- `verify_staging_datasets.py`
- `verify_and_regenerate_dashboards.py`
- `analyze_production_structure.py`

### Limpeza (Já executados, não mais necessários)
- `clean_staging_data.py` (usar automate_dashboard_creation.py)
- `clean_production_data.py` (criado dinamicamente pelo script completo)

### Restauração Antiga (Substituídos)
- `restore_backup_to_staging.py` (usar clean_and_recreate se necessário)

### Correção de Staging (Específicos para staging)
- `fix_dashboard_metadata_from_csv.py`
- `fix_remaining_dashboards.py`

### Recuperação de Dados Antigos (Já executados)
- `recover_lost_dashboards.py`

### Migração (Já executada)
- `migrate_staging_to_production.py`

### Verificação de Datasets (Já executadas)
- `check_bigquery_dashboards.py`
- `check_production_datasets.py`
- `check_all_firestore_collections.py`

---

## 📁 ESTRUTURA RECOMENDADA

```
south-media-ia/
│
├── 📁 core/                           # Código principal
│   ├── cloud_run_mvp.py
│   ├── bigquery_firestore_manager.py
│   ├── real_google_sheets_extractor.py
│   ├── google_sheets_service.py
│   ├── config.py
│   ├── gunicorn.conf.py
│   └── date_normalizer.py
│
├── 📁 static/                         # Templates HTML
│   ├── dash_generic_template.html
│   └── dash_remarketing_cpm_template.html
│
├── 📁 scripts/                        # Scripts de manutenção
│   ├── deploy/
│   │   ├── deploy_gen_dashboard_ia.sh
│   │   ├── deploy_stg_gen_dashboard_ia.sh
│   │   ├── deploy_hml_gen_dashboard_ia.sh
│   │   └── deploy_production_complete.sh
│   │
│   ├── maintenance/
│   │   ├── backup_production_data.py
│   │   ├── clean_and_recreate_production.py
│   │   ├── clean_and_recreate_hml.py
│   │   └── automate_dashboard_creation.py
│   │
│   ├── verification/
│   │   └── check_all_environments.py
│   │
│   └── fixes/
│       ├── fix_production_metadata.py
│       └── fix_remaining_production_dashboards.py
│
├── 📁 docs/                           # Documentação
│   ├── GUIA_DEFINITIVO_DEPLOY.md
│   ├── QUICK_REFERENCE.md
│   ├── DEPLOY_PRODUCTION_README.md
│   ├── CHANGELOG.md
│   └── RESUMO_EXECUTIVO.md
│
├── 📁 data/
│   └── dashboards.csv                 # Lista mestra
│
├── 📁 backups/                        # Backups (gitignored)
│   └── production_backup_*/
│
├── README.md                          # Documentação principal
├── requirements.txt
├── Dockerfile
└── .gitignore
```

---

## 🧹 COMANDO DE LIMPEZA

### Remover Scripts Temporários
```bash
# Criar script de limpeza
cat > cleanup_temp_scripts.sh << 'EOF'
#!/bin/bash
echo "🧹 LIMPANDO SCRIPTS TEMPORÁRIOS"

# Scripts de debug
rm -f debug_*.py
rm -f check_production_cleanup.py
rm -f compare_csv_with_firestore.py
rm -f verify_staging_datasets.py
rm -f verify_and_regenerate_dashboards.py
rm -f analyze_production_structure.py

# Scripts já executados
rm -f clean_staging_data.py
rm -f restore_backup_to_staging.py
rm -f recover_lost_dashboards.py
rm -f migrate_staging_to_production.py
rm -f check_bigquery_dashboards.py
rm -f check_production_datasets.py
rm -f check_all_firestore_collections.py
rm -f fix_dashboard_metadata_from_csv.py
rm -f fix_remaining_dashboards.py

# Scripts de correção de staging (manter versão de produção)
# fix_production_metadata.py - MANTER
# fix_remaining_production_dashboards.py - MANTER

echo "✅ Limpeza concluída!"
echo "📁 Scripts essenciais mantidos"
EOF

chmod +x cleanup_temp_scripts.sh
```

### Executar Limpeza (Opcional)
```bash
./cleanup_temp_scripts.sh
```

**⚠️ ATENÇÃO:** Execute apenas se tiver certeza que não precisará mais dos scripts temporários!

---

## 📝 MANUTENÇÃO DO CSV

### Formato Correto
```csv
cliente,campanha,planilha,canal,kpi
copacol,Nome Campanha,https://docs.google.com/spreadsheets/d/ID,canal,cpm
```

### Validação Antes de Usar
```python
# Script de validação
python3 -c "
import csv
with open('dashboards.csv', 'r') as f:
    reader = csv.DictReader(f)
    dashboards = list(reader)
    keys = [f\"{d['cliente']}_{d['campanha']}\" for d in dashboards]
    duplicates = [k for k in keys if keys.count(k) > 1]
    
    print(f'Total: {len(dashboards)} dashboards')
    print(f'Duplicatas: {len(set(duplicates))}')
    
    if duplicates:
        print('⚠️ DUPLICATAS ENCONTRADAS:')
        for dup in set(duplicates):
            print(f'  - {dup}')
    else:
        print('✅ CSV válido!')
"
```

---

## 🎯 DECISÕES DE ARQUITETURA

### Por que Firestore para Metadados?
- Leituras extremamente rápidas (<50ms)
- Ideal para listagem de dashboards
- Custo baixo para operações frequentes

### Por que BigQuery para Dados?
- Capacidade analítica poderosa
- Escalável para grandes volumes
- Integração com ferramentas de BI

### Por que Dashboards Dinâmicos?
- Manutenção simplificada (1 template, N dashboards)
- Atualizações instantâneas em todos os dashboards
- Não acumula arquivos estáticos

---

## ✅ VALIDAÇÃO FINAL

### Todos os Ambientes Operacionais
- ✅ Produção: 31 dashboards
- ✅ Staging: 31 dashboards  
- ✅ HML: 31 dashboards

### Todas as Funcionalidades Implementadas
- ✅ Filtros de data funcionando
- ✅ Aba "Por Canal" funcionando
- ✅ Listagem de dashboards funcionando
- ✅ Geração via API funcionando
- ✅ Persistência funcionando

### Toda a Documentação Criada
- ✅ Guia definitivo
- ✅ Referência rápida
- ✅ README atualizado
- ✅ Changelog completo
- ✅ Resumo executivo

---

## 🎊 PROJETO CONCLUÍDO COM SUCESSO!

**Status:** ✅ **PRODUÇÃO ESTÁVEL**  
**Dashboards:** 31 por ambiente  
**Ambientes:** 3 funcionais  
**Documentação:** 100% completa  
**Deploy:** Automatizado  

**🚀 Sistema pronto para uso e evolução!**

