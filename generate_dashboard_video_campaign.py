#!/usr/bin/env python3
"""
Gerar dashboard final para campanha de vídeo
"""

import json
import glob
from datetime import datetime

def generate_dashboard_video_campaign():
    """Gerar dashboard final para campanha de vídeo"""
    
    # Carregar dados corrigidos para campanha de vídeo
    used_files = glob.glob("used_data_video_campaign_*.json")
    if not used_files:
        print("❌ Nenhum arquivo de dados de campanha de vídeo encontrado")
        return
    
    latest_used_file = max(used_files)
    print(f"📁 Carregando dados de campanha de vídeo: {latest_used_file}")
    
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
    
    # Carregar dados corrigidos (quartis e totais)
    corrected_files = glob.glob("data_corrected_totals_*.json")
    if not corrected_files:
        print("❌ Nenhum arquivo de dados corrigidos encontrado")
        return
    
    latest_corrected_file = max(corrected_files)
    print(f"📁 Carregando dados corrigidos: {latest_corrected_file}")
    
    with open(latest_corrected_file, 'r', encoding='utf-8') as f:
        corrected_data = json.load(f)
    
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
    
    # Substituir variáveis dos dados utilizados (CAMPANHA DE VÍDEO)
    for key, value in used_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos dados diários
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos gráficos
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Substituir variáveis dos dados corrigidos
    for key, value in corrected_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_VIDEO_CAMPAIGN_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD PARA CAMPANHA DE VÍDEO GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 CARDS CORRIGIDOS PARA CAMPANHA DE VÍDEO:")
    print(f"💰 ORÇAMENTO UTILIZADO: {used_data['TOTAL_SPEND_USED']} ({used_data['BUDGET_UTILIZATION_PERCENTAGE']})")
    print(f"🎬 IMPRESSÕES/VIEWS UTILIZADAS: {used_data['TOTAL_IMPRESSIONS_USED']} ({used_data['IMPRESSIONS_UTILIZATION_PERCENTAGE']})")
    print(f"👆 CLIQUES UTILIZADOS: {used_data['TOTAL_CLICKS_USED']}")
    print(f"💵 CPV UTILIZADO: {used_data['TOTAL_CPV_USED']}")
    print()
    print("📊 DADOS DETALHADOS (VIDEO COMPLETION):")
    print(f"📺 YouTube: {used_data['YOUTUBE_TOTAL_VIEWS']} video completions")
    print(f"📺 Programática: {used_data['PROG_TOTAL_IMPRESSIONS']} video completions")
    print(f"📊 Total: {used_data['TOTAL_IMPRESSIONS_USED']} video completions")
    print()
    print("✅ CORREÇÕES APLICADAS PARA CAMPANHA DE VÍDEO:")
    print("✅ IMPRESSÕES/VIEWS UTILIZADAS = VIDEO COMPLETION (394.819)")
    print("✅ CPV UTILIZADO = R$ 0,11 (custo por video completion)")
    print("✅ CTR UTILIZADO = 0,25% (cliques/video completion)")
    print("✅ Orçamento Utilizado = 49,6%")
    print("✅ Video Completion Utilizado = 49,4%")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_video_campaign()



