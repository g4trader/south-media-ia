#!/usr/bin/env python3
"""
Script para extrair dados da campanha Institucional Copacol | Remarketing |Historias | Video Programatico Impressões
"""

import pandas as pd
import json
from datetime import datetime
from google_sheets_processor import GoogleSheetsProcessor

def extract_copacol_video_data():
    """Extrai dados da campanha Video Programático da Copacol"""
    
    # Configuração da planilha principal
    sheet_id = "1ufjQXnXd_pXyoACqmBQrNfK5aK9mz8ERz-t7GKhev60"
    gid = "435258254"
    
    # Configuração da planilha de publishers
    publishers_gid = "1408077642"
    
    print("🔍 Extraindo dados da campanha Video Programático - Copacol...")
    
    try:
        # Inicializar processador
        processor = GoogleSheetsProcessor()
        
        # Verificar acesso às planilhas
        if not processor.validate_sheet_access(sheet_id):
            print("❌ Não foi possível acessar a planilha principal")
            return None
        
        # Ler dados da planilha principal
        print("📊 Lendo dados da planilha de entrega...")
        df_delivery = processor.read_sheet_data(sheet_id, gid=gid)
        
        if df_delivery.empty:
            print("❌ Nenhum dado encontrado na planilha de entrega")
            return None
        
        print(f"✅ {len(df_delivery)} linhas encontradas na planilha de entrega")
        print(f"📋 Colunas: {list(df_delivery.columns)}")
        
        # Ler dados da planilha de publishers
        print("📊 Lendo dados da planilha de publishers...")
        df_publishers = processor.read_sheet_data(sheet_id, gid=publishers_gid)
        
        publishers_list = []
        if not df_publishers.empty:
            print(f"✅ {len(df_publishers)} publishers encontrados")
            # Extrair lista de publishers (assumindo que está em uma coluna)
            for _, row in df_publishers.iterrows():
                for col in df_publishers.columns:
                    value = str(row[col]).strip()
                    if value and value != 'nan' and len(value) > 3:
                        publishers_list.append(value)
        else:
            print("⚠️ Nenhum publisher encontrado, usando lista padrão")
            publishers_list = [
                "YouTube",
                "Google Display Network",
                "Facebook Video",
                "Instagram Video",
                "TikTok Ads",
                "Snapchat Ads"
            ]
        
        # Processar dados da campanha
        campaign_data = process_campaign_data(df_delivery)
        
        # Adicionar publishers à estrutura de dados
        campaign_data['publishers'] = publishers_list
        
        # Salvar dados processados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"copacol_video_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(campaign_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados salvos em: {filename}")
        
        return campaign_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return None

def process_campaign_data(df):
    """Processa os dados da campanha para o formato do dashboard"""
    
    # Informações da campanha
    campaign_info = {
        "name": "Institucional Copacol | Remarketing |Historias | Video Programatico Impressões",
        "channel": "Video Programático",
        "period_start": "08/09/2025",
        "period_end": "05/10/2025",
        "contracted_impressions": 352941,
        "contracted_budget": 30000.00,
        "publishers": []
    }
    
    # Processar dados diários
    daily_data = []
    
    # Mapear colunas (ajustar conforme estrutura real da planilha)
    column_mapping = {
        'date': ['Data', 'Date', 'Dia'],
        'creative': ['Criativo', 'Creative', 'Ad'],
        'spend': ['Gasto', 'Spend', 'Investimento', 'Valor'],
        'impressions': ['Impressões', 'Impressions', 'Views'],
        'clicks': ['Cliques', 'Clicks'],
        'completion_100': ['100%', 'Complete', 'Completion', 'VTR']
    }
    
    # Encontrar colunas reais
    actual_columns = {}
    for key, possible_names in column_mapping.items():
        for col in df.columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    actual_columns[key] = col
                    break
            if key in actual_columns:
                break
    
    print(f"🔍 Colunas mapeadas: {actual_columns}")
    
    # Processar cada linha
    for _, row in df.iterrows():
        try:
            # Extrair data
            date_str = None
            if 'date' in actual_columns:
                date_str = str(row[actual_columns['date']]).strip()
            
            if not date_str or date_str == 'nan':
                continue
            
            # Formatar data
            formatted_date = format_date(date_str)
            if not formatted_date:
                continue
            
            # Extrair outros campos
            creative = str(row[actual_columns.get('creative', '')]).strip() if 'creative' in actual_columns else 'Video 15s'
            spend = parse_currency(str(row[actual_columns.get('spend', '0')]).strip()) if 'spend' in actual_columns else 0
            impressions = parse_number(str(row[actual_columns.get('impressions', '0')]).strip()) if 'impressions' in actual_columns else 0
            clicks = parse_number(str(row[actual_columns.get('clicks', '0')]).strip()) if 'clicks' in actual_columns else 0
            completion_100 = parse_number(str(row[actual_columns.get('completion_100', '0')]).strip()) if 'completion_100' in actual_columns else 0
            
            # Calcular métricas derivadas
            vtr = (completion_100 / impressions * 100) if impressions > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpv = (spend / completion_100) if completion_100 > 0 else 0
            cpm = (spend / impressions * 1000) if impressions > 0 else 0
            
            daily_record = {
                'date': formatted_date,
                'channel': 'Video Programático',
                'creative': creative,
                'spend': spend,
                'impressions': impressions,
                'clicks': clicks,
                'completion_100': completion_100,
                'vtr': vtr,
                'ctr': ctr,
                'cpv': cpv,
                'cpm': cpm
            }
            
            daily_data.append(daily_record)
            
        except Exception as e:
            print(f"⚠️ Erro ao processar linha: {e}")
            continue
    
    # Calcular totais
    total_spend = sum(record['spend'] for record in daily_data)
    total_impressions = sum(record['impressions'] for record in daily_data)
    total_clicks = sum(record['clicks'] for record in daily_data)
    total_completions = sum(record['completion_100'] for record in daily_data)
    
    # Calcular métricas consolidadas
    avg_vtr = (total_completions / total_impressions * 100) if total_impressions > 0 else 0
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpv = (total_spend / total_completions) if total_completions > 0 else 0
    avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    pacing = (total_spend / campaign_info['contracted_budget'] * 100) if campaign_info['contracted_budget'] > 0 else 0
    
    # Estrutura final dos dados
    result = {
        "campaign_info": campaign_info,
        "consolidated_data": {
            "Budget Contratado (R$)": campaign_info['contracted_budget'],
            "Budget Utilizado (R$)": total_spend,
            "Impressões": total_impressions,
            "Cliques": total_clicks,
            "CTR (%)": avg_ctr,
            "VC (100%)": total_completions,
            "VTR (100%)": avg_vtr / 100,
            "CPV (R$)": avg_cpv,
            "CPM (R$)": avg_cpm,
            "Pacing (%)": pacing
        },
        "channel_data": [{
            "Canal": "Video Programático",
            "Budget Contratado (R$)": campaign_info['contracted_budget'],
            "Budget Utilizado (R$)": total_spend,
            "Impressões": total_impressions,
            "Cliques": total_clicks,
            "CTR (%)": avg_ctr,
            "VC (100%)": total_completions,
            "VTR (100%)": avg_vtr / 100,
            "CPV (R$)": avg_cpv,
            "CPM (R$)": avg_cpm,
            "Pacing (%)": pacing,
            "Criativos Únicos": len(set(record['creative'] for record in daily_data))
        }],
        "daily_data": daily_data
    }
    
    print(f"✅ Processamento concluído:")
    print(f"   📊 {len(daily_data)} registros diários")
    print(f"   💰 R$ {total_spend:.2f} gastos")
    print(f"   🎬 {total_impressions:,} impressões")
    print(f"   📈 {avg_vtr:.1f}% VTR")
    print(f"   ⏱️ {pacing:.1f}% pacing")
    
    return result

