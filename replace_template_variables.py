#!/usr/bin/env python3
"""
Script para substituir variáveis no template genérico
"""

def replace_template_variables(template_content: str, campaign_data: dict) -> str:
    """
    Substitui todas as variáveis do template com dados reais
    """
    replacements = {
        'CLIENT_NAME': campaign_data.get('client_name', 'Nome do Cliente'),
        'CAMPAIGN_NAME': campaign_data.get('campaign_name', 'Nome da Campanha'),
        'CAMPAIGN_STATUS': campaign_data.get('campaign_status', 'ATIVA'),
        'CAMPAIGN_PERIOD': campaign_data.get('campaign_period', '01/01/2024 a 31/01/2024'),
        'CAMPAIGN_DESCRIPTION': campaign_data.get('campaign_description', 'Performance do Canal - Complete View'),
        'CAMPAIGN_OBJECTIVES': campaign_data.get('campaign_objectives', 'Objetivos da campanha...'),
        'TOTAL_BUDGET': campaign_data.get('total_budget', '50.000,00'),
        'BUDGET_USED': campaign_data.get('budget_used', '25.000,00'),
        'PACING_PERCENTAGE': campaign_data.get('pacing_percentage', '50'),
        'TARGET_VC': campaign_data.get('target_vc', '500.000'),
        'CPV_CONTRACTED': campaign_data.get('cpv_contracted', '0,10'),
        'CPV_CURRENT': campaign_data.get('cpv_current', '0,12'),
        'PRIMARY_CHANNEL': campaign_data.get('primary_channel', 'YOUTUBE'),
        'CHANNEL_BADGES': campaign_data.get('channel_badges', '<span style="background:rgba(255,107,53,0.2); padding:6px 12px; border-radius:20px; font-size:0.9rem">YOUTUBE</span>'),
        'SEGMENTATION_STRATEGY': campaign_data.get('segmentation_strategy', '<li><strong>🎯 Segmentação:</strong> Estratégia focada em canais específicos</li>'),
        'CREATIVE_STRATEGY': campaign_data.get('creative_strategy', '<li><strong>📱 Criativos:</strong> Testar variações focando nos primeiros segundos</li>'),
        'FORMAT_SPECIFICATIONS': campaign_data.get('format_specifications', '<li>Complete View (30s) para máxima atenção</li>'),
        'API_ENDPOINT': campaign_data.get('api_endpoint', 'https://south-media-ia-609095880025.us-central1.run.app/api/CAMPAIGN_KEY/data'),
        'CAMPAIGN_KEY': campaign_data.get('campaign_key', 'campaign_key_placeholder'),
        'ORIGINAL_HTML': campaign_data.get('original_html', '<!-- HTML original será inserido aqui -->')
    }
    
    result = template_content
    for placeholder, value in replacements.items():
        result = result.replace(f"{{{{{placeholder}}}}}", str(value))
    
    return result

if __name__ == "__main__":
    with open('static/dash_generic_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    campaign_data = {
        "client_name": "SEBRAE PR",
        "campaign_name": "Institucional Setembro",
        "campaign_status": "ATIVA",
        "campaign_period": "01/09/2024 a 30/09/2024",
        "campaign_description": "Performance do YouTube - Complete View",
        "campaign_objectives": "Fortalecer a marca e comunicar valores institucionais",
        "total_budget": "30.000,00",
        "budget_used": "15.000,00",
        "pacing_percentage": "50",
        "target_vc": "300.000",
        "cpv_contracted": "0,10",
        "cpv_current": "0,12",
        "primary_channel": "YOUTUBE",
        "channel_badges": '<span style="background:rgba(255,107,53,0.2); padding:6px 12px; border-radius:20px; font-size:0.9rem">YOUTUBE</span>',
        "api_endpoint": "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_institucional_setembro/data",
        "campaign_key": "sebrae_pr_institucional_setembro"
    }
    
    result = replace_template_variables(template, campaign_data)
    
    with open('static/dash_test_output.html', 'w', encoding='utf-8') as f:
        f.write(result)
    
    print("✅ Template processado e salvo em static/dash_test_output.html")

