#!/usr/bin/env python3
"""
Calcular dados para os gráficos baseados nos dados reais das planilhas
"""

import json
import pandas as pd
from datetime import datetime

def calculate_charts_data():
    """Calcular dados para os gráficos"""
    
    # Valores contratados originais
    contracted_values = {
        "youtube_budget_contracted": 50000.00,
        "youtube_impressions_contracted": 625000,
        "prog_budget_contracted": 40000.00,
        "prog_impressions_contracted": 173914
    }
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    # Calcular percentuais de conclusão
    youtube_budget_completion = (youtube_total_spend / contracted_values['youtube_budget_contracted']) * 100
    youtube_impressions_completion = (youtube_total_views / contracted_values['youtube_impressions_contracted']) * 100
    
    prog_budget_completion = (prog_total_spend / contracted_values['prog_budget_contracted']) * 100
    prog_impressions_completion = (prog_total_impressions / contracted_values['prog_impressions_contracted']) * 100
    
    # Calcular médias de conclusão por canal
    youtube_avg_completion = (youtube_budget_completion + youtube_impressions_completion) / 2
    prog_avg_completion = (prog_budget_completion + prog_impressions_completion) / 2
    
    # Criar dados para os gráficos
    charts_data = {
        # Dados para barras de progresso
        "CHANNEL_1_NAME": "YouTube",
        "CHANNEL_1_COMPLETION": f"{youtube_avg_completion:.1f}",
        "CHANNEL_2_NAME": "Programática Video", 
        "CHANNEL_2_COMPLETION": f"{prog_avg_completion:.1f}",
        
        # Dados para gráfico de distribuição
        "CHART_LABELS": ["YouTube", "Programática Video"],
        "CHART_DATA": [youtube_avg_completion, prog_avg_completion],
        "CHART_COLORS": ["#FB923C", "#8B5CF6"],
        
        # Dados detalhados para debug
        "youtube_budget_completion": youtube_budget_completion,
        "youtube_impressions_completion": youtube_impressions_completion,
        "prog_budget_completion": prog_budget_completion,
        "prog_impressions_completion": prog_impressions_completion,
        "youtube_total_spend": youtube_total_spend,
        "youtube_total_views": youtube_total_views,
        "prog_total_spend": prog_total_spend,
        "prog_total_impressions": prog_total_impressions
    }
    
    # Salvar dados dos gráficos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"charts_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(charts_data, f, indent=2, ensure_ascii=False)
    
    print("✅ DADOS DOS GRÁFICOS CALCULADOS!")
    print("=" * 60)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 TAXA DE CONCLUSÃO POR ESTRATÉGIA:")
    print(f"🎬 {charts_data['CHANNEL_1_NAME']}: {charts_data['CHANNEL_1_COMPLETION']}%")
    print(f"🎬 {charts_data['CHANNEL_2_NAME']}: {charts_data['CHANNEL_2_COMPLETION']}%")
    print()
    print("📈 DETALHES DOS CÁLCULOS:")
    print(f"📺 YouTube:")
    print(f"   💰 Orçamento: {youtube_budget_completion:.1f}% ({youtube_total_spend:,.2f} de {contracted_values['youtube_budget_contracted']:,.2f})")
    print(f"   👁️ Impressões: {youtube_impressions_completion:.1f}% ({youtube_total_views:,} de {contracted_values['youtube_impressions_contracted']:,})")
    print(f"   📊 Média: {youtube_avg_completion:.1f}%")
    print()
    print(f"📺 Programática Video:")
    print(f"   💰 Orçamento: {prog_budget_completion:.1f}% ({prog_total_spend:,.2f} de {contracted_values['prog_budget_contracted']:,.2f})")
    print(f"   👁️ Impressões: {prog_impressions_completion:.1f}% ({prog_total_impressions:,} de {contracted_values['prog_impressions_contracted']:,})")
    print(f"   📊 Média: {prog_avg_completion:.1f}%")
    
    return filename

if __name__ == "__main__":
    calculate_charts_data()



