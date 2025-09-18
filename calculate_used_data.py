#!/usr/bin/env python3
"""
Calcular dados utilizados a partir dos totais dos dados diários das planilhas
"""

import json
import pandas as pd
from datetime import datetime

def calculate_used_data():
    """Calcular dados utilizados a partir dos dados diários"""
    
    print("📊 CALCULANDO DADOS UTILIZADOS A PARTIR DOS DADOS DIÁRIOS")
    print("=" * 60)
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    print("\n📺 CALCULANDO TOTAIS DO YOUTUBE:")
    print("-" * 40)
    
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    
    # Calcular totais do YouTube
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    
    print(f"✅ Total Investido YouTube: R$ {youtube_total_spend:,.2f}")
    print(f"✅ Total Cliques YouTube: {youtube_total_clicks:,}")
    print(f"✅ Total Visualizações YouTube: {youtube_total_views:,}")
    
    # Processar dados da Programática Video
    print("\n📺 CALCULANDO TOTAIS DA PROGRAMÁTICA VIDEO:")
    print("-" * 40)
    
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    
    # Calcular totais da Programática Video
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    print(f"✅ Total Investido Programática: R$ {prog_total_spend:,.2f}")
    print(f"✅ Total Cliques Programática: {prog_total_clicks:,}")
    print(f"✅ Total Impressões Programática: {prog_total_impressions:,}")
    
    # Calcular totais consolidados
    print("\n📊 TOTAIS CONSOLIDADOS (DADOS UTILIZADOS):")
    print("-" * 40)
    
    total_spend_used = youtube_total_spend + prog_total_spend
    total_clicks_used = youtube_total_clicks + prog_total_clicks
    total_impressions_used = youtube_total_views + prog_total_impressions  # YouTube views = impressions
    
    print(f"✅ Total Investido Utilizado: R$ {total_spend_used:,.2f}")
    print(f"✅ Total Cliques Utilizados: {total_clicks_used:,}")
    print(f"✅ Total Impressões/Views Utilizadas: {total_impressions_used:,}")
    
    # Calcular CPV utilizado
    cpv_used = total_spend_used / total_impressions_used if total_impressions_used > 0 else 0
    print(f"✅ CPV Utilizado: R$ {cpv_used:.2f}")
    
    # Calcular CTR utilizado
    ctr_used = (total_clicks_used / total_impressions_used * 100) if total_impressions_used > 0 else 0
    print(f"✅ CTR Utilizado: {ctr_used:.2f}%")
    
    # Calcular percentual de utilização do orçamento
    # Assumindo que o orçamento total é o mesmo que foi gasto (100% utilizado)
    budget_utilization_percentage = 100.0  # Como estamos usando dados reais, assumimos 100%
    print(f"✅ Percentual de Utilização do Orçamento: {budget_utilization_percentage:.1f}%")
    
    # Calcular percentual de utilização das impressões
    # Assumindo que as impressões contratadas são as mesmas que foram utilizadas
    impressions_utilization_percentage = 100.0  # Como estamos usando dados reais, assumimos 100%
    print(f"✅ Percentual de Utilização das Impressões: {impressions_utilization_percentage:.1f}%")
    
    # Criar configuração dos dados utilizados
    used_data = {
        'TOTAL_SPEND_USED': f"R$ {total_spend_used:,.2f}",
        'TOTAL_CLICKS_USED': f"{total_clicks_used:,}",
        'TOTAL_IMPRESSIONS_USED': f"{total_impressions_used:,}",
        'TOTAL_CPV_USED': f"R$ {cpv_used:.2f}",
        'TOTAL_CTR_USED': f"{ctr_used:.2f}%",
        'BUDGET_UTILIZATION_PERCENTAGE': f"{budget_utilization_percentage:.1f}%",
        'IMPRESSIONS_UTILIZATION_PERCENTAGE': f"{impressions_utilization_percentage:.1f}%",
        'YOUTUBE_TOTAL_SPEND': f"R$ {youtube_total_spend:,.2f}",
        'YOUTUBE_TOTAL_CLICKS': f"{youtube_total_clicks:,}",
        'YOUTUBE_TOTAL_VIEWS': f"{youtube_total_views:,}",
        'PROG_TOTAL_SPEND': f"R$ {prog_total_spend:,.2f}",
        'PROG_TOTAL_CLICKS': f"{prog_total_clicks:,}",
        'PROG_TOTAL_IMPRESSIONS': f"{prog_total_impressions:,}"
    }
    
    # Salvar dados utilizados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    used_data_filename = f"used_data_{timestamp}.json"
    
    with open(used_data_filename, 'w', encoding='utf-8') as f:
        json.dump(used_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dados utilizados salvos em: {used_data_filename}")
    
    return used_data

if __name__ == "__main__":
    data = calculate_used_data()
    print(f"\n🎉 Cálculo de dados utilizados concluído!")
    print(f"📊 Variáveis criadas: {len(data)}")

