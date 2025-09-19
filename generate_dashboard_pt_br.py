#!/usr/bin/env python3
"""
Gerar dashboard final com formatações pt-BR
"""

import json
import glob
from datetime import datetime

def generate_dashboard_pt_br():
    """Gerar dashboard final com formatações pt-BR"""
    
    # Carregar dados com formatação pt-BR
    formatted_files = glob.glob("data_pt_br_formatted_*.json")
    if not formatted_files:
        print("❌ Nenhum arquivo de dados formatados encontrado")
        return
    
    latest_formatted_file = max(formatted_files)
    print(f"📁 Carregando dados formatados: {latest_formatted_file}")
    
    with open(latest_formatted_file, 'r', encoding='utf-8') as f:
        formatted_data = json.load(f)
    
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
    
    # Substituir variáveis dos dados formatados (PT-BR)
    for key, value in formatted_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos dados diários
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos gráficos
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_PT_BR_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD COM FORMATAÇÃO PT-BR GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 CARDS COM FORMATAÇÃO PT-BR:")
    print(f"💰 ORÇAMENTO UTILIZADO: {formatted_data['TOTAL_SPEND_USED']} ({formatted_data['BUDGET_UTILIZATION_PERCENTAGE']})")
    print(f"🎬 IMPRESSÕES/VIEWS UTILIZADAS: {formatted_data['TOTAL_IMPRESSIONS_USED']} ({formatted_data['IMPRESSIONS_UTILIZATION_PERCENTAGE']})")
    print(f"👆 CLIQUES UTILIZADOS: {formatted_data['TOTAL_CLICKS_USED']}")
    print(f"💵 CPV UTILIZADO: {formatted_data['TOTAL_CPV_USED']}")
    print()
    print("📊 QUARTIS COM FORMATAÇÃO PT-BR:")
    print(f"25% ASSISTIDOS: {formatted_data['QUARTIL_25_VALUE']} ({formatted_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {formatted_data['QUARTIL_50_VALUE']} ({formatted_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {formatted_data['QUARTIL_75_VALUE']} ({formatted_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {formatted_data['QUARTIL_100_VALUE']} ({formatted_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 ESTRATÉGIAS COM FORMATAÇÃO PT-BR:")
    print(f"🎬 YouTube: {formatted_data['YOUTUBE_BUDGET']} | {formatted_data['YOUTUBE_VIDEO_COMPLETION']} | {formatted_data['YOUTUBE_CLICKS']} | {formatted_data['YOUTUBE_CTR']} | {formatted_data['YOUTUBE_CPV']} | {formatted_data['YOUTUBE_COMPLETION']}")
    print(f"🎬 Programática: {formatted_data['PROG_BUDGET']} | {formatted_data['PROG_VIDEO_COMPLETION']} | {formatted_data['PROG_CLICKS']} | {formatted_data['PROG_CTR']} | {formatted_data['PROG_CPV']} | {formatted_data['PROG_COMPLETION']}")
    print(f"📊 TOTAL: {formatted_data['TOTAL_BUDGET']} | {formatted_data['TOTAL_VIDEO_COMPLETION']} | {formatted_data['TOTAL_CLICKS']} | {formatted_data['TOTAL_CTR']} | {formatted_data['TOTAL_CPV']} | {formatted_data['TOTAL_COMPLETION']}")
    print()
    print("✅ FORMATAÇÕES PT-BR APLICADAS:")
    print("✅ Números: Ponto para milhares (1.000), vírgula para decimais (0,50)")
    print("✅ Valores monetários: R$ 44.681,12")
    print("✅ Percentuais: 49,6%")
    print("✅ Números grandes: 394.819")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_pt_br()


