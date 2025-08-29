# South Media IA - Project Summary

## 🎯 Visão Geral

O projeto South Media IA é um sistema completo de dashboard para gestão e visualização de campanhas de mídia digital. O sistema inclui uma área administrativa e dashboards personalizados para clientes.

## 🏗️ Arquitetura

### Frontend (React)
- **Framework**: React 18
- **Roteamento**: React Router DOM
- **UI**: Componentes customizados com CSS
- **Gráficos**: Chart.js com React Chart.js 2
- **Notificações**: React Hot Toast
- **Deploy**: Vercel

### Backend (FastAPI)
- **Framework**: FastAPI (Python)
- **Banco de Dados**: Google BigQuery
- **Autenticação**: JWT
- **Deploy**: Google Cloud Run

## 🔑 Credenciais Configuradas

### GitHub Token
```
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
```
**Uso**: Autenticação com GitHub, GitHub Actions, e operações de repositório.

### Vercel Token
```
5w8zipRxMJnLEET9OMESteB7
```
**Uso**: Deploy automático do frontend para Vercel.

## 📁 Estrutura do Projeto

```
south-media-ia/
├── 📁 frontend/                 # Aplicação React
│   ├── 📁 src/
│   │   ├── 📁 components/       # Componentes React
│   │   ├── 📁 services/         # Serviços de API
│   │   └── 📁 contexts/         # Contextos React
│   ├── 📄 config.js            # Configuração centralizada
│   ├── 📄 deploy.sh            # Script de deploy
│   └── 📄 package.json         # Dependências Node.js
├── 📁 backend/                  # API FastAPI
│   ├── 📁 src/
│   │   ├── 📁 routes/          # Rotas da API
│   │   ├── 📁 models/          # Modelos de dados
│   │   └── 📁 services/        # Serviços de negócio
│   └── 📄 requirements.txt     # Dependências Python
├── 📁 .github/workflows/       # GitHub Actions
├── 📄 setup-project.sh         # Script de setup automático
├── 📄 quick-start.sh           # Script de início rápido
├── 📄 SETUP.md                 # Guia de configuração
├── 📄 INSTALLATION.md          # Guia de instalação
├── 📄 SECURITY.md              # Guia de segurança
└── 📄 README.md                # Documentação principal
```

## 🚀 Como Começar

### Opção 1: Início Rápido (Recomendado)
```bash
./quick-start.sh
```

### Opção 2: Setup Manual
```bash
# 1. Instalar pré-requisitos
brew install node python@3.9 git

# 2. Executar setup do projeto
./setup-project.sh
```

### Opção 3: Configuração Manual
```bash
# Frontend
cd frontend
npm install
npm start

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## 🌐 URLs de Acesso

- **Admin Dashboard**: https://south-media-ia.vercel.app/admin
- **Cliente Dashboard**: https://south-media-ia.vercel.app/client/{client_id}
- **API Backend**: https://api.iasouth.tech/api

## 🔐 Credenciais de Acesso

### Admin
- **Usuário**: `g4trader`
- **Senha**: `g4trader@M4nu5`

## 📊 Funcionalidades

### Área Administrativa
- ✅ Login seguro para administradores
- ✅ Gestão de clientes e campanhas
- ✅ Upload e importação de dados via CSV
- ✅ Dashboard administrativo completo

### Dashboard do Cliente
- ✅ Acesso via URL personalizada
- ✅ Visualização de métricas em tempo real
- ✅ Interface moderna e responsiva
- ✅ Análises e insights automáticos

## 🔧 Configurações Implementadas

### Frontend
- ✅ Configuração centralizada (`config.js`)
- ✅ Script de deploy automatizado (`deploy.sh`)
- ✅ Integração com Vercel
- ✅ Configuração de ambiente

### Backend
- ✅ Configuração de ambiente
- ✅ Integração com BigQuery
- ✅ Autenticação JWT
- ✅ API REST completa

### DevOps
- ✅ GitHub Actions para deploy automático
- ✅ Scripts de setup automatizados
- ✅ Configuração de segurança
- ✅ Documentação completa

## 🛡️ Segurança

### Implementado
- ✅ Tokens armazenados em variáveis de ambiente
- ✅ Arquivos `.env` no `.gitignore`
- ✅ Secrets do GitHub Actions
- ✅ Configuração de CORS
- ✅ Autenticação JWT

### Recomendações
- 🔄 Rotacionar tokens regularmente
- 🔄 Monitorar logs de acesso
- 🔄 Configurar alertas de segurança
- 🔄 Revisar permissões periodicamente

## 📈 Próximos Passos

### Desenvolvimento
1. **Instalar Node.js** (se não instalado)
2. **Executar setup**: `./setup-project.sh`
3. **Configurar secrets** no GitHub
4. **Iniciar desenvolvimento**

### Deploy
1. **Configurar Vercel** com o token fornecido
2. **Configurar GitHub Actions** com os secrets
3. **Fazer push** para branch main/master
4. **Monitorar deploy** automático

### Manutenção
1. **Monitorar logs** de aplicação
2. **Verificar performance** regularmente
3. **Atualizar dependências** periodicamente
4. **Fazer backup** dos dados

## 📞 Suporte

### Documentação
- **SETUP.md**: Guia completo de configuração
- **INSTALLATION.md**: Instruções de instalação
- **SECURITY.md**: Melhores práticas de segurança
- **README.md**: Documentação principal

### Contato
Para suporte técnico ou dúvidas sobre o projeto, entre em contato com a equipe South Media IA.

---

**Projeto configurado e pronto para uso!** 🚀

**Desenvolvido pela equipe South Media IA**
