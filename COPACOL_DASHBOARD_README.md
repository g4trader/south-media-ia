# Dashboard COPACOL INSTITUCIONAL PROGRAMÁTICA 30s

## Visão Geral

Dashboard criado para monitorar a campanha de vídeo programática da COPACOL, focada em alcance institucional através de sites premium.

## Especificações da Campanha

- **Nome**: COPACOL INSTITUCIONAL PROGRAMÁTICA 30s
- **Canal**: Programática Video
- **Período**: 08/09/2025 a 05/10/2025
- **Valor Contratado**: R$ 46.373,00
- **CPV**: R$ 0,23
- **Impressões Contratadas**: 201.625
- **Estratégia**: Cidades de entrega conforme solicitação do cliente

## Estrutura do Dashboard

### 1. Visão Geral
- Métricas principais da campanha
- Gráficos de investimento e performance
- Tabela resumo com dados contratados vs realizados

### 2. Performance
- Métricas detalhadas de performance
- Tabela de entrega diária com quartis de visualização
- Dados de starts, 25%, 50%, 75%, 100%

### 3. Publishers
- Lista completa de sites premium utilizados
- Categorização por tipo de mídia
- Descrição de cada publisher

### 4. Planejamento
- Objetivo da campanha
- Dados contratados
- Estratégia de execução
- KPIs principais
- Diretrizes de otimização

## Publishers Utilizados

A campanha utiliza uma lista premium de publishers incluindo:

- **Portais de Notícias**: UOL, G1, Terra, R7, Brasil 247
- **Jornais Digitais**: Folha de S.Paulo, Estadão, Valor Econômico
- **Revistas Digitais**: Veja, Exame, InfoMoney, Revista Época, IstoÉ, CartaCapital
- **Portais Especializados**: The Intercept

## KPIs Monitorados

- **VTR (Video Through Rate) 100%**: Taxa de visualização completa
- **CPV (Custo por Visualização)**: Eficiência de custo
- **CTR (Click Through Rate)**: Taxa de cliques
- **Impressões**: Alcance da campanha
- **Pacing**: Percentual de execução do orçamento

## Dados Simulados

Como não foi possível acessar diretamente a planilha Google Sheets, o dashboard foi criado com dados simulados baseados nas especificações contratadas:

- **Pacing**: 27% (simulado)
- **VTR**: 18% (simulado)
- **CTR**: 1.8% (simulado)
- **CPV Realizado**: R$ 0,23 (mantendo o contratado)

## Arquivos

- **Dashboard**: `/static/dash_copacol_institucional_programatica.html`
- **Script de Extração**: `/extract_copacol_data.py`
- **Documentação**: `/COPACOL_DASHBOARD_README.md`

## Como Atualizar com Dados Reais

1. Configure as credenciais do Google Sheets no arquivo `google_sheets_service.py`
2. Execute o script `extract_copacol_data.py`
3. O dashboard será automaticamente atualizado com os dados reais da planilha

## URLs das Planilhas

- **Dados de Entrega**: https://docs.google.com/spreadsheets/d/1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8/edit?gid=1667459933#gid=1667459933
- **Lista de Publishers**: https://docs.google.com/spreadsheets/d/1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8/edit?gid=1065935170#gid=1065935170

## Características Técnicas

- **Framework**: HTML5 + CSS3 + JavaScript vanilla
- **Gráficos**: Chart.js
- **Design**: Interface moderna com tema escuro
- **Responsivo**: Adaptável a diferentes tamanhos de tela
- **Navegação**: Sistema de abas para organização do conteúdo

## Próximos Passos

1. Integrar com dados reais da planilha Google Sheets
2. Implementar atualizações automáticas
3. Adicionar alertas de performance
4. Criar relatórios exportáveis
5. Implementar comparações com campanhas anteriores
