# 🚀 Dashboard Builder - Sistema de Produção

## 📋 Visão Geral

Sistema robusto e profissional para criação de dashboards com dados reais do Google Sheets. **Sem dados simulados, sem fallbacks, sem "fazer de conta que funciona"**.

## 🏗️ Arquitetura

### **Backend (Google Cloud Run)**
- **API Flask** robusta e escalável
- **Integração real** com Google Sheets API
- **Processamento de dados** em tempo real
- **Atualizações diárias** automáticas

### **Frontend (Vercel)**
- **Interface amigável** para usuários comuns
- **Responsiva** e moderna
- **Integração completa** com backend

## 🔧 Configuração

### **1. Google Cloud Run (Backend)**

#### **Pré-requisitos:**
```bash
# Instalar Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Configurar projeto
gcloud config set project YOUR_PROJECT_ID
```

#### **Configurar Service Account:**
```bash
# Criar Service Account
gcloud iam service-accounts create dashboard-builder-sa \
    --display-name="Dashboard Builder Service Account"

# Dar permissões necessárias
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:dashboard-builder-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/sheets.reader"

# Criar chave
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=dashboard-builder-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### **Deploy:**
```bash
# Build e deploy
gcloud builds submit --config cloudbuild.yaml

# Ou deploy manual
gcloud run deploy dashboard-builder \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080
```

### **2. Vercel (Frontend)**

#### **Pré-requisitos:**
```bash
# Instalar Vercel CLI
npm i -g vercel
```

#### **Deploy:**
```bash
# Login no Vercel
vercel login

# Deploy
vercel --prod
```

## 📊 Como Usar

### **1. Criar Campanha**
1. Acesse a interface web
2. Preencha os dados da campanha
3. Configure os canais (YouTube, Programática Video, etc.)
4. **Forneça IDs reais das planilhas**
5. Clique em "Criar Dashboard"

### **2. Sistema Valida**
- ✅ **Acesso às planilhas** - verifica se consegue acessar
- ✅ **Dados válidos** - processa dados reais
- ✅ **Cálculos corretos** - métricas baseadas em dados reais
- ✅ **Dashboard gerado** - HTML com dados reais

### **3. Atualizações Diárias**
- 🔄 **Processamento automático** dos dados
- 📊 **Métricas atualizadas** em tempo real
- 📈 **Dashboard sempre atualizado**

## 🔐 Segurança

### **Autenticação Google Sheets**
- **Service Account** para produção
- **OAuth** para desenvolvimento local
- **Permissões mínimas** necessárias

### **API Security**
- **CORS** configurado
- **Rate limiting** (implementar se necessário)
- **Validação** de todos os inputs

## 📁 Estrutura do Projeto

```
├── app.py                      # API principal
├── google_sheets_service.py    # Integração Google Sheets
├── dashboard_generator.py      # Gerador de dashboards
├── campaign_manager.py         # Gerenciador de campanhas
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Container Docker
├── cloudbuild.yaml            # Google Cloud Build
├── vercel.json                # Configuração Vercel
├── package.json               # Configuração Node.js
├── templates/                 # Templates HTML
├── static/                    # Arquivos estáticos
└── README_PRODUCAO.md         # Este arquivo
```

## 🚨 Importante

### **❌ NÃO TOLERAMOS:**
- Dados simulados
- Fallbacks
- "Fazer de conta que funciona"
- Placeholders não substituídos
- Dados hardcoded

### **✅ EXIGIMOS:**
- **Dados reais** das planilhas
- **Validação** de acesso às planilhas
- **Processamento** correto dos dados
- **Cálculos** baseados em dados reais
- **Atualizações** automáticas

## 🔄 Fluxo de Dados

1. **Usuário** cria campanha com IDs das planilhas
2. **Sistema** valida acesso às planilhas
3. **Google Sheets API** retorna dados reais
4. **Processamento** calcula métricas
5. **Dashboard** é gerado com dados reais
6. **Atualizações** diárias mantêm dados atualizados

## 🛠️ Desenvolvimento

### **Local:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar credenciais
cp env.example .env
# Editar .env com suas credenciais

# Executar localmente
python app.py
```

### **Testes:**
```bash
# Testar API
curl http://localhost:8080/health

# Testar criação de campanha
curl -X POST http://localhost:8080/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{"campaignName": "Teste", "channels": [...]}'
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs do Cloud Run
2. Verificar logs do Vercel
3. Testar conectividade com Google Sheets
4. Validar configurações de ambiente

---

**🎯 Sistema profissional, robusto e confiável para criação de dashboards com dados reais!**
