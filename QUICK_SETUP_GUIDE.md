# 🚀 GUIA DE CONFIGURAÇÃO RÁPIDA

## ✅ PLANILHAS CONFIGURADAS

As seguintes planilhas já foram configuradas no sistema:

### 📊 **CANAIS DE MÍDIA**
- **YouTube**: `1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo` (GID: 1863167182)
- **TikTok**: `1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM` (GID: 1727929489)
- **Netflix**: `1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo` (GID: 1743413064)
- **Disney**: `1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o` (GID: 1743413064)
- **CTV**: `1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U` (GID: 1743413064)
- **Footfall Display**: `10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA` (GID: 1743413064)

### 🏪 **DADOS FOOTFALL**
- **Footfall Data**: `10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA` (GID: 120680471)

---

## 🔧 CONFIGURAÇÃO RÁPIDA (3 PASSOS)

### **PASSO 1: Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **PASSO 2: Configurar Credenciais Google**
1. Acesse: https://console.cloud.google.com/
2. Crie um projeto ou selecione existente
3. Habilite a **Google Sheets API**
4. Crie credenciais **OAuth 2.0** (Desktop Application)
5. Baixe o arquivo `credentials.json`
6. Coloque em: `credentials/credentials.json`

### **PASSO 3: Testar Conexão**
```bash
python test_sheets_connection.py
```

---

## 🚀 EXECUTAR AUTOMAÇÃO

### **Modo Interativo (Recomendado)**
```bash
python run_automation.py
```

### **Modo Linha de Comando**
```bash
# Testar configuração
python run_automation.py check

# Atualização única
python run_automation.py update

# Automação contínua (a cada 3h)
python run_automation.py start

# Monitoramento
python run_automation.py monitor
```

### **Scripts Prontos**
```bash
# Windows
start_automation.bat

# Linux/Mac
./start_automation.sh
```

---

## 🔍 VERIFICAÇÃO DE SAÚDE

### **Teste Completo**
```bash
python test_automation_setup.py
```

### **Teste das Planilhas**
```bash
python test_sheets_connection.py
```

### **Monitoramento**
```bash
python monitoring.py
```

---

## 📋 CHECKLIST DE CONFIGURAÇÃO

- [ ] ✅ Dependências instaladas (`pip install -r requirements.txt`)
- [ ] ✅ Projeto Google Cloud criado
- [ ] ✅ Google Sheets API habilitada
- [ ] ✅ Credenciais OAuth 2.0 criadas
- [ ] ✅ Arquivo `credentials.json` baixado e colocado em `credentials/`
- [ ] ✅ Planilhas compartilhadas com o email da conta de serviço
- [ ] ✅ Teste de conexão executado com sucesso
- [ ] ✅ Automação testada com atualização única

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### **Erro: "Credentials not found"**
- Verifique se `credentials/credentials.json` existe
- Refazer configuração das credenciais Google

### **Erro: "Permission denied"**
- Compartilhar planilhas com o email da conta de serviço
- Verificar permissões de leitura

### **Erro: "Sheet not found"**
- Verificar se URLs das planilhas estão corretas
- Confirmar se GIDs estão atualizados

### **Dashboard não atualiza**
- Verificar logs: `tail -f logs/dashboard_automation.log`
- Executar monitoramento: `python monitoring.py`

---

## 📞 SUPORTE

### **Logs Úteis**
```bash
# Logs da automação
tail -f logs/dashboard_automation.log

# Status do sistema
cat logs/dashboard_status.json

# Erros recentes
grep "ERROR" logs/dashboard_automation.log
```

### **Comandos de Diagnóstico**
```bash
# Teste completo
python test_automation_setup.py

# Teste das planilhas
python test_sheets_connection.py

# Monitoramento
python monitoring.py
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Configure as credenciais** (Passo 2)
2. **Teste a conexão** (Passo 3)
3. **Execute a automação**: `python run_automation.py`
4. **Escolha opção 3** para iniciar automação contínua
5. **Monitore os logs** para acompanhar o funcionamento

**🚀 Sua automação estará funcionando e atualizando o dashboard a cada 3 horas!**
