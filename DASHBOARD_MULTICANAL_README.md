# Dashboard Multicanal - Spotify + Programática

## 📋 Visão Geral

Dashboard desenvolvido para monitorar campanhas multicanal combinando **Spotify** (áudio) e **Programática** (vídeo) com objetivo de otimizar performance e ROI.

## 🎯 Campanhas Monitoradas

### 🎵 Spotify - Escuta Completa
- **Período:** 02/09 - 11/09
- **Objetivo:** Escuta Completa
- **Impressões Contratadas:** 52.083
- **Valor Contratado:** R$ 6.249,96
- **Planilha:** [Link da Planilha Spotify](https://docs.google.com/spreadsheets/d/1-rSt7tYoZFdEiGEBM3GIVt928-8OugHa5sPF2XguYp0/edit?gid=1604556822#gid=1604556822)

### 📺 Programática - Complete View
- **Período:** 02/09 - 11/09
- **Objetivo:** Complete View
- **Impressões Contratadas:** 98.913
- **Valor Contratado:** R$ 22.749,99
- **CPV Contratado:** R$ 0,23
- **Planilha:** [Link da Planilha Programática](https://docs.google.com/spreadsheets/d/1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M/edit?gid=1791112204#gid=1791112204)

## 🌐 Sites Premium

Lista de portais selecionados para a campanha programática:
[Lista de Sites](https://docs.google.com/spreadsheets/d/1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M/edit?gid=409983185#gid=409983185)

## 📊 Funcionalidades do Dashboard

### 1. 📊 Visão Geral
- Métricas consolidadas de ambos os canais
- Performance comparativa
- Evolução diária das campanhas
- Tabela de comparação de canais

### 2. 🧭 Por Canal
- **Spotify:** Métricas específicas de áudio (CPE, Taxa de Escuta Completa)
- **Programática:** Métricas de vídeo (CPV, CTR, VTR100)
- Visualização individual de cada canal
- Lista de sites premium utilizados

### 3. 📈 Análise & Insights
- Gráfico de eficiência (CPC vs Taxa de Conversão)
- Pacing da campanha (Utilizado vs Contratado)
- Insights automáticos baseados nos dados
- Recomendações de otimização

### 4. 📋 Planejamento
- **DoubleVerify - Verificação da Entrega:**
  - Empreendedores
  - Interesse em Empreendedorismo
- Métricas de verificação (Viewability, Brand Safety)
- Lista completa de sites premium

## 🚀 Como Usar

### Acesso Rápido
```bash
# Abrir dashboard no navegador
open static/dash_multicanal_spotify_programatica.html
```

### Atualização de Dados
```bash
# Atualizar dados das planilhas (requer credenciais Google Sheets)
python3 update_multicanal_data.py

# Ou usar integração completa
python3 integrate_multicanal_dashboard.py
```

## 🔧 Configuração

### Google Sheets (Opcional)
Para dados em tempo real das planilhas:

1. **Configurar credenciais:**
   ```bash
   # Baixar credentials.json do Google Cloud Console
   # Executar autenticação
   python3 -c "from google_sheets_service import GoogleSheetsService; GoogleSheetsService()"
   ```

2. **Testar conexão:**
   ```bash
   python3 -c "from google_sheets_service import GoogleSheetsService; print(GoogleSheetsService().test_connection())"
   ```

### Dados Simulados
Se não houver credenciais configuradas, o dashboard usa dados simulados baseados nas metas contratadas.

## 📁 Arquivos do Dashboard

```
static/
├── dash_multicanal_spotify_programatica.html  # Dashboard principal
├── integrate_multicanal_dashboard.py          # Integração com planilhas
├── update_multicanal_data.py                  # Script de atualização
└── DASHBOARD_MULTICANAL_README.md            # Esta documentação
```

## 🎨 Características Técnicas

- **Framework:** HTML5 + CSS3 + JavaScript (Vanilla)
- **Gráficos:** Chart.js
- **Design:** Dark theme com gradientes
- **Responsivo:** Adaptável a diferentes telas
- **Integração:** Google Sheets API
- **Dados:** JSON dinâmico

## 📈 Métricas Principais

### Spotify
- **CPE (Custo por Escuta):** R$ 0,46
- **Taxa de Escuta Completa:** 27,8%
- **Impressões:** 45.000
- **Escutas Completas:** 12.500

### Programática
- **CPV (Custo por Visualização):** R$ 1,14
- **CTR (Click Through Rate):** 2,47%
- **VTR100 (View Through Rate 100%):** 21,8%
- **Impressões:** 85.000
- **Visualizações 100%:** 18.500

## 🔄 Atualizações

O dashboard é atualizado automaticamente quando:
- Novos dados são carregados das planilhas
- O script de integração é executado
- Dados simulados são recalculados

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verificar se as planilhas estão acessíveis
2. Confirmar configuração do Google Sheets
3. Executar scripts de diagnóstico
4. Consultar logs de erro

---

**Desenvolvido para:** Campanha Multicanal Spotify + Programática  
**Período:** 02/09 - 11/09  
**Status:** ✅ Funcional
