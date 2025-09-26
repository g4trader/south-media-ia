#!/usr/bin/env python3
"""
Script para corrigir dashboards que estão retornando erro 404
Uso: python3 dashboard_fix.py [campaign_key]
"""

import requests
import json
import time
import sys

def fix_dashboard(campaign_key="copacol_institucional_30s"):
    """Corrigir dashboard específico"""
    print(f"🔧 Corrigindo dashboard: {campaign_key}")
    
    base_url = "http://localhost:5001"
    
    # Configurações das campanhas conhecidas
    campaigns_config = {
        "copacol_institucional_30s": {
            "client": "Copacol",
            "campaign": "Institucional 30s",
            "sheet_id": "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8",
            "channel": "Video Programática"
        }
    }
    
    if campaign_key not in campaigns_config:
        print(f"❌ Campanha '{campaign_key}' não encontrada nas configurações")
        print(f"📋 Campanhas disponíveis: {list(campaigns_config.keys())}")
        return False
    
    config = campaigns_config[campaign_key]
    
    # 1. Verificar se a API está funcionando
    print("🔍 Verificando API...")
    try:
        response = requests.get(f"{base_url}/api/{campaign_key}/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API já está funcionando!")
                campaign = data['data']['campaign_summary']
                print(f"💰 Investimento: R$ {campaign['total_spend']:,.2f}")
                print(f"🎯 VC Realizadas: {campaign['total_video_completions']:,}")
                return True
    except:
        pass
    
    print("❌ API retornando 404, regenerando campanha...")
    
    # 2. Regenerar campanha
    campaign_data = {
        "campaign_key": campaign_key,
        **config
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-dashboard",
            headers={"Content-Type": "application/json"},
            data=json.dumps(campaign_data),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Campanha regenerada com sucesso!")
                
                # 3. Aguardar e verificar
                print("⏳ Aguardando processamento...")
                time.sleep(3)
                
                # 4. Verificar se está funcionando
                response = requests.get(f"{base_url}/api/{campaign_key}/data", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        campaign = data['data']['campaign_summary']
                        print("🎉 Dashboard corrigido com sucesso!")
                        print(f"💰 Investimento: R$ {campaign['total_spend']:,.2f}")
                        print(f"🎯 VC Realizadas: {campaign['total_video_completions']:,}")
                        print(f"💵 CPV Atual: R$ {campaign['cpv']:.2f}")
                        print(f"📈 CTR: {campaign['ctr']:.2f}%")
                        print(f"🎬 VTR: {campaign['vtr']:.1f}%")
                        print()
                        print(f"🌐 Dashboard: {base_url}/static/dash_{campaign_key}.html")
                        return True
                
        print("❌ Erro ao regenerar campanha")
        print(f"Resposta: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def list_campaigns():
    """Listar campanhas disponíveis"""
    print("📋 Campanhas configuradas:")
    campaigns = {
        "copacol_institucional_30s": "Copacol - Institucional 30s"
    }
    
    for key, name in campaigns.items():
        print(f"  {key}: {name}")
    
    print("\n💡 Uso:")
    print("  python3 dashboard_fix.py copacol_institucional_30s")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        campaign_key = sys.argv[1]
        fix_dashboard(campaign_key)
    else:
        list_campaigns()

