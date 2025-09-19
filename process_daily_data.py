#!/usr/bin/env python3
"""
Processar dados diários das planilhas para a aba "Entrega Diária"
"""

import json
import pandas as pd
from datetime import datetime

def process_daily_data():
    """Processar dados diários das planilhas"""
    
    print("📊 PROCESSANDO DADOS DIÁRIOS DAS PLANILHAS")
    print("=" * 60)
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    print("\n📺 PROCESSANDO DADOS DIÁRIOS DO YOUTUBE:")
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
    
    # Calcular médias diárias do YouTube
    youtube_avg_views = int(youtube_df['Visualizações'].sum() / len(youtube_df))
    youtube_avg_investment = youtube_df['Valor investido'].sum() / len(youtube_df)
    youtube_avg_clicks = int(youtube_df['Cliques'].sum() / len(youtube_df))
    youtube_avg_ctr = youtube_df['CTR'].mean()
    
    print(f"✅ Média de Visualizações: {youtube_avg_views:,}/dia")
    print(f"✅ Média de Investimento: R$ {youtube_avg_investment:.2f}/dia")
    print(f"✅ Média de Cliques: {youtube_avg_clicks}/dia")
    print(f"✅ CTR Médio: {youtube_avg_ctr:.2f}%")
    
    # Processar dados da Programática Video
    print("\n📺 PROCESSANDO DADOS DIÁRIOS DA PROGRAMÁTICA VIDEO:")
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
    
    # Calcular médias diárias da Programática Video
    prog_avg_impressions = int(prog_df['Imps'].sum() / len(prog_df))
    prog_avg_investment = prog_df['valor investido'].sum() / len(prog_df)
    prog_avg_clicks = int(prog_df['Clicks'].sum() / len(prog_df))
    prog_avg_ctr = prog_df['CTR '].mean()
    
    print(f"✅ Média de Impressões: {prog_avg_impressions:,}/dia")
    print(f"✅ Média de Investimento: R$ {prog_avg_investment:.2f}/dia")
    print(f"✅ Média de Cliques: {prog_avg_clicks}/dia")
    print(f"✅ CTR Médio: {prog_avg_ctr:.2f}%")
    
    # Criar dados da tabela diária
    print("\n📋 CRIANDO DADOS DA TABELA DIÁRIA:")
    print("-" * 40)
    
    daily_table_rows = []
    
    # Adicionar dados do YouTube
    for _, row in youtube_df.iterrows():
        date = row['Data']
        views = int(row['Visualizações'])
        clicks = int(row['Cliques'])
        ctr = row['CTR']
        investment = row['Valor investido']
        
        daily_table_rows.append({
            'date': date,
            'channel': 'YouTube',
            'impressions': views,
            'clicks': clicks,
            'ctr': ctr,
            'investment': investment
        })
    
    # Adicionar dados da Programática Video
    for _, row in prog_df.iterrows():
        date = row['Day']
        # Converter formato de data de 2025-09-01 para 01/09
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date = date_obj.strftime('%d/%m')
        except:
            pass
        
        impressions = int(row['Imps'])
        clicks = int(row['Clicks'])
        ctr = row['CTR ']
        investment = row['valor investido']
        
        daily_table_rows.append({
            'date': date,
            'channel': 'Programática Video',
            'impressions': impressions,
            'clicks': clicks,
            'ctr': ctr,
            'investment': investment
        })
    
    # Ordenar por data
    daily_table_rows.sort(key=lambda x: x['date'])
    
    # Gerar HTML das linhas da tabela
    table_rows_html = ""
    for row in daily_table_rows:
        table_rows_html += f'<tr><td>{row["date"]}</td><td>{row["channel"]}</td><td>{row["impressions"]:,}</td><td>{row["clicks"]}</td><td>{row["ctr"]:.2f}%</td><td>R$ {row["investment"]:,.2f}</td></tr>\n'
    
    print(f"✅ {len(daily_table_rows)} linhas de dados diários criadas")
    
    # Criar configuração das variáveis
    daily_variables = {
        'YOUTUBE_AVG_VIEWS': f"{youtube_avg_views:,}",
        'YOUTUBE_AVG_INVESTMENT': f"R$ {youtube_avg_investment:,.2f}",
        'YOUTUBE_AVG_CLICKS': f"{youtube_avg_clicks}",
        'YOUTUBE_AVG_CTR': f"{youtube_avg_ctr:.2f}",
        'PROG_AVG_IMPRESSIONS': f"{prog_avg_impressions:,}",
        'PROG_AVG_INVESTMENT': f"R$ {prog_avg_investment:,.2f}",
        'PROG_AVG_CLICKS': f"{prog_avg_clicks}",
        'PROG_AVG_CTR': f"{prog_avg_ctr:.2f}",
        'DAILY_DATA_TABLE_ROWS': table_rows_html
    }
    
    # Salvar variáveis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    variables_filename = f"daily_variables_{timestamp}.json"
    
    with open(variables_filename, 'w', encoding='utf-8') as f:
        json.dump(daily_variables, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Variáveis salvas em: {variables_filename}")
    
    return daily_variables

if __name__ == "__main__":
    variables = process_daily_data()
    print(f"\n🎉 Processamento de dados diários concluído!")
    print(f"📊 Variáveis criadas: {len(variables)}")


