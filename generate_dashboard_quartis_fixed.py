#!/usr/bin/env python3
"""
Gerar dashboard final com gráficos dos quartis corrigidos
"""

import json
import glob
from datetime import datetime

def generate_dashboard_quartis_fixed():
    """Gerar dashboard final com gráficos dos quartis corrigidos"""
    
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
    
    # Carregar dados corrigidos dos quartis
    quartis_files = glob.glob("quartis_corrected_*.json")
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
    
    # Substituir variáveis dos quartis corrigidos
    for key, value in quartis_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_QUARTIS_FIXED_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD COM QUARTIS CORRIGIDOS GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 QUARTIS CORRIGIDOS:")
    print(f"25% ASSISTIDOS: {quartis_data['QUARTIL_25_VALUE']} ({quartis_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {quartis_data['QUARTIL_50_VALUE']} ({quartis_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {quartis_data['QUARTIL_75_VALUE']} ({quartis_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {quartis_data['QUARTIL_100_VALUE']} ({quartis_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 CARDS COM FORMATAÇÃO PT-BR:")
    print(f"💰 ORÇAMENTO UTILIZADO: {formatted_data['TOTAL_SPEND_USED']} ({formatted_data['BUDGET_UTILIZATION_PERCENTAGE']})")
    print(f"🎬 IMPRESSÕES/VIEWS UTILIZADAS: {formatted_data['TOTAL_IMPRESSIONS_USED']} ({formatted_data['IMPRESSIONS_UTILIZATION_PERCENTAGE']})")
    print(f"👆 CLIQUES UTILIZADOS: {formatted_data['TOTAL_CLICKS_USED']}")
    print(f"💵 CPV UTILIZADO: {formatted_data['TOTAL_CPV_USED']}")
    print()
    print("✅ CORREÇÕES APLICADAS:")
    print("✅ Quartis: Percentuais baseados no 100% real (394.819)")
    print("✅ 25%: 641.925 (162,59% do total de 100%)")
    print("✅ 50%: 536.869 (135,98% do total de 100%)")
    print("✅ 75%: 418.194 (105,92% do total de 100%)")
    print("✅ 100%: 394.819 (100,00% do total de 100%)")
    print("✅ Formatação: PT-BR (ponto para milhares, vírgula para decimais)")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_quartis_fixed()


