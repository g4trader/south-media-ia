#!/usr/bin/env python3
"""
Sistema de configuração para gerador de dashboards
Versão simplificada para integração com o sistema existente
"""

import json
import os
from typing import Dict, Optional

class CampaignConfig:
    def __init__(self, client: str, campaign: str, sheet_id: str, tabs: Dict[str, str]):
        self.client = client
        self.campaign = campaign
        self.sheet_id = sheet_id
        self.tabs = tabs
    
    def get_slug(self) -> str:
        """Gerar slug para nome de arquivo"""
        client_slug = self.client.lower().replace(' ', '_').replace('-', '_')
        campaign_slug = self.campaign.lower().replace(' ', '_').replace('-', '_')
        return f"{client_slug}_{campaign_slug}"
    
    def get_dashboard_title(self) -> str:
        """Gerar título do dashboard"""
        return f"Dashboard {self.client} - {self.campaign}"
    
    @property
    def api_endpoint(self) -> str:
        """Endpoint da API"""
        return f"/api/{self.get_slug()}/data"

CONFIG_FILE = "generator_config.json"

def load_campaigns() -> Dict[str, CampaignConfig]:
    """Carregar campanhas do arquivo JSON"""
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
        print(f"Erro ao carregar campanhas: {e}")
        return {}

def save_campaign(campaign_key: str, config: CampaignConfig) -> bool:
    """Salvar nova campanha"""
    try:
        campaigns = load_campaigns()
        campaigns[campaign_key] = config
        
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
    except Exception as e:
        print(f"Erro ao salvar campanha: {e}")
        return False

def get_campaign(campaign_key: str) -> Optional[CampaignConfig]:
    """Obter campanha específica"""
    campaigns = load_campaigns()
    return campaigns.get(campaign_key)

def get_all_campaigns() -> Dict[str, CampaignConfig]:
    """Obter todas as campanhas"""
    return load_campaigns()

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando sistema de configuração simplificado...")
    
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
    if save_campaign("teste_cliente_teste_campanha", test_config):
        print("✅ Campanha de teste salva com sucesso")
    else:
        print("❌ Erro ao salvar campanha de teste")
    
    # Carregar campanhas
    campaigns = get_all_campaigns()
    print(f"📊 Campanhas carregadas: {len(campaigns)}")
    
    for key, config in campaigns.items():
        print(f"  - {key}: {config.client} - {config.campaign}")
