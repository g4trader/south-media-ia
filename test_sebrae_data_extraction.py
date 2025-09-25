#!/usr/bin/env python3
"""
Script para testar a extração de dados específica da campanha SEBRAE PR Feira do Empreendedor
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(__file__))

from static.generator.processors.extract_video_campaign_data import VideoCampaignDataExtractor
from dashboard_database import CampaignConfig

def test_sebrae_data_extraction():
    """Testa a extração de dados da campanha SEBRAE PR Feira do Empreendedor"""
    
    print("🔍 Testando extração de dados da campanha SEBRAE PR Feira do Empreendedor...")
    
    # Configuração da campanha com dados corretos
    campaign_config = CampaignConfig(
        campaign_key="sebrae_pr_feira_do_empreendedor",
        client="SEBRAE PR",
        campaign="Feira do Empreendedor",
        sheet_id="1scA5ykf49DLobPTAKSL5fNgGM_iomcJmgSJqXolV679M",
        tabs={
            "daily_data": "1791112204",
            "contract": "1738408005", 
            "strategies": "587646711",
            "publishers": "409983185"
        }
    )
    
    print(f"📊 Sheet ID: {campaign_config.sheet_id}")
    print(f"📋 GIDs: {campaign_config.tabs}")
    
    try:
        # Criar extrator
        extractor = VideoCampaignDataExtractor(campaign_config)
        
        # Extrair dados
        print("\n🔄 Extraindo dados...")
        data = extractor.extract_data()
        
        if data:
            print("✅ Dados extraídos com sucesso!")
            print(f"📊 Cliente: {data.get('contract', {}).get('client', 'N/A')}")
            print(f"📊 Campanha: {data.get('contract', {}).get('campaign', 'N/A')}")
            print(f"📊 Daily Data Records: {len(data.get('daily_data', []))}")
            print(f"📊 Publishers: {len(data.get('publishers', []))}")
            print(f"📊 Strategies: {len(data.get('strategies', []))}")
            
            # Verificar se há dados reais
            if data.get('daily_data') and len(data['daily_data']) > 0:
                print("✅ Dados reais encontrados!")
                print(f"📅 Primeiro registro: {data['daily_data'][0]}")
            else:
                print("⚠️ Nenhum dado diário encontrado")
                
            return True
        else:
            print("❌ Nenhum dado extraído")
            return False
            
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sebrae_data_extraction()
