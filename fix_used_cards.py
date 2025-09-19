#!/usr/bin/env python3
"""
Corrigir cards IMPRESSÕES/VIEWS UTILIZADAS e CPV UTILIZADO
"""

import json
import pandas as pd
from datetime import datetime

def fix_used_cards():
    """Corrigir cards com dados utilizados corretos"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔧 CORRIGINDO CARDS IMPRESSÕES/VIEWS UTILIZADAS E CPV UTILIZADO")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas do YouTube
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Video assistido 100%'] = youtube_df['Video assistido 100%'].astype(int)
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Video assistido 100%'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas da Programática
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    # Calcular totais utilizados
    total_spend_used = youtube_total_spend + prog_total_spend
    total_clicks_used = youtube_total_clicks + prog_total_clicks
    total_impressions_used = youtube_total_views + prog_total_impressions  # YouTube views + Programática impressions
    
    # Calcular CPV utilizado (custo por visualização/impressão)
    total_cpv_used = total_spend_used / total_impressions_used if total_impressions_used > 0 else 0
    
    # Calcular CTR utilizado
    total_ctr_used = (total_clicks_used / total_impressions_used * 100) if total_impressions_used > 0 else 0
    
    # Dados contratados (imutáveis)
    total_budget_contracted = 90000.00
    total_impressions_contracted = 798914  # 625000 (YouTube) + 173914 (Programática)
    
    # Calcular percentuais de utilização
    budget_utilization = (total_spend_used / total_budget_contracted * 100) if total_budget_contracted > 0 else 0
    impressions_utilization = (total_impressions_used / total_impressions_contracted * 100) if total_impressions_contracted > 0 else 0
    
    print(f"📊 DADOS UTILIZADOS CALCULADOS:")
    print(f"📺 YouTube:")
    print(f"   💰 Investido: R$ {youtube_total_spend:,.2f}")
    print(f"   👆 Cliques: {youtube_total_clicks:,}")
    print(f"   👁️ Views (100%): {youtube_total_views:,}")
    
    print(f"\n📺 Programática:")
    print(f"   💰 Investido: R$ {prog_total_spend:,.2f}")
    print(f"   👆 Cliques: {prog_total_clicks:,}")
    print(f"   👁️ Impressões: {prog_total_impressions:,}")
    
    print(f"\n📊 TOTAIS UTILIZADOS:")
    print(f"💰 Total Investido: R$ {total_spend_used:,.2f}")
    print(f"👆 Total Cliques: {total_clicks_used:,}")
    print(f"👁️ Total Impressões/Views: {total_impressions_used:,}")
    print(f"💵 CPV Utilizado: R$ {total_cpv_used:.2f}")
    print(f"📊 CTR Utilizado: {total_ctr_used:.2f}%")
    
    print(f"\n📊 PERCENTUAIS DE UTILIZAÇÃO:")
    print(f"💰 Orçamento: {budget_utilization:.1f}%")
    print(f"👁️ Impressões/Views: {impressions_utilization:.1f}%")
    
    # Criar dados corrigidos
    corrected_data = {
        # Dados contratados (imutáveis)
        "TOTAL_BUDGET_CONTRACTED": "R$ 90,000.00",
        "TOTAL_IMPRESSIONS_CONTRACTED": "798,914",
        
        # Dados utilizados (corrigidos)
        "TOTAL_SPEND_USED": f"R$ {total_spend_used:,.2f}",
        "TOTAL_CLICKS_USED": f"{total_clicks_used:,}",
        "TOTAL_IMPRESSIONS_USED": f"{total_impressions_used:,}",
        "TOTAL_CPV_USED": f"R$ {total_cpv_used:.2f}",
        "TOTAL_CTR_USED": f"{total_ctr_used:.2f}%",
        
        # Percentuais de utilização
        "BUDGET_UTILIZATION_PERCENTAGE": f"{budget_utilization:.1f}%",
        "IMPRESSIONS_UTILIZATION_PERCENTAGE": f"{impressions_utilization:.1f}%",
        
        # Dados individuais por canal
        "YOUTUBE_TOTAL_SPEND": f"R$ {youtube_total_spend:,.2f}",
        "YOUTUBE_TOTAL_CLICKS": f"{youtube_total_clicks:,}",
        "YOUTUBE_TOTAL_VIEWS": f"{youtube_total_views:,}",
        "PROG_TOTAL_SPEND": f"R$ {prog_total_spend:,.2f}",
        "PROG_TOTAL_CLICKS": f"{prog_total_clicks:,}",
        "PROG_TOTAL_IMPRESSIONS": f"{prog_total_impressions:,}"
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"used_data_fixed_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS CORRIGIDOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ IMPRESSÕES/VIEWS UTILIZADAS: {total_impressions_used:,}")
    print(f"✅ CPV UTILIZADO: R$ {total_cpv_used:.2f}")
    print(f"✅ CTR UTILIZADO: {total_ctr_used:.2f}%")
    print(f"✅ Orçamento Utilizado: {budget_utilization:.1f}%")
    print(f"✅ Impressões Utilizadas: {impressions_utilization:.1f}%")
    
    return filename

if __name__ == "__main__":
    fix_used_cards()


