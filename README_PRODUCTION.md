# 🚀 MVP Dashboard Builder - Ambiente de Produção

[![Status](https://img.shields.io/badge/Status-Produção-brightgreen)](https://mvp-dashboard-builder-609095880025.us-central1.run.app/health)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-mvp--dashboard--builder-blue)](https://console.cloud.google.com/run/detail/us-central1/mvp-dashboard-builder)
[![Vercel](https://img.shields.io/badge/Vercel-dash.iasouth.tech-black)](https://dash.iasouth.tech)

## 🎯 Visão Geral

Sistema de geração automática de dashboards para campanhas de marketing digital, totalmente funcional em ambiente de produção.

## 🌐 Acesso Rápido

| Serviço | URL | Status |
|---------|-----|--------|
| **Dashboard Builder** | https://mvp-dashboard-builder-609095880025.us-central1.run.app | ✅ |
| **Git Manager** | https://git-manager-improved-609095880025.us-central1.run.app | ✅ |
| **Frontend** | https://dash.iasouth.tech | ✅ |
| **Gerador** | https://mvp-dashboard-builder-609095880025.us-central1.run.app/dash-generator-pro | ✅ |

## 📊 Estatísticas de Produção

- **52+ Dashboards** gerados e funcionais
- **15+ Clientes** atendidos
- **8 Canais** suportados (YouTube, LinkedIn, Netflix, etc.)
- **4 KPIs** disponíveis (CPV, CPM, CPC, CPA)
- **100% Uptime** desde deploy

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Cloud Run      │    │   Google Cloud  │
│   Frontend      │◄──►│   Dashboard      │◄──►│   Storage       │
│   dash.iasouth  │    │   Builder        │    │   Credentials   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Git Manager    │
                       │   (Microservice) │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   GitHub         │
                       │   Repository     │
                       └──────────────────┘
```

## 🚀 Como Usar

### 1. Gerar Novo Dashboard
1. Acesse: https://mvp-dashboard-builder-609095880025.us-central1.run.app/dash-generator-pro
2. Preencha os dados da campanha
3. Selecione canal e KPI
4. Clique em "Gerar Dashboard"
5. Aguarde o processamento automático

### 2. Acessar Dashboard Existente
- **Via Vercel**: https://dash.iasouth.tech/static/{nome_do_dashboard}
- **Via Cloud Run**: https://mvp-dashboard-builder-609095880025.us-central1.run.app/static/{nome_do_dashboard}

### 3. API de Dados
```bash
curl "https://mvp-dashboard-builder-609095880025.us-central1.run.app/api/{campaign_key}/data"
```

## 📋 Dashboards Disponíveis

### Copacol (21 dashboards)
- YouTube (30s, 90s, Remarketing)
- Netflix (30s, Institucional)
- Video Programático (Remarketing)
- Semana do Pescado

### Sebrae (6 dashboards)
- Feira do Empreendedor (Spotify, Programática)
- Netflix (Sebrae PR)
- Institucional Setembro

### SENAI (6 dashboards)
- LinkedIn (Sponsored Video, Display)
- Native (PGR, Testes)

### SESI (5 dashboards)
- LinkedIn (NR1, PGR)
- Native (NR1, PGR, Institucional)

### Outros (14 dashboards)
- Unimed, Iquine, Dauher, Unicesusc, etc.

## 🔧 Manutenção

### Health Checks
```bash
# Dashboard Builder
curl https://mvp-dashboard-builder-609095880025.us-central1.run.app/health

# Git Manager
curl https://git-manager-improved-609095880025.us-central1.run.app/health
```

### Logs
```bash
# Logs do Dashboard Builder
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mvp-dashboard-builder" --limit=20

# Logs do Git Manager
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=git-manager-improved" --limit=20
```

### Backup
```bash
# Download do backup mais recente
gsutil cp gs://south-media-backups/20250927_141850.tar.gz .

# Extrair backup
tar -xzf 20250927_141850.tar.gz
```

## 📚 Documentação

- **[Ambiente de Produção](PRODUCTION_ENVIRONMENT.md)** - Documentação completa
- **[Especificações Técnicas](TECHNICAL_SPECIFICATIONS.md)** - Detalhes técnicos
- **[Backup Info](backup/BUCKET_INFO.txt)** - Informações do backup

## 🆘 Suporte

### Problemas Comuns

#### Dashboard não carrega dados
```bash
# Verificar API
curl "https://mvp-dashboard-builder-609095880025.us-central1.run.app/api/{campaign_key}/data"

# Verificar logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mvp-dashboard-builder AND severity>=ERROR" --limit=5
```

#### Erro de credenciais Google Sheets
```bash
# Verificar arquivo no bucket
gsutil ls gs://south-media-credentials/
gsutil cat gs://south-media-credentials/service-account-key.json | head -5
```

#### Dashboard não atualiza no Vercel
```bash
# Verificar Git Manager
curl https://git-manager-improved-609095880025.us-central1.run.app/health

# Verificar logs de commit
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=git-manager-improved" --limit=10
```

## 📞 Contatos

- **Projeto**: `automatizar-452311`
- **Região**: `us-central1`
- **Service Account**: `southmedia@automatizar-452311.iam.gserviceaccount.com`

---

**Última atualização**: 27/09/2025  
**Versão**: 1.0.0  
**Status**: ✅ Produção Operacional
