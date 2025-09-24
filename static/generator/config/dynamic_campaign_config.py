#!/usr/bin/env python3
"""
Sistema de configuração dinâmica de campanhas
Permite adicionar novas campanhas sem modificar o código
"""

import json
import os
import sys
from typing import Dict, Optional

# Adicionar o diretório atual ao path para importar campaign_config
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from campaign_config import CampaignConfig

CONFIG_FILE = "static/generator/config/dynamic_campaigns.json"

def load_dynamic_campaigns() -> Dict[str, CampaignConfig]:
    """Carregar campanhas dinâmicas do arquivo JSON"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        campaigns = {}
        for key, config_data in data.items():
            campaigns[key] = CampaignConfig(
                client=config_data['client'],
                campaign=config_data['campaign'],
                sheet_id=config_data['sheet_id'],
                tabs=config_data['tabs']
            )
        
        return campaigns
    except Exception as e:
        print(f"Erro ao carregar campanhas dinâmicas: {e}")
        return {}

def save_dynamic_campaign(campaign_key: str, config: CampaignConfig) -> bool:
    """Salvar nova campanha dinâmica"""
    try:
        # Carregar campanhas existentes
        campaigns = load_dynamic_campaigns()
        
        # Adicionar nova campanha
        campaigns[campaign_key] = config
        
        # Converter para formato JSON
        data = {}
        for key, config_obj in campaigns.items():
            data[key] = {
                'client': config_obj.client,
                'campaign': config_obj.campaign,
                'sheet_id': config_obj.sheet_id,
                'tabs': config_obj.tabs
            }
        
        # Salvar no arquivo
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar campanha dinâmica: {e}")
        return False

def get_all_dynamic_campaigns() -> Dict[str, CampaignConfig]:
    """Obter todas as campanhas dinâmicas"""
    return load_dynamic_campaigns()

def get_dynamic_campaign(campaign_key: str) -> Optional[CampaignConfig]:
    """Obter campanha dinâmica específica"""
    campaigns = load_dynamic_campaigns()
    return campaigns.get(campaign_key)

def delete_dynamic_campaign(campaign_key: str) -> bool:
    """Deletar campanha dinâmica"""
    try:
        campaigns = load_dynamic_campaigns()
        if campaign_key in campaigns:
            del campaigns[campaign_key]
            
            # Salvar arquivo atualizado
            data = {}
            for key, config_obj in campaigns.items():
                data[key] = {
                    'client': config_obj.client,
                    'campaign': config_obj.campaign,
                    'sheet_id': config_obj.sheet_id,
                    'tabs': config_obj.tabs
                }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        return False
    except Exception as e:
        print(f"Erro ao deletar campanha dinâmica: {e}")
        return False

def get_all_campaigns_combined() -> Dict[str, CampaignConfig]:
    """Obter todas as campanhas (estáticas + dinâmicas)"""
    from campaign_config import get_all_campaigns as get_static_campaigns
    
    # Carregar campanhas estáticas
    static_campaigns = get_static_campaigns()
    
    # Carregar campanhas dinâmicas
    dynamic_campaigns = load_dynamic_campaigns()
    
    # Combinar (dinâmicas têm prioridade sobre estáticas)
    all_campaigns = {**static_campaigns, **dynamic_campaigns}
    
    return all_campaigns

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando sistema de configuração dinâmica...")
    
    # Criar campanha de teste
    test_config = CampaignConfig(
        client="Teste Cliente",
        campaign="Teste Campanha",
        sheet_id="1234567890",
        tabs={
            "daily_data": "111111111",
            "contract": "222222222",
            "strategies": "333333333",
            "publishers": "444444444"
        }
    )
    
    # Salvar campanha de teste
    if save_dynamic_campaign("teste_cliente_teste_campanha", test_config):
        print("✅ Campanha de teste salva com sucesso")
    else:
        print("❌ Erro ao salvar campanha de teste")
    
    # Carregar campanhas
    campaigns = get_all_dynamic_campaigns()
    print(f"📊 Campanhas dinâmicas carregadas: {len(campaigns)}")
    
    for key, config in campaigns.items():
        print(f"  - {key}: {config.client} - {config.campaign}")
    
    # Testar combinação
    all_campaigns = get_all_campaigns_combined()
    print(f"📊 Total de campanhas (estáticas + dinâmicas): {len(all_campaigns)}")
