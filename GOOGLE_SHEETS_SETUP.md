# 📊 Configuração das Planilhas Google Sheets

## 🎯 Planilhas Configuradas

### **📺 CTV**
- **ID**: `1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U`
- **URL**: https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit
- **Aba**: Entrega Diária
- **Estrutura**: Data, Creative, Starts, Skips, Q25, Q50, Q75, Q100, Active Views, Valor investido

### **🎬 Disney**
- **ID**: `1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o`
- **URL**: https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit
- **Aba**: Entrega Diária
- **Estrutura**: Day, Completion Rate, Q25, Q50, Q75, Q100, Starts, Valor investido, Criativo

### **🖼️ Footfall Display**
- **ID**: `10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA`
- **URL**: https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064
- **Aba**: Entrega Diária
- **GID**: 1743413064
- **Estrutura**: Date, Creative, Impressions, Clicks, CTR, VALOR DO INVESTIMENTO, CPM

### **🎬 Netflix**
- **ID**: `1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo`
- **URL**: https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit
- **Aba**: Entrega Diária
- **Estrutura**: Day, Completion Rate, Q25, Q50, Q75, Q100, Starts, Valor investido, Criativo

### **📱 TikTok**
- **ID**: `1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM`
- **URL**: https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true
- **Aba**: Entrega Diária
- **Estrutura**: Ad name, By Day, Valor Investido, CPC, CPM, Impressions, Clicks, CTR

### **📺 YouTube**
- **ID**: `1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo`
- **URL**: https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182
- **Aba**: Entrega Diária
- **GID**: 1863167182
- **Estrutura**: Date, Starts, Q25, Q50, Q75, Q100, Active Views, criativo, Valor investido

---

## 🔧 Configuração do Sistema

### **1. Variáveis de Ambiente**
```bash
# Copiar configuração
cp backend/sheets_config_real.env backend/.env

# IDs já configurados:
FOOTFALL_DISPLAY_SPREADSHEET_ID=10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA
DISNEY_SPREADSHEET_ID=1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o
CTV_SPREADSHEET_ID=1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U
NETFLIX_SPREADSHEET_ID=1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo
TIKTOK_SPREADSHEET_ID=1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM
YOUTUBE_SPREADSHEET_ID=1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo
```

### **2. Credenciais Google**
```bash
# Arquivo necessário: backend/credentials.json
# Obter em: https://console.cloud.google.com/
# Service Account com acesso às planilhas
```

### **3. Permissões**
- Compartilhar todas as planilhas com o email da Service Account
- Dar permissão de "Editor" ou "Visualizador"
- Verificar se a aba "Entrega Diária" existe em cada planilha

---

## 🧪 Testes

### **Testar Conexão**
```bash
python3 test_real_sheets.py
```

### **Ver Instruções**
```bash
python3 test_real_sheets.py setup
```

### **Ver Resumo**
```bash
python3 test_real_sheets.py summary
```

---

## 📊 Estrutura de Dados por Canal

### **Canais de Vídeo** (CTV, Disney, Netflix, YouTube)
- **Métricas**: starts, q25, q50, q75, q100
- **Dados**: Data, Creative, Spend, Video Metrics

### **Canais de Display** (Footfall Display)
- **Métricas**: impressions, clicks
- **Dados**: Data, Creative, Spend, Display Metrics

### **Canais Sociais** (TikTok)
- **Métricas**: impressions, clicks
- **Dados**: Data, Creative, Spend, Social Metrics

---

## 🚀 Próximos Passos

1. **Configurar credenciais** Google Sheets
2. **Compartilhar planilhas** com Service Account
3. **Testar conexões** com `test_real_sheets.py`
4. **Iniciar sistema** com dados reais
5. **Monitorar atualizações** automáticas

---

## 📞 Suporte

Para problemas:
1. Verificar credenciais em `backend/credentials.json`
2. Confirmar permissões das planilhas
3. Testar conexões individuais
4. Verificar logs do sistema
