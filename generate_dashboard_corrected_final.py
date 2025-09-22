#!/usr/bin/env python3
"""
Gerar dashboard final com dados corrigidos das planilhas
"""

import json
import glob
from datetime import datetime

def generate_dashboard_corrected_final():
    """Gerar dashboard final com dados corrigidos"""
    
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
    
    # Carregar dados corrigidos das planilhas
    corrected_files = glob.glob("data_corrected_*.json")
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
    
    # Substituir variáveis dos dados corrigidos
    for key, value in corrected_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_CORRECTED_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ DASHBOARD FINAL CORRIGIDO GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 MÉTRICAS DE QUARTIS DE VÍDEO (YouTube):")
    print(f"25% ASSISTIDOS: {corrected_data['QUARTIL_25_VALUE']} ({corrected_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {corrected_data['QUARTIL_50_VALUE']} ({corrected_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {corrected_data['QUARTIL_75_VALUE']} ({corrected_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {corrected_data['QUARTIL_100_VALUE']} ({corrected_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 ESTRATÉGIAS (DADOS CORRETOS DAS PLANILHAS):")
    print(f"🎬 YouTube: {corrected_data['YOUTUBE_BUDGET']} | {corrected_data['YOUTUBE_VIDEO_COMPLETION']} | {corrected_data['YOUTUBE_CLICKS']} | {corrected_data['YOUTUBE_CTR']} | {corrected_data['YOUTUBE_CPV']} | {corrected_data['YOUTUBE_COMPLETION']}")
    print(f"🎬 Programática: {corrected_data['PROG_BUDGET']} | {corrected_data['PROG_VIDEO_COMPLETION']} | {corrected_data['PROG_CLICKS']} | {corrected_data['PROG_CTR']} | {corrected_data['PROG_CPV']} | {corrected_data['PROG_COMPLETION']}")
    print(f"📊 TOTAL: {corrected_data['TOTAL_BUDGET']} | {corrected_data['TOTAL_VIDEO_COMPLETION']} | {corrected_data['TOTAL_CLICKS']} | {corrected_data['TOTAL_CTR']} | {corrected_data['TOTAL_CPV']} | {corrected_data['TOTAL_COMPLETION']}")
    print()
    print("✅ CORREÇÕES APLICADAS:")
    print("✅ YouTube: Usando 'Visualizações' como 100% Complete (309.114)")
    print("✅ Programática: Usando coluna '100% Complete' (82.269)")
    print("✅ Total Video Completion: 391.383 (YouTube + Programática 100% Complete)")
    
    return filename

if __name__ == "__main__":
    generate_dashboard_corrected_final()

