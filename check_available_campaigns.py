#!/usr/bin/env python3
"""
Script para verificar quais campanhas têm dados disponíveis
"""

import requests
import json

def check_campaign(campaign_key, api_url="https://mvp-dashboard-builder-609095880025.us-central1.run.app"):
    """Verificar se uma campanha tem dados disponíveis"""
    
    url = f"{api_url}/api/{campaign_key}/data"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            daily_data_count = len(data.get('daily_data', [])) if data.get('daily_data') else 0
            
            return {
                "campaign_key": campaign_key,
                "status": "✅ OK",
                "has_data": True,
                "daily_records": daily_data_count,
                "has_campaign_summary": bool(data.get('campaign_summary')),
                "has_contract": bool(data.get('contract'))
            }
        else:
            return {
                "campaign_key": campaign_key,
                "status": f"❌ Erro {response.status_code}",
                "has_data": False
            }
    
    except Exception as e:
        return {
            "campaign_key": campaign_key,
            "status": f"❌ Erro: {str(e)[:50]}",
            "has_data": False
        }

def main():
    """Função principal"""
    
    print("🔍 Verificando campanhas disponíveis...\n")
    
    # Lista de campanhas para verificar (baseado nos arquivos HTML)
    campaigns = [
        "copacol_video_de_30s_campanha_institucional_netflix",
        "copacol_campanha_institucional_de_video_de_90s_em_youtube",
        "copacol_institucional_30s_programatica",
        "copacol_remarketing_youtube",
        "sebrae_pr_feira_do_empreendedor",
        "sesi_institucional_native",
        "senai_linkedin_sponsored_video",
        "copacol_mestre_das_grelhas",
        "copacol_semana_do_pescado",
        "dauher_hidrabene",
        "iquine_pin_pinterest"
    ]
    
    results = []
    
    for campaign in campaigns:
        print(f"📊 Verificando: {campaign}")
        result = check_campaign(campaign)
        results.append(result)
        
        if result['has_data']:
            print(f"   {result['status']} - {result['daily_records']} registros diários")
        else:
            print(f"   {result['status']}")
        print()
    
    # Salvar resultados
    with open("available_campaigns.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DE CAMPANHAS DISPONÍVEIS:\n")
    
    available = [r for r in results if r['has_data']]
    
    if available:
        print(f"✅ {len(available)} campanhas com dados disponíveis:\n")
        for r in available:
            print(f"   🎯 {r['campaign_key']}")
            print(f"      Dashboard: http://localhost:8080/static/dash_{r['campaign_key']}.html")
            print(f"      Registros: {r['daily_records']} dias de dados")
            print()
    else:
        print("❌ Nenhuma campanha com dados disponíveis")
    
    print(f"\n📁 Resultados salvos em: available_campaigns.json")

if __name__ == "__main__":
    main()
