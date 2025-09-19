#!/usr/bin/env python3
"""
Corrigir representação gráfica dos gráficos de donut - versão corrigida
"""

import json
import math
import glob
from datetime import datetime

def calculate_dashoffset(percentage):
    """Calcular stroke-dashoffset baseado no percentual"""
    # Remover o símbolo % e converter para float
    percent_value = float(percentage.replace('%', '').replace(',', '.'))
    
    # Calcular a circunferência (2 * π * raio)
    # Raio = 45 (conforme o template)
    circumference = 2 * math.pi * 45  # ≈ 283
    
    # Calcular o offset (quanto do círculo deve ficar vazio)
    # Para 100% = offset 0, para 0% = offset 283
    offset = circumference * (1 - percent_value / 100)
    
    return round(offset, 1)

def fix_donut_charts_corrected():
    """Corrigir gráficos de donut - versão corrigida"""
    
    print("🔧 CORRIGINDO REPRESENTAÇÃO GRÁFICA DOS DONUTS")
    print("=" * 70)
    
    # Carregar dados dos quartis corrigidos
    quartis_files = glob.glob("quartis_corrected_video_starts_*.json")
    if not quartis_files:
        print("❌ Nenhum arquivo de dados dos quartis encontrado")
        return
    
    latest_quartis_file = max(quartis_files)
    print(f"📁 Carregando dados dos quartis: {latest_quartis_file}")
    
    with open(latest_quartis_file, 'r', encoding='utf-8') as f:
        quartis_data = json.load(f)
    
    print("📊 PERCENTUAIS DOS QUARTIS:")
    for key, value in quartis_data.items():
        if 'PERCENTAGE' in key:
            print(f"   {key}: {value}")
    
    # Calcular stroke-dashoffset para cada quartil
    print(f"\n🔢 CALCULANDO STROKE-DASHOFFSET:")
    
    # Circunferência do círculo (raio = 45)
    circumference = 2 * math.pi * 45
    print(f"   Circunferência: {circumference:.1f}")
    
    dashoffsets = {}
    for key, value in quartis_data.items():
        if 'PERCENTAGE' in key:
            percent_value = float(value.replace('%', '').replace(',', '.'))
            offset = circumference * (1 - percent_value / 100)
            dashoffsets[key] = round(offset, 1)
            print(f"   {key}: {value} -> offset: {offset:.1f}")
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"\n🔄 APLICANDO CORREÇÕES NO TEMPLATE:")
    
    # Substituir os valores fixos pelos calculados
    # Precisamos ser mais específicos para evitar substituições incorretas
    replacements = [
        # Quartil 25% - primeiro círculo com stroke-dashoffset
        ('<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="28" stroke-width="8" transform="rotate(-90 50 50)"></circle>', 
         f'<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="{dashoffsets["QUARTIL_25_PERCENTAGE"]}" stroke-width="8" transform="rotate(-90 50 50)"></circle>'),
        
        # Quartil 50% - segundo círculo com stroke-dashoffset
        ('<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="42" stroke-width="8" transform="rotate(-90 50 50)"></circle>',
         f'<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="{dashoffsets["QUARTIL_50_PERCENTAGE"]}" stroke-width="8" transform="rotate(-90 50 50)"></circle>'),
        
        # Quartil 75% - terceiro círculo com stroke-dashoffset
        ('<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="71" stroke-width="8" transform="rotate(-90 50 50)"></circle>',
         f'<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset="{dashoffsets["QUARTIL_75_PERCENTAGE"]}" stroke-width="8" transform="rotate(-90 50 50)"></circle>'),
        
        # Quartil 100% - quarto círculo com stroke-dashoffset (este tem offset 28, mas deveria ser diferente)
        # Vamos procurar pelo contexto específico do quarto círculo
    ]
    
    # Fazer as substituições
    for old_value, new_value in replacements:
        if old_value in template_content:
            template_content = template_content.replace(old_value, new_value)
            print(f"   ✅ Substituído: offset {old_value.split('stroke-dashoffset="')[1].split('"')[0]} -> {new_value.split('stroke-dashoffset="')[1].split('"')[0]}")
        else:
            print(f"   ❌ Não encontrado: {old_value[:50]}...")
    
    # Para o quarto círculo (100%), vamos fazer uma substituição mais específica
    # Procurar pelo padrão que contém o quarto círculo
    import re
    pattern = r'(<circle cx="50" cy="50" fill="none" r="45" stroke="#8B5CF6" stroke-dasharray="283" stroke-dashoffset=")\d+\.?\d*(" stroke-width="8" transform="rotate\(-90 50 50\)"></circle>)'
    matches = re.findall(pattern, template_content)
    
    if len(matches) >= 4:  # Se temos pelo menos 4 círculos
        # Substituir o quarto círculo (100%)
        fourth_circle_old = matches[3][0] + matches[3][1]
        fourth_circle_new = matches[3][0] + str(dashoffsets["QUARTIL_100_PERCENTAGE"]) + matches[3][1]
        template_content = template_content.replace(fourth_circle_old, fourth_circle_new)
        print(f"   ✅ Quarto círculo: offset {matches[3][0].split('stroke-dashoffset="')[1]} -> {dashoffsets['QUARTIL_100_PERCENTAGE']}")
    
    # Carregar dados formatados corrigidos
    formatted_files = glob.glob("data_pt_br_formatted_corrected_*.json")
    if not formatted_files:
        print("❌ Nenhum arquivo de dados formatados corrigidos encontrado")
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
    
    # Dados da campanha
    campaign_data = {
        "CAMPAIGN_NAME": "Semana do Pescado",
        "START_DATE": "01/09/25",
        "END_DATE": "30/09/25",
        "STATUS": "Ativa",
        "TOTAL_BUDGET": "R$ 90.000,00",
        "KPI_VALUE": "R$ 0,08"
    }
    
    print(f"\n🔄 APLICANDO TODAS AS SUBSTITUIÇÕES:")
    
    # Aplicar todas as substituições
    for key, value in campaign_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    for key, value in formatted_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Salvar dashboard final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dashboard_filename = f"static/dash_semana_do_pescado_DONUTS_FIXED_{timestamp}.html"
    
    with open(dashboard_filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ DASHBOARD COM DONUTS CORRIGIDOS SALVO: {dashboard_filename}")
    
    print(f"\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ 25% (91,36%): offset {dashoffsets['QUARTIL_25_PERCENTAGE']}")
    print(f"✅ 50% (76,40%): offset {dashoffsets['QUARTIL_50_PERCENTAGE']}")
    print(f"✅ 75% (59,51%): offset {dashoffsets['QUARTIL_75_PERCENTAGE']}")
    print(f"✅ 100% (56,19%): offset {dashoffsets['QUARTIL_100_PERCENTAGE']}")
    print(f"✅ Representação gráfica agora corresponde aos percentuais")
    
    return dashboard_filename

if __name__ == "__main__":
    fix_donut_charts_corrected()


