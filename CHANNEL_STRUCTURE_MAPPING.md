# 📊 Mapeamento da Estrutura de Dados por Canal

## 🎯 Visão Geral

Cada canal tem uma estrutura de dados única e específica. Este documento mapeia exatamente como os dados são organizados em cada arquivo TSV de entrega diária.

---

## 📺 **CTV (Connected TV)**

### **Estrutura do Arquivo:**
```
Coluna 1: Data (DD/MM/YYYY)
Coluna 2: Creative
Coluna 3: Starts (Video)
Coluna 4: Skips (Video)
Coluna 5: First-Quartile Views (Video)
Coluna 6: Midpoint Views (Video)
Coluna 7: Third-Quartile Views (Video)
Coluna 8: Complete Views (Video)
Coluna 9: Active View: % Audible and Visible at Start
Coluna 10: Active View: % Play Time Visible
Coluna 11: Active View: % Play Time Audible and Visible
Coluna 12: Valor investido
```

### **Exemplo de Dados:**
```
01/09/2025 | Sonho 15s | 891 | 0 | 889 | 871 | 864 | 859 | 98,389% | 99,861% | 99,012% | 171,8
```

### **Mapeamento para API:**
- `date` → Coluna 1
- `creative` → Coluna 2
- `starts` → Coluna 3
- `q25` → Coluna 5 (First-Quartile)
- `q50` → Coluna 6 (Midpoint)
- `q75` → Coluna 7 (Third-Quartile)
- `q100` → Coluna 8 (Complete Views)
- `spend` → Coluna 12

---

## 🎬 **Disney**

### **Estrutura do Arquivo:**
```
Coluna 1: Day (DD/MM/YYYY)
Coluna 2: Video Completion Rate %
Coluna 3: 25% Video Complete
Coluna 4: 50% Video Complete
Coluna 5: 75% Video Complete
Coluna 6: 100% Complete
Coluna 7: Video Starts
Coluna 8: Valor investido
Coluna 9: Criativo
```

### **Exemplo de Dados:**
```
01/09/2025 | 0,97811 | 861 | 859 | 855 | 845 | 893 | 388,7 | Sonho 30s
```

### **Mapeamento para API:**
- `date` → Coluna 1
- `creative` → Coluna 9
- `starts` → Coluna 7
- `q25` → Coluna 3
- `q50` → Coluna 4
- `q75` → Coluna 5
- `q100` → Coluna 6
- `spend` → Coluna 8

---

## 🎬 **Netflix**

### **Estrutura do Arquivo:**
```
Coluna 1: Day (DD/MM/YYYY)
Coluna 2: Video Completion Rate %
Coluna 3: 25% Video Complete
Coluna 4: 50% Video Complete
Coluna 5: 75% Video Complete
Coluna 6: 100% Complete
Coluna 7: Video Starts
Coluna 8: Valor investido
Coluna 9: Criativo
```

### **Exemplo de Dados:**
```
01/09/2025 | 0,928509 | 367 | 364 | 361 | 357 | 369 | 117,81 | Sonho 30s
```

### **Mapeamento para API:**
- `date` → Coluna 1
- `creative` → Coluna 9
- `starts` → Coluna 7
- `q25` → Coluna 3
- `q50` → Coluna 4
- `q75` → Coluna 5
- `q100` → Coluna 6
- `spend` → Coluna 8

---

## 📱 **TikTok**

### **Estrutura do Arquivo:**
```
Coluna 1: Ad name
Coluna 2: By Day (YYYY-MM-DD)
Coluna 3: Valor Investido
Coluna 4: CPC
Coluna 5: CPM
Coluna 6: Impressions
Coluna 7: Clicks
Coluna 8: CTR
```

### **Exemplo de Dados:**
```
Sonho 15 segundos | 2025-09-02 | R$ 176,52 | 0,062 | R$ 15,20 | 11613 | 11 | 0,095
```

### **Mapeamento para API:**
- `date` → Coluna 2
- `creative` → Coluna 1
- `spend` → Coluna 3 (remover "R$ " e converter)
- `impressions` → Coluna 6
- `clicks` → Coluna 7

---

## 📺 **YouTube**

### **Estrutura do Arquivo:**
```
Coluna 1: Date (YYYY/MM/DD)
Coluna 2: Starts (Video)
Coluna 3: First-Quartile Views (Video)
Coluna 4: Midpoint Views (Video)
Coluna 5: Third-Quartile Views (Video)
Coluna 6: Complete Views (Video)
Coluna 7: Active View: % Audible and Visible at Start
Coluna 8: Active View: % Play Time Visible
Coluna 9: Active View: % Play Time Audible and Visible
Coluna 10: criativo
Coluna 11: Valor investido
```

