#!/usr/bin/env python3
"""
Gerar dashboard final com dados atualizados (YouTube com coluna 100%)
"""

import json
import glob
from datetime import datetime

def generate_dashboard_updated_final():
    """Gerar dashboard final com dados atualizados"""
    
    # Carregar dados corrigidos
    used_files = glob.glob("used_data_corrected_*.json")
    if not used_files:
        print("❌ Nenhum arquivo de dados corrigidos encontrado")
        return
    
    latest_used_file = max(used_files)
    print(f"📁 Carregando dados corrigidos: {latest_used_file}")
    
    with open(latest_used_file, 'r', encoding='utf-8') as f:
        used_data = json.load(f)
    
    # Carregar dados diários
    daily_files = glob.glob("daily_variables_*.json")
    if not daily_files:
        print("❌ Nenhum arquivo de dados diários encontrado")
        return
    
    latest_daily_file = max(daily_files)
    print(f"📁 Carregando dados diários: {latest_daily_file}")
    
    with open(latest_daily_file, 'r', encoding='utf-8') as f:
        daily_data = json.load(f)
    
    # Carregar dados dos gráficos
    charts_files = glob.glob("charts_data_*.json")
    if not charts_files:
        print("❌ Nenhum arquivo de dados dos gráficos encontrado")
        return
    
    latest_charts_file = max(charts_files)
    print(f"📁 Carregando dados dos gráficos: {latest_charts_file}")
    
    with open(latest_charts_file, 'r', encoding='utf-8') as f:
        charts_data = json.load(f)
    
    # Carregar dados atualizados (YouTube com coluna 100%)
    updated_files = glob.glob("data_updated_youtube_100_*.json")
    if not updated_files:
        print("❌ Nenhum arquivo de dados atualizados encontrado")
        return
    
    latest_updated_file = max(updated_files)
    print(f"📁 Carregando dados atualizados: {latest_updated_file}")
    
    with open(latest_updated_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Dados da campanha
    campaign_data = {
        "CAMPAIGN_NAME": "Semana do Pescado",
        "START_DATE": "01/09/25",
        "END_DATE": "30/09/25",
        "STATUS": "Ativa",
        "TOTAL_BUDGET": "R$ 90.000,00",
        "KPI_VALUE": "R$ 0,08"
    }
    
    # Substituir variáveis da campanha
    for key, value in campaign_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos dados utilizados
    for key, value in used_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos dados diários
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos gráficos
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Substituir variáveis dos dados atualizados
    for key, value in updated_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_UPDATED_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD FINAL ATUALIZADO GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 MÉTRICAS DE QUARTIS DE VÍDEO (YouTube com coluna 100%):")
    print(f"25% ASSISTIDOS: {updated_data['QUARTIL_25_VALUE']} ({updated_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {updated_data['QUARTIL_50_VALUE']} ({updated_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {updated_data['QUARTIL_75_VALUE']} ({updated_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {updated_data['QUARTIL_100_VALUE']} ({updated_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 ESTRATÉGIAS (DADOS ATUALIZADOS COM COLUNA 100%):")
    print(f"🎬 YouTube: {updated_data['YOUTUBE_BUDGET']} | {updated_data['YOUTUBE_VIDEO_COMPLETION']} | {updated_data['YOUTUBE_CLICKS']} | {updated_data['YOUTUBE_CTR']} | {updated_data['YOUTUBE_CPV']} | {updated_data['YOUTUBE_COMPLETION']}")
    print(f"🎬 Programática: {updated_data['PROG_BUDGET']} | {updated_data['PROG_VIDEO_COMPLETION']} | {updated_data['PROG_CLICKS']} | {updated_data['PROG_CTR']} | {updated_data['PROG_CPV']} | {updated_data['PROG_COMPLETION']}")
    print(f"📊 TOTAL: {updated_data['TOTAL_BUDGET']} | {updated_data['TOTAL_VIDEO_COMPLETION']} | {updated_data['TOTAL_CLICKS']} | {updated_data['TOTAL_CTR']} | {updated_data['TOTAL_CPV']} | {updated_data['TOTAL_COMPLETION']}")
    print()
    print("✅ ATUALIZAÇÕES APLICADAS:")
    print("✅ YouTube: Usando coluna 'Video assistido 100%' real (307.515)")
    print("✅ Programática: Usando coluna '100% Video Complete' real (87.304)")
    print("✅ Total Video Completion: 394.819 (soma correta das colunas 100%)")
    print("✅ Quartis: Baseados na coluna 100% real do YouTube")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_updated_final()



