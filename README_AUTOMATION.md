# 🤖 AUTOMAÇÃO DO DASHBOARD

Sistema completo de automação que atualiza o dashboard a cada 3 horas usando dados do Google Sheets.

## 📋 VISÃO GERAL

Este sistema automatiza a atualização do dashboard `dash_sonho.html` coletando dados de planilhas do Google Sheets para cada canal:

- **YouTube**
- **TikTok** 
- **Netflix**
- **Disney**
- **CTV**
- **Footfall Display**

### ✨ FUNCIONALIDADES

- 🔄 **Atualização automática** a cada 3 horas
- 📊 **Coleta de dados** de múltiplas planilhas Google Sheets
- 💾 **Backup automático** antes de cada atualização
- 📝 **Logs detalhados** de todas as operações
- 🔍 **Monitoramento** de saúde do sistema
- 📧 **Notificações** por email/webhook (opcional)
- 🧪 **Testes automatizados** de configuração

## 🚀 INSTALAÇÃO E CONFIGURAÇÃO

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciais Google Sheets

#### Passo a passo:

1. **Acesse o Google Cloud Console**
   - Vá para: https://console.cloud.google.com/

2. **Crie um projeto**
   - Clique em "Select a project" > "New Project"
   - Digite um nome (ex: "Dashboard Automation")
   - Clique em "Create"

3. **Habilite a API do Google Sheets**
   - Vá em "APIs & Services" > "Library"
   - Procure por "Google Sheets API"
   - Clique em "Enable"

4. **Crie credenciais OAuth 2.0**
   - Vá em "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth 2.0 Client ID"
   - Escolha "Desktop Application"
   - Digite um nome (ex: "Dashboard Client")
   - Clique em "Create"

5. **Baixe o arquivo de credenciais**
   - Clique no download (ícone de download)
   - Salve como `credentials.json`
   - Coloque na pasta `credentials/`

### 3. Configurar IDs das Planilhas

Execute o script de configuração:

```bash
python setup_automation.py
```

Siga as instruções para inserir os IDs das planilhas de cada canal.

**Como encontrar o ID da planilha:**
1. Abra a planilha no Google Sheets
2. O ID está na URL: `https://docs.google.com/spreadsheets/d/ID_AQUI/edit`
3. Copie apenas a parte do ID

**Exemplo:**
- URL: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
- ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### 4. Verificar Configuração

Execute o teste de configuração:

```bash
python test_automation_setup.py
```

## 🎯 COMO USAR

### Modo Interativo (Recomendado)

```bash
python run_automation.py
```

Menu de opções:
1. **Verificar configuração** - Testa se tudo está configurado
2. **Executar atualização única** - Atualiza o dashboard uma vez
3. **Iniciar automação contínua** - Inicia atualização a cada 3 horas
4. **Executar monitoramento** - Verifica saúde do sistema
5. **Sair**

### Modo Linha de Comando

```bash
# Verificar configuração
python run_automation.py check

# Executar atualização única
python run_automation.py update

# Iniciar automação contínua
python run_automation.py start

# Executar monitoramento
python run_automation.py monitor

# Executar configuração inicial
python run_automation.py setup
```

### Scripts de Inicialização

**Windows:**
```bash
start_automation.bat
```

**Linux/Mac:**
```bash
./start_automation.sh
```

## 📁 ESTRUTURA DE ARQUIVOS

```
south-media-ia/
├── dashboard_automation.py      # Script principal de automação
├── google_sheets_processor.py   # Processador de dados Google Sheets
├── monitoring.py                # Sistema de monitoramento
├── setup_automation.py          # Script de configuração
├── test_automation_setup.py     # Testes de configuração
├── run_automation.py            # Script principal de execução
├── config.py                    # Configurações
├── requirements.txt             # Dependências Python
├── credentials.json             # Credenciais Google (criado após setup)
├── logs/                        # Logs de execução
│   ├── dashboard_automation.log
│   └── dashboard_status.json
├── backups/                     # Backups do dashboard
│   └── dash_sonho_backup_YYYYMMDD_HHMMSS.html
└── credentials/                 # Pasta para credenciais
    └── credentials.json
```

## 📊 DADOS PROCESSADOS

### Estrutura dos Dados

Para cada canal, o sistema processa:

- **Data** (formato DD/MM/AAAA)
- **Criativo** (nome do banner/anúncio)
- **Valor Investido** (em R$)
- **Impressões** (número de visualizações)
- **Cliques** (número de cliques)
- **Visitas** (quando disponível)

