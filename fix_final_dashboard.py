#!/usr/bin/env python3
"""
Corrigir dashboard final com os dados corretos dos quartis
"""

import json
import glob
from datetime import datetime

def fix_final_dashboard():
    """Corrigir dashboard final"""
    
    print("🔧 CORRIGINDO DASHBOARD FINAL COM DADOS CORRETOS")
    print("=" * 70)
    
    # Carregar dados dos quartis corrigidos (Video Starts)
    quartis_files = glob.glob("quartis_corrected_video_starts_*.json")
    if not quartis_files:
        print("❌ Nenhum arquivo de dados dos quartis encontrado")
        return
    
    latest_quartis_file = max(quartis_files)
    print(f"📁 Carregando dados dos quartis: {latest_quartis_file}")
    
    with open(latest_quartis_file, 'r', encoding='utf-8') as f:
        quartis_data = json.load(f)
    
    # Carregar dados com formatação pt-BR
    formatted_files = glob.glob("data_pt_br_formatted_*.json")
    if not formatted_files:
        print("❌ Nenhum arquivo de dados formatados encontrado")
        return
    
    latest_formatted_file = max(formatted_files)
    print(f"📁 Carregando dados formatados: {latest_formatted_file}")
    
    with open(latest_formatted_file, 'r', encoding='utf-8') as f:
        formatted_data = json.load(f)
    
    # Atualizar os dados formatados com os quartis corretos
    print(f"\n🔄 ATUALIZANDO DADOS COM QUARTIS CORRETOS:")
    for key, value in quartis_data.items():
        if key in formatted_data:
            old_value = formatted_data[key]
            formatted_data[key] = value
            print(f"   ✅ {key}: {old_value} -> {value}")
        else:
            formatted_data[key] = value
            print(f"   ✅ {key}: {value} (novo)")
    
    # Salvar dados atualizados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_filename = f"data_pt_br_formatted_corrected_{timestamp}.json"
    
    with open(updated_filename, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS ATUALIZADOS SALVOS: {updated_filename}")
    
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
    
    print(f"\n🔄 APLICANDO SUBSTITUIÇÕES:")
    
    # Substituir variáveis da campanha
    for key, value in campaign_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
        print(f"   ✅ {key}: {value}")
    
    # Substituir variáveis dos dados formatados (PT-BR) - AGORA COM QUARTIS CORRETOS
    for key, value in formatted_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
        if key.startswith("QUARTIL_"):
            print(f"   ✅ {key}: {value}")
    
    # Substituir variáveis dos dados diários
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Substituir variáveis dos gráficos
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    # Verificar se ainda há placeholders não substituídos
    import re
    remaining_placeholders = re.findall(r'\{\{[^}]+\}\}', template_content)
    if remaining_placeholders:
        print(f"\n⚠️  PLACEHOLDERS NÃO SUBSTITUÍDOS:")
        for placeholder in set(remaining_placeholders):
            print(f"   ❌ {placeholder}")
    else:
        print(f"\n✅ TODOS OS PLACEHOLDERS FORAM SUBSTITUÍDOS")
    
    # Verificar se os quartis corretos estão no template
    print(f"\n🔍 VERIFICANDO QUARTIS NO TEMPLATE:")
    expected_quartis = ["91,36%", "76,40%", "59,51%", "56,19%"]
    for quartil in expected_quartis:
        if quartil in template_content:
            print(f"   ✅ {quartil} encontrado")
        else:
            print(f"   ❌ {quartil} NÃO encontrado")
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"static/dash_semana_do_pescado_FIXED_{timestamp}.html"
    
    # Salvar dashboard
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ DASHBOARD CORRIGIDO GERADO!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 QUARTIS CORRIGIDOS (Video Starts como base):")
    print(f"25% ASSISTIDOS: {quartis_data['QUARTIL_25_VALUE']} ({quartis_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {quartis_data['QUARTIL_50_VALUE']} ({quartis_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {quartis_data['QUARTIL_75_VALUE']} ({quartis_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {quartis_data['QUARTIL_100_VALUE']} ({quartis_data['QUARTIL_100_PERCENTAGE']})")
    
    return filename

if __name__ == "__main__":
    fix_final_dashboard()

