#!/usr/bin/env python3
"""
Mostrar detalhadamente os dados usados nos cálculos totalizadores da aba Visão Geral
"""

import json
import pandas as pd

def show_calculation_data():
    """Mostrar dados detalhados dos cálculos"""
    
    print("📊 DADOS USADOS NOS CÁLCULOS TOTALIZADORES DA ABA VISÃO GERAL")
    print("=" * 80)
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("\n📺 DADOS DO YOUTUBE:")
    print("-" * 50)
    
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    
    print(f"📋 Total de registros: {len(youtube_df)}")
    print(f"📅 Período: {youtube_df['Data'].min()} a {youtube_df['Data'].max()}")
    print()
    
    print("📊 DADOS DIÁRIOS DO YOUTUBE:")
    for _, row in youtube_df.iterrows():
        print(f"  {row['Data']}: R$ {row['Valor investido']:,.2f} | {row['Cliques']} cliques | {row['Visualizações']:,} views")
    
    print()
    print("🔢 TOTAIS CALCULADOS DO YOUTUBE:")
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    
    print(f"  💰 Total Investido: R$ {youtube_total_spend:,.2f}")
    print(f"  👆 Total Cliques: {youtube_total_clicks:,}")
    print(f"  👁️ Total Visualizações: {youtube_total_views:,}")
    
    print("\n" + "="*80)
    print("\n📺 DADOS DA PROGRAMÁTICA VIDEO:")
    print("-" * 50)
    
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    
    print(f"📋 Total de registros: {len(prog_df)}")
    print(f"📅 Período: {prog_df['Day'].min()} a {prog_df['Day'].max()}")
    print()
    
    print("📊 DADOS DIÁRIOS DA PROGRAMÁTICA VIDEO (primeiros 10 registros):")
    for i, (_, row) in enumerate(prog_df.head(10).iterrows()):
        print(f"  {row['Day']}: R$ {row['valor investido']:,.2f} | {row['Clicks']} cliques | {row['Imps']:,} impressões")
    
    if len(prog_df) > 10:
        print(f"  ... e mais {len(prog_df) - 10} registros")
    
    print()
    print("🔢 TOTAIS CALCULADOS DA PROGRAMÁTICA VIDEO:")
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    print(f"  💰 Total Investido: R$ {prog_total_spend:,.2f}")
    print(f"  👆 Total Cliques: {prog_total_clicks:,}")
    print(f"  👁️ Total Impressões: {prog_total_impressions:,}")
    
    print("\n" + "="*80)
    print("\n📊 TOTAIS CONSOLIDADOS (USADOS NA ABA VISÃO GERAL):")
    print("-" * 50)
    
    total_spend_used = youtube_total_spend + prog_total_spend
    total_clicks_used = youtube_total_clicks + prog_total_clicks
    total_impressions_used = youtube_total_views + prog_total_impressions
    
    print(f"💰 ORÇAMENTO UTILIZADO: R$ {total_spend_used:,.2f}")
    print(f"   ├─ YouTube: R$ {youtube_total_spend:,.2f}")
    print(f"   └─ Programática: R$ {prog_total_spend:,.2f}")
    print()
    
    print(f"👆 CLIQUES UTILIZADOS: {total_clicks_used:,}")
    print(f"   ├─ YouTube: {youtube_total_clicks:,}")
    print(f"   └─ Programática: {prog_total_clicks:,}")
    print()
    
    print(f"👁️ IMPRESSÕES/VIEWS UTILIZADAS: {total_impressions_used:,}")
    print(f"   ├─ YouTube (Views): {youtube_total_views:,}")
    print(f"   └─ Programática (Impressões): {prog_total_impressions:,}")
    print()
    
    # Calcular métricas derivadas
    cpv_used = total_spend_used / total_impressions_used if total_impressions_used > 0 else 0
    ctr_used = (total_clicks_used / total_impressions_used * 100) if total_impressions_used > 0 else 0
    
    print(f"💰 CPV UTILIZADO: R$ {cpv_used:.2f}")
    print(f"   └─ Cálculo: R$ {total_spend_used:,.2f} ÷ {total_impressions_used:,} = R$ {cpv_used:.2f}")
    print()
    
    print(f"📊 CTR UTILIZADO: {ctr_used:.2f}%")
    print(f"   └─ Cálculo: {total_clicks_used:,} ÷ {total_impressions_used:,} × 100 = {ctr_used:.2f}%")
    print()
    
    print("📈 PERCENTUAIS DE UTILIZAÇÃO:")
    print(f"   💰 Orçamento: 100.0% (dados reais = 100% do que foi gasto)")
    print(f"   👁️ Impressões: 100.0% (dados reais = 100% do que foi entregue)")
    
    print("\n" + "="*80)
    print("✅ RESUMO: Todos os dados da aba 'Visão Geral' são calculados automaticamente")
    print("   a partir da soma dos dados diários das planilhas do Google Sheets.")

if __name__ == "__main__":
    show_calculation_data()

