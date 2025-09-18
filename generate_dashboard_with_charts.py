#!/usr/bin/env python3
"""
Gerar dashboard final com gráficos corrigidos
"""

import json
import glob
from datetime import datetime

def generate_dashboard_with_charts():
    """Gerar dashboard final com gráficos corrigidos"""
    
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
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_with_charts_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD FINAL GERADO COM GRÁFICOS CORRIGIDOS!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 DADOS DOS GRÁFICOS:")
    print(f"🎬 {charts_data['CHANNEL_1_NAME']}: {charts_data['CHANNEL_1_COMPLETION']}%")
    print(f"🎬 {charts_data['CHANNEL_2_NAME']}: {charts_data['CHANNEL_2_COMPLETION']}%")
    print()
    print("📊 VALORES CONTRATADOS (IMUTÁVEIS):")
    print(f"💰 Orçamento Total: {used_data['TOTAL_BUDGET_CONTRACTED']}")
    print(f"👁️ Impressões Contratadas: {used_data['TOTAL_IMPRESSIONS_CONTRACTED']}")
    print()
    print("📊 VALORES UTILIZADOS (MUTÁVEIS):")
    print(f"💰 Orçamento Utilizado: {used_data['TOTAL_SPEND_USED']}")
    print(f"👁️ Impressões Utilizadas: {used_data['TOTAL_IMPRESSIONS_USED']}")
    print()
    print("📈 PERCENTUAIS DE UTILIZAÇÃO:")
    print(f"💰 Orçamento: {used_data['BUDGET_UTILIZATION_PERCENTAGE']}")
    print(f"👁️ Impressões: {used_data['IMPRESSIONS_UTILIZATION_PERCENTAGE']}")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_with_charts()

