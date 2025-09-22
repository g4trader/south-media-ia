#!/usr/bin/env python3
"""
Debug script para verificar o mapeamento entre frontend e backend
"""

import requests
import json

def test_frontend_backend_mapping():
    """Teste para verificar se o mapeamento está correto"""
    
    # Simular exatamente o que o frontend deveria enviar
    frontend_data = {
        "campaignName": "TESTE MAPEAMENTO",
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
                "sheetId": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",  # camelCase
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    print("🧪 Testando mapeamento frontend → backend...")
    print(f"📊 Dados enviados (camelCase): {json.dumps(frontend_data, indent=2, ensure_ascii=False)}")
    
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
            print("✅ Sucesso! O mapeamento camelCase está funcionando.")
            return True
        else:
            print("❌ Erro! Vamos testar com snake_case...")
            
            # Testar com snake_case
            backend_data = frontend_data.copy()
            backend_data['channels'][0]['sheet_id'] = backend_data['channels'][0].pop('sheetId')
            
            print(f"📊 Dados enviados (snake_case): {json.dumps(backend_data, indent=2, ensure_ascii=False)}")
            
            response2 = requests.post(
                'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
                json=backend_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📡 Status (snake_case): {response2.status_code}")
            print(f"📄 Resposta (snake_case): {response2.text}")
            
            if response2.status_code == 200:
                print("✅ Sucesso! O mapeamento snake_case está funcionando.")
                return True
            else:
                print("❌ Ambos os mapeamentos falharam!")
                return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_backend_mapping()
    if not success:
        print("\n🔍 O problema está no mapeamento entre frontend e backend!")
        print("Precisamos verificar se o frontend está enviando os dados corretos.")
