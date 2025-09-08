#!/usr/bin/env python3
"""
Script para atualizar dados do dashboard com os novos valores contratados
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

def process_contract_data():
    """Processa dados de contratação dos arquivos TSV atualizados"""
    contract_data = []
    tsv_dir = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv'
    
    # Arquivos de contratação por canal
    contract_files = {
        'dash - CTV (1).tsv': 'CTV',
        'dash - Disney (1).tsv': 'Disney',
        'dash - footfall (1).tsv': 'Footfall Display',
        'dash - netflix (1).tsv': 'Netflix',
        'dash - tiktok (1).tsv': 'TikTok',
        'dash - youtube (1).tsv': 'YouTube'
    }
    
    for filename, channel in contract_files.items():
        filepath = os.path.join(tsv_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
                
                # Extrair dados do arquivo
                budget_contratado = None
                views_contratadas = None
                impressoes_contratadas = None
                cpv = None
                cpm = None
                
                for _, row in df.iterrows():
                    if 'Valor contratado' in str(row.iloc[0]):
                        budget_contratado = clean_value(row.iloc[1])
                    elif 'Views contratadas' in str(row.iloc[0]):
                        views_contratadas = clean_value(row.iloc[1])
                    elif 'Impressões contratadas' in str(row.iloc[0]) or 'impressões contratadas' in str(row.iloc[0]):
                        impressoes_contratadas = clean_value(row.iloc[1])
                    elif 'CPV' in str(row.iloc[0]):
                        cpv = clean_value(row.iloc[1])
                    elif 'CPM' in str(row.iloc[0]):
                        cpm = clean_value(row.iloc[1])
                
                contract_data.append({
                    'Canal': channel,
                    'Budget Contratado (R$)': budget_contratado,
                    'Views Contratadas': views_contratadas,
                    'Impressões Contratadas': impressoes_contratadas,
                    'CPV (R$)': cpv,
                    'CPM (R$)': cpm
                })
                
                print(f"Processado {channel}: R$ {budget_contratado}")
                
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
    
    return contract_data

def process_delivery_data():
    """Processa dados de entrega diária dos arquivos de relatório"""
    delivery_data = []
    tsv_dir = '/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv'
    
    # Arquivos de entrega por canal
    delivery_files = {
        'Report Sonho -  Sonho - CTV  Househoud Sync - Video - Setembro (2).tsv': 'CTV',
        '_Report Sonho -  Sonho - Disney - Setembro (1).tsv': 'Disney',
        'Report Sonho - Netflix - Setembro (1).tsv': 'Netflix',
        'Report Sonho _ TikTok.xlsx - Report (2).tsv': 'TikTok',
        'Report Sonho Youtube - Entrega (1).tsv': 'YouTube',
        '_Report Sonho -  Sonho -  Footfall - display - Setembro (2).tsv': 'Footfall Display'
    }
    
    for filename, channel in delivery_files.items():
        filepath = os.path.join(tsv_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
                
                # Processar cada linha de entrega
                for _, row in df.iterrows():
                    if len(row) >= 3:  # Garantir que tem pelo menos 3 colunas
                        date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                        creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                        
                        # O spend está sempre na última coluna
                        spend = clean_value(row.iloc[-1]) if len(row) > 0 else None
                        
                        # Extrair outras métricas baseado na estrutura do arquivo
                        if channel in ['CTV', 'Disney', 'Netflix', 'YouTube']:
                            # Para canais de vídeo: Date, Creative, Starts, Skips, Q25, Q50, Q75, Q100, ..., Spend
                            starts = clean_value(row.iloc[2]) if len(row) > 2 else None
                            q25 = clean_value(row.iloc[4]) if len(row) > 4 else None
                            q50 = clean_value(row.iloc[5]) if len(row) > 5 else None
                            q75 = clean_value(row.iloc[6]) if len(row) > 6 else None
                            q100 = clean_value(row.iloc[7]) if len(row) > 7 else None
                            impressions = None
                            clicks = None
                            visits = None
                        else:
                            # Para canais de display: Date, Creative, Impressions, Clicks, ..., Spend
                            starts = None
                            q25 = None
                            q50 = None
                            q75 = None
                            q100 = None
                            impressions = clean_value(row.iloc[2]) if len(row) > 2 else None
                            clicks = clean_value(row.iloc[3]) if len(row) > 3 else None
                            visits = None
                        
                        # Validar se spend é um valor razoável (não muito alto)
                        if spend and spend < 10000:  # Limitar a valores razoáveis
                            delivery_data.append({
                                'date': str(date),
                                'channel': channel,
                                'creative': str(creative) if creative else '',
                                'spend': spend,
                                'starts': starts,
                                'q25': q25,
                                'q50': q50,
                                'q75': q75,
                                'q100': q100,
                                'impressions': impressions,
                                'clicks': clicks,
                                'visits': visits
                            })
                
                print(f"Processado entrega {channel}: {len([d for d in delivery_data if d['channel'] == channel])} registros")
                
            except Exception as e:
                print(f"Erro ao processar entrega {filename}: {e}")
    
    return delivery_data

def calculate_consolidated_data(contract_data, delivery_data):
    """Calcula dados consolidados"""
    # Calcular totais
    total_budget_contratado = sum([c['Budget Contratado (R$)'] for c in contract_data if c['Budget Contratado (R$)']])
    total_budget_utilizado = sum([d['spend'] for d in delivery_data if d['spend']])
    total_impressions = sum([d['impressions'] for d in delivery_data if d['impressions']])
    total_clicks = sum([d['clicks'] for d in delivery_data if d['clicks']])
    total_vc = sum([d['q100'] for d in delivery_data if d['q100']])
    
    # Calcular métricas consolidadas
    ctr_cons = (total_clicks / total_impressions) if total_impressions > 0 else 0
    vtr_cons = (total_vc / total_impressions) if total_impressions > 0 else 0
    cpm_cons = (total_budget_utilizado / total_impressions * 1000) if total_impressions > 0 else 0
    cpv_cons = (total_budget_utilizado / total_vc) if total_vc > 0 else 0
    
    return {
        'Budget Contratado (R$)': total_budget_contratado,
        'Budget Utilizado (R$)': total_budget_utilizado,
        'Impressões': total_impressions,
        'Cliques': total_clicks,
        'CTR (cons.)': ctr_cons,
        'VC (100%)': total_vc,
        'VTR (cons.)': vtr_cons,
        'CPM (R$) cons.': cpm_cons,
        'CPV (R$) cons.': cpv_cons,
        'Visitas (Footfall)': 0,
        'Custo/Visita (R$) cons.': None
    }

def calculate_per_channel_data(contract_data, delivery_data):
    """Calcula dados por canal"""
    per_data = []
    
    for contract in contract_data:
        channel = contract['Canal']
        
        # Calcular dados de entrega para este canal
        channel_delivery = [d for d in delivery_data if d['channel'] == channel]
        budget_utilizado = sum([d['spend'] for d in channel_delivery if d['spend']])
        impressions = sum([d['impressions'] for d in channel_delivery if d['impressions']])
        clicks = sum([d['clicks'] for d in channel_delivery if d['clicks']])
        vc = sum([d['q100'] for d in channel_delivery if d['q100']])
        
        # Calcular métricas
        ctr = (clicks / impressions) if impressions > 0 else None
        vtr = (vc / impressions) if impressions > 0 else None
        cpm = (budget_utilizado / impressions * 1000) if impressions > 0 else None
        cpv = (budget_utilizado / vc) if vc > 0 else None
        pacing = (budget_utilizado / contract['Budget Contratado (R$)']) if contract['Budget Contratado (R$)'] > 0 else 0
        
        per_data.append({
            'Canal': channel,
            'Budget Contratado (R$)': contract['Budget Contratado (R$)'],
            'Budget Utilizado (R$)': budget_utilizado,
            'Impressões': impressions if impressions > 0 else None,
            'Cliques': clicks if clicks > 0 else None,
            'CTR': ctr,
            'VC (100%)': vc if vc > 0 else None,
            'VTR (100%)': vtr,
            'CPV (R$)': contract['CPV (R$)'] if contract['CPV (R$)'] else cpv,
            'CPM (R$)': contract['CPM (R$)'] if contract['CPM (R$)'] else cpm,
            'Visitas (Footfall)': 0,
            'Custo/Visita (R$)': None,
            'Pacing (%)': pacing
        })
    
    return per_data

def main():
    print("🔄 Processando dados atualizados...")
    
    # Processar dados de contratação
    print("\n📋 Processando dados de contratação...")
    contract_data = process_contract_data()
    
    # Processar dados de entrega
    print("\n📊 Processando dados de entrega...")
    delivery_data = process_delivery_data()
    
    # Calcular dados consolidados
    print("\n🧮 Calculando dados consolidados...")
    cons_data = calculate_consolidated_data(contract_data, delivery_data)
    
    # Calcular dados por canal
    print("\n📈 Calculando dados por canal...")
    per_data = calculate_per_channel_data(contract_data, delivery_data)
    
    # Gerar JavaScript
    print("\n💾 Gerando dados JavaScript...")
    
    js_content = f"""// Dados atualizados do dashboard
