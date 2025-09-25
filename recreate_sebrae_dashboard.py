#!/usr/bin/env python3
"""
Script para recriar o dashboard SEBRAE PR Feira do Empreendedor
com a configuração correta
"""

import requests
import json

# URL da API
API_URL = "https://south-media-ia-609095880025.us-central1.run.app"

def recreate_dashboard():
    """Recria o dashboard com a configuração correta"""
    
    # Dados corretos da planilha fornecidos pelo usuário
    campaign_data = {
        "client": "SEBRAE PR",
        "campaign": "Feira do Empreendedor", 
        "sheet_id": "1scA5ykf49DLobPTAKSL5fNgGM_iomcJmgSJqXolV679M",
        "tabs": {
            "daily_data": "1791112204",
            "contract": "1738408005",
            "strategies": "587646711", 
            "publishers": "409983185"
        },
        "campaign_key": "sebrae_pr_feira_do_empreendedor"
    }
    
    print("🔄 Recriando dashboard SEBRAE PR Feira do Empreendedor...")
    print(f"📊 Sheet ID: {campaign_data['sheet_id']}")
    print(f"📋 GIDs: {campaign_data['tabs']}")
    
    try:
        # Fazer requisição para gerar o dashboard
        response = requests.post(f"{API_URL}/api/generate-dashboard", json=campaign_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Dashboard recriado com sucesso!")
                print(f"🎯 Campanha: {result.get('client')} - {result.get('campaign')}")
                print(f"🔗 Dashboard URL: {result.get('dashboard_url')}")
                print(f"🔗 API Endpoint: {result.get('api_endpoint')}")
                print(f"📝 Git Committed: {result.get('git_committed', False)}")
                return True
            else:
                print(f"❌ Erro na criação: {result.get('message')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_campaign_data():
    """Testa se os dados da campanha estão sendo carregados corretamente"""
    
    print("\n🧪 Testando carregamento de dados da campanha...")
    
    try:
        response = requests.get(f"{API_URL}/api/sebrae_pr_feira_do_empreendedor/data")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Dados carregados com sucesso!")
                print(f"📊 Cliente: {result.get('contract', {}).get('client', 'N/A')}")
                print(f"📊 Campanha: {result.get('contract', {}).get('campaign', 'N/A')}")
                print(f"📊 Daily Data Records: {len(result.get('daily_data', []))}")
                print(f"📊 Publishers: {len(result.get('publishers', []))}")
                print(f"📊 Strategies: {len(result.get('strategies', []))}")
                
                # Verificar se não é modo de teste
                if result.get("test_mode"):
                    print("⚠️ Modo de teste ativo - usando dados simulados")
                else:
                    print("✅ Dados reais do Google Sheets carregados!")
                
                return True
            else:
                print(f"❌ Erro no carregamento: {result.get('message')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_dashboard_url():
    """Testa se o dashboard está acessível"""
    
    print("\n🌐 Testando acesso ao dashboard...")
    
    dashboard_url = f"{API_URL}/static/dash_sebrae_pr_feira_do_empreendedor.html"
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard acessível!")
            print(f"🔗 URL: {dashboard_url}")
            return True
        else:
            print(f"❌ Dashboard não acessível - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando recriação do dashboard SEBRAE PR Feira do Empreendedor")
    
    # Recriar dashboard
    if recreate_dashboard():
        # Testar dados
        if test_campaign_data():
            # Testar acesso ao dashboard
            test_dashboard_url()
    else:
        print("❌ Falha na recriação do dashboard")
    
    print("\n🎯 Processo concluído!")
