# 🚀 Estrutura Genérica para Campanhas de Vídeo Programática

## 📋 Visão Geral

Esta estrutura genérica permite criar e gerenciar múltiplas campanhas de vídeo programática de forma centralizada e escalável, substituindo a necessidade de criar arquivos específicos para cada cliente.

## 🏗️ Arquitetura

### 📁 Arquivos Principais

```
📦 Estrutura Genérica
├── 🎯 campaign_config.py          # Configurações centralizadas das campanhas
├── 📊 extract_video_campaign_data.py  # Extrator genérico de dados
├── 🧪 test_video_campaign_data.py     # Gerador de dados de teste
├── 🌐 cloud_run_app.py               # API com endpoints dinâmicos
├── 🎨 static/dash_video_programmatic_template.html  # Template genérico
└── 🧪 test_generic_structure.py      # Testes da estrutura
```

### 🔧 Componentes

#### 1. **CampaignConfig** (`campaign_config.py`)
- Define configurações de cada campanha
- Centraliza informações de planilhas, abas e endpoints
- Valida configurações automaticamente

#### 2. **VideoCampaignDataExtractor** (`extract_video_campaign_data.py`)
- Extrai dados de qualquer planilha Google Sheets
- Processa dados de múltiplas abas automaticamente
- Mapeia colunas de forma padronizada

#### 3. **API Dinâmica** (`cloud_run_app.py`)
- Endpoints automáticos: `/api/{campaign_key}/data`
- Listagem de campanhas: `/api/campaigns`
- Compatibilidade com código antigo

#### 4. **Template Genérico** (`dash_video_programmatic_template.html`)
- Dashboard reutilizável para qualquer campanha
- Carregamento dinâmico baseado em `campaign_key`
- Interface responsiva e moderna

## 🚀 Como Adicionar Nova Campanha

### 1. **Configurar Nova Campanha**

Edite `campaign_config.py` e adicione:

```python
CAMPAIGNS = {
    # ... campanhas existentes ...
    
    "novo_cliente": CampaignConfig(
        client="Novo Cliente",
        campaign="Campanha Exemplo",
        sheet_id="SHEET_ID_DA_PLANILHA",
        tabs={
            "daily_data": "GID_DADOS_DIARIOS",
            "contract": "GID_CONTRATO", 
            "strategies": "GID_ESTRATEGIAS",
            "publishers": "GID_PUBLISHERS"
        }
    ),
}
```

### 2. **Criar Dashboard Personalizado**

Copie o template genérico:

```bash
cp static/dash_video_programmatic_template.html static/dash_novo_cliente_campanha_exemplo.html
```

Edite o HTML para definir o `campaign_key`:

```html
<!-- No final do script -->
document.addEventListener('DOMContentLoaded', function() {
    const campaignKey = 'novo_cliente';  // ← Definir aqui
    initDashboard(campaignKey);
});
```

### 3. **Testar Nova Campanha**

```bash
python3 test_generic_structure.py
```

## 📊 Estrutura de Dados

### **Planilha Google Sheets**
Cada campanha deve ter uma planilha com 4 abas:

1. **Report** (dados diários)
   - Colunas: Day, Creative, Imps, Clicks, CTR %, Video Completion Rate %, etc.

2. **Informações de Contrato**
   - Cliente, Campanha, Canal, Tipo de criativo
   - Investimento, CPV contratado, VC contratados
   - Período de veiculação

3. **Estratégias**
   - Segmentações, Praças, White list

4. **Lista de Publishers**
   - Nome, App/URL

### **API Response**
```json
{
  "success": true,
  "data": {
    "campaign_name": "Cliente - Campanha",
    "dashboard_title": "Dashboard Cliente - Campanha",
    "channel": "Prográmatica",
    "creative_type": "Video",
    "period": "15/09/2025 - 30/09/2025",
    "metrics": { /* métricas calculadas */ },
    "daily_data": [ /* dados diários */ ],
    "contract": { /* dados de contratação */ },
    "strategies": { /* estratégias */ },
    "publishers": [ /* lista de publishers */ ]
  },
  "source": "google_sheets" | "test_data"
}
```

## 🔗 Endpoints da API

### **Listar Campanhas**
```http
GET /api/campaigns
```

### **Dados de Campanha Específica**
```http
GET /api/{campaign_key}/data
```

### **Compatibilidade (SEBRAE)**
```http
GET /api/sebrae/data  # Redireciona para /api/sebrae_pr/data
```

## 🧪 Testes

### **Teste Completo da Estrutura**
```bash
python3 test_generic_structure.py
```

### **Teste de Campanha Específica**
```bash
python3 -c "
from campaign_config import get_campaign_config
from test_video_campaign_data import create_test_data_for_campaign

config = get_campaign_config('sebrae_pr')
data = create_test_data_for_campaign('sebrae_pr')
print('✅ Campanha configurada:', config.client)
print('✅ Dados de teste:', len(data.get('publishers', [])))
"
```

## 🔄 Migração do Código Antigo

### **Arquivos Antigos (podem ser removidos)**
- `extract_sebrae_data.py` → Substituído por `extract_video_campaign_data.py`
- `test_sebrae_dashboard.py` → Substituído por `test_video_campaign_data.py`
- Dashboards específicos → Substituídos por template genérico

### **Compatibilidade Mantida**
- Endpoint `/api/sebrae/data` continua funcionando
- Dashboard SEBRAE atual continua funcionando
- Dados de teste idênticos aos originais

## 📈 Benefícios

### ✅ **Escalabilidade**
- Adicionar nova campanha = 3 linhas de configuração
- Sem duplicação de código
- Manutenção centralizada

### ✅ **Consistência**
- Mesmo padrão para todas as campanhas
- Validação automática de configurações
- Interface padronizada

### ✅ **Flexibilidade**
- Configuração por campanha
- Mapeamento de colunas personalizado
- Templates reutilizáveis

### ✅ **Manutenibilidade**
- Código único para todas as campanhas
- Bugs corrigidos uma vez, aplicados a todos
- Atualizações centralizadas

## 🚀 Próximos Passos

1. **Adicionar novas campanhas** usando a estrutura genérica
2. **Migrar campanhas existentes** para o novo sistema
3. **Expandir funcionalidades** (relatórios, alertas, etc.)
4. **Criar interface de administração** para gerenciar campanhas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do servidor Flask
2. Executar `test_generic_structure.py`
3. Validar configurações em `campaign_config.py`
4. Testar endpoints da API individualmente

---

**🎉 Estrutura genérica implementada com sucesso!**
**📊 Pronta para suportar múltiplas campanhas de forma escalável.**
