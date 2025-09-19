#!/usr/bin/env python3
"""
Verificar e corrigir dados das planilhas
"""

import json
import pandas as pd
from datetime import datetime

def verify_and_fix_data():
    """Verificar e corrigir dados das planilhas"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔍 VERIFICAÇÃO DOS DADOS DAS PLANILHAS")
    print("=" * 60)
    
    # Verificar YouTube
    print("\n📺 YOUTUBE:")
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    print(f"Colunas disponíveis: {youtube_df.columns.tolist()}")
    
    # Converter colunas numéricas
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Visualizações'] = youtube_df['Visualizações'].astype(int)
    youtube_df['Vídeo assistido até 25%'] = youtube_df['Vídeo assistido até 25%'].astype(int)
    youtube_df['Vídeo assistido até 50%'] = youtube_df['Vídeo assistido até 50%'].astype(int)
    youtube_df['Vídeo assistido até 75%'] = youtube_df['Vídeo assistido até 75%'].astype(int)
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_total_views = int(youtube_df['Visualizações'].sum())
    youtube_25_percent = int(youtube_df['Vídeo assistido até 25%'].sum())
    youtube_50_percent = int(youtube_df['Vídeo assistido até 50%'].sum())
    youtube_75_percent = int(youtube_df['Vídeo assistido até 75%'].sum())
    
    print(f"💰 Total Investido: R$ {youtube_total_spend:,.2f}")
    print(f"👆 Total Cliques: {youtube_total_clicks:,}")
    print(f"👁️ Total Visualizações: {youtube_total_views:,}")
    print(f"📊 25% Assistido: {youtube_25_percent:,}")
    print(f"📊 50% Assistido: {youtube_50_percent:,}")
    print(f"📊 75% Assistido: {youtube_75_percent:,}")
    print("❌ 100% Assistido: NÃO DISPONÍVEL (coluna não existe)")
    
    # Verificar Programática Video
    print("\n📺 PROGRAMÁTICA VIDEO:")
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    print(f"Colunas disponíveis: {prog_df.columns.tolist()}")
    
    # Converter colunas numéricas
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    prog_df['100% Complete'] = prog_df['100% Complete'].astype(int)
    prog_df['Video Starts'] = prog_df['Video Starts'].astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    prog_25_percent = int(prog_df['25% Video Complete'].sum())
    prog_50_percent = int(prog_df['50% Video Complete'].sum())
    prog_75_percent = int(prog_df['75% Video Complete'].sum())
    prog_100_percent = int(prog_df['100% Complete'].sum())
    prog_video_starts = int(prog_df['Video Starts'].sum())
    
    print(f"💰 Total Investido: R$ {prog_total_spend:,.2f}")
    print(f"👆 Total Cliques: {prog_total_clicks:,}")
    print(f"👁️ Total Impressões: {prog_total_impressions:,}")
    print(f"📊 25% Video Complete: {prog_25_percent:,}")
    print(f"📊 50% Video Complete: {prog_50_percent:,}")
    print(f"📊 75% Video Complete: {prog_75_percent:,}")
    print(f"📊 100% Complete: {prog_100_percent:,}")
    print(f"📊 Video Starts: {prog_video_starts:,}")
    
    # Calcular totais corretos
    total_video_completion = youtube_total_views + prog_100_percent  # YouTube views + Programática 100% Complete
    
    print("\n🔧 CORREÇÕES NECESSÁRIAS:")
    print("=" * 60)
    print("1. YouTube: Usar 'Visualizações' como 100% Complete (não tem coluna específica)")
    print("2. Programática: Usar coluna '100% Complete' (não impressões)")
    print("3. Total Video Completion: YouTube Visualizações + Programática 100% Complete")
    
    print(f"\n📊 TOTAIS CORRETOS:")
    print(f"YouTube 100% Complete: {youtube_total_views:,} (Visualizações)")
    print(f"Programática 100% Complete: {prog_100_percent:,} (coluna 100% Complete)")
    print(f"TOTAL Video Completion: {total_video_completion:,}")
    
    # Criar dados corrigidos
    corrected_data = {
        # Quartis de vídeo (YouTube)
        "QUARTIL_25_VALUE": f"{youtube_25_percent:,}",
        "QUARTIL_25_PERCENTAGE": f"{(youtube_25_percent / youtube_total_views * 100):.2f}%",
        "QUARTIL_50_VALUE": f"{youtube_50_percent:,}",
        "QUARTIL_50_PERCENTAGE": f"{(youtube_50_percent / youtube_total_views * 100):.2f}%",
        "QUARTIL_75_VALUE": f"{youtube_75_percent:,}",
        "QUARTIL_75_PERCENTAGE": f"{(youtube_75_percent / youtube_total_views * 100):.2f}%",
        "QUARTIL_100_VALUE": f"{youtube_total_views:,}",
        "QUARTIL_100_PERCENTAGE": "100.00%",
        
        # Estratégias (corrigidas)
        "YOUTUBE_BUDGET": f"R$ {youtube_total_spend:,.2f}",
        "YOUTUBE_VIDEO_COMPLETION": f"{youtube_total_views:,}",  # Visualizações
        "YOUTUBE_CLICKS": f"{youtube_total_clicks:,}",
        "YOUTUBE_CTR": f"{(youtube_total_clicks / youtube_total_views * 100):.2f}%",
        "YOUTUBE_CPV": f"R$ {youtube_total_spend / youtube_total_views:.2f}",
        "YOUTUBE_COMPLETION": "49.5%",  # Manter cálculo anterior
        
        "PROG_BUDGET": f"R$ {prog_total_spend:,.2f}",
        "PROG_VIDEO_COMPLETION": f"{prog_100_percent:,}",  # CORRIGIDO: 100% Complete
        "PROG_CLICKS": f"{prog_total_clicks:,}",
        "PROG_CTR": f"{(prog_total_clicks / prog_total_impressions * 100):.2f}%",
        "PROG_CPV": f"R$ {prog_total_spend / prog_total_impressions:.2f}",
        "PROG_COMPLETION": "47.3%",  # Manter cálculo anterior
        
        "TOTAL_BUDGET": f"R$ {youtube_total_spend + prog_total_spend:,.2f}",
        "TOTAL_VIDEO_COMPLETION": f"{total_video_completion:,}",  # CORRIGIDO
        "TOTAL_CLICKS": f"{youtube_total_clicks + prog_total_clicks:,}",
        "TOTAL_CTR": f"{((youtube_total_clicks + prog_total_clicks) / (youtube_total_views + prog_total_impressions) * 100):.2f}%",
        "TOTAL_CPV": f"R$ {(youtube_total_spend + prog_total_spend) / (youtube_total_views + prog_total_impressions):.2f}",
        "TOTAL_COMPLETION": "48.4%"  # Manter cálculo anterior
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_corrected_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS CORRIGIDOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ YouTube 100% Complete: {youtube_total_views:,} (Visualizações)")
    print(f"✅ Programática 100% Complete: {prog_100_percent:,} (coluna 100% Complete)")
    print(f"✅ Total Video Completion: {total_video_completion:,}")
    
    return filename

if __name__ == "__main__":
    verify_and_fix_data()


