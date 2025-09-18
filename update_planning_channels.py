#!/usr/bin/env python3
"""
Atualizar quadro CANAIS DE MÍDIA na aba Planejamento
"""

import json
import glob
from datetime import datetime

def update_planning_channels():
    """Atualizar quadro CANAIS DE MÍDIA"""
    
    print("🔄 ATUALIZANDO QUADRO CANAIS DE MÍDIA")
    print("=" * 70)
    
    # Carregar dados da campanha para obter informações dos canais
    campaign_files = glob.glob("campaigns/campaign_corrected_*.json")
    if not campaign_files:
        print("❌ Nenhum arquivo de dados da campanha encontrado")
        return
    
    latest_campaign_file = max(campaign_files)
    print(f"📁 Carregando dados da campanha: {latest_campaign_file}")
    
    with open(latest_campaign_file, 'r', encoding='utf-8') as f:
        campaign_data = json.load(f)
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"\n📊 CANAIS DA CAMPANHA:")
    for channel in campaign_data.get('channels', []):
        print(f"   - {channel.get('name', 'N/A')}: R$ {channel.get('budget', 0):,.2f}")
    
    # Procurar pela seção de canais de mídia
    print(f"\n🔍 PROCURANDO SEÇÃO CANAIS DE MÍDIA:")
    
    import re
    
    # Padrão para encontrar a seção de canais de mídia
    channels_pattern = r'(<h3 style="font-size: 1rem; font-weight: bold; color: white; margin-bottom: 1rem;">📺 CANAIS DE MÍDIA</h3>\s*<div style="display: flex; flex-direction: column; gap: 0\.75rem;">)(.*?)(</div>\s*</div>)'
    
    channels_match = re.search(channels_pattern, template_content, re.DOTALL)
    
    if channels_match:
        print(f"   ✅ Seção CANAIS DE MÍDIA encontrada")
        
        # Gerar novo conteúdo de canais
        new_channels_content = generate_channels_content(campaign_data)
        
        # Substituir o conteúdo
        new_section = channels_match.group(1) + new_channels_content + channels_match.group(3)
        template_content = template_content.replace(channels_match.group(0), new_section)
        
        print(f"   ✅ Conteúdo dos canais substituído")
        
    else:
        print(f"   ❌ Seção CANAIS DE MÍDIA não encontrada")
        return None
    
    # Salvar template atualizado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_template = f"templates/template_simple_planning_updated_{timestamp}.html"
    
    with open(updated_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ Template atualizado salvo: {updated_template}")
    
    return updated_template

def generate_channels_content(campaign_data):
    """Gerar conteúdo HTML para os canais de mídia"""
    
    channels = campaign_data.get('channels', [])
    content = ""
    
    # Cores e ícones para cada canal
    channel_configs = {
        'YouTube': {
            'color': '#FF0000',
            'bg_color': 'rgba(255, 0, 0, 0.2)',
            'border_color': '#FF0000',
            'icon': '📺',
            'description': 'Plataforma de vídeo com alta retenção e engajamento'
        },
        'Programática Video': {
            'color': '#8B5CF6',
            'bg_color': 'rgba(139, 92, 246, 0.2)',
            'border_color': '#8B5CF6',
            'icon': '🎯',
            'description': 'Programática com whitelist de sites premium para brand safety'
        },
        'Programática Display': {
            'color': '#3B82F6',
            'bg_color': 'rgba(59, 130, 246, 0.2)',
            'border_color': '#3B82F6',
            'icon': '📊',
            'description': 'Display programático com segmentação avançada'
        }
    }
    
    for channel in channels:
        channel_name = channel.get('name', '')
        budget = channel.get('budget', 0)
        quantity = channel.get('quantity', 0)
        
        # Obter configuração do canal
        config = channel_configs.get(channel_name, {
            'color': '#6B7280',
            'bg_color': 'rgba(107, 114, 128, 0.2)',
            'border_color': '#6B7280',
            'icon': '📱',
            'description': 'Canal de mídia digital'
        })
        
        # Formatar valores
        budget_formatted = f"R$ {budget:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        quantity_formatted = f"{quantity:,.0f}".replace(',', '.')
        
        content += f'''<div style="background: {config['bg_color']}; padding: 1rem; border-radius: 8px; border: 1px solid {config['border_color']};">
<div style="font-weight: bold; color: {config['color']}; font-size: 0.875rem; margin-bottom: 0.25rem;">{config['icon']} {channel_name}</div>
<div style="color: white; font-size: 0.75rem; margin-bottom: 0.5rem;">{config['description']}</div>
<div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #9CA3AF;">
<span>Orçamento: {budget_formatted}</span>
<span>Meta: {quantity_formatted}</span>
</div>
</div>
'''
    
    return content

if __name__ == "__main__":
    update_planning_channels()
