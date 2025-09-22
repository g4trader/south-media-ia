#!/usr/bin/env python3
"""
Processar dados reais das planilhas e gerar dashboard
"""

import json
import pandas as pd
from datetime import datetime
import os

def process_real_sheets_data():
    """Processar dados reais das planilhas"""
    
    print("📊 PROCESSANDO DADOS REAIS DAS PLANILHAS")
    print("=" * 60)
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    print("\n📺 PROCESSANDO YOUTUBE:")
    print("-" * 40)
    
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['CPV'] = youtube_df['CPV'].str.replace(',', '.').astype(float)
    youtube_df['CPC'] = youtube_df['CPC'].str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['CTR'] = youtube_df['CTR'].str.replace(',', '.').astype(float)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    
    # Calcular totais YouTube
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    youtube_avg_ctr = float(youtube_df['CTR'].mean())
    youtube_avg_cpv = float(youtube_df['CPV'].mean())
    
    print(f"✅ Total Investido: R$ {youtube_total_spend:,.2f}")
    print(f"✅ Total Cliques: {youtube_total_clicks:,}")
    print(f"✅ Total Visualizações: {youtube_total_views:,}")
    print(f"✅ CTR Médio: {youtube_avg_ctr:.3f}")
    print(f"✅ CPV Médio: R$ {youtube_avg_cpv:.2f}")
    
    # Processar dados da Programática Video
    print("\n📺 PROCESSANDO PROGRAMÁTICA VIDEO:")
    print("-" * 40)
    
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['CPV'] = prog_df['CPV'].str.replace('R$ ', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    prog_df['CTR '] = prog_df['CTR '].str.replace(',', '.').astype(float)
    prog_df['CPC'] = prog_df['CPC'].str.replace(',', '.').astype(float)
    
    # Calcular totais Programática Video
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    prog_avg_ctr = float(prog_df['CTR '].mean())
    prog_avg_cpv = float(prog_df['CPV'].mean())
    
    print(f"✅ Total Investido: R$ {prog_total_spend:,.2f}")
    print(f"✅ Total Cliques: {prog_total_clicks:,}")
    print(f"✅ Total Impressões: {prog_total_impressions:,}")
    print(f"✅ CTR Médio: {prog_avg_ctr:.3f}")
    print(f"✅ CPV Médio: R$ {prog_avg_cpv:.2f}")
    
    # Calcular totais consolidados
    print("\n📊 TOTAIS CONSOLIDADOS:")
    print("-" * 40)
    
    total_spend = youtube_total_spend + prog_total_spend
    total_clicks = youtube_total_clicks + prog_total_clicks
    total_impressions = youtube_total_views + prog_total_impressions  # YouTube views = impressions
    
    print(f"✅ Total Investido: R$ {total_spend:,.2f}")
    print(f"✅ Total Cliques: {total_clicks:,}")
    print(f"✅ Total Impressões: {total_impressions:,}")
    
    # Criar configuração da campanha
    campaign_config = {
        "campaign_name": "Semana do Pescado",
        "start_date": "01/09/25",
        "end_date": "30/09/25",
        "total_budget": total_spend,
        "kpi_type": "CPV",
        "kpi_value": 0.08,
        "report_model": "Simple",
        "channels": [
            {
                "name": "YouTube",
                "display_name": "YouTube",
                "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
                "gid": "304137877",
                "budget": youtube_total_spend,
                "quantity": youtube_total_views,
                "actual_spend": youtube_total_spend,
                "actual_clicks": youtube_total_clicks,
                "actual_impressions": youtube_total_views,
                "actual_ctr": youtube_avg_ctr,
                "actual_cpv": youtube_avg_cpv
            },
            {
                "name": "Programática Video",
                "display_name": "Programática Video",
                "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
                "gid": "1489416055",
                "budget": prog_total_spend,
                "quantity": prog_total_impressions,
                "actual_spend": prog_total_spend,
                "actual_clicks": prog_total_clicks,
                "actual_impressions": prog_total_impressions,
                "actual_ctr": prog_avg_ctr,
                "actual_cpv": prog_avg_cpv
            }
        ],
        "consolidated_metrics": {
            "total_spend": total_spend,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_budget": total_spend,
            "budget_used": total_spend,
            "budget_remaining": 0,
            "completion_percentage": 100.0
        }
    }
    
    # Salvar configuração
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_filename = f"campaigns/campaign_real_data_{timestamp}.json"
    
    os.makedirs("campaigns", exist_ok=True)
    with open(config_filename, 'w', encoding='utf-8') as f:
        json.dump(campaign_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Configuração salva em: {config_filename}")
    
    return campaign_config

if __name__ == "__main__":
    config = process_real_sheets_data()
    print(f"\n🎉 Processamento concluído!")
    print(f"📊 Campanha: {config['campaign_name']}")
    print(f"💰 Orçamento Total: R$ {config['total_budget']:,.2f}")
    print(f"📺 Canais: {len(config['channels'])}")
