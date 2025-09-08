# 🚀 Próximos Passos - Google Cloud Run

## ✅ **Deploy Concluído com Sucesso!**

O backend foi deployado com sucesso no Google Cloud Run:

- **URL do Serviço**: `https://south-media-ia-backend-6f3ckz7c7q-uc.a.run.app`
- **Status**: ✅ Funcionando
- **Health Check**: ✅ `{"status":"healthy"}`
- **Frontend**: ✅ Configurado para usar a nova URL

## 🔧 **Próximos Passos para Integração Completa**

### 1. **Configurar Credenciais do Google Sheets**

Para que a integração com as planilhas funcione completamente, você precisa:

#### A. Criar Service Account no Google Cloud Console
1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Selecione o projeto: `automatizar-452311`
3. Clique em "Criar Conta de Serviço"
4. Nome: `south-media-sheets-service`
5. Descrição: `Service account para integração com Google Sheets`

#### B. Baixar Credenciais JSON
1. Após criar, clique na conta de serviço
2. Vá para a aba "Chaves"
3. Clique em "Adicionar Chave" → "Criar Nova Chave"
4. Tipo: JSON
5. Baixe o arquivo `credentials.json`

#### C. Configurar Permissões nas Planilhas
Para cada planilha, você precisa compartilhar com o email da service account:
- **CTV**: https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit
- **YouTube**: https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182
- **TikTok**: https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true
- **Disney**: https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit
- **Netflix**: https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit
- **Footfall Display**: https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064

**Ação**: Compartilhar cada planilha com o email da service account (ex: `south-media-sheets-service@automatizar-452311.iam.gserviceaccount.com`) com permissão de **"Visualizador"**.

### 2. **Configurar Variáveis de Ambiente no Cloud Run**

Execute os comandos abaixo para configurar as credenciais:

```bash
# Configurar credenciais do Google Sheets
gcloud run services update south-media-ia-backend \
  --region=us-central1 \
  --set-env-vars="GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json" \
  --project=automatizar-452311

# Upload do arquivo de credenciais
gcloud run services update south-media-ia-backend \
  --region=us-central1 \
  --update-secrets="GOOGLE_CREDENTIALS_JSON=credentials-secret:latest" \
  --project=automatizar-452311
```

### 3. **Deploy da Versão Completa**

Após configurar as credenciais, faça o deploy da versão completa:

```bash
# Deploy com a aplicação completa
gcloud builds submit --config=backend/cloudbuild.yaml --project=automatizar-452311
```

### 4. **Testar Integração**

Após o deploy completo, teste os endpoints:

```bash
# Testar health check
curl https://south-media-ia-backend-6f3ckz7c7q-uc.a.run.app/health

# Testar endpoint de dados do dashboard
curl https://south-media-ia-backend-6f3ckz7c7q-uc.a.run.app/api/dashboard/data
```

### 5. **Atualizar Frontend**

O frontend já está configurado para usar a nova URL. Após o deploy completo, ele automaticamente começará a usar os dados reais das planilhas.

## 🎯 **Status Atual**

### ✅ **Concluído**
- [x] Deploy do backend no Google Cloud Run
- [x] Health check funcionando
- [x] Frontend configurado com nova URL
- [x] Estrutura de integração com Google Sheets pronta
- [x] Dados mock funcionando como fallback

### 🔄 **Em Andamento**
- [ ] Configuração de credenciais do Google Sheets
- [ ] Deploy da versão completa com todas as funcionalidades
- [ ] Teste da integração completa

### 📋 **Pendente**
- [ ] Configurar permissões nas planilhas
- [ ] Testar endpoint `/api/dashboard/data` com dados reais
- [ ] Validar integração completa no frontend

## 🔗 **URLs Importantes**

- **Backend**: https://south-media-ia-backend-6f3ckz7c7q-uc.a.run.app
- **Frontend**: https://dash.iasouth.tech/multicanal
- **Admin Dashboard**: https://dash.iasouth.tech/admin/dashboard
- **Google Cloud Console**: https://console.cloud.google.com/run/detail/us-central1/south-media-ia-backend

## 📞 **Suporte**

Para dúvidas sobre a configuração:
- **Documentação**: `GOOGLE_SHEETS_INTEGRATION.md`
- **Logs do Cloud Run**: https://console.cloud.google.com/logs/viewer
- **Status do Serviço**: https://console.cloud.google.com/run/detail/us-central1/south-media-ia-backend

---

**🎉 O backend está funcionando! Agora é só configurar as credenciais do Google Sheets para ter a integração completa!**
