#!/usr/bin/env python3
"""
Sistema de configuração de campanhas para dashboards de vídeo programática
Permite configurar múltiplas campanhas de forma centralizada
"""

import os
from typing import Dict, List, Optional

class CampaignConfig:
    """Configuração de uma campanha de vídeo programática"""
    
    def __init__(self, 
                 client: str,
                 campaign: str,
                 sheet_id: str,
                 tabs: Dict[str, str],
                 dashboard_template: str = "video_programmatic_template.html",
                 api_endpoint: str = None):
        """
        Args:
            client: Nome do cliente (ex: "SEBRAE PR")
            campaign: Nome da campanha (ex: "Institucional Setembro")
            sheet_id: ID da planilha Google Sheets
            tabs: Dicionário com nomes das abas e seus GIDs
            dashboard_template: Template HTML a ser usado
            api_endpoint: Endpoint da API (se None, será gerado automaticamente)
        """
        self.client = client
        self.campaign = campaign
        self.sheet_id = sheet_id
        self.tabs = tabs
        self.dashboard_template = dashboard_template
        self.api_endpoint = api_endpoint or f"/api/{self.get_slug()}/data"
        
    def get_slug(self) -> str:
        """Gera slug único para a campanha"""
        return f"{self.client.lower().replace(' ', '_')}_{self.campaign.lower().replace(' ', '_')}"
    
    def get_dashboard_title(self) -> str:
        """Gera título do dashboard"""
        return f"Dashboard {self.client} - {self.campaign}"
    
    def get_campaign_name(self) -> str:
        """Gera nome da campanha para exibição"""
        return f"{self.client} {self.campaign.upper()}"

# Configurações das campanhas
CAMPAIGNS = {
    "sebrae_pr": CampaignConfig(
        client="SEBRAE PR",
        campaign="Institucional Setembro",
        sheet_id="1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",
        tabs={
            "daily_data": "668487440",      # Aba Report
            "contract": "719245615",        # Aba Informações de Contrato
            "strategies": "511331032",      # Aba Estratégias
            "publishers": "531141406"       # Aba Lista de Publishers
        },
        dashboard_template="video_programmatic_template.html"
    ),
    
    # Exemplo de como adicionar novas campanhas:
    "exemplo_cliente": CampaignConfig(
        client="Cliente Exemplo",
        campaign="Campanha Exemplo",
        sheet_id="SHEET_ID_AQUI",
        tabs={
            "daily_data": "GID_DADOS_DIARIOS",
            "contract": "GID_CONTRATO",
            "strategies": "GID_ESTRATEGIAS",
            "publishers": "GID_PUBLISHERS"
        },
        dashboard_template="video_programmatic_template.html"
    ),
}

def get_campaign_config(campaign_key: str) -> Optional[CampaignConfig]:
    """Obter configuração de uma campanha específica"""
    return CAMPAIGNS.get(campaign_key)

def get_all_campaigns() -> Dict[str, CampaignConfig]:
    """Obter todas as configurações de campanhas"""
    return CAMPAIGNS

def get_campaign_by_endpoint(endpoint: str) -> Optional[CampaignConfig]:
    """Encontrar campanha pelo endpoint da API"""
    for campaign in CAMPAIGNS.values():
        if campaign.api_endpoint == endpoint:
            return campaign
    return None

def validate_campaign_config(config: CampaignConfig) -> List[str]:
    """Validar configuração de campanha"""
    errors = []
    
    if not config.client:
        errors.append("Cliente não pode ser vazio")
    
    if not config.campaign:
        errors.append("Campanha não pode ser vazia")
    
    if not config.sheet_id:
        errors.append("Sheet ID não pode ser vazio")
    
    required_tabs = ["daily_data", "contract", "strategies", "publishers"]
    for tab in required_tabs:
        if tab not in config.tabs:
            errors.append(f"Aba '{tab}' é obrigatória")
    
    return errors

# Configurações padrão para extração de dados
DEFAULT_COLUMN_MAPPING = {
    'Day': 'date',
    'Creative': 'creative',
    'Imps': 'impressions',
    'Clicks': 'clicks',
    'CTR %': 'ctr',
    'Video Completion Rate %': 'vtr',
    'Video Skip Rate %': 'skip_rate',
    'Video Start Rate %': 'start_rate',
    '25% Video Complete': 'q25',
    '50% Video Complete': 'q50',
    '75% Video Complete': 'q75',
    '100% Complete': 'q100',
    'Video Starts': 'starts',
    'Valor Investido': 'spend',
    'CPV': 'cpv'
}

# Mapeamento de campos de contrato padrão
DEFAULT_CONTRACT_MAPPING = {
    'cliente': 'client',
    'campanha': 'campaign',
    'canal': 'channel',
    'tipo de criativo': 'creative_type',
    'investimento': 'investment',
    'cpv contratado': 'cpv_contracted',
    'complete views contrado': 'complete_views_contracted',
    'periodo de veiculação': 'period'
}

if __name__ == "__main__":
    # Teste das configurações
    print("📊 Configurações de Campanhas:")
    print("=" * 50)
    
    for key, config in CAMPAIGNS.items():
        print(f"\n🎯 {config.client} - {config.campaign}")
        print(f"   Slug: {config.get_slug()}")
        print(f"   API Endpoint: {config.api_endpoint}")
        print(f"   Dashboard: {config.get_dashboard_title()}")
        print(f"   Abas: {len(config.tabs)}")
        
        # Validar configuração
        errors = validate_campaign_config(config)
        if errors:
            print(f"   ❌ Erros: {', '.join(errors)}")
        else:
            print(f"   ✅ Configuração válida")
