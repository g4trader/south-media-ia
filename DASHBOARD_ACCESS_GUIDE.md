# 🌐 Guia de Acesso ao Dashboard

## 📊 **Dashboard Principal: `dash_sonho.html`**

### **🔗 URLs de Acesso:**

#### **1. 🚀 Vercel (Recomendado)**
```
https://south-media-ia.vercel.app/
https://south-media-ia.vercel.app/dash_sonho.html
https://south-media-ia.vercel.app/static/dash_sonho.html
```

#### **2. 🌐 GitHub Pages (Alternativo)**
```
https://g4trader.github.io/south-media-ia/static/dash_sonho.html
```

#### **3. 💻 Local (Desenvolvimento)**
```bash
# Navegar para a pasta static
cd static

# Iniciar servidor local
python3 -m http.server 8080

# Acessar em:
http://localhost:8080/dash_sonho.html
```

---

## 🎯 **Funcionalidades do Dashboard:**

### **📈 Abas Disponíveis:**
- **📊 Visão Geral** - Métricas principais e KPIs
- **📺 Por Canal** - Análise detalhada por canal (CTV, Disney, Netflix, TikTok, YouTube, Footfall)
- **📋 Planejamento** - Estratégias e objetivos da campanha
- **🔍 Análise & Insights** - Otimizações e recomendações
- **👣 Footfall** - Relatório específico de footfall

### **🔄 Atualização Automática:**
- **⏰ Intervalo**: A cada 5 minutos
- **📊 Fonte**: Google Sheets (6 planilhas configuradas)
- **🔄 Status**: Indicador visual de última atualização

---

## 🛠️ **Configuração para Deploy na Vercel:**

### **1. 📁 Estrutura do Projeto:**
```
south-media-ia/
├── static/
│   ├── dash_sonho.html          # Dashboard principal
│   ├── dashboard-updater.js     # Script de atualização
│   ├── analise_footfall_embed.html
│   └── tsv/                     # Dados de exemplo
├── vercel.json                  # Configuração Vercel
└── backend/                     # API backend
```

### **2. ⚙️ Configuração Vercel:**
```json
{
  "version": 2,
  "name": "south-media-dashboard",
  "builds": [
    {
      "src": "static/**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "/static/dash_sonho.html"
    }
  ]
}
```

### **3. 🚀 Deploy na Vercel:**
```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Fazer login
vercel login

# 3. Deploy
vercel --prod

# 4. Configurar domínio (opcional)
vercel domains add dash.iasouth.tech
```

---

## 🔧 **Configuração do Backend:**

### **🌐 API Endpoints:**
```
https://south-media-ia-backend.vercel.app/api/dashboard/data
https://south-media-ia-backend.vercel.app/api/dashboard/test-sheets
```

### **📊 Integração Google Sheets:**
- **✅ 6 planilhas** configuradas
- **🔄 Atualização** automática
- **📈 Dados em tempo real**

---

## 🎨 **Personalização:**

### **🎯 Para Diferentes Clientes:**
1. **Copiar** `dash_sonho.html`
2. **Renomear** para `dash_[cliente].html`
3. **Personalizar** dados e branding
4. **Deploy** separado

### **📱 Responsividade:**
- **✅ Mobile** otimizado
- **✅ Tablet** compatível
- **✅ Desktop** completo

---

## 🚨 **Solução de Problemas:**

### **❌ Dashboard não carrega:**
1. Verificar URL correta
2. Confirmar deploy na Vercel
3. Verificar console do navegador

### **❌ Dados não atualizam:**
1. Verificar conexão Google Sheets
2. Confirmar credenciais
3. Testar endpoint `/api/dashboard/test-sheets`

### **❌ Erro CORS:**
1. Verificar configuração Vercel
2. Confirmar headers CORS no backend
3. Testar em modo incógnito

---

## 📞 **Suporte:**

### **🔗 Links Úteis:**
- **Vercel Dashboard**: https://vercel.com/dashboard
- **GitHub Repository**: https://github.com/g4trader/south-media-ia
- **Google Sheets**: Planilhas configuradas

### **📧 Contato:**
- **Issues**: GitHub Issues
- **Documentação**: README.md
- **Logs**: Vercel Functions Logs

---

## 🎉 **Resultado Final:**

**✅ Dashboard acessível em:**
- **🌐 Vercel**: `https://south-media-ia.vercel.app/`
- **📊 Funcional**: Todas as abas e funcionalidades
- **🔄 Atualizado**: Dados em tempo real do Google Sheets
- **📱 Responsivo**: Funciona em todos os dispositivos

**🚀 Pronto para uso em produção!**
