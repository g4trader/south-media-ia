# 🔧 Configuração do Google Sheets - Passo a Passo

## ✅ **Status Atual:**
- ✅ Service Account criado: `southmedia@automatizar-452311.iam.gserviceaccount.com`
- ✅ Chave JSON baixada
- ✅ Backend preparado para integração

## 📋 **Próximos Passos:**

### 1. **Adicionar o arquivo `credentials.json` ao repositório**

Você precisa colocar o arquivo `credentials.json` na raiz do projeto:

```bash
# Copie o arquivo credentials.json para a raiz do projeto
cp /caminho/para/seu/credentials.json /Users/lucianoterres/Documents/GitHub/south-media-ia/
```

### 2. **Compartilhar as planilhas com a Service Account**

Para cada planilha, você precisa compartilhar com o email da service account:

**Email da Service Account:** `southmedia@automatizar-452311.iam.gserviceaccount.com`

**Planilhas para compartilhar:**
- **CTV**: https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit
- **YouTube**: https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182
- **TikTok**: https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true
- **Disney**: https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit
- **Netflix**: https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit
- **Footfall Display**: https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064

**Como compartilhar:**
1. Abra cada planilha
2. Clique em "Compartilhar" (botão azul no canto superior direito)
3. Adicione o email: `southmedia@automatizar-452311.iam.gserviceaccount.com`
4. Defina a permissão como **"Visualizador"**
5. Clique em "Enviar"

### 3. **Fazer commit do arquivo credentials.json**

```bash
git add credentials.json
git commit -m "feat: Adicionar credenciais do Google Sheets"
git push origin main
```

### 4. **Deploy do backend com integração Google Sheets**

```bash
gcloud builds submit --config=backend/cloudbuild-google-sheets.yaml --project=automatizar-452311
```

## 🧪 **Teste da Integração:**

Após o deploy, teste o endpoint:

```bash
curl -s https://south-media-ia-backend-609095880025.us-central1.run.app/api/dashboard/data
```

**Resposta esperada:**
```json
{
  "message": "Dashboard data - Google Sheets integration active",
  "source": "google_sheets_real",
  "data": {
    "CONS": { ... },
    "PER": [ ... ],
    "DAILY": [ ... ]
  }
}
```

## 🔍 **Verificação no Frontend:**

No dashboard, você deve ver:
- **Antes**: "🔄 Dados dinâmicos simulados (API funcionando)"
- **Depois**: "✅ Dados reais do Google Sheets"

## 🚨 **Troubleshooting:**

### Se aparecer erro de permissão:
- Verifique se todas as planilhas foram compartilhadas com a service account
- Confirme que a permissão é "Visualizador"

### Se aparecer erro de credenciais:
- Verifique se o arquivo `credentials.json` está na raiz do projeto
- Confirme que o arquivo não está corrompido

### Se os dados não aparecerem:
- Verifique se as planilhas têm dados nas abas corretas
- Confirme se os nomes das colunas estão corretos

## 📞 **Suporte:**

Se encontrar problemas:
1. Verifique os logs do Cloud Run
2. Teste o endpoint manualmente
3. Confirme as permissões das planilhas

---

**🎯 Objetivo:** Ter dados reais das planilhas Google Sheets no dashboard em vez de dados mock!