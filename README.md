# South Media IA - Sistema de Dashboard de Mídia

Sistema completo para gestão e visualização de campanhas de mídia digital para clientes.

## 🚀 Funcionalidades

### Área Administrativa
- Login seguro para administradores
- Gestão de clientes e campanhas
- Upload e importação de dados de performance via CSV
- Dashboard administrativo completo

### Dashboard do Cliente
- Acesso via URL personalizada por cliente
- Visualização de métricas de campanhas em tempo real
- Interface moderna e responsiva
- Análises e insights automáticos

## 🏗️ Arquitetura

### Backend
- **Framework**: FastAPI (Python)
- **Banco de Dados**: Google BigQuery
- **Autenticação**: JWT
- **Deploy**: Google Cloud Run

### Frontend
- **Framework**: React
- **Estilização**: CSS Modules
- **Deploy**: Vercel
- **Integração**: API REST

## 📊 Estrutura de Dados

### Tabelas BigQuery
- `clients`: Informações dos clientes
- `campaigns`: Dados das campanhas
- `campaign_performance_data`: Métricas de performance

## 🔧 Configuração

### Pré-requisitos
- Node.js 18+
- Python 3.9+
- Conta Google Cloud com BigQuery habilitado
- Conta Vercel para deploy do frontend

### Instalação

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 🌐 Deploy

- **Frontend**: Vercel (automático via GitHub)
- **Backend**: Google Cloud Run (automático via GitHub Actions)

## 📝 Credenciais Administrativas

- **Usuário**: g4trader
- **Senha**: g4trader@M4nu5

## 🎯 URLs de Acesso

- **Admin**: `https://south-media-ia.vercel.app/admin`
- **Cliente**: `https://south-media-ia.vercel.app/client/{client_id}`

---

Desenvolvido pela equipe South Media IA

