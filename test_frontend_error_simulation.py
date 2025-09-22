#!/usr/bin/env python3
"""
Teste para simular exatamente o que o frontend está enviando quando há erro
"""

import requests
import json

def test_frontend_error_scenarios():
    """Testar cenários que podem causar o erro 'ID da planilha obrigatório'"""
    
    base_url = 'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards'
    
    # Cenário 1: sheetId vazio
    print("🧪 Teste 1: sheetId vazio")
    data1 = {
        "campaignName": "TESTE SHEET ID VAZIO",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Teste",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": "",  # VAZIO
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    test_scenario(data1, "sheetId vazio")
    
    # Cenário 2: sheetId null
    print("\n🧪 Teste 2: sheetId null")
    data2 = {
        "campaignName": "TESTE SHEET ID NULL",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Teste",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": None,  # NULL
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    test_scenario(data2, "sheetId null")
    
    # Cenário 3: sheetId ausente
    print("\n🧪 Teste 3: sheetId ausente")
    data3 = {
        "campaignName": "TESTE SHEET ID AUSENTE",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Teste",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                # sheetId ausente
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    test_scenario(data3, "sheetId ausente")
    
    # Cenário 4: sheetId com espaços
    print("\n🧪 Teste 4: sheetId com espaços")
    data4 = {
        "campaignName": "TESTE SHEET ID ESPACOS",
        "startDate": "2025-09-15",
        "endDate": "2025-09-30",
        "totalBudget": 10000,
        "reportModel": "Simples",
        "kpiType": "CPV",
        "kpiValue": 0.16,
        "kpiTarget": 1000,
        "strategies": "Teste",
        "channels": [
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": "   ",  # APENAS ESPAÇOS
                "gid": "668487440",
                "budget": 10000,
                "quantity": 1000
            }
        ]
    }
    
    test_scenario(data4, "sheetId com espaços")

def test_scenario(data, scenario_name):
    """Testar um cenário específico"""
    try:
        response = requests.post(
            'https://dashboard-builder-609095880025.us-central1.run.app/api/dashboards',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 400:
            print(f"✅ Cenário '{scenario_name}' reproduziu o erro 400 como esperado")
        else:
            print(f"❌ Cenário '{scenario_name}' não reproduziu o erro esperado")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_frontend_error_scenarios()
