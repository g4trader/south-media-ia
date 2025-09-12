#!/bin/bash

# Script para configurar token do GitHub no Secret Manager
# Execute este script para configurar o token do GitHub para automação

echo "🔐 Configurando token do GitHub para automação..."

# Verificar se o token foi fornecido
if [ -z "$1" ]; then
    echo "❌ Erro: Token do GitHub não fornecido"
    echo "📋 Uso: $0 <GITHUB_TOKEN>"
    echo ""
    echo "📝 Para obter um token do GitHub:"
    echo "   1. Acesse: https://github.com/settings/tokens"
    echo "   2. Clique em 'Generate new token (classic)'"
    echo "   3. Selecione escopo 'repo' (acesso completo aos repositórios)"
    echo "   4. Copie o token gerado"
    echo "   5. Execute: $0 <seu_token_aqui>"
    exit 1
fi

GITHUB_TOKEN="$1"

echo "📋 Configurando token no Secret Manager..."

# Habilitar API do Secret Manager
gcloud services enable secretmanager.googleapis.com

# Criar ou atualizar o secret
echo "$GITHUB_TOKEN" | gcloud secrets create github-token --data-file=- 2>/dev/null || \
echo "$GITHUB_TOKEN" | gcloud secrets versions add github-token --data-file=-

echo "✅ Token configurado no Secret Manager como 'github-token'"

# Atualizar Cloud Run para usar o token
echo "🔄 Atualizando Cloud Run service..."

gcloud run services update dashboard-automation \
    --region=us-central1 \
    --update-secrets="GITHUB_TOKEN=github-token:latest"

echo "✅ Cloud Run atualizado com sucesso!"
echo ""
echo "🌐 Próximos passos:"
echo "   1. Execute uma atualização: curl -X POST https://dashboard-automation-609095880025.us-central1.run.app/trigger"
echo "   2. O dashboard será atualizado no GitHub automaticamente"
echo "   3. Configure Vercel para servir o dashboard do GitHub"
echo ""
echo "🎉 Configuração concluída!"
