# 📊 South Media IA - Sistema de Dashboards

Sistema profissional de geração e visualização de dashboards de campanhas de mídia com análise em tempo real.

## 🎯 Funcionalidades

- ✅ **Geração Dinâmica de Dashboards** via API
- ✅ **Filtros Interativos** (Todos, 30 dias, 7 dias, Hoje)
- ✅ **Análise por Canal** com métricas consolidadas
- ✅ **Persistência Definitiva** (BigQuery + Firestore)
- ✅ **3 Ambientes Isolados** (Produção, Staging, HML)
- ✅ **Templates KPI-Específicos** (CPV e CPM)
- ✅ **Listagem de Dashboards** com busca e filtros
- ✅ **Backup e Rollback** automatizados

## 🌐 Ambientes

| Ambiente | URL | Status | Dashboards |
|----------|-----|--------|------------|
| **Produção** | [gen-dashboard-ia](https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list) | ✅ Ativo | 31 |
| **Staging** | [stg-gen-dashboard-ia](https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list) | ✅ Ativo | 31 |
| **HML** | [hml-gen-dashboard-ia](https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list) | ✅ Ativo | 31 |

## 🚀 Quick Start

### Deploy Completo (Produção)
```bash
./deploy_production_complete.sh
```

### Adicionar Novo Dashboard
```bash
# 1. Adicionar linha no dashboards.csv
# 2. Gerar via API
curl -X POST https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/generate-dashboard \
  -H 'Content-Type: application/json' \
  -d '{"campaign_key": "cliente_campanha", "client": "Cliente", "campaign_name": "Campanha", "sheet_id": "ID_PLANILHA", "channel": "canal", "kpi": "CPM"}'
```

### Verificar Status
```bash
python3 check_all_environments.py
```

## 📚 Documentação

### Guias Principais
- **[GUIA_DEFINITIVO_DEPLOY.md](GUIA_DEFINITIVO_DEPLOY.md)** - Guia completo e detalhado
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Referência rápida de comandos
- **[DEPLOY_PRODUCTION_README.md](DEPLOY_PRODUCTION_README.md)** - Processo de deploy

### Para Deploy
1. **Primeira vez?** → Leia `GUIA_DEFINITIVO_DEPLOY.md`
2. **Deploy rápido?** → Use `QUICK_REFERENCE.md`
3. **Dúvida específica?** → Consulte seção de troubleshooting

## 🏗️ Arquitetura

### Stack Tecnológico
- **Backend:** Python 3.11 + Flask
- **Frontend:** HTML5 + CSS3 + JavaScript (Vanilla)
- **Charts:** Chart.js 3.9.1
- **Data Sources:** Google Sheets API
- **Persistence:** Google BigQuery + Firestore
- **Deploy:** Google Cloud Run (Docker)
- **CI/CD:** Cloud Build

### Estrutura de Dados

**BigQuery:**
- `campaigns` - Dados históricos de campanhas
- `dashboards` - Registro de dashboards criados
- `metrics` - Métricas diárias detalhadas

**Firestore:**
- `campaigns` - Metadados de campanhas (cache rápido)
- `dashboards` - Metadados de dashboards (listagem rápida)

## 📋 Pré-requisitos

### Desenvolvimento Local
```bash
pip install -r requirements.txt
```

### Ferramentas Necessárias
- Python 3.11+
- gcloud CLI
- Docker (para builds locais)
- Google Cloud Project configurado

### Permissões Necessárias
- BigQuery Data Editor
- Firestore User
- Cloud Run Admin
- Storage Object Viewer

## 🔧 Desenvolvimento

### Executar Localmente
```bash
# Definir variáveis de ambiente
export ENVIRONMENT=development
export PROJECT_ID=automatizar-452311
export PORT=8080

# Executar
python3 cloud_run_mvp.py
```

Acesse: http://localhost:8080

### Testar Templates
```bash
# Abrir template no browser
open static/dash_generic_template.html
open static/dash_remarketing_cpm_template.html
```

## 📊 Dashboards Disponíveis

