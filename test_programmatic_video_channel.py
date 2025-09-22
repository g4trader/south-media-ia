#!/usr/bin/env python3
"""
Teste específico para o canal programmatic_video com dados exatos do usuário
"""

import requests
import json

def test_programmatic_video_with_user_data():
    """Teste com dados exatos que o usuário está tentando usar"""
    
    # Dados exatos baseados no que o usuário está tentando fazer
    user_data = {
        "campaignName": "SEBRAE INSTITUCIONAL SETEMBRO",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Segmentações DoubleVerify - DV: VIDEO Fraud & Invalid Traffic>Fraud & IVT by Site/App>Safe from Fraudulent or No Ads Sites/Apps (100% Invalid Traffic) (13963543)",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    print("🧪 Testando canal programmatic_video com dados do usuário...")
    print(f"📊 Dados enviados: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso!")
            print(f"📊 Dashboard criado: {result['dashboard']['name']}")
            print(f"📄 Arquivo: {result['dashboard']['html_file']}")
            return True
        else:
            print("❌ Erro na API")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_programmatic_video_with_user_data()
    if success:
        print("\n🎉 Teste passou! O canal programmatic_video funciona corretamente.")
        print("O problema deve estar no frontend, não na API.")
    else:
        print("\n❌ Teste falhou! Há um problema com o canal programmatic_video.")
