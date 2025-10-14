#!/bin/bash
# 🛡️ SCRIPT DE DEPLOY SEGURO PARA PRODUÇÃO
# Inclui verificações de integridade e confirmação do usuário

set -e  # Para execução ao primeiro erro

echo "🚀 DEPLOY SEGURO PARA PRODUÇÃO"
echo "================================"
echo ""

# 1. Verificação de integridade
echo "🔍 1/5 - Verificando arquivos críticos..."
python3 pre_deploy_check.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ DEPLOY CANCELADO - Arquivos críticos faltando ou corrompidos"
    exit 1
fi

echo ""

# 2. Backup de templates de produção
echo "📦 2/5 - Criando backup de templates de produção..."
BACKUP_DIR="production_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "   Baixando templates de produção..."
curl -s "https://gen-dashboard-ia-609095880025.us-central1.run.app/static/dash_generic_template.html" > "$BACKUP_DIR/dash_generic_template.html" || echo "   ⚠️ Não foi possível baixar dash_generic_template.html"
curl -s "https://gen-dashboard-ia-609095880025.us-central1.run.app/static/dash_remarketing_cpm_template.html" > "$BACKUP_DIR/dash_remarketing_cpm_template.html" || echo "   ⚠️ Não foi possível baixar dash_remarketing_cpm_template.html"
curl -s "https://gen-dashboard-ia-609095880025.us-central1.run.app/static/dash_generic_cpe_template.html" > "$BACKUP_DIR/dash_generic_cpe_template.html" || echo "   ⚠️ Não foi possível baixar dash_generic_cpe_template.html"

echo "   ✅ Backup salvo em: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"

echo ""

# 3. Mostrar o que será deployado
echo "📋 3/5 - Templates que serão deployados:"
ls -lh static/dash_*_template.html

echo ""

# 4. Confirmação do usuário
echo "⚠️ 4/5 - CONFIRMAÇÃO NECESSÁRIA"
echo ""
echo "Você está prestes a fazer deploy em PRODUÇÃO:"
echo "  🌐 URL: https://gen-dashboard-ia-609095880025.us-central1.run.app"
echo "  📁 Backup criado em: $BACKUP_DIR"
echo ""
echo "Templates a serem deployados:"
echo "  ✅ dash_generic_template.html (CPV)"
echo "  ✅ dash_remarketing_cpm_template.html (CPM)"
echo "  ✅ dash_generic_cpe_template.html (CPE)"
echo ""
read -p "Digite 'CONFIRMO' para continuar: " confirmacao

if [ "$confirmacao" != "CONFIRMO" ]; then
    echo ""
    echo "❌ Deploy cancelado pelo usuário"
    exit 1
fi

echo ""

# 5. Deploy
echo "🚀 5/5 - Executando deploy..."
gcloud run deploy gen-dashboard-ia \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production \
    --quiet

echo ""

# 6. Validação pós-deploy
echo "✅ 6/6 - Validando deploy..."
sleep 5

echo "   Verificando se templates foram deployados corretamente..."
TEMPLATE_CHECK=$(curl -s "https://gen-dashboard-ia-609095880025.us-central1.run.app/static/dash_generic_template.html" | head -1)

if [[ $TEMPLATE_CHECK == *"<!DOCTYPE html>"* ]]; then
    echo "   ✅ Template CPV OK"
else
    echo "   ❌ Problema com template CPV"
fi

echo ""
echo "================================"
echo "✅ DEPLOY CONCLUÍDO"
echo ""
echo "📊 Próximos passos:"
echo "  1. Testar geração de dashboard em produção"
echo "  2. Verificar /dashboards-list"
echo "  3. Validar filtros em todos os KPIs"
echo ""
echo "📁 Backup disponível em: $BACKUP_DIR"
echo "================================"