### Cálculos Automáticos

- **Dados CONS**: Totais consolidados de todos os canais
- **Dados PER**: Totais por canal individual
- **Pacing**: Percentual de utilização do budget

## 🔍 MONITORAMENTO

### Verificação de Saúde

O sistema monitora:

- ✅ **Última atualização** (não deve passar de 6 horas)
- ✅ **Arquivo do dashboard** (deve existir)
- ✅ **Logs de erro** (detecta problemas)
- ✅ **Conexão Google Sheets** (testa conectividade)

### Logs

Todos os logs são salvos em `logs/dashboard_automation.log`:

- 🔄 Início/fim de atualizações
- 📊 Estatísticas de dados processados
- ❌ Erros e problemas
- ✅ Sucessos e confirmações

### Notificações (Opcional)

Configure no arquivo `config.py`:

```python
NOTIFICATION_CONFIG = {
    "enabled": True,
    "webhook_url": "https://hooks.slack.com/...",  # Webhook Slack
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "seu-email@gmail.com",
        "password": "sua-senha-app",
        "to_email": "destinatario@email.com"
    }
}
```

## 🛠️ MANUTENÇÃO

### Backup Automático

- Backup criado antes de cada atualização
- Salvos em `backups/` com timestamp
- Nome: `dash_sonho_backup_YYYYMMDD_HHMMSS.html`

### Limpeza de Logs

Para limpar logs antigos:

```bash
# Manter apenas últimos 30 dias
find logs/ -name "*.log" -mtime +30 -delete
```

### Atualização de Credenciais

Se as credenciais expirarem:

1. Baixe novo arquivo `credentials.json`
2. Substitua em `credentials/credentials.json`
3. Execute teste: `python test_automation_setup.py`

## 🚨 SOLUÇÃO DE PROBLEMAS

### Erro: "Credentials not found"

```bash
# Verificar se arquivo existe
ls credentials/credentials.json

# Se não existe, refazer configuração
python setup_automation.py
```

### Erro: "Sheet ID not found"

```bash
# Verificar configuração
python test_automation_setup.py

# Reconfigurar IDs das planilhas
python setup_automation.py
```

### Erro: "Permission denied"

1. Verificar se a planilha está compartilhada
2. Adicionar email do serviço como editor
3. Testar acesso manualmente

### Dashboard não atualiza

```bash
# Verificar logs
tail -f logs/dashboard_automation.log

# Executar monitoramento
python run_automation.py monitor

# Testar atualização manual
python run_automation.py update
```

## 📈 PERFORMANCE

### Otimizações Implementadas

- ⚡ **Processamento paralelo** de múltiplas planilhas
- 💾 **Cache de credenciais** (evita re-autenticação)
- 📝 **Logs estruturados** (fácil debug)
- 🔄 **Retry automático** em caso de falhas temporárias

### Recursos Necessários

- **RAM**: Mínimo 512MB
- **CPU**: Qualquer processador moderno
- **Rede**: Conexão estável com internet
- **Armazenamento**: ~100MB para logs e backups

## 🔒 SEGURANÇA

### Boas Práticas

- ✅ **Credenciais isoladas** em pasta separada
- ✅ **Logs sem dados sensíveis**
- ✅ **Backups locais** (não enviam dados externos)
- ✅ **Permissões mínimas** no Google Sheets

### Recomendações

- Use conta de serviço específica para automação
- Configure 2FA na conta Google
- Monitore logs regularmente
- Mantenha backups em local seguro

## 📞 SUPORTE

### Logs Úteis para Debug

```bash
# Últimas 50 linhas de log
tail -50 logs/dashboard_automation.log

# Erros apenas
grep "ERROR" logs/dashboard_automation.log

# Atualizações bem-sucedidas
grep "Atualização automática concluída" logs/dashboard_automation.log
```

### Comandos de Diagnóstico

```bash
# Teste completo
python test_automation_setup.py

# Teste de conexão Google
python google_sheets_processor.py

# Monitoramento de saúde
python monitoring.py
```

---

## 🎉 PRONTO PARA USAR!

Após seguir todos os passos:

1. ✅ Dependências instaladas
2. ✅ Credenciais Google configuradas  
3. ✅ IDs das planilhas configurados
4. ✅ Testes passando

**Execute:**
```bash
python run_automation.py
```

**E escolha a opção 3 para iniciar a automação contínua!**

🚀 Seu dashboard será atualizado automaticamente a cada 3 horas com os dados mais recentes das planilhas!
