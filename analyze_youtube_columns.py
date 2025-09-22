#!/usr/bin/env python3
"""
Analisar colunas do YouTube para encontrar equivalente ao Video Starts
"""

import json
import pandas as pd

def analyze_youtube_columns():
    """Analisar colunas do YouTube"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔍 ANALISANDO COLUNAS DO YOUTUBE")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    print("📺 YOUTUBE - Análise das colunas:")
    print()
    
    # Mostrar algumas linhas de exemplo
    print("📊 PRIMEIRAS 3 LINHAS DE DADOS:")
    for i in range(min(3, len(youtube_df))):
        print(f"   Linha {i+1}:")
        for col in youtube_df.columns:
            print(f"     {col}: {youtube_df.iloc[i][col]}")
        print()
    
    # Analisar se existe uma coluna que pode ser equivalente ao Video Starts
    print("🔍 ANÁLISE PARA ENCONTRAR EQUIVALENTE AO VIDEO STARTS:")
    print()
    
    # Verificar se existe alguma coluna que pode representar o início do vídeo
    possible_starts_columns = []
    for col in youtube_df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['start', 'início', 'begin', 'view', 'visualização', 'impressão']):
            possible_starts_columns.append(col)
    
    if possible_starts_columns:
        print("✅ Possíveis colunas equivalentes ao Video Starts:")
        for col in possible_starts_columns:
            print(f"   - {col}")
    else:
        print("❌ Nenhuma coluna equivalente ao Video Starts encontrada")
    
    # Verificar se a coluna "Vídeo assistido até 25%" pode ser usada como base
    print(f"\n💡 SUGESTÃO:")
    print("Como o YouTube não tem 'Video Starts', podemos usar:")
    print("1. 'Vídeo assistido até 25%' como base (maior número)")
    print("2. Ou somar YouTube + Programática Video Starts")
    print("3. Ou usar apenas os dados da Programática")
    
    # Calcular usando "Vídeo assistido até 25%" como base
    youtube_25 = youtube_df['Vídeo assistido até 25%'].astype(int).sum()
    youtube_50 = youtube_df['Vídeo assistido até 50%'].astype(int).sum()
    youtube_75 = youtube_df['Vídeo assistido até 75%'].astype(int).sum()
    youtube_100 = youtube_df['Video assistido 100%'].astype(int).sum()
    
    print(f"\n📊 CÁLCULO USANDO 'Vídeo assistido até 25%' COMO BASE:")
    print(f"   Base (25%): {youtube_25:,}")
    print(f"   50%: {youtube_50:,} ({youtube_50/youtube_25*100:.2f}%)")
    print(f"   75%: {youtube_75:,} ({youtube_75/youtube_25*100:.2f}%)")
    print(f"   100%: {youtube_100:,} ({youtube_100/youtube_25*100:.2f}%)")
    
    return youtube_df.columns.tolist()

if __name__ == "__main__":
    analyze_youtube_columns()



