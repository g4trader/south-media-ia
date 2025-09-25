#!/usr/bin/env python3
"""
Script para atualizar a configuração da campanha SEBRAE PR Feira do Empreendedor
com o Sheet ID correto e os GIDs corretos
"""

import requests
import json

# URL da API
API_URL = "https://south-media-ia-609095880025.us-central1.run.app"

def update_campaign_config():
    """Atualiza a configuração da campanha com os dados corretos"""
    
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
    
    print("🔄 Atualizando configuração da campanha SEBRAE PR Feira do Empreendedor...")
    print(f"📊 Sheet ID: {campaign_data['sheet_id']}")
    print(f"📋 GIDs: {campaign_data['tabs']}")
    
    try:
        # Fazer requisição para atualizar a configuração
        response = requests.post(f"{API_URL}/api/update-campaign", json=campaign_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Configuração atualizada com sucesso!")
                print(f"🎯 Campanha: {result.get('client')} - {result.get('campaign')}")
                print(f"🔗 API Endpoint: {result.get('api_endpoint')}")
                return True
            else:
                print(f"❌ Erro na atualização: {result.get('message')}")
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

if __name__ == "__main__":
    print("🚀 Iniciando atualização da campanha SEBRAE PR Feira do Empreendedor")
    
    # Atualizar configuração
    if update_campaign_config():
        # Testar dados
        test_campaign_data()
    else:
        print("❌ Falha na atualização da configuração")
    
    print("\n🎯 Processo concluído!")
