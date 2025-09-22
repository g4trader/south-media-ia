#!/usr/bin/env python3
"""
Script para debugar a seleção de canais
"""

import requests
import json

def test_channel_selection():
    """Testar seleção de canais"""
    
    # Dados de teste
    test_data = {
        "campaignName": "TESTE DEBUG CANAL",
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
                "name": "programmatic_display",
                "displayName": "🎯 Programática Display",
                "sheetId": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    print("🧪 Testando seleção de canal...")
    print(f"📊 Dados enviados: {json.dumps(test_data, indent=2)}")
    
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
            print(f"📊 Dashboard criado: {result.get('dashboard', {}).get('name')}")
        else:
            print("❌ Erro na API")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_channel_selection()