### **Exemplo de Dados:**
```
2025/09/01 | 2093 | 1831 | 1734 | 1637 | 1563 | 95,762% | 99,863% | 99,808% | shorts | 46,89
```

### **Mapeamento para API:**
- `date` → Coluna 1
- `creative` → Coluna 10
- `starts` → Coluna 2
- `q25` → Coluna 3
- `q50` → Coluna 4
- `q75` → Coluna 5
- `q100` → Coluna 6
- `spend` → Coluna 11

---

## 🖼️ **Footfall Display**

### **Estrutura do Arquivo:**
```
Coluna 1: Date (YYYY/MM/DD)
Coluna 2: Creative
Coluna 3: Impressions
Coluna 4: Clicks
Coluna 5: Click Rate (CTR)
Coluna 6: VALOR DO INVESTIMENTO
Coluna 7: CPM
```

### **Exemplo de Dados:**
```
2025/08/30 | 180x150 -cta 2 | 783 | 12 | 1,533% | R$ 14,88 | R$ 19,00
```

### **Mapeamento para API:**
- `date` → Coluna 1
- `creative` → Coluna 2
- `impressions` → Coluna 3
- `clicks` → Coluna 4
- `spend` → Coluna 6 (remover "R$ " e converter)

---

## 🔧 **Implementação no Código**

### **Função de Mapeamento por Canal:**

```python
def map_channel_data(channel, raw_data):
    """Mapeia dados brutos para estrutura padrão baseado no canal"""
    
    if channel == "CTV":
        return {
            "date": raw_data[0],
            "creative": raw_data[1],
            "starts": safe_float(raw_data[2]),
            "q25": safe_float(raw_data[4]),
            "q50": safe_float(raw_data[5]),
            "q75": safe_float(raw_data[6]),
            "q100": safe_float(raw_data[7]),
            "spend": safe_float(raw_data[11])
        }
    
    elif channel in ["Disney", "Netflix"]:
        return {
            "date": raw_data[0],
            "creative": raw_data[8],
            "starts": safe_float(raw_data[6]),
            "q25": safe_float(raw_data[2]),
            "q50": safe_float(raw_data[3]),
            "q75": safe_float(raw_data[4]),
            "q100": safe_float(raw_data[5]),
            "spend": safe_float(raw_data[7])
        }
    
    elif channel == "TikTok":
        return {
            "date": raw_data[1],
            "creative": raw_data[0],
            "spend": safe_float(raw_data[2].replace("R$ ", "")),
            "impressions": safe_float(raw_data[5]),
            "clicks": safe_float(raw_data[6])
        }
    
    elif channel == "YouTube":
        return {
            "date": raw_data[0],
            "creative": raw_data[9],
            "starts": safe_float(raw_data[1]),
            "q25": safe_float(raw_data[2]),
            "q50": safe_float(raw_data[3]),
            "q75": safe_float(raw_data[4]),
            "q100": safe_float(raw_data[5]),
            "spend": safe_float(raw_data[10])
        }
    
    elif channel == "Footfall Display":
        return {
            "date": raw_data[0],
            "creative": raw_data[1],
            "impressions": safe_float(raw_data[2]),
            "clicks": safe_float(raw_data[3]),
            "spend": safe_float(raw_data[5].replace("R$ ", ""))
        }
```

---

## 📋 **Resumo das Diferenças**

| Canal | Data | Creative | Spend | Métricas Específicas |
|-------|------|----------|-------|---------------------|
| **CTV** | Col 1 | Col 2 | Col 12 | Starts, Q25-Q100, Active View |
| **Disney** | Col 1 | Col 9 | Col 8 | Starts, Q25-Q100, Completion Rate |
| **Netflix** | Col 1 | Col 9 | Col 8 | Starts, Q25-Q100, Completion Rate |
| **TikTok** | Col 2 | Col 1 | Col 3 | Impressions, Clicks, CPC, CPM |
| **YouTube** | Col 1 | Col 10 | Col 11 | Starts, Q25-Q100, Active View |
| **Footfall** | Col 1 | Col 2 | Col 6 | Impressions, Clicks, CTR, CPM |

---

## 🎯 **Próximos Passos**

1. **Atualizar SheetsService** com mapeamento específico por canal
2. **Implementar validação** de estrutura de dados
3. **Criar testes** para cada estrutura de canal
4. **Documentar** formato esperado das planilhas Google Sheets
