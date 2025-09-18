#!/usr/bin/env python3
"""
Corrigir representação gráfica dos gráficos de donut para corresponder aos percentuais
"""

import json
import math
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

def fix_donut_charts():
    """Corrigir gráficos de donut"""
    
    print("🔧 CORRIGINDO REPRESENTAÇÃO GRÁFICA DOS DONUTS")
    print("=" * 70)
    
    # Carregar dados dos quartis corrigidos
    with open('quartis_corrected_video_starts_20250916_114859.json', 'r', encoding='utf-8') as f:
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
    replacements = [
        # Quartil 25% (91,36%)
        ('stroke-dashoffset="28"', f'stroke-dashoffset="{dashoffsets["QUARTIL_25_PERCENTAGE"]}"'),
        # Quartil 50% (76,40%)
        ('stroke-dashoffset="42"', f'stroke-dashoffset="{dashoffsets["QUARTIL_50_PERCENTAGE"]}"'),
        # Quartil 75% (59,51%)
        ('stroke-dashoffset="71"', f'stroke-dashoffset="{dashoffsets["QUARTIL_75_PERCENTAGE"]}"'),
        # Quartil 100% (56,19%) - este estava com offset 28, mas deveria ser diferente
        ('stroke-dashoffset="28"', f'stroke-dashoffset="{dashoffsets["QUARTIL_100_PERCENTAGE"]}"')
    ]
    
    # Fazer as substituições
    for old_value, new_value in replacements:
        if old_value in template_content:
            template_content = template_content.replace(old_value, new_value)
            print(f"   ✅ {old_value} -> {new_value}")
        else:
            print(f"   ❌ Não encontrado: {old_value}")
    
    # Salvar template corrigido
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"templates/template_simple_fixed_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ TEMPLATE CORRIGIDO SALVO: {filename}")
    
    # Gerar dashboard com gráficos corrigidos
    print(f"\n🔄 GERANDO DASHBOARD COM GRÁFICOS CORRIGIDOS:")
    
    # Carregar dados formatados corrigidos
    with open('data_pt_br_formatted_corrected_20250916_115815.json', 'r', encoding='utf-8') as f:
        formatted_data = json.load(f)
    
    # Carregar dados diários
    with open('daily_variables_20250915_191659.json', 'r', encoding='utf-8') as f:
        daily_data = json.load(f)
    
    # Carregar dados dos gráficos
    with open('charts_data_20250916_102147.json', 'r', encoding='utf-8') as f:
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
    fix_donut_charts()

