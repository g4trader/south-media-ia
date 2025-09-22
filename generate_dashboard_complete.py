#!/usr/bin/env python3
"""
Gerar dashboard completo com todos os dados corrigidos
"""

import json
import glob
from datetime import datetime

def generate_dashboard_complete():
    """Gerar dashboard completo com todos os dados"""
    
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
    
    # Carregar dados dos quartis e estratégias
    quartis_files = glob.glob("quartis_strategies_data_*.json")
    if not quartis_files:
        print("❌ Nenhum arquivo de dados dos quartis encontrado")
        return
    
    latest_quartis_file = max(quartis_files)
    print(f"📁 Carregando dados dos quartis: {latest_quartis_file}")
    
    with open(latest_quartis_file, 'r', encoding='utf-8') as f:
        quartis_data = json.load(f)
    
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
    
    # Substituir variáveis dos quartis e estratégias
    for key, value in quartis_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_complete_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD COMPLETO GERADO COM TODOS OS DADOS!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 MÉTRICAS DE QUARTIS DE VÍDEO:")
    print(f"25% ASSISTIDOS: {quartis_data['QUARTIL_25_VALUE']} ({quartis_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {quartis_data['QUARTIL_50_VALUE']} ({quartis_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {quartis_data['QUARTIL_75_VALUE']} ({quartis_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {quartis_data['QUARTIL_100_VALUE']} ({quartis_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 ESTRATÉGIAS:")
    print(f"🎬 YouTube: {quartis_data['YOUTUBE_BUDGET']} | {quartis_data['YOUTUBE_VIDEO_COMPLETION']} | {quartis_data['YOUTUBE_CLICKS']} | {quartis_data['YOUTUBE_CTR']} | {quartis_data['YOUTUBE_CPV']} | {quartis_data['YOUTUBE_COMPLETION']}")
    print(f"🎬 Programática: {quartis_data['PROG_BUDGET']} | {quartis_data['PROG_VIDEO_COMPLETION']} | {quartis_data['PROG_CLICKS']} | {quartis_data['PROG_CTR']} | {quartis_data['PROG_CPV']} | {quartis_data['PROG_COMPLETION']}")
    print(f"📊 TOTAL: {quartis_data['TOTAL_BUDGET']} | {quartis_data['TOTAL_VIDEO_COMPLETION']} | {quartis_data['TOTAL_CLICKS']} | {quartis_data['TOTAL_CTR']} | {quartis_data['TOTAL_CPV']} | {quartis_data['TOTAL_COMPLETION']}")
    print()
    print("📊 DADOS DOS GRÁFICOS:")
    print(f"🎬 {charts_data['CHANNEL_1_NAME']}: {charts_data['CHANNEL_1_COMPLETION']}%")
    print(f"🎬 {charts_data['CHANNEL_2_NAME']}: {charts_data['CHANNEL_2_COMPLETION']}%")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_complete()

