#!/usr/bin/env python3
"""
Gerar dashboard com dados reais das planilhas
"""

import json
import os
from datetime import datetime

def generate_dashboard_from_real_data():
    """Gerar dashboard a partir dos dados reais"""
    
    print("🎯 GERANDO DASHBOARD COM DADOS REAIS")
    print("=" * 60)
    
    # Carregar configuração mais recente
    campaigns_dir = "campaigns"
    config_files = [f for f in os.listdir(campaigns_dir) if f.startswith("campaign_real_data_")]
    
    if not config_files:
        print("❌ Nenhuma configuração de dados reais encontrada")
        return
    
    # Pegar o arquivo mais recente
    latest_config = sorted(config_files)[-1]
    config_path = os.path.join(campaigns_dir, latest_config)
    
    print(f"📂 Carregando configuração: {latest_config}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Carregar template
    template_path = "templates/template_simple.html"
    print(f"📄 Carregando template: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Substituir variáveis no template
    print("🔄 Substituindo variáveis no template...")
    
    # Carregar variáveis diárias
    import glob
    daily_files = glob.glob("daily_variables_*.json")
    if daily_files:
        latest_daily = sorted(daily_files)[-1]
        with open(latest_daily, 'r', encoding='utf-8') as f:
            daily_vars = json.load(f)
        print(f"📊 Carregando variáveis diárias de: {latest_daily}")
    else:
        daily_vars = {}
        print("⚠️ Nenhuma variável diária encontrada")
    
    # Carregar dados utilizados
    used_files = glob.glob("used_data_*.json")
    if used_files:
        latest_used = sorted(used_files)[-1]
        with open(latest_used, 'r', encoding='utf-8') as f:
            used_vars = json.load(f)
        print(f"📊 Carregando dados utilizados de: {latest_used}")
    else:
        used_vars = {}
        print("⚠️ Nenhum dado utilizado encontrado")
    
    # Dados básicos da campanha
    template_content = template_content.replace('{{CAMPAIGN_NAME}}', config['campaign_name'])
    template_content = template_content.replace('{{START_DATE}}', config['start_date'])
    template_content = template_content.replace('{{END_DATE}}', config['end_date'])
    template_content = template_content.replace('{{STATUS}}', 'active')
    template_content = template_content.replace('{{TOTAL_BUDGET}}', f"R$ {config['total_budget']:,.2f}")
    template_content = template_content.replace('{{KPI_VALUE}}', f"R$ {config['kpi_value']:.2f}")
    
    # Variáveis da aba Entrega Diária
    template_content = template_content.replace('{{YOUTUBE_AVG_VIEWS}}', daily_vars.get('YOUTUBE_AVG_VIEWS', '0'))
    template_content = template_content.replace('{{YOUTUBE_AVG_INVESTMENT}}', daily_vars.get('YOUTUBE_AVG_INVESTMENT', 'R$ 0,00'))
    template_content = template_content.replace('{{YOUTUBE_AVG_CLICKS}}', daily_vars.get('YOUTUBE_AVG_CLICKS', '0'))
    template_content = template_content.replace('{{YOUTUBE_AVG_CTR}}', daily_vars.get('YOUTUBE_AVG_CTR', '0.00'))
    template_content = template_content.replace('{{PROG_AVG_IMPRESSIONS}}', daily_vars.get('PROG_AVG_IMPRESSIONS', '0'))
    template_content = template_content.replace('{{PROG_AVG_INVESTMENT}}', daily_vars.get('PROG_AVG_INVESTMENT', 'R$ 0,00'))
    template_content = template_content.replace('{{PROG_AVG_CLICKS}}', daily_vars.get('PROG_AVG_CLICKS', '0'))
    template_content = template_content.replace('{{PROG_AVG_CTR}}', daily_vars.get('PROG_AVG_CTR', '0.00'))
    template_content = template_content.replace('{{DAILY_DATA_TABLE_ROWS}}', daily_vars.get('DAILY_DATA_TABLE_ROWS', ''))
    
    # Dados utilizados (calculados a partir dos dados diários)
    template_content = template_content.replace('{{TOTAL_SPEND_USED}}', used_vars.get('TOTAL_SPEND_USED', 'R$ 0,00'))
    template_content = template_content.replace('{{TOTAL_CLICKS_USED}}', used_vars.get('TOTAL_CLICKS_USED', '0'))
    template_content = template_content.replace('{{TOTAL_IMPRESSIONS_USED}}', used_vars.get('TOTAL_IMPRESSIONS_USED', '0'))
    template_content = template_content.replace('{{TOTAL_CPV_USED}}', used_vars.get('TOTAL_CPV_USED', 'R$ 0,00'))
    template_content = template_content.replace('{{TOTAL_CTR_USED}}', used_vars.get('TOTAL_CTR_USED', '0.00%'))
    template_content = template_content.replace('{{BUDGET_UTILIZATION_PERCENTAGE}}', used_vars.get('BUDGET_UTILIZATION_PERCENTAGE', '0.0%'))
    template_content = template_content.replace('{{IMPRESSIONS_UTILIZATION_PERCENTAGE}}', used_vars.get('IMPRESSIONS_UTILIZATION_PERCENTAGE', '0.0%'))
    
    # Dados consolidados (mantidos para compatibilidade)
    cons = config['consolidated_metrics']
    template_content = template_content.replace('{{TOTAL_IMPRESSIONS}}', f"{cons['total_impressions']:,}")
    template_content = template_content.replace('{{TOTAL_SPEND}}', f"R$ {cons['total_spend']:,.2f}")
    template_content = template_content.replace('{{TOTAL_CTR}}', f"{cons['total_clicks']/cons['total_impressions']*100:.2f}%")
    template_content = template_content.replace('{{TOTAL_CLICKS}}', f"{cons['total_clicks']:,}")
    template_content = template_content.replace('{{TOTAL_CPV}}', f"R$ {cons['total_spend']/cons['total_impressions']:.2f}")
    
    # Dados dos canais
    channels = config['channels']
    if len(channels) >= 1:
        ch1 = channels[0]
        template_content = template_content.replace('{{CHANNEL_1_NAME}}', ch1['display_name'])
        template_content = template_content.replace('{{CHANNEL_1_COMPLETION}}', f"{ch1['actual_spend']/ch1['budget']*100:.1f}%")
        template_content = template_content.replace('{{CHANNEL_1_SPEND}}', f"R$ {ch1['actual_spend']:,.2f}")
        template_content = template_content.replace('{{CHANNEL_1_CLICKS}}', f"{ch1['actual_clicks']:,}")
        template_content = template_content.replace('{{CHANNEL_1_IMPRESSIONS}}', f"{ch1['actual_impressions']:,}")
        template_content = template_content.replace('{{CHANNEL_1_CTR}}', f"{ch1['actual_ctr']*100:.2f}%")
        template_content = template_content.replace('{{CHANNEL_1_CPV}}', f"R$ {ch1['actual_cpv']:.2f}")
    
    if len(channels) >= 2:
        ch2 = channels[1]
        template_content = template_content.replace('{{CHANNEL_2_NAME}}', ch2['display_name'])
        template_content = template_content.replace('{{CHANNEL_2_COMPLETION}}', f"{ch2['actual_spend']/ch2['budget']*100:.1f}%")
        template_content = template_content.replace('{{CHANNEL_2_SPEND}}', f"R$ {ch2['actual_spend']:,.2f}")
        template_content = template_content.replace('{{CHANNEL_2_CLICKS}}', f"{ch2['actual_clicks']:,}")
        template_content = template_content.replace('{{CHANNEL_2_IMPRESSIONS}}', f"{ch2['actual_impressions']:,}")
        template_content = template_content.replace('{{CHANNEL_2_CTR}}', f"{ch2['actual_ctr']*100:.2f}%")
        template_content = template_content.replace('{{CHANNEL_2_CPV}}', f"R$ {ch2['actual_cpv']:.2f}")
    
    # Configuração JavaScript
    js_config = {
        "campaign": {
            "name": config['campaign_name'],
            "startDate": config['start_date'],
            "endDate": config['end_date'],
            "totalBudget": config['total_budget'],
            "kpiType": config['kpi_type'],
            "kpiValue": config['kpi_value']
        },
        "channels": []
    }
    
    for channel in channels:
        js_config["channels"].append({
            "name": channel['name'],
            "displayName": channel['display_name'],
            "budget": channel['budget'],
            "quantity": channel['quantity'],
            "actualSpend": channel['actual_spend'],
            "actualClicks": channel['actual_clicks'],
            "actualImpressions": channel['actual_impressions'],
            "actualCTR": channel['actual_ctr'],
            "actualCPV": channel['actual_cpv']
        })
    
    js_config_str = json.dumps(js_config, indent=2, ensure_ascii=False)
    template_content = template_content.replace('{{JS_CONFIG}}', js_config_str)
    
    # Configuração dos canais
    channels_config = {
        "channels": []
    }
    
    for channel in channels:
        channels_config["channels"].append({
            "sheet_id": channel['sheet_id'],
            "gid": channel['gid'],
            "display_name": channel['display_name'],
            "budget": channel['budget'],
            "quantity": channel['quantity']
        })
    
    channels_config_str = json.dumps(channels_config, indent=2, ensure_ascii=False)
    template_content = template_content.replace('{{CHANNELS_CONFIG}}', channels_config_str)
    
    # Salvar dashboard
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dashboard_filename = f"static/dash_{config['campaign_name'].lower().replace(' ', '_')}_{timestamp}.html"
    
    with open(dashboard_filename, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ Dashboard gerado: {dashboard_filename}")
    print(f"📊 Campanha: {config['campaign_name']}")
    print(f"💰 Orçamento: R$ {config['total_budget']:,.2f}")
    print(f"📺 Canais: {len(channels)}")
    
    return dashboard_filename

if __name__ == "__main__":
    dashboard_file = generate_dashboard_from_real_data()
    if dashboard_file:
        print(f"\n🎉 Dashboard criado com sucesso!")
        print(f"📂 Arquivo: {dashboard_file}")
        print(f"🌐 Abra no navegador para visualizar")
