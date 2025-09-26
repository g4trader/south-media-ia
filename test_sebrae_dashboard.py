#!/usr/bin/env python3
"""
Teste do dashboard SEBRAE com dados simulados baseados na planilha real
"""

import json
from datetime import datetime

def create_sebrae_test_data():
    """Criar dados de teste baseados na planilha real do SEBRAE"""
    
    # Dados baseados na planilha real
    campaign_data = {
        "campaign_name": "SEBRAE PR - Institucional Setembro",
        "dashboard_title": "Dashboard SEBRAE PR - Institucional Setembro",
        "channel": "Prográmatica",
        "creative_type": "Video",
        "period": "15/09/2025 - 30/09/2025",
        "budget_contracted": 31000.00,
        "vc_contracted": 193750,
        "contract": {
            "client": "SEBRAE PR",
            "campaign": "Institucional Setembro",
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
                "Microempreendedores",
                "Jovens Empreendedores em Ascensão"
            ],
            "objectives": [
                "Alcance em PARANÁ",
                "White list para grandes portais"
            ]
        },
        "publishers": [
            {"name": "Gazeta do Povo", "type": "Site: gazetadopovo.com.br"},
            {"name": "Bem Paraná", "type": "Site: bemparana.com.br"},
            {"name": "Tribuna PR", "type": "Site: tribunapr.com.br"},
            {"name": "Bonde", "type": "Site: bonde.com.br"},
            {"name": "Massa News", "type": "Site: massanews.com"},
            {"name": "Paraná Portal", "type": "Site: paranaportal.com"},
            {"name": "Plural Curitiba", "type": "Site: plural.jor.br"},
            {"name": "O Paraná", "type": "Site: oparana.com.br"},
            {"name": "AEN-PR", "type": "Site: aen.pr.gov.br"},
            {"name": "IPARDES", "type": "Site: ipardes.pr.gov.br"},
            {"name": "Revista PEGN", "type": "Site: revistapegn.globo.com"},
            {"name": "Exame", "type": "Site: exame.com"},
            {"name": "InfoMoney", "type": "Site: infomoney.com.br"},
            {"name": "Valor Econômico", "type": "Site: valor.com.br"},
            {"name": "Folha de S.Paulo", "type": "Site: folha.uol.com.br"},
            {"name": "O Estado de S.Paulo", "type": "Site: estadao.com.br"},
            {"name": "Globo.com", "type": "Site: g1.globo.com"},
            {"name": "UOL", "type": "Site: uol.com.br"},
            {"name": "Terra", "type": "Site: terra.com.br"},
            {"name": "R7", "type": "Site: r7.com"}
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
            "vtr": 79.1,  # VTR médio
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
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 1087.36,
                "impressions": 10036,
                "clicks": 5,
                "starts": 10035,
                "q25": 8238,
                "q50": 7583,
                "q75": 7165,
                "q100": 6796,
                "ctr": 0.0498,
                "vtr": 67.72,
                "cpv": 0.16
            },
            {
                "date": "2025-09-18", 
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 673.92,
                "impressions": 6514,
                "clicks": 0,
                "starts": 6513,
                "q25": 5260,
                "q50": 4854,
                "q75": 4506,
                "q100": 4212,
                "ctr": 0.0,
                "vtr": 64.66,
                "cpv": 0.16
            },
            {
                "date": "2025-09-19",
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)", 
                "spend": 1511.68,
                "impressions": 11609,
                "clicks": 1,
                "starts": 11609,
                "q25": 10367,
                "q50": 9992,
                "q75": 9698,
                "q100": 9448,
                "ctr": 0.0086,
                "vtr": 81.39,
                "cpv": 0.16
            },
            {
                "date": "2025-09-20",
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 346.40,
                "impressions": 3130,
                "clicks": 2,
                "starts": 3130,
                "q25": 2671,
                "q50": 2480,
                "q75": 2267,
                "q100": 2165,
                "ctr": 0.0639,
                "vtr": 69.17,
                "cpv": 0.16
            },
            {
                "date": "2025-09-21",
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 230.40,
                "impressions": 1757,
                "clicks": 0,
                "starts": 1757,
                "q25": 1629,
                "q50": 1531,
                "q75": 1466,
                "q100": 1440,
                "ctr": 0.0,
                "vtr": 81.96,
                "cpv": 0.16
            },
            {
                "date": "2025-09-22",
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 2577.44,
                "impressions": 19936,
                "clicks": 32,
                "starts": 19934,
                "q25": 17703,
                "q50": 17015,
                "q75": 16492,
                "q100": 16109,
                "ctr": 0.1605,
                "vtr": 80.80,
                "cpv": 0.16
            },
            {
                "date": "2025-09-23",
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 5488.32,
                "impressions": 41184,
                "clicks": 2,
                "starts": 41183,
                "q25": 37210,
                "q50": 35971,
                "q75": 35091,
                "q100": 34302,
                "ctr": 0.0049,
                "vtr": 83.29,
                "cpv": 0.16
            }
        ],
        "per_data": [
            {
                "creative": "TEASER SEBRAE 02 30s_V4.mp4 (667576613)",
                "spend": 10873.68,
                "impressions": 100036,
                "clicks": 40,
                "starts": 100035,
                "q25": 8238,
                "q50": 7583,
                "q75": 7165,
                "q100": 6796,
                "ctr": 0.04,
                "vtr": 79.1,
                "cpv": 0.16,
                "cpm": 16.00
            }
        ]
    }
    
    return campaign_data

def test_dashboard_data():
    """Testar dados do dashboard"""
    data = create_sebrae_test_data()
    
    print("✅ Dados de teste criados para SEBRAE")
    print(f"📊 Total investido: R$ {data['metrics']['spend']:,.2f}")
    print(f"👁️ Total impressões: {data['metrics']['impressions']:,}")
    print(f"👆 Total cliques: {data['metrics']['clicks']}")
    print(f"🎬 Total starts: {data['metrics']['starts']:,}")
    print(f"📈 VTR: {data['metrics']['vtr']:.1f}%")
    print(f"💰 CPV: R$ {data['metrics']['cpv']:.2f}")
    print(f"⏱️ Pacing: {data['metrics']['pacing']:.1f}%")
    print(f"📅 Dias com dados: {len(data['daily_data'])}")

    total_starts = sum(item.get("starts", 0) for item in data["daily_data"])
    total_q100 = sum(item.get("q100", 0) for item in data["daily_data"])
    consolidated_vtr = (total_q100 / total_starts * 100) if total_starts else 0

    assert round(data["metrics"].get("vtr", 0), 1) == round(consolidated_vtr, 1), (
        f"VTR total ({data['metrics'].get('vtr')}) deve corresponder ao consolidado "
        f"dos dias ({consolidated_vtr})"
    )

    # Salvar dados de teste
    with open('sebrae_test_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Dados salvos em sebrae_test_data.json")
    return data

if __name__ == "__main__":
    test_dashboard_data()
