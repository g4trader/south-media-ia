#!/usr/bin/env python3
"""
Gerar dashboard final com aba Análise e Insights atualizada
"""

import json
import glob
from datetime import datetime

def generate_dashboard_insights_updated():
    """Gerar dashboard com insights atualizados"""
    
    print("🔄 GERANDO DASHBOARD COM INSIGHTS ATUALIZADOS")
    print("=" * 70)
    
    # Carregar template atualizado
    template_files = glob.glob("templates/template_simple_insights_updated_*.html")
    if not template_files:
        print("❌ Nenhum template atualizado encontrado")
        return
    
    latest_template = max(template_files)
    print(f"📁 Carregando template: {latest_template}")
    
    with open(latest_template, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
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
    
    # Carregar dados dos quartis corrigidos
    quartis_files = glob.glob("quartis_corrected_video_starts_*.json")
    if not quartis_files:
        print("❌ Nenhum arquivo de dados dos quartis encontrado")
        return
    
    latest_quartis_file = max(quartis_files)
    print(f"📁 Carregando dados dos quartis: {latest_quartis_file}")
    
    with open(latest_quartis_file, 'r', encoding='utf-8') as f:
        quartis_data = json.load(f)
    
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
        print(f"   ✅ {key}: {value}")
    
    for key, value in formatted_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    for key, value in daily_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    for key, value in charts_data.items():
        if key.startswith("CHANNEL_"):
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    for key, value in quartis_data.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", value)
    
    # Salvar dashboard final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dashboard_filename = f"static/dash_semana_do_pescado_INSIGHTS_UPDATED_{timestamp}.html"
    
    with open(dashboard_filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ DASHBOARD COM INSIGHTS ATUALIZADOS SALVO: {dashboard_filename}")
    
    # Verificar se os insights estão no dashboard
    print(f"\n🔍 VERIFICANDO INSIGHTS NO DASHBOARD:")
    
    # Verificar se os dados dos insights estão presentes
    insights_checks = [
        "YouTube: Excelente Retenção",
        "Programática Video: Alto Engajamento",
        "Superação de Meta",
        "Otimização de Budget",
        "Estratégia Vencedora",
        "Formato Ideal"
    ]
    
    for check in insights_checks:
        if check in template_content:
            print(f"   ✅ {check}")
        else:
            print(f"   ❌ {check}")
    
    print(f"\n📊 RESUMO:")
    print(f"✅ Template atualizado com insights coerentes")
    print(f"✅ Dados formatados aplicados")
    print(f"✅ Dados diários aplicados")
    print(f"✅ Dados dos gráficos aplicados")
    print(f"✅ Dados dos quartis aplicados")
    print(f"✅ Dashboard final gerado")
    
    return dashboard_filename

if __name__ == "__main__":
    generate_dashboard_insights_updated()



