#!/usr/bin/env python3
"""
Testar interface amigável de criação de dashboards
"""

import requests
import json
import time
from datetime import datetime

def test_api_health():
    """Testar saúde da API"""
    print("🔍 TESTANDO SAÚDE DA API")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8084/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API está saudável")
            print(f"📊 Google Sheets: {'Disponível' if data.get('sheets_available') else 'Não disponível'}")
            print(f"🕒 Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def test_create_dashboard():
    """Testar criação de dashboard"""
    print("\n🚀 TESTANDO CRIAÇÃO DE DASHBOARD")
    print("=" * 50)
    
    # Dados de teste
    test_data = {
        "campaignName": "Teste Interface Amigável",
        "startDate": "2025-09-20",
        "endDate": "2025-09-30",
        "totalBudget": 50000,
        "kpiType": "CPV",
        "kpiValue": 0.10,
        "reportModel": "simple",
        "strategies": "Campanha de teste para validar a interface amigável de criação de dashboards.",
        "channels": [
            {
                "name": "YouTube",
                "sheet_id": "1ABC123",
                "gid": "0",
                "budget": 30000,
                "quantity": 500000
            },
            {
                "name": "Programática Video",
                "sheet_id": "1XYZ789",
                "gid": "0",
                "budget": 20000,
                "quantity": 200000
            }
        ]
    }
    
    try:
        response = requests.post(
            'http://localhost:8084/api/dashboards',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Dashboard criado com sucesso!")
                print(f"📊 ID: {data['dashboard']['id']}")
                print(f"📝 Nome: {data['dashboard']['name']}")
                print(f"📁 Arquivo: {data['dashboard'].get('html_file', 'N/A')}")
                return data['dashboard']['id']
            else:
                print(f"❌ Erro na criação: {data.get('error')}")
                if data.get('details'):
                    print(f"📋 Detalhes: {data['details']}")
                return None
        else:
            print(f"❌ API retornou status {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_list_dashboards():
    """Testar listagem de dashboards"""
    print("\n📋 TESTANDO LISTAGEM DE DASHBOARDS")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8084/api/dashboards', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                dashboards = data.get('dashboards', [])
                print(f"✅ {len(dashboards)} dashboard(s) encontrado(s)")
                
                for i, dashboard in enumerate(dashboards, 1):
                    print(f"  {i}. {dashboard['name']} ({dashboard['status']})")
                    print(f"     ID: {dashboard['id']}")
                    print(f"     Criado: {dashboard['created_at']}")
                    if dashboard.get('html_file'):
                        print(f"     Arquivo: {dashboard['html_file']}")
                    print()
                
                return dashboards
            else:
                print(f"❌ Erro na listagem: {data.get('error')}")
                return []
        else:
            print(f"❌ API retornou status {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []

def test_validate_dashboard(dashboard_id):
    """Testar validação de dashboard"""
    print(f"\n✅ TESTANDO VALIDAÇÃO DO DASHBOARD {dashboard_id}")
    print("=" * 50)
    
    try:
        response = requests.post(
            f'http://localhost:8084/api/dashboards/{dashboard_id}/validate',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Dashboard validado com sucesso!")
                return True
            else:
                print(f"❌ Erro na validação: {data.get('error')}")
                return False
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_activate_dashboard(dashboard_id):
    """Testar ativação de dashboard"""
    print(f"\n🚀 TESTANDO ATIVAÇÃO DO DASHBOARD {dashboard_id}")
    print("=" * 50)
    
    try:
        response = requests.post(
            f'http://localhost:8084/api/dashboards/{dashboard_id}/activate',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Dashboard ativado com sucesso!")
                return True
            else:
                print(f"❌ Erro na ativação: {data.get('error')}")
                return False
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_download_dashboard(dashboard_id):
    """Testar download de dashboard"""
    print(f"\n📥 TESTANDO DOWNLOAD DO DASHBOARD {dashboard_id}")
    print("=" * 50)
    
    try:
        response = requests.get(
            f'http://localhost:8084/api/dashboards/{dashboard_id}/download',
            timeout=30
        )
        
        if response.status_code == 200:
            # Verificar se é um arquivo HTML
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print(f"✅ Download realizado com sucesso!")
                print(f"📄 Tamanho: {len(response.content)} bytes")
                print(f"📋 Content-Type: {content_type}")
                return True
            else:
                print(f"⚠️ Download realizado mas content-type inesperado: {content_type}")
                return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_templates():
    """Testar listagem de templates"""
    print("\n📄 TESTANDO LISTAGEM DE TEMPLATES")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8084/api/templates', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                templates = data.get('templates', [])
                print(f"✅ {len(templates)} template(s) encontrado(s)")
                
                for i, template in enumerate(templates, 1):
                    print(f"  {i}. {template['name']}")
                
                return templates
            else:
                print(f"❌ Erro na listagem: {data.get('error')}")
                return []
        else:
            print(f"❌ API retornou status {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return []

def main():
    """Executar todos os testes"""
    print("🧪 TESTE COMPLETO DA INTERFACE AMIGÁVEL")
    print("=" * 70)
    print(f"🕒 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Teste 1: Saúde da API
    if not test_api_health():
        print("\n❌ API não está disponível. Inicie o servidor com:")
        print("   python3 dashboard_builder_api_enhanced.py")
        return
    
    # Teste 2: Listar templates
    test_templates()
    
    # Teste 3: Listar dashboards existentes
    existing_dashboards = test_list_dashboards()
    
    # Teste 4: Criar novo dashboard
    dashboard_id = test_create_dashboard()
    
    if dashboard_id:
        # Teste 5: Validar dashboard
        test_validate_dashboard(dashboard_id)
        
        # Teste 6: Ativar dashboard
        test_activate_dashboard(dashboard_id)
        
        # Teste 7: Download dashboard
        test_download_dashboard(dashboard_id)
        
        # Teste 8: Listar dashboards novamente
        test_list_dashboards()
    
    print("\n🎉 TESTES CONCLUÍDOS!")
    print("=" * 70)
    print("📋 Para testar a interface web:")
    print("   1. Abra: dashboard-builder-user-friendly.html")
    print("   2. Preencha o formulário")
    print("   3. Clique em 'Criar Dashboard'")
    print("   4. Verifique se o dashboard foi criado com sucesso")

if __name__ == "__main__":
    main()