const CONS = {json.dumps(cons_data, ensure_ascii=False, indent=2)};
const PER = {json.dumps(per_data, ensure_ascii=False, indent=2)};
const DAILY = {json.dumps(delivery_data, ensure_ascii=False, indent=2)};

// Dados de footfall (mantidos do arquivo anterior)
const FOOTFALL_POINTS = [
    {{"lat": -8.09233930867147, "lon": -34.8847507746984, "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina", "users": 1740.0, "rate": 3.0}},
    {{"lat": -8.13196914950721, "lon": -34.9069687730163, "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300", "users": 1892.0, "rate": 7.0}},
    {{"lat": -8.04591568467357, "lon": -34.9092152269836, "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310", "users": 211.0, "rate": 9.0}},
    {{"lat": -8.047434924792, "lon": -34.9001621153442, "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040", "users": 548.0, "rate": 8.0}},
    {{"lat": -8.02988247354862, "lon": -34.9066516730163, "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380", "users": 555.0, "rate": 11.0}},
    {{"lat": -8.11993224900449, "lon": -34.9009126846557, "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050", "users": 1020.0, "rate": 6.0}},
    {{"lat": -8.14254391419425, "lon": -34.9081091134918, "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300", "users": 1089.0, "rate": 5.0}},
    {{"lat": -8.0281307802215, "lon": -34.9025068846557, "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005", "users": 4328.0, "rate": 11.0}},
    {{"lat": -7.99956677243255, "lon": -34.8464921711639, "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260", "users": 5121.0, "rate": 12.0}},
    {{"lat": -8.18360115521895, "lon": -34.919450028836, "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010", "users": 1212.0, "rate": 11.0}},
    {{"lat": -8.18233405479681, "lon": -34.9200238558197, "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400", "users": 1573.0, "rate": 14.0}},
    {{"lat": -8.01836781970679, "lon": -34.9962135137705, "name": "Recibom - Timbi, Camaragibe - PE, 54765-290", "users": null, "rate": null}}
];"""
    
    # Salvar arquivo
    with open('/Users/lucianoterres/Documents/GitHub/south-media-ia/updated_dashboard_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("\n✅ Dados atualizados gerados com sucesso!")
    print(f"📊 Total contratado: R$ {cons_data['Budget Contratado (R$)']:,.2f}")
    print(f"💰 Total utilizado: R$ {cons_data['Budget Utilizado (R$)']:,.2f}")
    print(f"📈 Pacing geral: {(cons_data['Budget Utilizado (R$)'] / cons_data['Budget Contratado (R$)'] * 100):.1f}%")
    
    return cons_data, per_data, delivery_data

if __name__ == "__main__":
    main()
