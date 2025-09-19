#!/usr/bin/env python3
"""
Coletar Video Starts das planilhas para calcular percentuais corretos
"""

import json
import pandas as pd
from datetime import datetime

def collect_video_starts():
    """Coletar Video Starts das planilhas"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔍 COLETANDO VIDEO STARTS DAS PLANILHAS")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    print("📺 YOUTUBE - Colunas disponíveis:")
    for i, col in enumerate(youtube_df.columns):
        print(f"   {i+1}. {col}")
    
    # Verificar se existe coluna Video Starts no YouTube
    youtube_video_starts = None
    if 'Video Starts' in youtube_df.columns:
        youtube_df['Video Starts'] = youtube_df['Video Starts'].astype(int)
        youtube_video_starts = int(youtube_df['Video Starts'].sum())
        print(f"\n✅ YouTube Video Starts encontrado: {youtube_video_starts:,}")
    else:
        print(f"\n❌ YouTube não tem coluna 'Video Starts'")
        print("   Colunas disponíveis:", list(youtube_df.columns))
    
    # Converter outras colunas numéricas do YouTube
    youtube_df['Vídeo assistido até 25%'] = youtube_df['Vídeo assistido até 25%'].astype(int)
    youtube_df['Vídeo assistido até 50%'] = youtube_df['Vídeo assistido até 50%'].astype(int)
    youtube_df['Vídeo assistido até 75%'] = youtube_df['Vídeo assistido até 75%'].astype(int)
    youtube_df['Video assistido 100%'] = youtube_df['Video assistido 100%'].astype(int)
    
    youtube_25 = int(youtube_df['Vídeo assistido até 25%'].sum())
    youtube_50 = int(youtube_df['Vídeo assistido até 50%'].sum())
    youtube_75 = int(youtube_df['Vídeo assistido até 75%'].sum())
    youtube_100 = int(youtube_df['Video assistido 100%'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    print(f"\n📺 PROGRAMÁTICA - Colunas disponíveis:")
    for i, col in enumerate(prog_df.columns):
        print(f"   {i+1}. {col}")
    
    # Verificar se existe coluna Video Starts na Programática
    prog_video_starts = None
    if 'Video Starts' in prog_df.columns:
        prog_df['Video Starts'] = prog_df['Video Starts'].astype(int)
        prog_video_starts = int(prog_df['Video Starts'].sum())
        print(f"\n✅ Programática Video Starts encontrado: {prog_video_starts:,}")
    else:
        print(f"\n❌ Programática não tem coluna 'Video Starts'")
        print("   Colunas disponíveis:", list(prog_df.columns))
    
    # Converter outras colunas numéricas da Programática
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    prog_df['100%  Video Complete'] = prog_df['100%  Video Complete'].astype(int)
    
    prog_25 = int(prog_df['25% Video Complete'].sum())
    prog_50 = int(prog_df['50% Video Complete'].sum())
    prog_75 = int(prog_df['75% Video Complete'].sum())
    prog_100 = int(prog_df['100%  Video Complete'].sum())
    
    # Calcular totais
    total_25 = youtube_25 + prog_25
    total_50 = youtube_50 + prog_50
    total_75 = youtube_75 + prog_75
    total_100 = youtube_100 + prog_100
    
    # Calcular Video Starts total
    total_video_starts = 0
    if youtube_video_starts is not None:
        total_video_starts += youtube_video_starts
    if prog_video_starts is not None:
        total_video_starts += prog_video_starts
    
    print(f"\n📊 RESUMO DOS DADOS:")
    print(f"📺 YouTube:")
    print(f"   Video Starts: {youtube_video_starts:,}" if youtube_video_starts else "   Video Starts: NÃO ENCONTRADO")
    print(f"   25%: {youtube_25:,}")
    print(f"   50%: {youtube_50:,}")
    print(f"   75%: {youtube_75:,}")
    print(f"   100%: {youtube_100:,}")
    
    print(f"\n📺 Programática:")
    print(f"   Video Starts: {prog_video_starts:,}" if prog_video_starts else "   Video Starts: NÃO ENCONTRADO")
    print(f"   25%: {prog_25:,}")
    print(f"   50%: {prog_50:,}")
    print(f"   75%: {prog_75:,}")
    print(f"   100%: {prog_100:,}")
    
    print(f"\n📊 TOTAIS:")
    print(f"   Video Starts: {total_video_starts:,}" if total_video_starts > 0 else "   Video Starts: NÃO DISPONÍVEL")
    print(f"   25%: {total_25:,}")
    print(f"   50%: {total_50:,}")
    print(f"   75%: {total_75:,}")
    print(f"   100%: {total_100:,}")
    
    if total_video_starts > 0:
        print(f"\n🔍 PERCENTUAIS CORRETOS (baseados em Video Starts):")
        print("=" * 50)
        print("FÓRMULA: (Valor do Quartil / Video Starts) × 100")
        print()
        
        percent_25 = (total_25 / total_video_starts * 100)
        percent_50 = (total_50 / total_video_starts * 100)
        percent_75 = (total_75 / total_video_starts * 100)
        percent_100 = (total_100 / total_video_starts * 100)
        
        print(f"25%: ({total_25:,} ÷ {total_video_starts:,}) × 100 = {percent_25:.2f}%")
        print(f"50%: ({total_50:,} ÷ {total_video_starts:,}) × 100 = {percent_50:.2f}%")
        print(f"75%: ({total_75:,} ÷ {total_video_starts:,}) × 100 = {percent_75:.2f}%")
        print(f"100%: ({total_100:,} ÷ {total_video_starts:,}) × 100 = {percent_100:.2f}%")
        
        # Salvar dados com Video Starts
        video_starts_data = {
            "YOUTUBE_VIDEO_STARTS": youtube_video_starts,
            "PROG_VIDEO_STARTS": prog_video_starts,
            "TOTAL_VIDEO_STARTS": total_video_starts,
            "TOTAL_25": total_25,
            "TOTAL_50": total_50,
            "TOTAL_75": total_75,
            "TOTAL_100": total_100,
            "PERCENT_25": percent_25,
            "PERCENT_50": percent_50,
            "PERCENT_75": percent_75,
            "PERCENT_100": percent_100
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_starts_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(video_starts_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ DADOS COM VIDEO STARTS SALVOS: {filename}")
        
    else:
        print(f"\n❌ ERRO: Video Starts não encontrado nas planilhas!")
        print("   Verifique se as planilhas têm a coluna 'Video Starts'")
    
    return total_video_starts > 0

if __name__ == "__main__":
    collect_video_starts()


