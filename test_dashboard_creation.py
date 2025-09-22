#!/usr/bin/env python3
"""
Script de teste para criação de dashboard
Testando com dados reais da campanha "Semana do Pescado"
"""

import requests
import json
from datetime import datetime

# Configuração da API
API_BASE_URL = "http://localhost:8081"

def test_dashboard_creation():
    """Testar criação de dashboard com dados reais"""
    
    # Dados da campanha
    campaign_data = {
        "campaignName": "Semana do Pescado",
        "startDate": "2025-09-01",
        "endDate": "2025-09-30",
        "totalBudget": 90000.00,
        "reportModel": "simple",
        "kpiType": "cpv",
        "kpiValue": 0.08,
        "kpiTarget": 798914,  # 625.000 + 173.914
        "strategies": "Campanha de vídeo para promover a Semana do Pescado, utilizando YouTube e Programática Video para alcançar audiência ampla através de sites de notícias e entretenimento. Foco em CPV otimizado e alcance de impressões contratadas.",
        "channels": [
            {
                "name": "youtube",
                "displayName": "📺 YouTube",
                "sheetId": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
                "gid": "304137877",
                "budget": 50000.00,
                "quantity": 625000
            },
            {
                "name": "programmatic_video",
                "displayName": "🎬 Programática Video",
                "sheetId": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
                "gid": "1489416055",
                "budget": 40000.00,
                "quantity": 173914
            }
        ]
    }
    
    print("🚀 Testando criação de dashboard...")
    print(f"📊 Campanha: {campaign_data['campaignName']}")
    print(f"📅 Período: {campaign_data['startDate']} a {campaign_data['endDate']}")
    print(f"💰 Orçamento Total: R$ {campaign_data['totalBudget']:,.2f}")
    print(f"📺 Canais: {len(campaign_data['channels'])}")
    
    try:
        # Fazer requisição para criar dashboard
        response = requests.post(
            f"{API_BASE_URL}/api/dashboards",
            headers={"Content-Type": "application/json"},
            json=campaign_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                dashboard = result.get('dashboard', {})
                print("\n✅ Dashboard criado com sucesso!")
                print(f"🆔 ID: {dashboard.get('id')}")
                print(f"📁 Arquivo: {dashboard.get('fileName')}")
                print(f"📊 Status: {dashboard.get('status')}")
                print(f"📅 Criado em: {dashboard.get('createdAt')}")
                
                # Testar listagem de dashboards
                print("\n📋 Testando listagem de dashboards...")
                list_response = requests.get(f"{API_BASE_URL}/api/dashboards")
                if list_response.status_code == 200:
                    dashboards = list_response.json()
                    print(f"✅ {len(dashboards)} dashboards encontrados")
                    for dash in dashboards:
                        print(f"  - {dash.get('campaignName')} ({dash.get('status')})")
                
                return True
            else:
                print(f"❌ Erro na criação: {result.get('message')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API")
        print("💡 Certifique-se de que a API está rodando em http://localhost:8081")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_health_check():
    """Testar health check da API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está funcionando")
            return True
        else:
            print(f"⚠️ API respondeu com status {response.status_code}")
            return False
    except:
        print("❌ API não está respondendo")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Criação de Dashboard")
    print("=" * 50)
    
    # Testar health check primeiro
    if test_health_check():
        print()
        # Testar criação de dashboard
        success = test_dashboard_creation()
        
        if success:
            print("\n🎉 Teste concluído com sucesso!")
            print("💡 Próximos passos:")
            print("  1. Verificar arquivo HTML gerado")
            print("  2. Testar validação do dashboard")
            print("  3. Testar ativação do dashboard")
        else:
            print("\n❌ Teste falhou")
            print("💡 Verifique os logs da API para mais detalhes")
    else:
        print("\n❌ API não está disponível")
        print("💡 Execute: python dashboard_builder_api.py")



