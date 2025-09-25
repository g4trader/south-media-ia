#!/usr/bin/env python3
"""
Script para mostrar detalhes completos da planilha (Sheet ID e GIDs)
"""

import requests
import json

def get_campaign_details(campaign_key):
    """Obter detalhes completos da campanha incluindo Sheet ID e GIDs"""
    try:
        # Primeiro, obter a configuração da campanha
        url = f"https://south-media-ia-609095880025.us-central1.run.app/api/{campaign_key}/data"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 DETALHES DA CAMPANHA: {campaign_key}")
            print(f"┌─────────────────────────────────────────────────────────┐")
            print(f"│ Cliente: {data.get('client', 'N/A'):<45} │")
            print(f"│ Campanha: {data.get('campaign', 'N/A'):<44} │")
            print(f"└─────────────────────────────────────────────────────────┘")
            
            # Verificar se há dados da planilha
            if 'data' in data:
                campaign_data = data['data']
                
                # Procurar informações sobre a planilha nos dados
                if 'sheet_info' in campaign_data:
                    sheet_info = campaign_data['sheet_info']
                    print(f"\n📋 INFORMAÇÕES DA PLANILHA:")
                    print(f"  • Sheet ID: {sheet_info.get('sheet_id', 'N/A')}")
                    print(f"  • Tabs/GIDs:")
                    for tab_name, gid in sheet_info.get('tabs', {}).items():
                        print(f"    - {tab_name}: {gid}")
                
                # Mostrar dados de contrato se disponíveis
                contract = campaign_data.get('contract', {})
                if contract:
                    print(f"\n💼 DADOS DO CONTRATO:")
                    print(f"  • Investimento: R$ {contract.get('investment', 'N/A')}")
                    print(f"  • VC Contratado: {contract.get('complete_views_contracted', 'N/A')}")
                    print(f"  • CPV Contratado: R$ {contract.get('cpv_contracted', 'N/A')}")
                    print(f"  • Período: {contract.get('period_start', 'N/A')} a {contract.get('period_end', 'N/A')}")
                
                # Verificar se há dados de publishers e strategies
                if 'publishers' in campaign_data:
                    print(f"\n📺 PUBLISHERS ({len(campaign_data['publishers'])} encontrados):")
                    for pub in campaign_data['publishers'][:3]:  # Mostrar apenas os primeiros 3
                        print(f"  • {pub}")
                    if len(campaign_data['publishers']) > 3:
                        print(f"  ... e mais {len(campaign_data['publishers']) - 3} publishers")
                
                if 'strategies' in campaign_data:
                    print(f"\n🎯 SEGMENTAÇÕES ({len(campaign_data['strategies'])} encontradas):")
                    for strategy in campaign_data['strategies'][:3]:  # Mostrar apenas as primeiras 3
                        print(f"  • {strategy}")
                    if len(campaign_data['strategies']) > 3:
                        print(f"  ... e mais {len(campaign_data['strategies']) - 3} segmentações")
            
            # Se não há dados específicos, mostrar mensagem de teste
            if data.get('test_mode'):
                print(f"\n⚠️ MODO DE TESTE ATIVO")
                print(f"  • {data.get('test_message', 'Dados simulados sendo utilizados')}")
                
        else:
            print(f"❌ Erro ao acessar dados da campanha: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao obter detalhes: {e}")

def show_all_campaigns():
    """Mostrar todas as campanhas disponíveis"""
    try:
        url = "https://south-media-ia-609095880025.us-central1.run.app/api/campaigns"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('campaigns', [])
            
            print(f"📋 TODAS AS CAMPANHAS DISPONÍVEIS ({len(campaigns)}):")
            print(f"┌─────────────────────────────────────────────────────────┐")
            print(f"│ {'Campaign Key':<30} │ {'Cliente':<20} │")
            print(f"├─────────────────────────────────────────────────────────┤")
            
            for campaign in campaigns:
                key = campaign.get('key', 'N/A')[:30]
                client = campaign.get('client', 'N/A')[:20]
                print(f"│ {key:<30} │ {client:<20} │")
            
            print(f"└─────────────────────────────────────────────────────────┘")
            
            return [c.get('key') for c in campaigns]
        else:
            print(f"❌ Erro ao listar campanhas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao listar campanhas: {e}")
        return []

if __name__ == "__main__":
    import sys
    
    print("🔍 DETALHES DA PLANILHA E CAMPANHA")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        campaign_key = sys.argv[1]
        get_campaign_details(campaign_key)
    else:
        # Mostrar todas as campanhas
        campaigns = show_all_campaigns()
        
        if campaigns:
            print(f"\n💡 Para ver detalhes de uma campanha específica:")
            print(f"   python3 show_sheet_details.py <campaign_key>")
            print(f"\n📝 Exemplo:")
            print(f"   python3 show_sheet_details.py {campaigns[0]}")
    
    print("\n" + "=" * 60)
    print("✅ Verificação concluída!")
