#!/usr/bin/env python3
"""
Debug script para testar exatamente os dados que o frontend está enviando
"""

import requests
import json

def test_exact_frontend_data():
    """Teste com dados exatos que o frontend deveria enviar"""
    
    # Dados exatos que o frontend deveria enviar baseado na URL fornecida
    frontend_data = {
        "campaignName": "TESTE FRONTEND EXATO",
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
                "sheetId": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",  # ID extraído da URL
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    print("🧪 Testando dados exatos do frontend...")
    print(f"📊 Dados enviados: {json.dumps(frontend_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
            json=frontend_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso!")
            print(f"📊 Dashboard criado: {result['dashboard']['name']}")
        else:
            print("❌ Erro na API")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_exact_frontend_data()
