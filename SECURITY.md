# Security Guide - South Media IA

## 🔐 Gerenciamento de Credenciais

### ⚠️ Importante: Segurança das Credenciais

As credenciais fornecidas são sensíveis e devem ser tratadas com cuidado:

- **GitHub Token**: `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`
- **Vercel Token**: `5w8zipRxMJnLEET9OMESteB7`

### 🛡️ Boas Práticas de Segurança

#### 1. Nunca commite credenciais no código
- Use variáveis de ambiente
- Use arquivos `.env` (adicionados ao `.gitignore`)
- Use secrets do GitHub Actions

#### 2. Rotação de Tokens
- Troque os tokens regularmente
- Revogue tokens não utilizados
- Use tokens com escopo mínimo necessário

#### 3. Acesso Limitado
- Use tokens apenas para as operações necessárias
- Configure permissões mínimas
- Monitore o uso dos tokens

### 🔧 Configuração Segura

#### Frontend (.env.local)
```env
REACT_APP_API_URL=https://api.iasouth.tech/api
REACT_APP_VERCEL_TOKEN=5w8zipRxMJnLEET9OMESteB7
REACT_APP_GITHUB_TOKEN=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
```

#### Backend (.env)
```env
SECRET_KEY=south-media-secret-key-2024
GOOGLE_CLOUD_PROJECT=automatizar-452311
BIGQUERY_DATASET=south_media_dashboard
FLASK_ENV=development
PORT=8080
```

#### GitHub Secrets
Configure estes secrets no seu repositório GitHub:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `GITHUB_TOKEN`

### 🚨 Em Caso de Comprometimento

1. **Revogue imediatamente os tokens comprometidos**
2. **Gere novos tokens**
3. **Atualize todas as configurações**
4. **Monitore logs de acesso**
5. **Investigue a causa do comprometimento**

### 📋 Checklist de Segurança

- [ ] Tokens não estão no código fonte
- [ ] Arquivos `.env` estão no `.gitignore`
- [ ] Secrets do GitHub estão configurados
- [ ] Tokens têm permissões mínimas
- [ ] Monitoramento de acesso ativo
- [ ] Backup das configurações seguras

### 🔍 Monitoramento

- Monitore logs de acesso do GitHub
- Verifique logs do Vercel
- Configure alertas para uso anômalo
- Revise permissões regularmente

---

**Lembre-se: A segurança é responsabilidade de todos!** 🔒
