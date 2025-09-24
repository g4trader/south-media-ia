#!/usr/bin/env python3
"""
Script para criar um novo dashboard de campanha usando a estrutura genérica
"""

import os
import shutil
from campaign_config import get_campaign_config, get_all_campaigns

def create_campaign_dashboard(campaign_key):
    """Criar dashboard para uma nova campanha"""
    
    # Verificar se a campanha existe
    config = get_campaign_config(campaign_key)
    if not config:
        print(f"❌ Campanha '{campaign_key}' não encontrada!")
        print("📋 Campanhas disponíveis:")
        for key, cfg in get_all_campaigns().items():
            print(f"   - {key}: {cfg.client} - {cfg.campaign}")
        return False
    
    print(f"🎯 Criando dashboard para: {config.client} - {config.campaign}")
    
    # Nome do arquivo do dashboard
    dashboard_filename = f"dash_{config.get_slug()}.html"
    dashboard_path = f"static/{dashboard_filename}"
    
    # Copiar template genérico
    template_path = "static/dash_video_programmatic_template.html"
    if not os.path.exists(template_path):
        print(f"❌ Template genérico não encontrado: {template_path}")
        return False
    
    # Copiar arquivo
    shutil.copy2(template_path, dashboard_path)
    print(f"✅ Dashboard criado: {dashboard_path}")
    
    # Personalizar o arquivo para a campanha específica
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir campaign_key genérico pelo específico
    content = content.replace(
        'let campaignKey = urlParams.get(\'campaign\') || \'sebrae_pr\';',
        f'let campaignKey = \'{campaign_key}\'; // Definido para {config.client}'
    )
    
    # Substituir título da página
    content = content.replace(
        'Carregando Dashboard...',
        f'Dashboard {config.client} - {config.campaign}'
    )
    
    # Salvar arquivo personalizado
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard personalizado para {config.client}")
    
    # Informações sobre o dashboard criado
    print(f"\n📊 INFORMAÇÕES DO DASHBOARD:")
    print(f"   📁 Arquivo: {dashboard_path}")
    print(f"   🌐 URL: http://localhost:5000/{dashboard_path}")
    print(f"   🔗 API: {config.api_endpoint}")
    print(f"   📊 Cliente: {config.client}")
    print(f"   📊 Campanha: {config.campaign}")
    
    return True

def main():
    """Função principal"""
    print("🚀 CRIADOR DE DASHBOARDS DE CAMPANHA")
    print("=" * 50)
    
    # Mostrar campanhas disponíveis
    campaigns = get_all_campaigns()
    if not campaigns:
        print("❌ Nenhuma campanha configurada!")
        return
    
    print("📋 Campanhas disponíveis:")
    for key, config in campaigns.items():
        print(f"   - {key}: {config.client} - {config.campaign}")
    
    print(f"\n🎯 Para criar um dashboard, execute:")
    print(f"   python3 create_new_campaign_dashboard.py [campaign_key]")
    print(f"\n📝 Exemplo:")
    print(f"   python3 create_new_campaign_dashboard.py sebrae_pr")
    
    # Se foi passado um campaign_key como argumento
    import sys
    if len(sys.argv) > 1:
        campaign_key = sys.argv[1]
        print(f"\n🎯 Criando dashboard para: {campaign_key}")
        create_campaign_dashboard(campaign_key)
    else:
        print(f"\n💡 Dica: Execute com um campaign_key para criar o dashboard automaticamente!")

if __name__ == "__main__":
    main()
