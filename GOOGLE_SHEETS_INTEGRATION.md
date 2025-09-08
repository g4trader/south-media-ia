# Integração com Google Sheets - Dashboard Multicanal

## 📊 Visão Geral

O dashboard React agora está integrado com as planilhas do Google Sheets para exibir dados reais de campanhas multicanal. A integração inclui dados de todos os canais: CTV, YouTube, TikTok, Disney, Netflix e Footfall Display.

## 🔗 URLs das Planilhas

### Canais de Vídeo
- **CTV**: https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit
- **YouTube**: https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182
- **TikTok**: https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true
- **Disney**: https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit
- **Netflix**: https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit

### Canais de Display
- **Footfall Display**: https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064

## 🏗️ Arquitetura da Integração

### 1. Backend (API)
- **Endpoint**: `/api/dashboard/data`
- **Serviço**: `SheetsService` em `backend/src/services/sheets_service.py`
- **Autenticação**: Google Service Account
- **Processamento**: Mapeamento específico por canal

### 2. Frontend (React)
- **Componente**: `MulticanalDashboard.js`
- **Dados**: `mockSheetsData.js` (fallback)
- **Auto-refresh**: A cada 5 minutos
- **Status**: Indicadores visuais de fonte dos dados

## 📋 Estrutura dos Dados

### Dados Contratados (CONS)
```javascript
{
  "Budget Contratado (R$)": 500000,
  "Budget Utilizado (R$)": 125000,
  "Impressões": 25000000,
  "Cliques": 125000,
  "Visitas (Footfall)": 8500
}
```

### Dados por Canal (PER)
```javascript
[
  {
    "Canal": "CTV",
    "Budget Contratado (R$)": 120000,
    "Budget Utilizado (R$)": 30000,
    "Impressões": 6000000,
    "Cliques": 30000,
    "CTR": 0.5,
    "VC (100%)": 0.85,
    "VTR (100%)": 0.83,
    "CPV (R$)": 1.0
  }
  // ... outros canais
]
```

### Dados Diários (DAILY)
```javascript
[
  {
    "Canal": "CTV",
    "Data": "2024-01-15",
    "Criativo": "CTV_001",
    "Investimento (R$)": 1500,
    "Starts": 7500,
    "25%": 6000,
    "50%": 4500,
    "75%": 3000,
    "100%": 1500,
    "Impressões": 150000,
    "Cliques": 750
  }
  // ... outros registros diários
]
```

## 🔄 Fluxo de Dados

1. **Carregamento Inicial**
   - Frontend tenta buscar dados da API
   - Se API indisponível, usa dados mock
   - Exibe indicador de status

2. **Atualização Automática**
   - Auto-refresh a cada 5 minutos
   - Mantém dados sempre atualizados

3. **Atualização Manual**
   - Botão "🔄 Atualizar Dados" no header
   - Força nova busca na API

## 🎯 Mapeamento por Canal

### CTV
- **Métricas**: VTR, CPV, VC, Starts, Q25, Q50, Q75, Q100
- **Publishers**: Lista específica de publishers CTV

### YouTube
- **Métricas**: VTR, CPV, VC, Starts, Q25, Q50, Q75, Q100
- **GID**: 1863167182

### TikTok
- **Métricas**: VTR, CPV, VC, CPM, Starts, Q25, Q50, Q75, Q100
- **Tipo**: Canal misto (vídeo + display)

### Disney
- **Métricas**: VTR, CPV, VC, Starts, Q25, Q50, Q75, Q100

### Netflix
- **Métricas**: VTR, CPV, VC, Starts, Q25, Q50, Q75, Q100

### Footfall Display
- **Métricas**: CPM, Impressões, Cliques
- **GID**: 1743413064
- **Sites**: Lista de publishers utilizados

## 🚀 Como Usar

### Acesso ao Dashboard
1. **Via AdminDashboard**: `https://dash.iasouth.tech/admin/dashboard`
2. **Direto**: `https://dash.iasouth.tech/multicanal`
3. **Alias**: `https://dash.iasouth.tech/dash-sonho`

### Funcionalidades
- **Visão Geral**: Métricas consolidadas e gráficos
- **Por Canal**: Análise detalhada por canal
- **Análise & Insights**: Otimizações e recomendações
- **Planejamento**: Estratégia da campanha
- **Footfall**: Relatório específico de conversão

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# IDs das planilhas
CTV_SPREADSHEET_ID=1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U
DISNEY_SPREADSHEET_ID=1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o
FOOTFALL_DISPLAY_SPREADSHEET_ID=10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA
NETFLIX_SPREADSHEET_ID=1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo
TIKTOK_SPREADSHEET_ID=1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM
YOUTUBE_SPREADSHEET_ID=1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo

# URL da API
REACT_APP_API_URL=https://south-media-ia-backend.vercel.app
```

### Credenciais Google Sheets
- **Service Account**: Configurado no backend
- **Permissões**: Leitura das planilhas
- **Arquivo**: `google-credentials.json`

## 📊 Status dos Dados

### Indicadores Visuais
- **✅ Verde**: Dados reais do Google Sheets
- **⚠️ Amarelo**: Dados simulados (API indisponível)
- **🔄 Azul**: Atualizando dados

### Logs do Console
- **✅**: Dados reais carregados
- **⚠️**: Erro na API, usando dados mock
- **📊**: Informações sobre planilhas integradas

## 🔮 Próximos Passos

1. **Deploy do Backend**: Configurar API na Vercel
2. **Credenciais**: Configurar Google Service Account
3. **Testes**: Validar integração com planilhas reais
4. **Otimizações**: Cache e performance
5. **Alertas**: Notificações de mudanças nos dados

## 📞 Suporte

Para dúvidas sobre a integração:
- **Documentação**: Este arquivo
- **Código**: `frontend/src/components/MulticanalDashboard.js`
- **Dados**: `frontend/src/data/mockSheetsData.js`
- **API**: `backend/src/routes/dashboard.py`
