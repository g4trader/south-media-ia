# South Media IA - Setup Guide

Este guia contém todas as informações necessárias para configurar e executar o projeto South Media IA.

## 🔑 Credenciais do Projeto

### GitHub Token
```
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
```

### Vercel Token
```
5w8zipRxMJnLEET9OMESteB7
```

## 🚀 Configuração Rápida

### 1. Executar Script de Setup Automático
```bash
./setup-project.sh
```

Este script irá:
- Verificar pré-requisitos (Node.js, npm, Python)
- Instalar dependências do frontend e backend
- Criar ambiente virtual Python
- Configurar variáveis de ambiente
- Fornecer instruções para secrets do GitHub

### 2. Configurar Secrets do GitHub

Para habilitar deploy automático, adicione os seguintes secrets no seu repositório GitHub:

1. Vá para **Settings > Secrets and variables > Actions**
2. Adicione os seguintes secrets:

| Secret | Valor |
|--------|-------|
| `VERCEL_TOKEN` | `5w8zipRxMJnLEET9OMESteB7` |
| `VERCEL_ORG_ID` | (Obtenha do dashboard do Vercel) |
| `VERCEL_PROJECT_ID` | (Obtenha do dashboard do Vercel) |
| `GITHUB_TOKEN` | `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` |

## 🏃‍♂️ Executando o Projeto

### Frontend (React)
```bash
cd frontend
npm start
```
Acesse: http://localhost:3000

### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
uvicorn src.main:app --reload
```
Acesse: http://localhost:8080

## 🌐 Deploy

### Deploy Manual para Vercel
```bash
cd frontend
./deploy.sh
```

### Deploy Automático
O projeto está configurado com GitHub Actions para deploy automático quando houver push para `main` ou `master`.

## 📊 URLs de Acesso

- **Admin Dashboard**: https://south-media-ia.vercel.app/admin
- **Cliente Dashboard**: https://south-media-ia.vercel.app/client/{client_id}
- **API Backend**: https://api.iasouth.tech/api

## 🔐 Credenciais de Acesso

### Admin
- **Usuário**: `g4trader`
- **Senha**: `g4trader@M4nu5`

## 🛠️ Estrutura do Projeto

```
south-media-ia/
├── frontend/                 # React App
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── services/         # Serviços de API
│   │   └── contexts/         # Contextos React
│   ├── config.js            # Configuração centralizada
│   └── deploy.sh            # Script de deploy
├── backend/                  # FastAPI Backend
│   ├── src/
│   │   ├── routes/          # Rotas da API
│   │   ├── models/          # Modelos de dados
│   │   └── services/        # Serviços de negócio
│   └── requirements.txt     # Dependências Python
├── .github/workflows/       # GitHub Actions
└── setup-project.sh         # Script de setup
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente Frontend
Crie um arquivo `.env.local` na pasta `frontend/`:

```env
REACT_APP_API_URL=https://api.iasouth.tech/api
REACT_APP_VERCEL_TOKEN=5w8zipRxMJnLEET9OMESteB7
REACT_APP_GITHUB_TOKEN=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
```

### Variáveis de Ambiente Backend
O arquivo `.env` será criado automaticamente pelo script de setup.

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de dependências**
   ```bash
   cd frontend && npm install
   cd backend && pip install -r requirements.txt
   ```

2. **Erro de porta em uso**
   - Frontend: Mude a porta no package.json
   - Backend: Use `uvicorn src.main:app --reload --port 8081`

3. **Erro de CORS**
   - Verifique se o backend está rodando na porta correta
   - Confirme a URL da API no config.js

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o projeto, entre em contato com a equipe South Media IA.

---

**Desenvolvido pela equipe South Media IA** 🚀