**31 dashboards ativos** cobrindo:
- **7 clientes:** Copacol, SENAI, SESI, SEBRAE PR, Iquine, Unimed, Sonho
- **12 canais:** YouTube, Netflix, LinkedIn, Display, Native, Geofence, Spotify, Pinterest, TikTok, Disney, CTV, Video Programática
- **2 KPIs:** CPV (Cost per View), CPM (Cost per Mille)

Ver lista completa: [dashboards.csv](dashboards.csv)

## 🛠️ Scripts Utilitários

### Manutenção
```bash
backup_production_data.py              # Backup completo
clean_and_recreate_production.py       # Limpar e recriar produção
clean_and_recreate_hml.py              # Limpar e recriar HML
check_all_environments.py              # Verificar todos ambientes
```

### Correção
```bash
fix_production_metadata.py             # Corrigir metadados
fix_remaining_production_dashboards.py # Correções manuais
verify_and_regenerate_dashboards.py    # Verificar e regenerar
```

### Automação
```bash
automate_dashboard_creation.py         # Criar dashboards via API
deploy_production_complete.sh          # Deploy completo automatizado
```

## 🎨 Templates

### CPV Template (`dash_generic_template.html`)
Para campanhas com KPI de **Cost per View**:
- YouTube
- Netflix
- Spotify
- Vídeos programáticos

**Métricas principais:** Views, CPV, CTR, Conversões

---

### CPM Template (`dash_remarketing_cpm_template.html`)
Para campanhas com KPI de **Cost per Mille**:
- Display
- LinkedIn
- Native
- Remarketing

**Métricas principais:** Impressões, CPM, CTR, Cliques

---

**🎯 Ambos os templates incluem:**
- Filtros de data interativos
- Gráficos dinâmicos (Chart.js)
- Aba "Visão Geral"
- Aba "Por Canal"
- Tabelas de entrega diária
- Responsivo e moderno

## 🔐 Segurança

### Dados Sensíveis
- ❌ **Não commitar:** Chaves API, tokens, credenciais
- ✅ **Usar:** Cloud Run environment variables
- ✅ **Usar:** Secret Manager para dados críticos

### Permissões
- Service accounts com least privilege
- Firestore rules configuradas
- BigQuery IAM policies aplicadas

## 📈 Métricas e Monitoramento

### KPIs do Sistema
- **Uptime:** > 99.9%
- **Tempo de Resposta:** < 5s
- **Taxa de Sucesso:** > 95%
- **Dashboards Ativos:** 31

### Monitoramento
```bash
# Logs em tempo real
gcloud run logs tail gen-dashboard-ia --region=us-central1

# Buscar erros
gcloud run logs read gen-dashboard-ia --region=us-central1 --filter="severity=ERROR"
```

## 🤝 Contribuindo

### Workflow de Mudanças
1. Criar feature branch
2. Fazer alterações
3. Testar localmente
4. Deploy em staging
5. Testar em staging
6. Pull request e code review
7. Deploy em produção
8. Validação final

### Padrões de Código
- Python: PEP 8
- JavaScript: ES6+
- Comentários em português
- Logging detalhado

## 📞 Suporte

### Documentação
- 📘 [Guia Definitivo](GUIA_DEFINITIVO_DEPLOY.md) - Documentação completa
- ⚡ [Referência Rápida](QUICK_REFERENCE.md) - Comandos essenciais

### Recursos
- [Console GCP](https://console.cloud.google.com/run?project=automatizar-452311)
- [BigQuery Console](https://console.cloud.google.com/bigquery?project=automatizar-452311)
- [Firestore Console](https://console.cloud.google.com/firestore?project=automatizar-452311)

## 🎉 Status Atual

### ✅ Sistema em Produção
- **31 dashboards ativos**
- **3 ambientes funcionais**
- **Filtros interativos implementados**
- **Persistência definitiva (BigQuery + Firestore)**
- **Backup e rollback prontos**
- **100% documentado**

### 🔄 Última Atualização
- **Data:** 2025-10-11
- **Versão:** 2.0
- **Revisão Cloud Run:** gen-dashboard-ia-00027-qbn
- **Status:** ✅ Estável

---

## 📄 Licença

Propriedade de South Media IA
Todos os direitos reservados.

---

**Desenvolvido com ❤️ para análise profissional de campanhas de mídia**

