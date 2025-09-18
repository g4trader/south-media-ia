#!/usr/bin/env python3
"""
Gerar dashboard HTML com dados reais
"""

import json
import os
from datetime import datetime

def format_date_to_dd_mm_aa(date_str):
    """Converter data de YYYY-MM-DD para dd/mm/aa"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%y')
    except:
        return date_str

def generate_dashboard_html(config):
    """Gerar HTML do dashboard com dados reais"""
    
    # Ler template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Converter datas
    start_date = format_date_to_dd_mm_aa(config['startDate'])
    end_date = format_date_to_dd_mm_aa(config['endDate'])
    
    # Obter métricas
    metrics = config['metrics']
    
    # Substituições
    replacements = {
        '{{CAMPAIGN_NAME}}': config['campaignName'],
        '{{CAMPAIGN_ID}}': config['id'],
        '{{START_DATE}}': start_date,
        '{{END_DATE}}': end_date,
        '{{TOTAL_BUDGET}}': f"{config['totalBudget']:,.2f}",
        '{{KPI_TYPE}}': config['kpiType'].upper(),
        '{{KPI_VALUE}}': f"{config['kpiValue']:.2f}",
        '{{KPI_TARGET}}': f"{config['kpiTarget']:,}",
        '{{STRATEGIES}}': config['strategies'],
        '{{STATUS}}': config['status'],
        '{{CREATED_AT}}': config['createdAt'],
        
        # Métricas dinâmicas
        '{{TOTAL_IMPRESSIONS}}': f"{metrics['total_impressions']:,}",
        '{{TOTAL_CLICKS}}': f"{metrics['total_clicks']:,}",
        '{{TOTAL_SPEND}}': f"R$ {metrics['total_spend']:,.2f}",
        '{{TOTAL_CTR}}': f"{metrics['total_ctr']:.2f}%",
        '{{TOTAL_CPV}}': f"R$ {metrics['total_cpv']:.2f}",
        
        # Canais
        '{{CHANNEL_1_NAME}}': config['channels'][0]['displayName'],
        '{{CHANNEL_1_COMPLETION}}': str(metrics['channels']['YouTube']['completion_rate']),
        '{{CHANNEL_2_NAME}}': config['channels'][1]['displayName'],
        '{{CHANNEL_2_COMPLETION}}': str(metrics['channels']['Programática Video']['completion_rate']),
        
        # Configuração JavaScript
        '{{JS_CONFIG}}': json.dumps({
            "campaign": {
                "id": config['id'],
                "name": config['campaignName'],
                "startDate": config['startDate'],
                "endDate": config['endDate'],
                "totalBudget": config['totalBudget'],
                "kpiType": config['kpiType'],
                "kpiValue": config['kpiValue'],
                "kpiTarget": config['kpiTarget'],
                "strategies": config['strategies'],
                "status": config['status'],
                "createdAt": config['createdAt']
            },
            "channels": config['channels'],
            "metrics": metrics
        }, indent=2),
        
        '{{CHANNELS_CONFIG}}': json.dumps({
            "channels": [
                {
                    "display_name": ch['displayName'],
                    "sheet_id": ch['sheetId'],
                    "gid": ch['gid'],
                    "budget": ch['budget'],
                    "quantity": ch['quantity']
                }
                for ch in config['channels']
            ]
        }, indent=2)
    }
    
    # Aplicar substituições
    html_content = template
    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, str(value))
    
    return html_content

def main():
    """Função principal"""
    print("🎯 GERANDO DASHBOARD COM DADOS REAIS")
    print("=" * 50)
    
    # Carregar configuração mais recente
    campaigns_dir = 'campaigns'
    config_files = [f for f in os.listdir(campaigns_dir) if f.startswith('dash_semana_do_pescado_') and f.endswith('.json')]
    if not config_files:
        print("❌ Nenhum arquivo de configuração encontrado")
        return
    
    # Usar o arquivo mais recente
    config_file = os.path.join(campaigns_dir, sorted(config_files)[-1])
    
    if not os.path.exists(config_file):
        print("❌ Arquivo de configuração não encontrado")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"📊 Campanha: {config['campaignName']}")
    print(f"📅 Período: {config['startDate']} a {config['endDate']}")
    print(f"💰 Orçamento: R$ {config['totalBudget']:,.2f}")
    
    # Gerar HTML
    html_content = generate_dashboard_html(config)
    
    # Salvar dashboard
    os.makedirs('static', exist_ok=True)
    dashboard_file = f"static/{config['id']}.html"
    
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard gerado: {dashboard_file}")
    print(f"📊 Impressões: {config['metrics']['total_impressions']:,}")
    print(f"👆 Cliques: {config['metrics']['total_clicks']:,}")
    print(f"💰 Gasto: R$ {config['metrics']['total_spend']:,.2f}")
    print(f"📊 CTR: {config['metrics']['total_ctr']:.2f}%")
    print(f"📊 CPV: R$ {config['metrics']['total_cpv']:.2f}")
    
    print(f"\n🌐 Para visualizar: file://{os.path.abspath(dashboard_file)}")

if __name__ == "__main__":
    main()
