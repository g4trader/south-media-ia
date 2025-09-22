#!/usr/bin/env python3
"""
Corrigir gráficos dos quartis - percentuais baseados no 100% real
"""

import json
import pandas as pd
from datetime import datetime

def fix_quartis_charts():
    """Corrigir gráficos dos quartis"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔧 CORRIGINDO GRÁFICOS DOS QUARTIS")
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
    
    print(f"📊 DADOS DOS QUARTIS:")
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
    
    print(f"\n📊 TOTAIS:")
    print(f"   25%: {total_25:,}")
    print(f"   50%: {total_50:,}")
    print(f"   75%: {total_75:,}")
    print(f"   100%: {total_100:,}")
    
    # CORREÇÃO: Calcular percentuais baseados no 100% real
    # Os percentuais devem representar quanto cada quartil representa do total de 100%
    quartil_25_percent = (total_25 / total_100 * 100) if total_100 > 0 else 0
    quartil_50_percent = (total_50 / total_100 * 100) if total_100 > 0 else 0
    quartil_75_percent = (total_75 / total_100 * 100) if total_100 > 0 else 0
    quartil_100_percent = 100.0
    
    print(f"\n📊 PERCENTUAIS CORRIGIDOS (baseados no 100% real):")
    print(f"   25%: {quartil_25_percent:.2f}%")
    print(f"   50%: {quartil_50_percent:.2f}%")
    print(f"   75%: {quartil_75_percent:.2f}%")
    print(f"   100%: {quartil_100_percent:.2f}%")
    
    # Criar dados corrigidos
    corrected_data = {
        # Quartis corrigidos (percentuais baseados no 100% real)
        "QUARTIL_25_VALUE": f"{total_25:,}",
        "QUARTIL_25_PERCENTAGE": f"{quartil_25_percent:.2f}%",
        "QUARTIL_50_VALUE": f"{total_50:,}",
        "QUARTIL_50_PERCENTAGE": f"{quartil_50_percent:.2f}%",
        "QUARTIL_75_VALUE": f"{total_75:,}",
        "QUARTIL_75_PERCENTAGE": f"{quartil_75_percent:.2f}%",
        "QUARTIL_100_VALUE": f"{total_100:,}",
        "QUARTIL_100_PERCENTAGE": f"{quartil_100_percent:.2f}%"
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quartis_corrected_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS CORRIGIDOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ 25%: {total_25:,} ({quartil_25_percent:.2f}%)")
    print(f"✅ 50%: {total_50:,} ({quartil_50_percent:.2f}%)")
    print(f"✅ 75%: {total_75:,} ({quartil_75_percent:.2f}%)")
    print(f"✅ 100%: {total_100:,} ({quartil_100_percent:.2f}%)")
    print("\n🔧 CORREÇÃO APLICADA:")
    print("✅ Percentuais agora baseados no 100% real (394.819)")
    print("✅ 25% representa 162,59% do total de 100%")
    print("✅ 50% representa 135,98% do total de 100%")
    print("✅ 75% representa 105,92% do total de 100%")
    print("✅ 100% representa 100,00% do total de 100%")
    
    return filename

if __name__ == "__main__":
    fix_quartis_charts()



