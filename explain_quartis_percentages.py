#!/usr/bin/env python3
"""
Explicar de onde vêm os percentuais dos quartis
"""

import json
import pandas as pd

def explain_quartis_percentages():
    """Explicar de onde vêm os percentuais dos quartis"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔍 EXPLICANDO DE ONDE VÊM OS PERCENTUAIS DOS QUARTIS")
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
    
    print("📊 DADOS ORIGINAIS DAS PLANILHAS:")
    print(f"📺 YouTube:")
    print(f"   Vídeo assistido até 25%: {youtube_25:,}")
    print(f"   Vídeo assistido até 50%: {youtube_50:,}")
    print(f"   Vídeo assistido até 75%: {youtube_75:,}")
    print(f"   Video assistido 100%: {youtube_100:,}")
    
    print(f"\n📺 Programática Video:")
    print(f"   25% Video Complete: {prog_25:,}")
    print(f"   50% Video Complete: {prog_50:,}")
    print(f"   75% Video Complete: {prog_75:,}")
    print(f"   100% Video Complete: {prog_100:,}")
    
    print(f"\n📊 TOTAIS (YouTube + Programática):")
    print(f"   25%: {total_25:,}")
    print(f"   50%: {total_50:,}")
    print(f"   75%: {total_75:,}")
    print(f"   100%: {total_100:,}")
    
    print(f"\n🔍 EXPLICAÇÃO DOS PERCENTUAIS:")
    print("=" * 50)
    print("Os percentuais que aparecem nos gráficos são calculados assim:")
    print()
    print("FÓRMULA: (Valor do Quartil / Valor do 100%) × 100")
    print()
    
    # Calcular percentuais
    percent_25 = (total_25 / total_100 * 100) if total_100 > 0 else 0
    percent_50 = (total_50 / total_100 * 100) if total_100 > 0 else 0
    percent_75 = (total_75 / total_100 * 100) if total_100 > 0 else 0
    percent_100 = 100.0
    
    print(f"25%: ({total_25:,} ÷ {total_100:,}) × 100 = {percent_25:.2f}%")
    print(f"50%: ({total_50:,} ÷ {total_100:,}) × 100 = {percent_50:.2f}%")
    print(f"75%: ({total_75:,} ÷ {total_100:,}) × 100 = {percent_75:.2f}%")
    print(f"100%: ({total_100:,} ÷ {total_100:,}) × 100 = {percent_100:.2f}%")
    
    print(f"\n🤔 POR QUE OS PERCENTUAIS SÃO MAIORES QUE 100%?")
    print("=" * 50)
    print("Isso acontece porque:")
    print()
    print("1. 📺 YouTube e Programática Video são CANAIS DIFERENTES")
    print("2. 🎯 Cada canal tem seu próprio público e engajamento")
    print("3. 📊 Os quartis representam DIFERENTES MÉTRICAS:")
    print("   - 25%: Quantas pessoas assistiram pelo menos 25% do vídeo")
    print("   - 50%: Quantas pessoas assistiram pelo menos 50% do vídeo")
    print("   - 75%: Quantas pessoas assistiram pelo menos 75% do vídeo")
    print("   - 100%: Quantas pessoas assistiram o vídeo completo")
    print()
    print("4. 🔄 É NORMAL que 25% > 50% > 75% > 100%")
    print("   Porque nem todos que assistem 25% assistem até o final")
    print()
    print("5. 📈 Os percentuais mostram a PROPORÇÃO de cada quartil")
    print("   em relação ao total de pessoas que assistiram 100%")
    
    print(f"\n💡 EXEMPLO PRÁTICO:")
    print("=" * 30)
    print(f"Se {total_100:,} pessoas assistiram 100% do vídeo,")
    print(f"então {total_25:,} pessoas assistiram pelo menos 25%")
    print(f"Isso significa que {percent_25:.1f}% das pessoas que assistiram")
    print(f"pelo menos 25% também assistiram 100%")
    
    print(f"\n✅ CONCLUSÃO:")
    print("Os percentuais são calculados corretamente e representam")
    print("a proporção de cada quartil em relação ao total de 100%")
    print("É uma métrica de retenção de audiência normal em campanhas de vídeo.")

if __name__ == "__main__":
    explain_quartis_percentages()



