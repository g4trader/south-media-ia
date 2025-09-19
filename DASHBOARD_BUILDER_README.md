# 🎯 Dashboard Builder - Sistema de Criação de Dashboards Dinâmicos

## 📋 Visão Geral

O Dashboard Builder é um sistema completo para criação automática de dashboards de campanhas de marketing digital. Permite aos usuários criar dashboards personalizados com base em templates, configurar canais de mídia e automatizar a coleta de dados.

## 🚀 Funcionalidades Implementadas

### ✅ Concluído

1. **Modal de Criação de Dashboard**
   - Interface intuitiva no painel de controle
   - Formulário completo com validação em tempo real
   - Preview da configuração em tempo real

2. **Formulário Completo**
   - Nome da campanha
   - Período de veiculação (data início/fim)
   - Verba total líquida
   - KPI negociado (CPM, CPV, CPC, Lead, Conversão, Alcance, Engajamento)
   - Valor unitário do KPI e meta
   - Estratégias da campanha (texto longo)
   - Seleção de canais de mídia
   - Configuração de planilhas Google Sheets
   - Modelo de relatório (Simples/Multicanal)

3. **Sistema de Canais de Mídia**
   - YouTube, TikTok, Netflix, Disney+, CTV
   - Programática, Footfall Display, Footfall Mapa
   - Configuração individual de planilhas Google Sheets
   - Suporte a GID de abas específicas

4. **API Backend Completa**
   - Endpoints REST para CRUD de dashboards
   - Validação de dados
   - Geração automática de HTML
   - Sistema de status (created, validated, active, completed)

5. **Sistema de Validação**
   - Validação pelo usuário antes da ativação
   - Controle de status dos dashboards
   - Interface de validação intuitiva

6. **Templates de Dashboard**
   - Template Simples (métricas básicas)
   - Template Multicanal (análise completa)
   - Geração dinâmica baseada na configuração

## 🏗️ Arquitetura

### Frontend
- **Modal de Criação**: Interface responsiva com validação em tempo real
- **Preview Dinâmico**: Visualização da configuração conforme preenchimento
- **Sistema de Status**: Botões contextuais baseados no status do dashboard
- **Integração com API**: Comunicação completa com backend

### Backend
- **API REST**: Endpoints para gerenciamento completo
- **Validação de Dados**: Verificação rigorosa de todos os campos
- **Geração de HTML**: Templates dinâmicos baseados na configuração
- **Sistema de Arquivos**: Armazenamento de configurações e dashboards

## 📁 Estrutura de Arquivos

```
south-media-ia/
├── index.html                          # Painel de controle com modal
├── dashboard_builder_api.py            # API backend
├── static/                             # Dashboards gerados
├── campaigns/                          # Configurações de campanhas
└── templates/                          # Templates de dashboard
```

## 🔧 Como Usar

### 1. Iniciar o Sistema

```bash
# Iniciar a API do Dashboard Builder
python dashboard_builder_api.py

# Acessar o painel de controle
# Abrir index.html no navegador
```

### 2. Criar um Novo Dashboard

1. **Acessar o Painel**: Abrir `index.html` no navegador
2. **Clicar em "Criar Dashboard"**: Botão verde no header
3. **Preencher o Formulário**:
   - Nome da campanha
   - Datas de início e fim
   - Orçamento total
   - KPI e metas
   - Estratégias
   - Selecionar canais
   - Configurar planilhas Google Sheets
4. **Visualizar Preview**: Conferir configuração em tempo real
5. **Salvar**: Clicar em "Salvar Dashboard"

### 3. Validar o Dashboard

1. **Visualizar**: Clicar em "Visualizar" no card do dashboard
2. **Conferir**: Verificar se o dashboard está correto
3. **Validar**: Clicar em "Validar" no card
4. **Confirmar**: Dashboard muda para status "validated"

### 4. Ativar a Campanha

1. **Ativar**: Clicar em "Ativar" no dashboard validado
2. **Agendamento**: Sistema configura agendamento automático
3. **Coleta de Dados**: Inicia coleta automática das planilhas

## 🎨 Templates Disponíveis

### Template Simples
- Métricas básicas (investimento, impressões, cliques)
- Gráfico de performance por canal
- Evolução diária
- Progresso do KPI

### Template Multicanal
- Análise completa de todos os canais
- Métricas avançadas (CTR, VTR, CPV, CPM)
- Comparativo entre canais
- Análise de pacing

## 📊 Status dos Dashboards

- **Created**: Dashboard criado, aguardando validação
- **Validated**: Dashboard validado, pronto para ativação
- **Active**: Dashboard ativo, coletando dados automaticamente
- **Completed**: Campanha finalizada

## 🔌 Integração com Google Sheets

### Configuração de Planilhas
- **ID da Planilha**: Identificador único da planilha Google Sheets
- **GID da Aba**: Identificador da aba específica (opcional)
- **Formato de Dados**: Compatível com estrutura existente

### Canais Suportados
- YouTube, TikTok, Netflix, Disney+, CTV
- Programática, Footfall Display, Footfall Mapa
- Extensível para novos canais

## 🚧 Próximos Passos

### Pendente de Implementação

1. **Geração Dinâmica de HTML** (parcialmente implementado)
   - Melhorar templates multicanal
   - Adicionar mais opções de personalização

2. **Agendamento Automático no Google Scheduler**
   - Integração com Google Cloud Scheduler
   - Configuração automática de jobs
   - Gerenciamento de campanhas ativas

3. **Sistema de Gerenciamento de Campanhas**
   - Interface para gerenciar campanhas ativas/inativas
   - Relatórios de status
   - Histórico de execuções

4. **Integração com Google Sheets para Novos Canais**
   - Validação automática de planilhas
   - Mapeamento dinâmico de colunas
   - Suporte a novos formatos

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.11, Flask
- **Templates**: HTML dinâmico com Chart.js
- **Armazenamento**: Sistema de arquivos (JSON)

### Estrutura da API

```python
# Endpoints disponíveis
POST   /api/dashboards              # Criar dashboard
GET    /api/dashboards              # Listar dashboards
GET    /api/dashboards/{id}         # Obter dashboard específico
POST   /api/dashboards/{id}/validate # Validar dashboard
GET    /health                      # Health check
```

### Exemplo de Uso da API

```javascript
// Criar dashboard
const response = await fetch('http://localhost:8081/api/dashboards', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    campaignName: 'Campanha Black Friday 2025',
    startDate: '2025-11-01',
    endDate: '2025-11-30',
    totalBudget: 50000,
    reportModel: 'multichannel',
    kpiType: 'cpm',
    kpiValue: 2.50,
    kpiTarget: 10000,
    strategies: 'Estratégias da campanha...',
    channels: [
      {
        name: 'youtube',
        displayName: '📺 YouTube',
        sheetId: '1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo',
        gid: '1863167182'
      }
    ]
  })
});
```

## 🎉 Resultado

O sistema está funcional e permite:

1. ✅ **Criar dashboards dinâmicos** através de interface intuitiva
2. ✅ **Configurar múltiplos canais** de mídia com planilhas Google Sheets
3. ✅ **Validar dashboards** antes da ativação
4. ✅ **Gerar HTML automaticamente** baseado em templates
5. ✅ **Gerenciar status** das campanhas
6. ✅ **Preview em tempo real** da configuração

O sistema está pronto para uso e pode ser facilmente estendido com as funcionalidades pendentes de agendamento automático e integração completa com Google Scheduler.


