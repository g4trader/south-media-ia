#!/usr/bin/env python3
"""
Calcular dados "used" com valores contratados corretos usando dados das planilhas
"""

import json
import pandas as pd
from datetime import datetime

def calculate_used_data_corrected_final():
    """Calcular dados utilizados com valores contratados corretos"""
    
    # Valores contratados originais (IMUTÁVEIS) - dados fornecidos pelo usuário
    contracted_values = {
        "total_budget_contracted": 90000.00,  # R$ 50.000 + R$ 40.000
        "youtube_budget_contracted": 50000.00,
        "youtube_impressions_contracted": 625000,
        "prog_budget_contracted": 40000.00,
        "prog_impressions_contracted": 173914,
        "total_impressions_contracted": 798914  # 625.000 + 173.914
    }
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    # Calcular totais consolidados utilizados
    total_spend_used = youtube_total_spend + prog_total_spend
    total_clicks_used = youtube_total_clicks + prog_total_clicks
    total_impressions_used = youtube_total_views + prog_total_impressions
    
    # Calcular métricas derivadas
    cpv_used = total_spend_used / total_impressions_used if total_impressions_used > 0 else 0
    ctr_used = (total_clicks_used / total_impressions_used * 100) if total_impressions_used > 0 else 0
    
    # Calcular percentuais de utilização baseados nos valores CONTRATADOS
    budget_utilization_percentage = (total_spend_used / contracted_values['total_budget_contracted']) * 100
    impressions_utilization_percentage = (total_impressions_used / contracted_values['total_impressions_contracted']) * 100
    
    # Criar dados para o template
    used_data = {
        # Valores contratados (IMUTÁVEIS)
        "TOTAL_BUDGET_CONTRACTED": f"R$ {contracted_values['total_budget_contracted']:,.2f}",
        "YOUTUBE_BUDGET_CONTRACTED": f"R$ {contracted_values['youtube_budget_contracted']:,.2f}",
        "YOUTUBE_IMPRESSIONS_CONTRACTED": f"{contracted_values['youtube_impressions_contracted']:,}",
        "PROG_BUDGET_CONTRACTED": f"R$ {contracted_values['prog_budget_contracted']:,.2f}",
        "PROG_IMPRESSIONS_CONTRACTED": f"{contracted_values['prog_impressions_contracted']:,}",
        "TOTAL_IMPRESSIONS_CONTRACTED": f"{contracted_values['total_impressions_contracted']:,}",
        
        # Valores utilizados (MUTÁVEIS)
        "TOTAL_SPEND_USED": f"R$ {total_spend_used:,.2f}",
        "TOTAL_CLICKS_USED": f"{total_clicks_used:,}",
        "TOTAL_IMPRESSIONS_USED": f"{total_impressions_used:,}",
        "TOTAL_CPV_USED": f"R$ {cpv_used:.2f}",
        "TOTAL_CTR_USED": f"{ctr_used:.2f}%",
        
        # Percentuais de utilização
        "BUDGET_UTILIZATION_PERCENTAGE": f"{budget_utilization_percentage:.1f}%",
        "IMPRESSIONS_UTILIZATION_PERCENTAGE": f"{impressions_utilization_percentage:.1f}%",
        
        # Dados por canal (utilizados)
        "YOUTUBE_TOTAL_SPEND": f"R$ {youtube_total_spend:,.2f}",
        "YOUTUBE_TOTAL_CLICKS": f"{youtube_total_clicks:,}",
        "YOUTUBE_TOTAL_VIEWS": f"{youtube_total_views:,}",
        "PROG_TOTAL_SPEND": f"R$ {prog_total_spend:,.2f}",
        "PROG_TOTAL_CLICKS": f"{prog_total_clicks:,}",
        "PROG_TOTAL_IMPRESSIONS": f"{prog_total_impressions:,}"
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"used_data_corrected_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(used_data, f, indent=2, ensure_ascii=False)
    
    print("✅ DADOS 'USED' CORRIGIDOS COM VALORES CONTRATADOS!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 VALORES CONTRATADOS (IMUTÁVEIS):")
    print(f"💰 Orçamento Total: {used_data['TOTAL_BUDGET_CONTRACTED']}")
    print(f"   ├─ YouTube: {used_data['YOUTUBE_BUDGET_CONTRACTED']}")
    print(f"   └─ Programática: {used_data['PROG_BUDGET_CONTRACTED']}")
    print()
    print(f"👁️ Impressões Contratadas: {used_data['TOTAL_IMPRESSIONS_CONTRACTED']}")
    print(f"   ├─ YouTube: {used_data['YOUTUBE_IMPRESSIONS_CONTRACTED']}")
    print(f"   └─ Programática: {used_data['PROG_IMPRESSIONS_CONTRACTED']}")
    print()
    print("📊 VALORES UTILIZADOS (MUTÁVEIS):")
    print(f"💰 Orçamento Utilizado: {used_data['TOTAL_SPEND_USED']}")
    print(f"👁️ Impressões Utilizadas: {used_data['TOTAL_IMPRESSIONS_USED']}")
    print(f"👆 Cliques Utilizados: {used_data['TOTAL_CLICKS_USED']}")
    print(f"💰 CPV Utilizado: {used_data['TOTAL_CPV_USED']}")
    print(f"📊 CTR Utilizado: {used_data['TOTAL_CTR_USED']}")
    print()
    print("📈 PERCENTUAIS DE UTILIZAÇÃO:")
    print(f"💰 Orçamento: {used_data['BUDGET_UTILIZATION_PERCENTAGE']}")
    print(f"👁️ Impressões: {used_data['IMPRESSIONS_UTILIZATION_PERCENTAGE']}")
    
    return filename

if __name__ == "__main__":
    calculate_used_data_corrected_final()

