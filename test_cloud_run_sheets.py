#!/usr/bin/env python3
"""
Teste específico para verificar Google Sheets no Cloud Run
"""

import requests
import json

def test_cloud_run_sheets():
    """Testar Google Sheets no Cloud Run"""
    print("🔍 Testando Google Sheets no Cloud Run...")
    
    # Testar com a campanha que acabamos de criar
    campaign_key = "sebrae_pr_feira_do_empreendedor_final"
    url = f"https://dashboard-builder-609095880025.us-central1.run.app/api/{campaign_key}/data"
    
    print(f"📡 Testando URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida")
            print(f"📋 Test Mode: {data.get('test_mode', 'N/A')}")
            print(f"📋 Test Message: {data.get('test_message', 'N/A')}")
            print(f"📋 Success: {data.get('success', 'N/A')}")
            
            if 'data' in data:
                campaign_data = data['data']
                print(f"📊 Campaign Name: {campaign_data.get('campaign_name', 'N/A')}")
                print(f"📊 Channel: {campaign_data.get('channel', 'N/A')}")
                
                # Verificar se há dados reais ou simulados
                contract = campaign_data.get('contract', {})
                print(f"💼 Contract Investment: R$ {contract.get('investment', 'N/A')}")
                print(f"💼 VC Contratado: {contract.get('complete_views_contracted', 'N/A')}")
                
                daily_data = campaign_data.get('daily_data', [])
                print(f"📅 Daily Data Records: {len(daily_data)}")
                
                if daily_data:
                    first_day = daily_data[0]
                    print(f"📅 First Day: {first_day.get('date', 'N/A')} - Spend: R$ {first_day.get('spend', 'N/A')}")
                
                # Verificar se os dados são da planilha real ou simulados
                if data.get('test_mode'):
                    print("⚠️ DADOS SIMULADOS - Google Sheets não está funcionando")
                else:
                    print("✅ DADOS REAIS - Google Sheets funcionando!")
                    
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📋 Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_cloud_run_sheets()
