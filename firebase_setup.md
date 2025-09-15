# 🔥 Firebase Setup - Sistema de Autenticação

## 📋 **Configuração do Firebase Firestore**

### **1. Criar Projeto Firebase**

1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Clique em "Adicionar projeto"
3. Nome do projeto: `south-media-ia`
4. Ative o Google Analytics (opcional)
5. Clique em "Criar projeto"

### **2. Configurar Firestore Database**

1. No painel do Firebase, vá para "Firestore Database"
2. Clique em "Criar banco de dados"
3. Escolha "Iniciar no modo de teste" (para desenvolvimento)
4. Selecione a localização: `us-central1` (Iowa)
5. Clique em "Próximo" e "Ativar"

### **3. Configurar Regras de Segurança**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
    
    // Companies collection
    match /companies/{companyId} {
      allow read, write: if request.auth != null;
    }
    
    // Dashboards collection
    match /dashboards/{dashboardId} {
      allow read, write: if request.auth != null;
    }
    
    // Sessions collection
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null;
    }
    
    // Logs collection
    match /logs/{logId} {
      allow read, write: if request.auth != null;
    }
    
    // Roles collection
    match /roles/{roleId} {
      allow read, write: if request.auth != null;
    }
    
    // Permissions collection
    match /permissions/{permissionId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### **4. Obter Configuração do Projeto**

1. No painel do Firebase, vá para "Configurações do projeto" (ícone de engrenagem)
2. Role para baixo até "Seus aplicativos"
3. Clique em "Adicionar app" e escolha "Web" (ícone `</>`)
4. Nome do app: `south-media-ia-web`
5. Marque "Também configurar o Firebase Hosting" (opcional)
6. Clique em "Registrar app"

### **5. Copiar Configuração**

Copie a configuração que aparece e substitua no arquivo `firebase_config.js`:

```javascript
const firebaseConfig = {
    apiKey: "SUA_API_KEY_AQUI",
    authDomain: "south-media-ia.firebaseapp.com",
    projectId: "south-media-ia",
    storageBucket: "south-media-ia.appspot.com",
    messagingSenderId: "SEU_SENDER_ID",
    appId: "SEU_APP_ID"
};
```

### **6. Instalar Firebase SDK**

```bash
npm install firebase
```

### **7. Estrutura das Coleções**

#### **users**
```javascript
{
  id: "user_001",
  username: "admin",
  password: "dashboard2025",
  role: "super_admin",
  company_id: null,
  profile: {
    full_name: "Administrador do Sistema",
    email: "admin@iasouth.tech",
    avatar: "👑"
  },
  status: "active",
  last_login: "2025-01-14T10:30:00Z",
  created_at: "2025-01-14T10:00:00Z",
  updated_at: "2025-01-14T10:30:00Z"
}
```

#### **companies**
```javascript
{
  id: "company_001",
  name: "IA South Tech",
  code: "IASOUTH",
  description: "Empresa de tecnologia e inteligência artificial",
  settings: {
    theme: "dark",
    timezone: "America/Sao_Paulo",
    language: "pt-BR"
  },
  contact: {
    email: "contato@iasouth.tech",
    phone: "+55 11 99999-9999",
    address: "São Paulo, SP, Brasil"
  },
  status: "active",
  created_at: "2025-01-14T10:00:00Z",
  updated_at: "2025-01-14T10:00:00Z"
}
```

#### **dashboards**
```javascript
{
  id: "dashboard_001",
  file: "dash_sonho.html",
  name: "Dashboard Sonho",
  company_id: "company_002",
  description: "Dashboard principal da Sonho Digital",
  thumbnail: "sonho_thumb.png",
  status: "active",
  last_updated: "2025-01-14T10:00:00Z",
  created_at: "2025-01-14T10:00:00Z",
  updated_at: "2025-01-14T10:00:00Z"
}
```

### **8. Migração Automática**

O sistema inclui migração automática do localStorage para Firestore:

- ✅ **Dados existentes preservados**
- ✅ **Migração transparente**
- ✅ **Fallback para localStorage se Firebase falhar**
- ✅ **Logs de atividade**

### **9. Benefícios do Firebase**

- 🚀 **Performance**: Consultas otimizadas
- 🔒 **Segurança**: Regras de acesso granulares
- 📊 **Escalabilidade**: Suporta milhões de usuários
- 🔄 **Sincronização**: Dados em tempo real
- 📱 **Multiplataforma**: Web, mobile, desktop
- 💾 **Backup automático**: Dados sempre seguros

### **10. Próximos Passos**

1. ✅ Configurar Firebase
2. ✅ Atualizar `firebase_config.js` com suas credenciais
3. ✅ Testar sistema de autenticação
4. ✅ Verificar migração de dados
5. ✅ Configurar regras de segurança
6. ✅ Deploy em produção

---

## 🚨 **IMPORTANTE**

- **Nunca commite as credenciais do Firebase** no repositório
- **Use variáveis de ambiente** para produção
- **Configure regras de segurança** adequadas
- **Faça backup** dos dados antes da migração
- **Teste em ambiente de desenvolvimento** primeiro
