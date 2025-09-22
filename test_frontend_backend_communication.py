#!/usr/bin/env python3
"""
Teste para verificar a comunicação entre frontend e backend
"""

import requests
import json

def test_frontend_backend_communication():
    """Teste exato dos dados que o frontend está enviando"""
    
    # Dados exatos que o frontend está enviando (baseado no debug)
    frontend_exact_data = {
        "campaignName": "TESTE COMUNICACAO FRONTEND BACKEND",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 31000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 193750,
        "strategies": "Teste de estratégias",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",
                "gid": "null",  # Exatamente como o frontend está enviando
                "budget": 31000,
                "quantity": 193750
            }
        ]
    }
    
    print("🧪 Testando comunicação frontend → backend...")
    print(f"📊 Dados enviados (exatos do frontend): {json.dumps(frontend_exact_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
            json=frontend_exact_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso! A comunicação está funcionando.")
            print(f"📊 Dashboard criado: {result['dashboard']['name']}")
            return True
        else:
            print("❌ Erro na comunicação!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_backend_communication()
    if success:
        print("\n🎉 A comunicação frontend → backend está funcionando!")
        print("O problema deve estar em outro lugar.")
    else:
        print("\n❌ Há um problema na comunicação frontend → backend.")
