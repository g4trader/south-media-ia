#!/usr/bin/env python3
"""
Atualizar dados com a nova coluna 100% do YouTube
"""

import json
import pandas as pd
from datetime import datetime

def update_with_youtube_100_percent():
    """Atualizar dados com a nova coluna 100% do YouTube"""
    
    # Carregar dados atualizados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔄 ATUALIZANDO DADOS COM NOVA COLUNA 100% DO YOUTUBE")
    print("=" * 70)
    
    # Processar dados do YouTube (agora com coluna 100%)
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    print(f"📺 YOUTUBE - Colunas disponíveis: {youtube_df.columns.tolist()}")
    
    # Converter colunas numéricas
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Vídeo assistido até 25%'] = youtube_df['Vídeo assistido até 25%'].astype(int)
    youtube_df['Vídeo assistido até 50%'] = youtube_df['Vídeo assistido até 50%'].astype(int)
    youtube_df['Vídeo assistido até 75%'] = youtube_df['Vídeo assistido até 75%'].astype(int)
    youtube_df['Video assistido 100%'] = youtube_df['Video assistido 100%'].astype(int)  # NOVA COLUNA
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_25_percent = int(youtube_df['Vídeo assistido até 25%'].sum())
    youtube_50_percent = int(youtube_df['Vídeo assistido até 50%'].sum())
    youtube_75_percent = int(youtube_df['Vídeo assistido até 75%'].sum())
    youtube_100_percent = int(youtube_df['Video assistido 100%'].sum())  # NOVO DADO
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    print(f"📺 PROGRAMÁTICA - Colunas disponíveis: {prog_df.columns.tolist()}")
    
    # Converter colunas numéricas
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    prog_df['100%  Video Complete'] = prog_df['100%  Video Complete'].astype(int)  # Note o espaço extra
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    prog_25_percent = int(prog_df['25% Video Complete'].sum())
    prog_50_percent = int(prog_df['50% Video Complete'].sum())
    prog_75_percent = int(prog_df['75% Video Complete'].sum())
    prog_100_percent = int(prog_df['100%  Video Complete'].sum())
    
    # Calcular totais corretos
    total_video_completion = youtube_100_percent + prog_100_percent  # Ambos com coluna 100%
    total_spend = youtube_total_spend + prog_total_spend
    total_clicks = youtube_total_clicks + prog_total_clicks
    total_impressions = youtube_100_percent + prog_total_impressions  # YouTube 100% + Programática impressões
    
    print(f"\n📊 DADOS ATUALIZADOS:")
    print(f"📺 YouTube:")
    print(f"   💰 Total Investido: R$ {youtube_total_spend:,.2f}")
    print(f"   👆 Total Cliques: {youtube_total_clicks:,}")
    print(f"   📊 25% Assistido: {youtube_25_percent:,}")
    print(f"   📊 50% Assistido: {youtube_50_percent:,}")
    print(f"   📊 75% Assistido: {youtube_75_percent:,}")
    print(f"   📊 100% Assistido: {youtube_100_percent:,} ✅ (NOVA COLUNA)")
    
    print(f"\n📺 Programática Video:")
    print(f"   💰 Total Investido: R$ {prog_total_spend:,.2f}")
    print(f"   👆 Total Cliques: {prog_total_clicks:,}")
    print(f"   👁️ Total Impressões: {prog_total_impressions:,}")
    print(f"   📊 25% Video Complete: {prog_25_percent:,}")
    print(f"   📊 50% Video Complete: {prog_50_percent:,}")
    print(f"   📊 75% Video Complete: {prog_75_percent:,}")
    print(f"   📊 100% Video Complete: {prog_100_percent:,}")
    
    print(f"\n📊 TOTAIS CONSOLIDADOS:")
    print(f"💰 Total Investido: R$ {total_spend:,.2f}")
    print(f"👆 Total Cliques: {total_clicks:,}")
    print(f"📊 Total Video Completion: {total_video_completion:,} (YouTube 100% + Programática 100%)")
    
    # Calcular percentuais de conclusão
    youtube_completion_percentage = (youtube_total_spend / 50000.00) * 100  # Orçamento contratado
    prog_completion_percentage = (prog_total_spend / 40000.00) * 100  # Orçamento contratado
    
    youtube_ctr = (youtube_total_clicks / youtube_100_percent * 100) if youtube_100_percent > 0 else 0
    prog_ctr = (prog_total_clicks / prog_total_impressions * 100) if prog_total_impressions > 0 else 0
    
    youtube_cpv = youtube_total_spend / youtube_100_percent if youtube_100_percent > 0 else 0
    prog_cpv = prog_total_spend / prog_total_impressions if prog_total_impressions > 0 else 0
    
    # Criar dados atualizados para o template
    updated_data = {
        # Quartis de vídeo (YouTube com coluna 100% real)
        "QUARTIL_25_VALUE": f"{youtube_25_percent:,}",
        "QUARTIL_25_PERCENTAGE": f"{(youtube_25_percent / youtube_100_percent * 100):.2f}%",
        "QUARTIL_50_VALUE": f"{youtube_50_percent:,}",
        "QUARTIL_50_PERCENTAGE": f"{(youtube_50_percent / youtube_100_percent * 100):.2f}%",
        "QUARTIL_75_VALUE": f"{youtube_75_percent:,}",
        "QUARTIL_75_PERCENTAGE": f"{(youtube_75_percent / youtube_100_percent * 100):.2f}%",
        "QUARTIL_100_VALUE": f"{youtube_100_percent:,}",
        "QUARTIL_100_PERCENTAGE": "100.00%",
        
        # Estratégias (dados atualizados)
        "YOUTUBE_BUDGET": f"R$ {youtube_total_spend:,.2f}",
        "YOUTUBE_VIDEO_COMPLETION": f"{youtube_100_percent:,}",  # Coluna 100% real
        "YOUTUBE_CLICKS": f"{youtube_total_clicks:,}",
        "YOUTUBE_CTR": f"{youtube_ctr:.2f}%",
        "YOUTUBE_CPV": f"R$ {youtube_cpv:.2f}",
        "YOUTUBE_COMPLETION": f"{youtube_completion_percentage:.1f}%",
        
        "PROG_BUDGET": f"R$ {prog_total_spend:,.2f}",
        "PROG_VIDEO_COMPLETION": f"{prog_100_percent:,}",  # Coluna 100% real
        "PROG_CLICKS": f"{prog_total_clicks:,}",
        "PROG_CTR": f"{prog_ctr:.2f}%",
        "PROG_CPV": f"R$ {prog_cpv:.2f}",
        "PROG_COMPLETION": f"{prog_completion_percentage:.1f}%",
        
        "TOTAL_BUDGET": f"R$ {total_spend:,.2f}",
        "TOTAL_VIDEO_COMPLETION": f"{total_video_completion:,}",  # Soma correta
        "TOTAL_CLICKS": f"{total_clicks:,}",
        "TOTAL_CTR": f"{(total_clicks / total_impressions * 100):.2f}%",
        "TOTAL_CPV": f"R$ {total_spend / total_impressions:.2f}",
        "TOTAL_COMPLETION": f"{((youtube_completion_percentage + prog_completion_percentage) / 2):.1f}%"
    }
    
    # Salvar dados atualizados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_updated_youtube_100_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS ATUALIZADOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS ATUALIZAÇÕES:")
    print(f"✅ YouTube 100% Complete: {youtube_100_percent:,} (coluna real)")
    print(f"✅ Programática 100% Complete: {prog_100_percent:,} (coluna real)")
    print(f"✅ Total Video Completion: {total_video_completion:,} (soma correta)")
    print(f"✅ Quartis: Baseados na coluna 100% real do YouTube")
    
    return filename

if __name__ == "__main__":
    update_with_youtube_100_percent()


