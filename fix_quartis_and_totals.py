#!/usr/bin/env python3
"""
Corrigir quartis e totais para incluir YouTube + Programática
"""

import json
import pandas as pd
from datetime import datetime

def fix_quartis_and_totals():
    """Corrigir quartis e totais para incluir YouTube + Programática"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔧 CORRIGINDO QUARTIS E TOTAIS (YouTube + Programática)")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas do YouTube
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
    
    # Converter colunas numéricas da Programática
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    prog_df['100%  Video Complete'] = prog_df['100%  Video Complete'].astype(int)
    
    prog_25 = int(prog_df['25% Video Complete'].sum())
    prog_50 = int(prog_df['50% Video Complete'].sum())
    prog_75 = int(prog_df['75% Video Complete'].sum())
    prog_100 = int(prog_df['100%  Video Complete'].sum())
    
    # Calcular totais (YouTube + Programática)
    total_25 = youtube_25 + prog_25
    total_50 = youtube_50 + prog_50
    total_75 = youtube_75 + prog_75
    total_100 = youtube_100 + prog_100
    
    print(f"📊 DADOS INDIVIDUAIS:")
    print(f"📺 YouTube:")
    print(f"   25%: {youtube_25:,}")
    print(f"   50%: {youtube_50:,}")
    print(f"   75%: {youtube_75:,}")
    print(f"   100%: {youtube_100:,}")
    
    print(f"\n📺 Programática:")
    print(f"   25%: {prog_25:,}")
    print(f"   50%: {prog_50:,}")
    print(f"   75%: {prog_75:,}")
    print(f"   100%: {prog_100:,}")
    
    print(f"\n📊 TOTAIS (YouTube + Programática):")
    print(f"   25%: {total_25:,}")
    print(f"   50%: {total_50:,}")
    print(f"   75%: {total_75:,}")
    print(f"   100%: {total_100:,}")
    
    # Calcular percentuais baseados no total 100%
    total_25_percent = (total_25 / total_100 * 100) if total_100 > 0 else 0
    total_50_percent = (total_50 / total_100 * 100) if total_100 > 0 else 0
    total_75_percent = (total_75 / total_100 * 100) if total_100 > 0 else 0
    total_100_percent = 100.0
    
    print(f"\n📊 PERCENTUAIS (baseados no total 100%):")
    print(f"   25%: {total_25_percent:.2f}%")
    print(f"   50%: {total_50_percent:.2f}%")
    print(f"   75%: {total_75_percent:.2f}%")
    print(f"   100%: {total_100_percent:.2f}%")
    
    # Criar dados corrigidos
    corrected_data = {
        # Quartis corrigidos (YouTube + Programática)
        "QUARTIL_25_VALUE": f"{total_25:,}",
        "QUARTIL_25_PERCENTAGE": f"{total_25_percent:.2f}%",
        "QUARTIL_50_VALUE": f"{total_50:,}",
        "QUARTIL_50_PERCENTAGE": f"{total_50_percent:.2f}%",
        "QUARTIL_75_VALUE": f"{total_75:,}",
        "QUARTIL_75_PERCENTAGE": f"{total_75_percent:.2f}%",
        "QUARTIL_100_VALUE": f"{total_100:,}",
        "QUARTIL_100_PERCENTAGE": f"{total_100_percent:.2f}%",
        
        # Estratégias (dados individuais)
        "YOUTUBE_BUDGET": "R$ 24,601.20",
        "YOUTUBE_VIDEO_COMPLETION": f"{youtube_100:,}",
        "YOUTUBE_CLICKS": "596",
        "YOUTUBE_CTR": "0.19%",
        "YOUTUBE_CPV": "R$ 0.08",
        "YOUTUBE_COMPLETION": "49.2%",
        
        "PROG_BUDGET": "R$ 20,079.92",
        "PROG_VIDEO_COMPLETION": f"{prog_100:,}",
        "PROG_CLICKS": "374",
        "PROG_CTR": "0.35%",
        "PROG_CPV": "R$ 0.19",
        "PROG_COMPLETION": "50.2%",
        
        # Totais corrigidos
        "TOTAL_BUDGET": "R$ 44,681.12",
        "TOTAL_VIDEO_COMPLETION": f"{total_100:,}",
        "TOTAL_CLICKS": "970",
        "TOTAL_CTR": "0.23%",
        "TOTAL_CPV": "R$ 0.11",
        "TOTAL_COMPLETION": "49.7%"
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_corrected_totals_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS CORRIGIDOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ Quartis: Agora mostram YouTube + Programática")
    print(f"✅ 25% Total: {total_25:,} ({total_25_percent:.2f}%)")
    print(f"✅ 50% Total: {total_50:,} ({total_50_percent:.2f}%)")
    print(f"✅ 75% Total: {total_75:,} ({total_75_percent:.2f}%)")
    print(f"✅ 100% Total: {total_100:,} (100.00%)")
    
    return filename

if __name__ == "__main__":
    fix_quartis_and_totals()

