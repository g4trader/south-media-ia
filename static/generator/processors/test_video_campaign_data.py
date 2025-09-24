#!/usr/bin/env python3
"""
Gerador de dados de teste genérico para campanhas de vídeo programática
Substitui os geradores específicos por cliente
"""

import json
from typing import Dict, Any
from campaign_config import CampaignConfig

def create_test_data(campaign_config: CampaignConfig) -> Dict[str, Any]:
    """Criar dados de teste baseados na configuração da campanha"""
    
    # Dados baseados na configuração da campanha
    campaign_data = {
        "campaign_name": f"{campaign_config.client} - {campaign_config.campaign}",
        "dashboard_title": f"Dashboard {campaign_config.client} - {campaign_config.campaign}",
        "channel": "Prográmatica",
        "creative_type": "Video",
        "period": "15/09/2025 - 30/09/2025",
        "budget_contracted": 31000.00,
        "vc_contracted": 193750,
        "contract": {
            "client": campaign_config.client,
            "campaign": campaign_config.campaign,
            "channel": "Prográmatica",
            "creative_type": "Video",
            "investment": 31000.00,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "period_start": "15/09/2025",
            "period_end": "30/09/2025"
        },
        "strategies": {
            "segmentation": [
                "Segmentação A",
                "Segmentação B"
            ],
            "objectives": [
                "Objetivo 1",
                "Objetivo 2"
            ]
        },
        "publishers": [
            {"name": "Publisher A", "type": "Site: publisher-a.com"},
            {"name": "Publisher B", "type": "Site: publisher-b.com"},
            {"name": "Publisher C", "type": "Site: publisher-c.com"},
            {"name": "Publisher D", "type": "Site: publisher-d.com"},
            {"name": "Publisher E", "type": "Site: publisher-e.com"}
        ],
        "metrics": {
            "spend": 10873.68,  # Total dos dados da planilha
            "impressions": 100036,  # Soma das impressões
            "clicks": 40,  # Soma dos cliques
            "starts": 100035,  # Soma dos starts
            "q25": 8238,  # Soma dos 25%
            "q50": 7583,  # Soma dos 50%
            "q75": 7165,  # Soma dos 75%
            "q100": 74472,  # Soma dos 100% (6796+4212+9448+2165+1440+16109+34302)
            "ctr": 0.04,  # CTR médio
            "vtr": 67.9,  # VTR médio
            "cpv": 0.16,  # CPV médio
            "cpm": 16.00,  # CPM calculado
            "pacing": 35.1,  # Pacing calculado
            "vc_contracted": 193750,  # VC contratado (R$ 31.000 / R$ 0,16)
            "vc_delivered": 74472,  # VC entregue (soma dos 100%)
            "vc_pacing": 38.4  # Pacing de VC (74472 / 193750 * 100)
        },
        "daily_data": [
            {
                "date": "2025-09-17",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 1087.36,
                "impressions": 10036,
                "clicks": 5,
                "starts": 10035,
                "q25": 8238,
                "q50": 7583,
                "q75": 7165,
                "q100": 6796,
                "ctr": 0.05,
                "vtr": 67.7,
                "cpv": 0.16
            },
            {
                "date": "2025-09-18",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 673.92,
                "impressions": 6514,
                "clicks": 0,
                "starts": 6513,
                "q25": 5260,
                "q50": 4854,
                "q75": 4506,
                "q100": 4212,
                "ctr": 0.0,
                "vtr": 64.7,
                "cpv": 0.16
            },
            {
                "date": "2025-09-19",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 1511.68,
                "impressions": 11609,
                "clicks": 1,
                "starts": 11609,
                "q25": 10367,
                "q50": 9992,
                "q75": 9698,
                "q100": 9448,
                "ctr": 0.01,
                "vtr": 81.4,
                "cpv": 0.16
            },
            {
                "date": "2025-09-20",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 346.40,
                "impressions": 3130,
                "clicks": 2,
                "starts": 3130,
                "q25": 2671,
                "q50": 2480,
                "q75": 2267,
                "q100": 2165,
                "ctr": 0.06,
                "vtr": 69.2,
                "cpv": 0.16
            },
            {
                "date": "2025-09-21",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 230.40,
                "impressions": 1757,
                "clicks": 0,
                "starts": 1757,
                "q25": 1629,
                "q50": 1531,
                "q75": 1466,
                "q100": 1440,
                "ctr": 0.0,
                "vtr": 82.0,
                "cpv": 0.16
            },
            {
                "date": "2025-09-22",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 2577.44,
                "impressions": 19936,
                "clicks": 32,
                "starts": 19934,
                "q25": 17703,
                "q50": 17015,
                "q75": 16492,
                "q100": 16109,
                "ctr": 0.16,
                "vtr": 80.8,
                "cpv": 0.16
            },
            {
                "date": "2025-09-23",
                "creative": f"Creative {campaign_config.client} 30s_V1.mp4",
                "spend": 5488.32,
                "impressions": 41184,
                "clicks": 2,
                "starts": 41183,
                "q25": 37210,
                "q50": 35971,
                "q75": 35091,
                "q100": 34302,
                "ctr": 0.005,
                "vtr": 83.3,
                "cpv": 0.16
            }
        ],
        "per_data": [
            {
                "metric": "Impressões",
                "contracted": 193750,
                "delivered": 100036,
                "pacing": 51.6
            },
            {
                "metric": "Cliques",
                "contracted": 1000,
                "delivered": 40,
                "pacing": 4.0
            },
            {
                "metric": "VC",
                "contracted": 193750,
                "delivered": 74472,
                "pacing": 38.4
            }
        ]
    }
    
    return campaign_data

def create_test_data_for_campaign(campaign_key: str) -> Dict[str, Any]:
    """Criar dados de teste para uma campanha específica"""
    from campaign_config import get_campaign_config
    
    config = get_campaign_config(campaign_key)
    if not config:
        print(f"❌ Configuração não encontrada para campanha: {campaign_key}")
        return {}
    
    return create_test_data(config)

if __name__ == "__main__":
    # Teste com campanha SEBRAE
    print("🧪 Testando gerador de dados de teste...")
    data = create_test_data_for_campaign("sebrae_pr")
    
    if data:
        print("✅ Dados de teste gerados com sucesso!")
        print(f"📊 Cliente: {data.get('contract', {}).get('client', 'N/A')}")
        print(f"📊 Campanha: {data.get('contract', {}).get('campaign', 'N/A')}")
        print(f"📊 Publishers: {len(data.get('publishers', []))}")
        print(f"📊 Dados diários: {len(data.get('daily_data', []))}")
    else:
        print("❌ Falha na geração de dados de teste")
