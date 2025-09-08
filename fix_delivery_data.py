#!/usr/bin/env python3
"""
Script para corrigir o processamento dos dados de entrega diária
"""

import os
import pandas as pd
import json
from datetime import datetime
import re

def clean_value(value):
    """Limpa valores numéricos removendo formatação brasileira"""
    if pd.isna(value) or value == '' or value == '—':
        return None
    
    # Remove formatação brasileira (R$, pontos, vírgulas)
    if isinstance(value, str):
        value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        return float(value)
    except:
        return None

def process_ctv_delivery():
    """Processa dados de entrega do CTV"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/Report Sonho -  Sonho - CTV  Househoud Sync - Video - Setembro (2).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 12:  # Garantir que tem todas as colunas
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                starts = clean_value(row.iloc[2])
                skips = clean_value(row.iloc[3])
                q25 = clean_value(row.iloc[4])
                q50 = clean_value(row.iloc[5])
                q75 = clean_value(row.iloc[6])
                q100 = clean_value(row.iloc[7])
                spend = clean_value(row.iloc[11])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'CTV',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': starts,
                        'q25': q25,
                        'q50': q50,
                        'q75': q75,
                        'q100': q100,
                        'impressions': None,
                        'clicks': None,
                        'visits': None
                    })
        
        print(f"CTV: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar CTV: {e}")
        return []

def process_footfall_delivery():
    """Processa dados de entrega do Footfall Display"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/_Report Sonho -  Sonho -  Footfall - display - Setembro (2).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 6:  # Garantir que tem todas as colunas
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                impressions = clean_value(row.iloc[2])
                clicks = clean_value(row.iloc[3])
                ctr = clean_value(row.iloc[4])
                spend = clean_value(row.iloc[5])
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'Footfall Display',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': None,
                        'q25': None,
                        'q50': None,
                        'q75': None,
                        'q100': None,
                        'impressions': impressions,
                        'clicks': clicks,
                        'visits': None
                    })
        
        print(f"Footfall Display: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar Footfall: {e}")
        return []

def process_tiktok_delivery():
    """Processa dados de entrega do TikTok"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/Report Sonho _ TikTok.xlsx - Report (2).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 7:  # Garantir que tem todas as colunas
                creative = row.iloc[0] if pd.notna(row.iloc[0]) else None
                date = row.iloc[1] if pd.notna(row.iloc[1]) else None
                spend = clean_value(row.iloc[2])
                cpc = clean_value(row.iloc[3])
                cpm = clean_value(row.iloc[4])
                impressions = clean_value(row.iloc[5])
                clicks = clean_value(row.iloc[6])
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'TikTok',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': None,
                        'q25': None,
                        'q50': None,
                        'q75': None,
                        'q100': None,
                        'impressions': impressions,
                        'clicks': clicks,
                        'visits': None
                    })
        
        print(f"TikTok: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar TikTok: {e}")
        return []

def process_youtube_delivery():
    """Processa dados de entrega do YouTube"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/Report Sonho Youtube - Entrega (1).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 11:  # Garantir que tem todas as colunas
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                starts = clean_value(row.iloc[1])
                q25 = clean_value(row.iloc[2])
                q50 = clean_value(row.iloc[3])
                q75 = clean_value(row.iloc[4])
                q100 = clean_value(row.iloc[5])
                creative = row.iloc[9] if pd.notna(row.iloc[9]) else None
                spend = clean_value(row.iloc[10])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'YouTube',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': starts,
                        'q25': q25,
                        'q50': q50,
                        'q75': q75,
                        'q100': q100,
                        'impressions': None,
                        'clicks': None,
                        'visits': None
                    })
        
        print(f"YouTube: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar YouTube: {e}")
        return []

def process_disney_delivery():
    """Processa dados de entrega do Disney"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/_Report Sonho -  Sonho - Disney - Setembro (1).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 9:  # Garantir que tem todas as colunas
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                vcr = clean_value(row.iloc[1])
                q25 = clean_value(row.iloc[2])
                q50 = clean_value(row.iloc[3])
                q75 = clean_value(row.iloc[4])
                q100 = clean_value(row.iloc[5])
                starts = clean_value(row.iloc[6])
                spend = clean_value(row.iloc[7])
                creative = row.iloc[8] if pd.notna(row.iloc[8]) else None
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'Disney',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': starts,
                        'q25': q25,
                        'q50': q50,
                        'q75': q75,
                        'q100': q100,
                        'impressions': None,
                        'clicks': None,
                        'visits': None
                    })
        
        print(f"Disney: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar Disney: {e}")
        return []

def process_netflix_delivery():
    """Processa dados de entrega do Netflix"""
    filepath = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv/Report Sonho - Netflix - Setembro (1).tsv'
    delivery_data = []
    
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 9:  # Garantir que tem todas as colunas
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                vcr = clean_value(row.iloc[1])
                q25 = clean_value(row.iloc[2])
                q50 = clean_value(row.iloc[3])
                q75 = clean_value(row.iloc[4])
                q100 = clean_value(row.iloc[5])
                starts = clean_value(row.iloc[6])
                spend = clean_value(row.iloc[7])
                creative = row.iloc[8] if pd.notna(row.iloc[8]) else None
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        'date': str(date),
                        'channel': 'Netflix',
                        'creative': str(creative) if creative else '',
                        'spend': spend,
                        'starts': starts,
                        'q25': q25,
                        'q50': q50,
                        'q75': q75,
                        'q100': q100,
                        'impressions': None,
                        'clicks': None,
                        'visits': None
                    })
        
        print(f"Netflix: {len(delivery_data)} registros processados")
        return delivery_data
        
    except Exception as e:
        print(f"Erro ao processar Netflix: {e}")
        return []

def main():
    print("🔄 Corrigindo dados de entrega diária...")
    
    # Processar cada canal individualmente
    all_delivery_data = []
    
    all_delivery_data.extend(process_ctv_delivery())
    all_delivery_data.extend(process_footfall_delivery())
    all_delivery_data.extend(process_tiktok_delivery())
    all_delivery_data.extend(process_youtube_delivery())
    all_delivery_data.extend(process_disney_delivery())
    all_delivery_data.extend(process_netflix_delivery())
    
    print(f"\n✅ Total de registros processados: {len(all_delivery_data)}")
    
    # Calcular totais por canal
    channels = {}
    for data in all_delivery_data:
        channel = data['channel']
        if channel not in channels:
            channels[channel] = {'spend': 0, 'count': 0}
        channels[channel]['spend'] += data['spend']
        channels[channel]['count'] += 1
    
    print("\n📊 Resumo por canal:")
    for channel, stats in channels.items():
        print(f"  {channel}: R$ {stats['spend']:,.2f} ({stats['count']} registros)")
    
    # Salvar dados corrigidos
    with open('/Users/lucianoterres/Documents/GitHub/south-media-ia/corrected_delivery_data.js', 'w', encoding='utf-8') as f:
        f.write(f"const DAILY = {json.dumps(all_delivery_data, ensure_ascii=False, indent=2)};")
    
    print("\n💾 Dados corrigidos salvos em corrected_delivery_data.js")
    
    return all_delivery_data

if __name__ == "__main__":
    main()
