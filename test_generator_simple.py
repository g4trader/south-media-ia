#!/usr/bin/env python3
"""
Teste simples do gerador de dashboard
"""

import os
import shutil
from campaign_config import CampaignConfig

def test_dashboard_generation():
    """Testar geração de dashboard"""
    print("🧪 Testando geração de dashboard...")
    
    # Criar configuração de teste
    config = CampaignConfig(
        client="Teste Cliente",
        campaign="Teste Campanha",
        sheet_id="1234567890",
        tabs={
            "daily_data": "111111111",
            "contract": "222222222",
            "strategies": "333333333",
            "publishers": "444444444"
        }
    )
    
    # Gerar nome do arquivo
    dashboard_filename = f"dash_{config.get_slug()}.html"
    dashboard_path = f"static/{dashboard_filename}"
    
    print(f"📊 Dashboard será criado: {dashboard_path}")
    
    # Verificar se template existe
    template_path = "static/dash_video_programmatic_template.html"
    if not os.path.exists(template_path):
        print(f"❌ Template não encontrado: {template_path}")
        return False
    
    # Copiar template
    shutil.copy2(template_path, dashboard_path)
    print(f"✅ Dashboard criado: {dashboard_path}")
    
    # Personalizar arquivo
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir campaign_key
    content = content.replace(
        'let campaignKey = urlParams.get(\'campaign\') || \'sebrae_pr\';',
        f'let campaignKey = \'{config.get_slug()}\'; // Definido para {config.client}'
    )
    
    # Salvar arquivo personalizado
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard personalizado para {config.client}")
    
    # Verificar se arquivo foi criado
    if os.path.exists(dashboard_path):
        print(f"✅ Dashboard final criado com sucesso!")
        print(f"📁 Arquivo: {dashboard_path}")
        print(f"🌐 URL: http://localhost:5000/{dashboard_path}")
        return True
    else:
        print(f"❌ Erro: Dashboard não foi criado")
        return False

if __name__ == "__main__":
    test_dashboard_generation()
