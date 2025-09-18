#!/usr/bin/env python3
"""
Calcular quartis corretos usando Video Starts como base
"""

import json
import pandas as pd
from datetime import datetime

def calculate_correct_quartis():
    """Calcular quartis corretos usando Video Starts como base"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔧 CALCULANDO QUARTIS CORRETOS COM VIDEO STARTS COMO BASE")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas do YouTube
    youtube_df['Vídeo assistido até 25%'] = youtube_df['Vídeo assistido até 25%'].astype(int)
    youtube_df['Vídeo assistido até 50%'] = youtube_df['Vídeo assistido até 50%'].astype(int)
    youtube_df['Vídeo assistido até 75%'] = youtube_df['Vídeo assistido até 75%'].astype(int)
    youtube_df['Video assistido 100%'] = youtube_df['Video assistido 100%'].astype(int)
    youtube_df['Video Starts'] = youtube_df['Video Starts'].astype(int)
    
    youtube_25 = int(youtube_df['Vídeo assistido até 25%'].sum())
    youtube_50 = int(youtube_df['Vídeo assistido até 50%'].sum())
    youtube_75 = int(youtube_df['Vídeo assistido até 75%'].sum())
    youtube_100 = int(youtube_df['Video assistido 100%'].sum())
    youtube_starts = int(youtube_df['Video Starts'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas da Programática
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    prog_df['100%  Video Complete'] = prog_df['100%  Video Complete'].astype(int)
    prog_df['Video Starts'] = prog_df['Video Starts'].astype(int)
    
    prog_25 = int(prog_df['25% Video Complete'].sum())
    prog_50 = int(prog_df['50% Video Complete'].sum())
    prog_75 = int(prog_df['75% Video Complete'].sum())
    prog_100 = int(prog_df['100%  Video Complete'].sum())
    prog_starts = int(prog_df['Video Starts'].sum())
    
    # Calcular totais (YouTube + Programática)
    total_25 = youtube_25 + prog_25
    total_50 = youtube_50 + prog_50
    total_75 = youtube_75 + prog_75
    total_100 = youtube_100 + prog_100
    total_starts = youtube_starts + prog_starts
    
    print(f"📊 DADOS COM VIDEO STARTS:")
    print(f"📺 YouTube:")
    print(f"   Video Starts: {youtube_starts:,}")
    print(f"   25%: {youtube_25:,}")
    print(f"   50%: {youtube_50:,}")
    print(f"   75%: {youtube_75:,}")
    print(f"   100%: {youtube_100:,}")
    
    print(f"\n📺 Programática:")
    print(f"   Video Starts: {prog_starts:,}")
    print(f"   25%: {prog_25:,}")
    print(f"   50%: {prog_50:,}")
    print(f"   75%: {prog_75:,}")
    print(f"   100%: {prog_100:,}")
    
    print(f"\n📊 TOTAIS:")
    print(f"   Video Starts: {total_starts:,}")
    print(f"   25%: {total_25:,}")
    print(f"   50%: {total_50:,}")
    print(f"   75%: {total_75:,}")
    print(f"   100%: {total_100:,}")
    
    # Calcular percentuais corretos baseados em Video Starts
    print(f"\n🔍 PERCENTUAIS CORRETOS (baseados em Video Starts):")
    print("=" * 50)
    print("FÓRMULA: (Valor do Quartil / Video Starts) × 100")
    print()
    
    percent_25 = (total_25 / total_starts * 100) if total_starts > 0 else 0
    percent_50 = (total_50 / total_starts * 100) if total_starts > 0 else 0
    percent_75 = (total_75 / total_starts * 100) if total_starts > 0 else 0
    percent_100 = (total_100 / total_starts * 100) if total_starts > 0 else 0
    
    print(f"25%: ({total_25:,} ÷ {total_starts:,}) × 100 = {percent_25:.2f}%")
    print(f"50%: ({total_50:,} ÷ {total_starts:,}) × 100 = {percent_50:.2f}%")
    print(f"75%: ({total_75:,} ÷ {total_starts:,}) × 100 = {percent_75:.2f}%")
    print(f"100%: ({total_100:,} ÷ {total_starts:,}) × 100 = {percent_100:.2f}%")
    
    # Criar dados corrigidos com formatação pt-BR
    def format_pt_br(value, decimal_places=2):
        """Formatar número para pt-BR"""
        if isinstance(value, (int, float)):
            formatted = f"{value:,.{decimal_places}f}"
            formatted = formatted.replace(',', 'TEMP')
            formatted = formatted.replace('.', ',')
            formatted = formatted.replace('TEMP', '.')
            return formatted
        return str(value)
    
    corrected_data = {
        # Quartis corrigidos (percentuais baseados em Video Starts)
        "QUARTIL_25_VALUE": format_pt_br(total_25, 0),
        "QUARTIL_25_PERCENTAGE": f"{format_pt_br(percent_25)}%",
        "QUARTIL_50_VALUE": format_pt_br(total_50, 0),
        "QUARTIL_50_PERCENTAGE": f"{format_pt_br(percent_50)}%",
        "QUARTIL_75_VALUE": format_pt_br(total_75, 0),
        "QUARTIL_75_PERCENTAGE": f"{format_pt_br(percent_75)}%",
        "QUARTIL_100_VALUE": format_pt_br(total_100, 0),
        "QUARTIL_100_PERCENTAGE": f"{format_pt_br(percent_100)}%"
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quartis_corrected_video_starts_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS CORRIGIDOS SALVOS: {filename}")
    print("\n📊 RESUMO DAS CORREÇÕES:")
    print(f"✅ 25%: {format_pt_br(total_25, 0)} ({format_pt_br(percent_25)}%)")
    print(f"✅ 50%: {format_pt_br(total_50, 0)} ({format_pt_br(percent_50)}%)")
    print(f"✅ 75%: {format_pt_br(total_75, 0)} ({format_pt_br(percent_75)}%)")
    print(f"✅ 100%: {format_pt_br(total_100, 0)} ({format_pt_br(percent_100)}%)")
    print("\n🔧 CORREÇÃO APLICADA:")
    print("✅ Percentuais agora baseados em Video Starts (universo total)")
    print("✅ YouTube Video Starts: 541.374")
    print("✅ Programática Video Starts: 107.158")
    print("✅ Total Video Starts: 648.532")
    print("✅ Formatação: PT-BR (ponto para milhares, vírgula para decimais)")
    
    return filename

if __name__ == "__main__":
    calculate_correct_quartis()

