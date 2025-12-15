# Atualização Automática do Dashboard Portal Auto Shopping

## 📋 Problema Identificado

O dashboard estava com dados incompletos porque:

1. **Dados não estavam sendo lidos corretamente** da planilha do Google Sheets
2. **Faltavam registros** - alguns dias não tinham todos os formatos de criativo
3. **Totais incorretos** - os valores consolidados (CONS e PER) não estavam sendo recalculados corretamente
4. **Processo manual** - cada atualização exigia edição manual do arquivo HTML

## ✅ Solução Implementada

Foi criado o script `update_portal_auto_dashboard.py` que:

1. **Lê automaticamente** os dados da planilha do Google Sheets:
   - Aba "Report" (dados diários de entrega)
   - Aba "Footfall" (dados geográficos de footfall)
2. **Processa e valida** todos os dados
3. **Garante completude** - assegura que todos os dias tenham todos os 5 formatos de criativo
4. **Recalcula totais** - atualiza automaticamente os valores consolidados (CONS e PER)
5. **Atualiza o dashboard** - modifica o arquivo HTML com os dados corretos:
   - Array `DAILY` (dados diários)
   - Array `FOOTFALL_POINTS` (dados geográficos)
   - Objeto `CONS` (totais consolidados)
   - Array `PER` (dados por canal)

## 🚀 Como Usar

### Execução Manual

```bash
python update_portal_auto_dashboard.py
```

ou

```bash
python3 update_portal_auto_dashboard.py
```

### O que o script faz:

1. Conecta ao Google Sheets usando as credenciais configuradas
2. Lê os dados da aba "Report" da planilha (dados diários)
3. Lê os dados da aba "Footfall" da planilha (dados geográficos)
4. Processa e valida os dados de ambas as abas
5. Garante que todos os dias tenham todos os formatos de criativo
6. Calcula os totais (impressões, cliques, investimento, CTR, pacing)
7. Atualiza o arquivo `static/dash_portal_auto_shopping_carbank_dezembro_footfall.html`:
   - Array `DAILY` com dados diários
   - Array `FOOTFALL_POINTS` com dados geográficos
   - Objeto `CONS` com totais consolidados
   - Array `PER` com dados por canal

### Exemplo de Saída:

```
======================================================================
🔄 ATUALIZANDO DASHBOARD PORTAL AUTO SHOPPING - CARBANK DEZEMBRO
======================================================================

📊 Conectando ao Google Sheets...
📋 Lendo dados da planilha 10AKOXuxx5vC2BlZ3tp1CxTlcIlxIj2-G8av0ramCOeg, aba 'Report'...
✅ Encontrados 35 registros na planilha

📊 Processando dados da aba Report...
✅ Processados dados de 7 dias

🗺️  Processando dados da aba Footfall...
📋 Lendo dados da planilha 10AKOXuxx5vC2BlZ3tp1CxTlcIlxIj2-G8av0ramCOeg, aba 'Footfall'...
✅ Encontrados 1 registros na aba Footfall
✅ Processados 1 pontos de Footfall

🔧 Garantindo formatos completos...
📝 Gerando array DAILY...
✅ Gerados 35 registros

🧮 Calculando totais...
   Impressões: 22,380
   Cliques: 397
   Investimento: R$ 559.59
   CTR: 1.77%
   Pacing: 18.65%

💾 Atualizando arquivo do dashboard...
✅ Dashboard atualizado com sucesso!

======================================================================
✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!
======================================================================

📅 Distribuição por dia:
   04/12/2025: 5 formatos | 5 com dados | 4,286 imps | 44 clicks | R$ 107.16
   05/12/2025: 5 formatos | 5 com dados | 3,668 imps | 39 clicks | R$ 91.72
   ...
```

## 🔧 Configuração

O script usa as seguintes configurações (definidas no início do arquivo):

