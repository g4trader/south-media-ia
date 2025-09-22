#!/usr/bin/env python3
"""
Debug script to test the frontend form submission with programmatic_video channel
"""

import requests
import json

def test_programmatic_video_channel():
    """Test the API with programmatic_video channel specifically"""
    
    # Test data that matches what the frontend would send
    test_data = {
        "campaignName": "TESTE PROGRAMMATIC VIDEO",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Teste de estratégias",
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
    
    print("🧪 Testando canal programmatic_video...")
    print(f"📊 Dados enviados: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
            json=test_data,
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
        else:
            print("❌ Erro na API")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_programmatic_video_channel()
