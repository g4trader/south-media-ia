# 🌐 Configuração do Dashboard na Nuvem

## 📋 Visão Geral

O dashboard agora está configurado para ser hospedado na nuvem com automação completa:

1. **✅ Automação**: Cloud Run executa a cada 3 horas
2. **✅ GitHub**: Dashboard atualizado automaticamente via GitHub API
3. **✅ Vercel**: Hospedagem gratuita do dashboard HTML
4. **✅ Dados**: Atualização automática via Google Sheets

## 🔧 Configuração Necessária

### 1. Token do GitHub

Para que a automação funcione, você precisa configurar um token do GitHub:

```bash
# Execute o script de configuração
./setup_github_token.sh <SEU_GITHUB_TOKEN>
```

**Como obter o token:**
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione escopo `repo` (acesso completo aos repositórios)
4. Copie o token gerado
5. Execute: `./setup_github_token.sh <seu_token>`

### 2. Configuração do Vercel

Após configurar o token, configure o Vercel:

1. **Acesse**: https://vercel.com
2. **Conecte sua conta** do GitHub
3. **Importe o projeto**: `south-media-ia`
4. **Configure**:
   - Framework Preset: `Other`
   - Build Command: `echo "Static site"`
   - Output Directory: `static`
5. **Deploy**

## 🌐 URLs do Sistema

### Automação (Cloud Run)
- **URL**: https://dashboard-automation-609095880025.us-central1.run.app
- **Status**: https://dashboard-automation-609095880025.us-central1.run.app/status
- **Logs**: https://dashboard-automation-609095880025.us-central1.run.app/logs

### Dashboard (Vercel)
- **URL**: https://south-media-ia.vercel.app (após configurar Vercel)
- **GitHub**: https://github.com/lucianoterres/south-media-ia/blob/main/static/dash_sonho.html

## 🔄 Como Funciona

1. **Cloud Scheduler** executa a cada 3 horas
2. **Cloud Run** coleta dados do Google Sheets
3. **Dashboard** é atualizado com novos dados
4. **GitHub API** faz commit/push automático
5. **Vercel** serve o dashboard atualizado

## 🧪 Teste Manual

Para testar a automação manualmente:

```bash
# Disparar atualização
curl -X POST https://dashboard-automation-609095880025.us-central1.run.app/trigger

# Verificar status
curl https://dashboard-automation-609095880025.us-central1.run.app/status

# Ver logs
curl https://dashboard-automation-609095880025.us-central1.run.app/logs
```

## 📊 Monitoramento

### Logs da Automação
```bash
gcloud run services logs read dashboard-automation --region=us-central1 --limit=50
```

### Status da Automação
- **Última execução**: Via API `/status`
- **Próxima execução**: A cada 3 horas automaticamente
- **Dados processados**: Via logs ou API `/logs`

## 🎯 Próximos Passos

1. **Configure o token do GitHub**: `./setup_github_token.sh <token>`
2. **Configure o Vercel** para hospedar o dashboard
3. **Teste a automação**: Execute uma atualização manual
4. **Monitore** o funcionamento via logs

## ✅ Checklist Final

- [ ] Token do GitHub configurado
- [ ] Vercel configurado e deployado
- [ ] Automação testada manualmente
- [ ] Dashboard acessível via URL do Vercel
- [ ] Cloud Scheduler funcionando (execução a cada 3h)

---

**🎉 Sistema completamente automatizado e hospedado na nuvem!**
