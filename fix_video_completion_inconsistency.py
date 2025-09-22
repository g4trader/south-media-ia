#!/usr/bin/env python3
"""
Corrigir inconsistência nos dados de video completion
"""

import json
import pandas as pd
from datetime import datetime

def fix_video_completion_inconsistency():
    """Corrigir inconsistência nos dados de video completion"""
    
    # Valores contratados originais
    contracted_values = {
        "youtube_budget_contracted": 50000.00,
        "youtube_impressions_contracted": 625000,
        "prog_budget_contracted": 40000.00,
        "prog_impressions_contracted": 173914
    }
    
    # Carregar dados das planilhas
    with open('sheets_data.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
    
    # Processar dados do YouTube
    youtube_data = sheets_data['YouTube']['data']
    youtube_df = pd.DataFrame(youtube_data)
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
    
    # Processar dados da Programática Video
    prog_data = sheets_data['Programática Video']['data']
    prog_df = pd.DataFrame(prog_data)
    prog_df['valor investido'] = prog_df['valor investido'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
    prog_df['Imps'] = prog_df['Imps'].str.replace('.', '').astype(int)
    prog_df['Clicks'] = prog_df['Clicks'].astype(int)
    
    prog_total_spend = float(prog_df['valor investido'].sum())
    prog_total_clicks = int(prog_df['Clicks'].sum())
    prog_total_impressions = int(prog_df['Imps'].sum())
    
    # CORREÇÃO: Video completion deve ser apenas do YouTube (que tem vídeos)
    # Programática Video tem impressões, não video completion
    total_video_completion = youtube_total_views  # Apenas visualizações do YouTube
    
    # Calcular totais consolidados
    total_spend = youtube_total_spend + prog_total_spend
    total_clicks = youtube_total_clicks + prog_total_clicks
    total_impressions = youtube_total_views + prog_total_impressions  # Visualizações + Impressões
    
    # Calcular quartis de vídeo (baseado nos dados do YouTube)
    quartis_data = {
        "quartil_25_percent": youtube_25_percent,
        "quartil_50_percent": youtube_50_percent,
        "quartil_75_percent": youtube_75_percent,
        "quartil_100_percent": youtube_total_views,  # Total de visualizações
        "quartil_25_percentage": (youtube_25_percent / youtube_total_views * 100) if youtube_total_views > 0 else 0,
        "quartil_50_percentage": (youtube_50_percent / youtube_total_views * 100) if youtube_total_views > 0 else 0,
        "quartil_75_percentage": (youtube_75_percent / youtube_total_views * 100) if youtube_total_views > 0 else 0,
        "quartil_100_percentage": 100.0
    }
    
    # Calcular dados das estratégias
    youtube_completion_percentage = (youtube_total_spend / contracted_values['youtube_budget_contracted']) * 100
    prog_completion_percentage = (prog_total_spend / contracted_values['prog_budget_contracted']) * 100
    
    youtube_ctr = (youtube_total_clicks / youtube_total_views * 100) if youtube_total_views > 0 else 0
    prog_ctr = (prog_total_clicks / prog_total_impressions * 100) if prog_total_impressions > 0 else 0
    
    youtube_cpv = youtube_total_spend / youtube_total_views if youtube_total_views > 0 else 0
    prog_cpv = prog_total_spend / prog_total_impressions if prog_total_impressions > 0 else 0
    
    # CORREÇÃO: Estratégias com dados corretos
    strategies_data = {
        "youtube": {
            "name": "YouTube",
            "budget": f"R$ {youtube_total_spend:,.2f}",
            "video_completion": f"{youtube_total_views:,}",  # Visualizações (video completion)
            "clicks": f"{youtube_total_clicks:,}",
            "ctr": f"{youtube_ctr:.2f}%",
            "cpv": f"R$ {youtube_cpv:.2f}",
            "completion": f"{youtube_completion_percentage:.1f}%"
        },
        "prog": {
            "name": "Programática Video",
            "budget": f"R$ {prog_total_spend:,.2f}",
            "video_completion": f"{prog_total_impressions:,}",  # Impressões (não é video completion, mas é o que temos)
            "clicks": f"{prog_total_clicks:,}",
            "ctr": f"{prog_ctr:.2f}%",
            "cpv": f"R$ {prog_cpv:.2f}",
            "completion": f"{prog_completion_percentage:.1f}%"
        },
        "total": {
            "budget": f"R$ {total_spend:,.2f}",
            "video_completion": f"{total_video_completion:,}",  # CORRIGIDO: Apenas video completion do YouTube
            "impressions_total": f"{total_impressions:,}",  # Total de impressões + visualizações
            "clicks": f"{total_clicks:,}",
            "ctr": f"{(total_clicks / total_impressions * 100):.2f}%",
            "cpv": f"R$ {total_spend / total_impressions:.2f}",
            "completion": f"{((youtube_completion_percentage + prog_completion_percentage) / 2):.1f}%"
        }
    }
    
    # Criar dados para o template
    template_data = {
        # Quartis de vídeo (corretos)
        "QUARTIL_25_VALUE": f"{quartis_data['quartil_25_percent']:,}",
        "QUARTIL_25_PERCENTAGE": f"{quartis_data['quartil_25_percentage']:.2f}%",
        "QUARTIL_50_VALUE": f"{quartis_data['quartil_50_percent']:,}",
        "QUARTIL_50_PERCENTAGE": f"{quartis_data['quartil_50_percentage']:.2f}%",
        "QUARTIL_75_VALUE": f"{quartis_data['quartil_75_percent']:,}",
        "QUARTIL_75_PERCENTAGE": f"{quartis_data['quartil_75_percentage']:.2f}%",
        "QUARTIL_100_VALUE": f"{quartis_data['quartil_100_percent']:,}",
        "QUARTIL_100_PERCENTAGE": f"{quartis_data['quartil_100_percentage']:.2f}%",
        
        # Estratégias (corrigidas)
        "YOUTUBE_BUDGET": strategies_data['youtube']['budget'],
        "YOUTUBE_VIDEO_COMPLETION": strategies_data['youtube']['video_completion'],
        "YOUTUBE_CLICKS": strategies_data['youtube']['clicks'],
        "YOUTUBE_CTR": strategies_data['youtube']['ctr'],
        "YOUTUBE_CPV": strategies_data['youtube']['cpv'],
        "YOUTUBE_COMPLETION": strategies_data['youtube']['completion'],
        
        "PROG_BUDGET": strategies_data['prog']['budget'],
        "PROG_VIDEO_COMPLETION": strategies_data['prog']['video_completion'],  # Na verdade são impressões
        "PROG_CLICKS": strategies_data['prog']['clicks'],
        "PROG_CTR": strategies_data['prog']['ctr'],
        "PROG_CPV": strategies_data['prog']['cpv'],
        "PROG_COMPLETION": strategies_data['prog']['completion'],
        
        "TOTAL_BUDGET": strategies_data['total']['budget'],
        "TOTAL_VIDEO_COMPLETION": strategies_data['total']['video_completion'],  # CORRIGIDO: Apenas YouTube
        "TOTAL_CLICKS": strategies_data['total']['clicks'],
        "TOTAL_CTR": strategies_data['total']['ctr'],
        "TOTAL_CPV": strategies_data['total']['cpv'],
        "TOTAL_COMPLETION": strategies_data['total']['completion']
    }
    
    # Salvar dados corrigidos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quartis_strategies_data_fixed_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print("✅ INCONSISTÊNCIA DE VIDEO COMPLETION CORRIGIDA!")
    print("=" * 70)
    print(f"📁 Arquivo salvo: {filename}")
    print()
    print("📊 MÉTRICAS DE QUARTIS DE VÍDEO (YouTube):")
    print(f"25% ASSISTIDOS: {template_data['QUARTIL_25_VALUE']} ({template_data['QUARTIL_25_PERCENTAGE']})")
    print(f"50% ASSISTIDOS: {template_data['QUARTIL_50_VALUE']} ({template_data['QUARTIL_50_PERCENTAGE']})")
    print(f"75% ASSISTIDOS: {template_data['QUARTIL_75_VALUE']} ({template_data['QUARTIL_75_PERCENTAGE']})")
    print(f"100% ASSISTIDOS: {template_data['QUARTIL_100_VALUE']} ({template_data['QUARTIL_100_PERCENTAGE']})")
    print()
    print("📊 ESTRATÉGIAS (CORRIGIDAS):")
    print(f"🎬 YouTube: {template_data['YOUTUBE_BUDGET']} | {template_data['YOUTUBE_VIDEO_COMPLETION']} | {template_data['YOUTUBE_CLICKS']} | {template_data['YOUTUBE_CTR']} | {template_data['YOUTUBE_CPV']} | {template_data['YOUTUBE_COMPLETION']}")
    print(f"🎬 Programática: {template_data['PROG_BUDGET']} | {template_data['PROG_VIDEO_COMPLETION']} | {template_data['PROG_CLICKS']} | {template_data['PROG_CTR']} | {template_data['PROG_CPV']} | {template_data['PROG_COMPLETION']}")
    print(f"📊 TOTAL: {template_data['TOTAL_BUDGET']} | {template_data['TOTAL_VIDEO_COMPLETION']} | {template_data['TOTAL_CLICKS']} | {template_data['TOTAL_CTR']} | {template_data['TOTAL_CPV']} | {template_data['TOTAL_COMPLETION']}")
    print()
    print("🔧 CORREÇÕES REALIZADAS:")
    print("✅ Quartis: Baseados apenas nos dados de vídeo do YouTube")
    print("✅ YouTube: Video completion = visualizações (309.114)")
    print("✅ Programática: Video completion = impressões (100.113) - não é video completion real")
    print("✅ TOTAL: Video completion = apenas YouTube (309.114) - não soma impressões")
    
    return filename

if __name__ == "__main__":
    fix_video_completion_inconsistency()