```python
SPREADSHEET_ID = "10AKOXuxx5vC2BlZ3tp1CxTlcIlxIj2-G8av0ramCOeg"
REPORT_SHEET_NAME = "Report"
FOOTFALL_SHEET_NAME = "Footfall"
FOOTFALL_GID = 1714301106  # GID da aba Footfall
DASHBOARD_PATH = Path("static/dash_portal_auto_shopping_carbank_dezembro_footfall.html")
BUDGET_CONTRATADO = 3000.0
CPM_CONTRATADO = 25.0
```

### Formatos de Criativo Esperados

O script garante que todos os dias tenham estes 5 formatos:

1. `20251201_ly_Drive-To-Store-360x300_A.png`
2. `20251201_ly_Drive-To-Store_300x250px_A.png`
3. `20251201_ly_Drive-To-Store_300x50px_A.png`
4. `20251201_ly_Drive-To-Store_320x480px_A.png`
5. `20251201_ly_Drive-To-Store_336x336px_A.png`

Se algum formato não tiver dados em um dia, será criado um registro com valores zero.

## 📊 Estrutura dos Dados

### Dados da Planilha

#### Aba "Report" (dados diários)

O script espera os seguintes dados na aba "Report":

- **Coluna A**: Data (formato: YYYY-MM-DD)
- **Coluna B**: Nome do criativo
- **Coluna C**: Impressões
- **Coluna D**: Cliques
- **Coluna E**: CPC (não usado)
- **Coluna F**: CTR % (não usado)
- **Coluna G**: Valor investido (formato: R$ XX,XX)
- **Coluna H**: CPM (não usado)

#### Aba "Footfall" (dados geográficos)

O script espera os seguintes dados na aba "Footfall":

- **Coluna A**: Latitude (formato: decimal, ex: -19.9077882899644)
- **Coluna B**: Longitude (formato: decimal, ex: -43.9592569000019)
- **Coluna C**: Nome do local (endereço completo)
- **Coluna D**: Número de usuários (inteiro)
- **Coluna E**: Taxa/Rate (decimal, opcional)

### Dados Atualizados no Dashboard

O script atualiza quatro estruturas JavaScript no arquivo HTML:

1. **`DAILY`**: Array com todos os registros diários de entrega
2. **`FOOTFALL_POINTS`**: Array com dados geográficos de footfall (lat, lon, name, users, rate)
3. **`CONS`**: Objeto com totais consolidados
4. **`PER`**: Array com dados por canal (Footfall Display)

## 🔄 Automação Futura

Para automatizar a atualização quando a planilha for modificada, você pode:

1. **Cron Job** (Linux/Mac):
   ```bash
   # Executar a cada hora
   0 * * * * cd /caminho/para/projeto && python3 update_portal_auto_dashboard.py
   ```

2. **Google Apps Script**: Criar um trigger que executa quando a planilha é modificada

3. **Webhook**: Configurar um webhook do Google Sheets para chamar uma API que executa o script

## ⚠️ Requisitos

- Python 3.7+
- Credenciais do Google Sheets configuradas (arquivo `credentials.json` ou variáveis de ambiente)
- Biblioteca `google_sheets_service` disponível no projeto
- Biblioteca `pandas` instalada

## 🐛 Troubleshooting

### Erro: "Serviço do Google Sheets não configurado"

Verifique se:
- O arquivo `credentials.json` existe no diretório raiz
- As credenciais estão válidas e têm permissão para ler a planilha

### Erro: "Nenhum dado encontrado na planilha"

Verifique se:
- O `SPREADSHEET_ID` está correto
- O nome da aba (`SHEET_NAME`) está correto
- A planilha tem dados nas colunas esperadas

### Erro: "Arquivo do dashboard não encontrado"

Verifique se:
- O caminho `DASHBOARD_PATH` está correto
- O arquivo HTML existe no local especificado

## 📝 Notas

- O script preserva a estrutura do arquivo HTML, apenas atualizando os arrays JavaScript
- Valores zero são mantidos para formatos sem dados (importante para completude)
- Os totais são recalculados automaticamente a cada execução
- O script é idempotente - pode ser executado múltiplas vezes sem problemas