def format_date(date_str):
    """Formata data para DD/MM/AAAA"""
    try:
        if not date_str or date_str == 'nan':
            return None
        
        date_str = str(date_str).strip()
        
        # Tenta diferentes formatos
        formats = [
            '%Y-%m-%d',      # 2025-09-01
            '%Y/%m/%d',      # 2025/09/01
            '%d/%m/%Y',      # 01/09/2025
            '%d-%m-%Y',      # 01-09-2025
            '%m/%d/%Y',      # 09/01/2025
            '%m-%d-%Y'       # 09-01-2025
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        # Se nenhum formato funcionou, tenta parsear manualmente
        if '/' in date_str or '-' in date_str:
            parts = date_str.replace('/', '-').split('-')
            if len(parts) == 3:
                year, month, day = parts
                # Assume formato YYYY-MM-DD se ano tem 4 dígitos
                if len(year) == 4:
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                else:
                    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        return None
        
    except Exception as e:
        print(f"⚠️ Erro ao formatar data {date_str}: {e}")
        return None

def parse_currency(value_str):
    """Converte string monetária para float"""
    try:
        if not value_str or str(value_str).lower() in ['nan', 'none', '']:
            return 0.0
        
        # Remove caracteres não numéricos exceto vírgula e ponto
        clean_str = str(value_str).replace('R$', '').replace(' ', '').strip()
        
        # Se tem vírgula e ponto, assume formato brasileiro (1.234,56)
        if ',' in clean_str and '.' in clean_str:
            clean_str = clean_str.replace('.', '').replace(',', '.')
        elif ',' in clean_str and '.' not in clean_str:
            # Se só tem vírgula, pode ser decimal brasileiro
            if len(clean_str.split(',')[1]) <= 2:  # Máximo 2 casas decimais
                clean_str = clean_str.replace(',', '.')
            else:
                clean_str = clean_str.replace(',', '')  # Remove vírgula de milhares
        
        return float(clean_str)
        
    except (ValueError, AttributeError):
        return 0.0

def parse_number(value):
    """Converte string numérica para int"""
    try:
        if not value or str(value).lower() in ['nan', 'none', '']:
            return 0
        
        # Remove caracteres não numéricos
        clean_str = str(value).replace(',', '').replace('.', '').strip()
        return int(float(clean_str))
        
    except (ValueError, AttributeError):
        return 0

if __name__ == "__main__":
    # Extrair dados
    data = extract_copacol_video_data()
    
    if data:
        print("\n🎉 Extração de dados concluída com sucesso!")
        print(f"📁 Arquivo salvo: copacol_video_data_*.json")
    else:
        print("\n❌ Falha na extração de dados")
