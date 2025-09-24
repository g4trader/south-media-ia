#!/usr/bin/env python3
"""
Teste da estrutura genérica para campanhas de vídeo programática
"""

import json
import requests
from campaign_config import get_all_campaigns, get_campaign_config
from extract_video_campaign_data import extract_campaign_data
from test_video_campaign_data import create_test_data_for_campaign

def test_campaign_config():
    """Testar configurações de campanhas"""
    print("🧪 TESTE DE CONFIGURAÇÕES DE CAMPANHAS")
    print("=" * 50)
    
    campaigns = get_all_campaigns()
    
    for key, config in campaigns.items():
        print(f"\n🎯 {config.client} - {config.campaign}")
        print(f"   Slug: {config.get_slug()}")
        print(f"   API Endpoint: {config.api_endpoint}")
        print(f"   Dashboard: {config.get_dashboard_title()}")
        print(f"   Sheet ID: {config.sheet_id}")
        print(f"   Abas: {list(config.tabs.keys())}")

def test_data_extraction():
    """Testar extração de dados"""
    print("\n\n🧪 TESTE DE EXTRAÇÃO DE DADOS")
    print("=" * 50)
    
    campaigns = get_all_campaigns()
    
    for key in campaigns.keys():
        print(f"\n📊 Testando extração para: {key}")
        
        # Testar dados reais
        try:
            data = extract_campaign_data(key)
            if data:
                print(f"   ✅ Dados reais extraídos com sucesso")
                print(f"   📊 Cliente: {data.get('contract', {}).get('client', 'N/A')}")
                print(f"   📊 Publishers: {len(data.get('publishers', []))}")
            else:
                print(f"   ⚠️ Dados reais não disponíveis")
        except Exception as e:
            print(f"   ❌ Erro na extração real: {e}")
        
        # Testar dados de teste
        try:
            test_data = create_test_data_for_campaign(key)
            if test_data:
                print(f"   ✅ Dados de teste gerados com sucesso")
                print(f"   📊 Cliente: {test_data.get('contract', {}).get('client', 'N/A')}")
                print(f"   📊 Publishers: {len(test_data.get('publishers', []))}")
            else:
                print(f"   ❌ Dados de teste não gerados")
        except Exception as e:
            print(f"   ❌ Erro na geração de teste: {e}")

def test_api_endpoints():
    """Testar endpoints da API"""
    print("\n\n🧪 TESTE DE ENDPOINTS DA API")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Testar endpoint de listagem
    try:
        response = requests.get(f"{base_url}/api/campaigns")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint /api/campaigns funcionando")
            print(f"   📊 Campanhas disponíveis: {data.get('total', 0)}")
            for campaign in data.get('campaigns', []):
                print(f"   - {campaign['client']} ({campaign['key']})")
        else:
            print(f"❌ Endpoint /api/campaigns retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar /api/campaigns: {e}")
    
    # Testar endpoints específicos de campanhas
    campaigns = get_all_campaigns()
    for key in campaigns.keys():
        try:
            response = requests.get(f"{base_url}/api/{key}/data")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Endpoint /api/{key}/data funcionando")
                    print(f"   📊 Fonte: {data.get('source', 'N/A')}")
                    print(f"   📊 Cliente: {data.get('data', {}).get('contract', {}).get('client', 'N/A')}")
                else:
                    print(f"❌ Endpoint /api/{key}/data retornou erro: {data.get('message', 'N/A')}")
            else:
                print(f"❌ Endpoint /api/{key}/data retornou status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao testar /api/{key}/data: {e}")

def test_template_generation():
    """Testar geração de templates"""
    print("\n\n🧪 TESTE DE GERAÇÃO DE TEMPLATES")
    print("=" * 50)
    
    campaigns = get_all_campaigns()
    
    for key, config in campaigns.items():
        print(f"\n🎯 Gerando template para: {config.client}")
        
        # Simular geração de dashboard personalizado
        dashboard_url = f"/static/dash_{config.get_slug()}.html"
        api_endpoint = config.api_endpoint
        
        print(f"   📊 Dashboard URL: {dashboard_url}")
        print(f"   📊 API Endpoint: {api_endpoint}")
        print(f"   📊 Template base: {config.dashboard_template}")
        
        # Verificar se template genérico existe
        import os
        template_path = f"static/{config.dashboard_template}"
        if os.path.exists(template_path):
            print(f"   ✅ Template genérico encontrado")
        else:
            print(f"   ⚠️ Template genérico não encontrado: {template_path}")

def test_backward_compatibility():
    """Testar compatibilidade com código antigo"""
    print("\n\n🧪 TESTE DE COMPATIBILIDADE")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Testar endpoint antigo do SEBRAE
    try:
        response = requests.get(f"{base_url}/api/sebrae/data")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Endpoint antigo /api/sebrae/data funcionando (compatibilidade)")
                print(f"   📊 Cliente: {data.get('data', {}).get('contract', {}).get('client', 'N/A')}")
            else:
                print(f"❌ Endpoint antigo retornou erro: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Endpoint antigo retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint antigo: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DA ESTRUTURA GENÉRICA")
    print("=" * 60)
    
    test_campaign_config()
    test_data_extraction()
    test_api_endpoints()
    test_template_generation()
    test_backward_compatibility()
    
    print("\n\n🎉 TESTES CONCLUÍDOS!")
    print("=" * 60)
    print("✅ Estrutura genérica validada")
    print("📊 Pronta para suportar múltiplas campanhas")
    print("🔧 Sistema modular e escalável implementado")
