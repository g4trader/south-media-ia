#!/usr/bin/env python3
"""
Corrigir formatações numéricas para pt-BR
"""

import json
import pandas as pd
from datetime import datetime

def format_pt_br(value, decimal_places=2):
    """Formatar número para pt-BR"""
    if isinstance(value, str):
        # Se já é string, tentar converter
        try:
            value = float(value.replace('.', '').replace(',', '.'))
        except:
            return value
    
    if isinstance(value, (int, float)):
        # Formatar com ponto para milhares e vírgula para decimais
        formatted = f"{value:,.{decimal_places}f}"
        # Trocar vírgula por ponto temporariamente
        formatted = formatted.replace(',', 'TEMP')
        # Trocar ponto por vírgula
        formatted = formatted.replace('.', ',')
        # Trocar TEMP por ponto
        formatted = formatted.replace('TEMP', '.')
        return formatted
    
    return str(value)

def fix_pt_br_formatting():
    """Corrigir formatações numéricas para pt-BR"""
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    print("🔧 CORRIGINDO FORMATAÇÕES NUMÉRICAS PARA PT-BR")
    print("=" * 70)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
    
    # Converter colunas numéricas do YouTube
    youtube_df['Valor investido'] = youtube_df['Valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    youtube_df['Cliques'] = youtube_df['Cliques'].astype(int)
    youtube_df['Video assistido 100%'] = youtube_df['Video assistido 100%'].astype(int)
    youtube_df['Vídeo assistido até 25%'] = youtube_df['Vídeo assistido até 25%'].astype(int)
    youtube_df['Vídeo assistido até 50%'] = youtube_df['Vídeo assistido até 50%'].astype(int)
    youtube_df['Vídeo assistido até 75%'] = youtube_df['Vídeo assistido até 75%'].astype(int)
    
    youtube_total_spend = float(youtube_df['Valor investido'].sum())
    youtube_total_clicks = int(youtube_df['Cliques'].sum())
    youtube_video_completion = int(youtube_df['Video assistido 100%'].sum())
    youtube_25 = int(youtube_df['Vídeo assistido até 25%'].sum())
    youtube_50 = int(youtube_df['Vídeo assistido até 50%'].sum())
    youtube_75 = int(youtube_df['Vídeo assistido até 75%'].sum())
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    
    # Converter colunas numéricas da Programática
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    prog_df['100%  Video Complete'] = prog_df['100%  Video Complete'].astype(int)
    prog_df['25% Video Complete'] = prog_df['25% Video Complete'].astype(int)
    prog_df['50% Video Complete'] = prog_df['50% Video Complete'].astype(int)
    prog_df['75% Video Complete'] = prog_df['75% Video Complete'].astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_video_completion = int(prog_df['100%  Video Complete'].sum())
    prog_25 = int(prog_df['25% Video Complete'].sum())
    prog_50 = int(prog_df['50% Video Complete'].sum())
    prog_75 = int(prog_df['75% Video Complete'].sum())
    
    # Calcular totais
    total_spend_used = youtube_total_spend + prog_total_spend
    total_clicks_used = youtube_total_clicks + prog_total_clicks
    total_video_completion = youtube_video_completion + prog_video_completion
    total_25 = youtube_25 + prog_25
    total_50 = youtube_50 + prog_50
    total_75 = youtube_75 + prog_75
    
    # Calcular métricas
    total_cpv_used = total_spend_used / total_video_completion if total_video_completion > 0 else 0
    total_ctr_used = (total_clicks_used / total_video_completion * 100) if total_video_completion > 0 else 0
    
    # Dados contratados
    total_budget_contracted = 90000.00
    total_video_completion_contracted = 798914
    
    # Calcular percentuais
    budget_utilization = (total_spend_used / total_budget_contracted * 100) if total_budget_contracted > 0 else 0
    video_completion_utilization = (total_video_completion / total_video_completion_contracted * 100) if total_video_completion_contracted > 0 else 0
    
    # Calcular percentuais dos quartis
    total_25_percent = (total_25 / total_video_completion * 100) if total_video_completion > 0 else 0
    total_50_percent = (total_50 / total_video_completion * 100) if total_video_completion > 0 else 0
    total_75_percent = (total_75 / total_video_completion * 100) if total_video_completion > 0 else 0
    total_100_percent = 100.0
    
    # Calcular métricas individuais
    youtube_ctr = (youtube_total_clicks / youtube_video_completion * 100) if youtube_video_completion > 0 else 0
    prog_ctr = (prog_total_clicks / prog_video_completion * 100) if prog_video_completion > 0 else 0
    youtube_cpv = youtube_total_spend / youtube_video_completion if youtube_video_completion > 0 else 0
    prog_cpv = prog_total_spend / prog_video_completion if prog_video_completion > 0 else 0
    youtube_completion_percentage = (youtube_total_spend / 50000.00) * 100
    prog_completion_percentage = (prog_total_spend / 40000.00) * 100
    
    print(f"📊 FORMATAÇÕES PT-BR APLICADAS:")
    print(f"💰 Orçamento: R$ {format_pt_br(total_spend_used)}")
    print(f"🎬 Video Completion: {format_pt_br(total_video_completion, 0)}")
    print(f"💵 CPV: R$ {format_pt_br(total_cpv_used)}")
    print(f"📊 CTR: {format_pt_br(total_ctr_used)}%")
    
    # Criar dados com formatação pt-BR
    formatted_data = {
        # Dados contratados (imutáveis)
        "TOTAL_BUDGET_CONTRACTED": "R$ 90.000,00",
        "TOTAL_IMPRESSIONS_CONTRACTED": format_pt_br(total_video_completion_contracted, 0),
        
        # Dados utilizados (formatação pt-BR)
        "TOTAL_SPEND_USED": f"R$ {format_pt_br(total_spend_used)}",
        "TOTAL_CLICKS_USED": format_pt_br(total_clicks_used, 0),
        "TOTAL_IMPRESSIONS_USED": format_pt_br(total_video_completion, 0),
        "TOTAL_CPV_USED": f"R$ {format_pt_br(total_cpv_used)}",
        "TOTAL_CTR_USED": f"{format_pt_br(total_ctr_used)}%",
        
        # Percentuais de utilização
        "BUDGET_UTILIZATION_PERCENTAGE": f"{format_pt_br(budget_utilization)}%",
        "IMPRESSIONS_UTILIZATION_PERCENTAGE": f"{format_pt_br(video_completion_utilization)}%",
        
        # Dados individuais por canal
        "YOUTUBE_TOTAL_SPEND": f"R$ {format_pt_br(youtube_total_spend)}",
        "YOUTUBE_TOTAL_CLICKS": format_pt_br(youtube_total_clicks, 0),
        "YOUTUBE_TOTAL_VIEWS": format_pt_br(youtube_video_completion, 0),
        "PROG_TOTAL_SPEND": f"R$ {format_pt_br(prog_total_spend)}",
        "PROG_TOTAL_CLICKS": format_pt_br(prog_total_clicks, 0),
        "PROG_TOTAL_IMPRESSIONS": format_pt_br(prog_video_completion, 0),
        
        # Quartis (formatação pt-BR)
        "QUARTIL_25_VALUE": format_pt_br(total_25, 0),
        "QUARTIL_25_PERCENTAGE": f"{format_pt_br(total_25_percent)}%",
        "QUARTIL_50_VALUE": format_pt_br(total_50, 0),
        "QUARTIL_50_PERCENTAGE": f"{format_pt_br(total_50_percent)}%",
        "QUARTIL_75_VALUE": format_pt_br(total_75, 0),
        "QUARTIL_75_PERCENTAGE": f"{format_pt_br(total_75_percent)}%",
        "QUARTIL_100_VALUE": format_pt_br(total_video_completion, 0),
        "QUARTIL_100_PERCENTAGE": f"{format_pt_br(total_100_percent)}%",
        
        # Estratégias (formatação pt-BR)
        "YOUTUBE_BUDGET": f"R$ {format_pt_br(youtube_total_spend)}",
        "YOUTUBE_VIDEO_COMPLETION": format_pt_br(youtube_video_completion, 0),
        "YOUTUBE_CLICKS": format_pt_br(youtube_total_clicks, 0),
        "YOUTUBE_CTR": f"{format_pt_br(youtube_ctr)}%",
        "YOUTUBE_CPV": f"R$ {format_pt_br(youtube_cpv)}",
        "YOUTUBE_COMPLETION": f"{format_pt_br(youtube_completion_percentage)}%",
        
        "PROG_BUDGET": f"R$ {format_pt_br(prog_total_spend)}",
        "PROG_VIDEO_COMPLETION": format_pt_br(prog_video_completion, 0),
        "PROG_CLICKS": format_pt_br(prog_total_clicks, 0),
        "PROG_CTR": f"{format_pt_br(prog_ctr)}%",
        "PROG_CPV": f"R$ {format_pt_br(prog_cpv)}",
        "PROG_COMPLETION": f"{format_pt_br(prog_completion_percentage)}%",
        
        "TOTAL_BUDGET": f"R$ {format_pt_br(total_spend_used)}",
        "TOTAL_VIDEO_COMPLETION": format_pt_br(total_video_completion, 0),
        "TOTAL_CLICKS": format_pt_br(total_clicks_used, 0),
        "TOTAL_CTR": f"{format_pt_br(total_ctr_used)}%",
        "TOTAL_CPV": f"R$ {format_pt_br(total_cpv_used)}",
        "TOTAL_COMPLETION": f"{format_pt_br((youtube_completion_percentage + prog_completion_percentage) / 2)}%"
    }
    
    # Salvar dados com formatação pt-BR
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_pt_br_formatted_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DADOS COM FORMATAÇÃO PT-BR SALVOS: {filename}")
    print("\n📊 EXEMPLOS DE FORMATAÇÃO PT-BR:")
    print(f"💰 Orçamento: R$ {format_pt_br(total_spend_used)}")
    print(f"🎬 Video Completion: {format_pt_br(total_video_completion, 0)}")
    print(f"💵 CPV: R$ {format_pt_br(total_cpv_used)}")
    print(f"📊 CTR: {format_pt_br(total_ctr_used)}%")
    print(f"📊 Quartis: {format_pt_br(total_25, 0)}, {format_pt_br(total_50, 0)}, {format_pt_br(total_75, 0)}, {format_pt_br(total_video_completion, 0)}")
    
    return filename

if __name__ == "__main__":
    fix_pt_br_formatting()

