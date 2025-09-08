# 🚀 Sistema de Atualização Dinâmica do Dashboard

## 📋 Visão Geral

O sistema de atualização dinâmica permite que os dados do dashboard sejam atualizados automaticamente sem necessidade de recarregar a página. Os dados são processados em tempo real a partir do Google Sheets e sincronizados com o frontend.

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Google Sheets  │───▶│   Backend API   │───▶│   Frontend      │
│   (6 canais)    │    │   /api/dashboard│    │   Auto-refresh  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Componentes

### 1. **Backend API** (`/backend/src/routes/dashboard.py`)
- **Endpoint**: `/api/dashboard/data`
- **Função**: Processa dados do Google Sheets e retorna dados estruturados
- **Frequência**: Sob demanda (quando solicitado pelo frontend)

### 2. **Google Sheets Service** (`/backend/src/services/sheets_service.py`)
- **Função**: Conecta e processa dados do Google Sheets
- **Canais**: CTV, Disney, Footfall Display, Netflix, TikTok, YouTube
- **Recursos**: Processamento específico por canal, fallback para dados mock

### 3. **Frontend Updater** (`/static/dashboard-updater.js`)
- **Função**: Faz requisições automáticas para a API
- **Frequência**: A cada 5 minutos
- **Recursos**: Retry automático, notificações visuais, controle manual

### 4. **Google Sheets** (6 planilhas)
- **Estrutura**: Uma planilha por canal com aba "Entrega Diária"
- **Dados**: Entrega diária, métricas específicas por canal

## 🚀 Como Usar

### 1. **Iniciar o Sistema**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd static
python3 -m http.server 8080
```

### 2. **Atualizar Dados**

#### Opção A: Substituir Arquivos TSV
```bash
# Substitua os arquivos em /static/tsv/
# O sistema detectará automaticamente na próxima sincronização
```

#### Opção B: Usar API Diretamente
```bash
# Testar API
python update-dashboard-example.py test

# Monitorar atualizações
python update-dashboard-example.py monitor
```

### 3. **Controles no Dashboard**

- **🔄 Botão de Refresh**: Atualização manual
- **🟢 Indicador Verde**: Sistema funcionando
- **🟠 Indicador Laranja**: Atualizando
- **🔴 Indicador Vermelho**: Erro

## 📊 Estrutura de Dados

### Dados Consolidados (CONS)
```json
{
  "Budget Contratado (R$)": 109481.25,
  "Budget Utilizado (R$)": 29008.23,
  "Impressões": 658113.0,
  "Cliques": 16593.0,
  "CTR (cons.)": 0.025,
  "VC (100%)": 146932.0,
  "VTR (cons.)": 0.223,
  "CPM (R$) cons.": 44.08,
  "CPV (R$) cons.": 0.197
}
```

### Dados por Canal (PER)
```json
[
  {
    "Canal": "CTV",
    "Budget Contratado (R$)": 11895.55,
    "Budget Utilizado (R$)": 2943.6,
    "VC (100%)": 14718.0,
    "VTR (100%)": 0.8329,
    "CPV (R$)": 0.2,
    "Pacing (%)": 0.247
  }
]
```

### Dados Diários (DAILY)
```json
[
  {
    "date": "01/09/2025",
    "channel": "CTV",
    "creative": "Sonho 15s",
    "spend": 171.8,
    "starts": 891.0,
    "q25": 889.0,
    "q50": 871.0,
    "q75": 864.0,
    "q100": 859.0
  }
]
```

## ⚙️ Configurações

### Frontend (`dashboard-updater.js`)
```javascript
// Intervalos de atualização
this.updateInterval = 5 * 60 * 1000;  // 5 minutos
this.retryInterval = 30 * 1000;       // 30 segundos
this.maxRetries = 3;                  // 3 tentativas
```

### Backend (`dashboard.py`)
```python
# Caminho dos arquivos TSV
tsv_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv"
```

## 🔍 Monitoramento

### 1. **Logs do Backend**
```bash
# Ver logs em tempo real
tail -f backend/logs/app.log
```

### 2. **Console do Browser**
```javascript
// Verificar status do updater
console.log(window.dashboardUpdater);

// Forçar atualização
window.dashboardUpdater.forceUpdate();

// Pausar auto-update
window.dashboardUpdater.pause();

// Retomar auto-update
window.dashboardUpdater.resume();
```

### 3. **API Health Check**
```bash
curl http://localhost:8000/api/dashboard/health
```

## 🐛 Troubleshooting

### Problema: Dados não atualizam
**Solução:**
1. Verificar se backend está rodando
2. Verificar console do browser para erros
3. Testar API manualmente: `python update-dashboard-example.py test`

### Problema: Erro de CORS
**Solução:**
1. Verificar configuração CORS no backend
2. Usar URLs corretas (localhost:8000 para API, localhost:8080 para frontend)

### Problema: Arquivos TSV não são processados
**Solução:**
1. Verificar formato dos arquivos TSV
2. Verificar encoding (UTF-8)
3. Verificar estrutura das colunas

## 📈 Próximos Passos

### Melhorias Futuras
1. **WebSocket**: Atualizações em tempo real
2. **Cache Redis**: Melhor performance
3. **Validação de Dados**: Verificação automática
4. **Histórico**: Versionamento de dados
5. **Alertas**: Notificações por email/Slack

### Integrações
1. **Google Sheets**: Sincronização automática
2. **APIs Externas**: Facebook, Google Ads, TikTok
3. **Webhooks**: Atualizações push
4. **Scheduler**: Atualizações agendadas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Testar endpoints da API
3. Consultar este README
4. Verificar configurações de rede

## 🔧 Configuração do Google Sheets

### 1. **Criar Credenciais:**
```bash
# 1. Acesse: https://console.cloud.google.com/
# 2. Crie um projeto ou selecione existente
# 3. Ative a Google Sheets API
# 4. Crie uma Service Account
# 5. Baixe o arquivo JSON de credenciais
# 6. Renomeie para 'credentials.json' e coloque em backend/
```

### 2. **Configurar Planilhas:**
```bash
# 1. Compartilhe suas planilhas com o email da Service Account
# 2. Cada canal deve ter uma planilha com aba "Entrega Diária"
# 3. Configure as variáveis de ambiente com os IDs das planilhas
```

### 3. **Configurar Variáveis:**
```bash
# 1. Copie o arquivo de configuração real
cp backend/sheets_config_real.env backend/.env

# 2. Os IDs das planilhas reais já estão configurados:
# CTV: 1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U
# Disney: 1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o
# Footfall: 10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA
# Netflix: 1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo
# TikTok: 1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM
# YouTube: 1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo
```

### 4. **Testar Integração:**
```bash
# Testar planilhas reais
python3 test_real_sheets.py

# Ver instruções detalhadas
python3 test_real_sheets.py setup

# Ver resumo das planilhas
python3 test_real_sheets.py summary
```

### 5. **Estrutura das Planilhas:**
```
📊 Estrutura esperada:
├── Coluna A: Data
├── Coluna B: Creative
├── Coluna C: Spend/Investimento
├── Colunas D-G: Métricas específicas por canal
│   ├── CTV/Disney/Netflix: Starts, Q25, Q50, Q75, Q100
│   ├── Footfall Display: Impressions, Clicks
│   └── TikTok/YouTube: Impressions, Clicks
```

---

**🎯 Objetivo**: Manter o dashboard sempre atualizado com os dados mais recentes do Google Sheets, proporcionando uma experiência fluida e em tempo real para os usuários.
