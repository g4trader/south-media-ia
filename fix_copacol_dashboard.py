#!/usr/bin/env python3
"""
Script para corrigir o dashboard Copacol quando a API retorna 404
"""

import requests
import json
import time

def fix_copacol_dashboard():
    """Corrigir dashboard Copacol regenerando a campanha"""
    print("🔧 Corrigindo dashboard Copacol...")
    
    base_url = "http://localhost:5001"
    campaign_key = "copacol_institucional_30s"
    
    # 1. Verificar se a API está funcionando
    print("🔍 Verificando API...")
    try:
        response = requests.get(f"{base_url}/api/{campaign_key}/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API já está funcionando!")
                return True
    except:
        pass
    
    print("❌ API retornando 404, regenerando campanha...")
    
    # 2. Regenerar campanha
    campaign_data = {
        "campaign_key": campaign_key,
        "client": "Copacol",
        "campaign": "Institucional 30s",
        "sheet_id": "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8",
        "channel": "Video Programática"
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
                
                # 3. Aguardar um pouco e verificar
                print("⏳ Aguardando processamento...")
                time.sleep(2)
                
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
                        print()
                        print(f"🌐 Dashboard: {base_url}/static/dash_{campaign_key}.html")
                        return True
                
        print("❌ Erro ao regenerar campanha")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    fix_copacol_dashboard()

