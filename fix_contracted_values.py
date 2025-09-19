#!/usr/bin/env python3
"""
Corrigir os valores contratados na configuração da campanha
"""

import json
from datetime import datetime

def fix_contracted_values():
    """Corrigir valores contratados com os dados originais fornecidos pelo usuário"""
    
    # Valores contratados originais fornecidos pelo usuário
    contracted_values = {
        "campaign_name": "Semana do Pescado",
        "start_date": "01/09/25",
        "end_date": "30/09/25",
        "total_budget": 90000.00,  # R$ 50.000 + R$ 40.000
        "kpi_type": "CPV",
        "kpi_value": 0.08,
        "report_model": "Simple",
        "channels": [
            {
                "name": "YouTube",
                "display_name": "YouTube",
                "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
                "gid": "304137877",
                "budget": 50000.00,  # Valor contratado original
                "quantity": 625000,  # Impressões contratadas originais
                "cpv_contracted": 0.08,  # CPV contratado
                # Dados reais (utilizados) - estes mudam
                "actual_spend": 24729.12,
                "actual_clicks": 577,
                "actual_impressions": 309114,
                "actual_ctr": 0.18669230769230769,
                "actual_cpv": 0.07999999999999999
            },
            {
                "name": "Programática Video",
                "display_name": "Programática Video",
                "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
                "gid": "1489416055",
                "budget": 40000.00,  # Valor contratado original
                "quantity": 173914,  # Impressões contratadas originais
                "cpv_contracted": 0.23,  # CPV contratado
                # Dados reais (utilizados) - estes mudam
                "actual_spend": 18921.87,
                "actual_clicks": 211,
                "actual_impressions": 100113,
                "actual_ctr": 0.2528571428571429,
                "actual_cpv": 0.23
            }
        ],
        "consolidated_metrics": {
            "total_budget_contracted": 90000.00,  # Total contratado
            "total_quantity_contracted": 798914,  # 625.000 + 173.914
            "total_spend_used": 43650.99,  # Total utilizado
            "total_clicks_used": 788,
            "total_impressions_used": 409227,
            "budget_utilization_percentage": 48.5,  # (43.650,99 / 90.000) * 100
            "impressions_utilization_percentage": 51.2  # (409.227 / 798.914) * 100
        }
    }
    
    # Salvar configuração corrigida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"campaigns/campaign_corrected_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(contracted_values, f, indent=2, ensure_ascii=False)
    
    print("✅ VALORES CONTRATADOS CORRIGIDOS!")
    print("=" * 60)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 VALORES CONTRATADOS (IMUTÁVEIS):")
    print(f"💰 Orçamento Total: R$ {contracted_values['total_budget']:,.2f}")
    print(f"   ├─ YouTube: R$ {contracted_values['channels'][0]['budget']:,.2f}")
    print(f"   └─ Programática: R$ {contracted_values['channels'][1]['budget']:,.2f}")
    print()
    print(f"👁️ Impressões Contratadas: {contracted_values['consolidated_metrics']['total_quantity_contracted']:,}")
    print(f"   ├─ YouTube: {contracted_values['channels'][0]['quantity']:,}")
    print(f"   └─ Programática: {contracted_values['channels'][1]['quantity']:,}")
    print()
    print("📊 VALORES UTILIZADOS (MUTÁVEIS):")
    print(f"💰 Orçamento Utilizado: R$ {contracted_values['consolidated_metrics']['total_spend_used']:,.2f}")
    print(f"👁️ Impressões Utilizadas: {contracted_values['consolidated_metrics']['total_impressions_used']:,}")
    print()
    print("📈 PERCENTUAIS DE UTILIZAÇÃO:")
    print(f"💰 Orçamento: {contracted_values['consolidated_metrics']['budget_utilization_percentage']:.1f}%")
    print(f"👁️ Impressões: {contracted_values['consolidated_metrics']['impressions_utilization_percentage']:.1f}%")
    
    return filename

if __name__ == "__main__":
    fix_contracted_values()


