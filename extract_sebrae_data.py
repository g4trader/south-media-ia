#!/usr/bin/env python3
"""
Extrator de dados para campanha SEBRAE - Programática Video
"""

import json
import pandas as pd
from google_sheets_service import GoogleSheetsService

def extract_sebrae_data():
    """Extrair dados da campanha SEBRAE - Programática Video"""
    
    # Configuração da planilha com múltiplas abas
    sheet_id = "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8"
    gids = {
        "daily_data": "668487440",  # Aba Report com dados diários
        "contract": "719245615",    # Aba Informações de Contrato
        "strategies": "511331032",  # Aba Estratégias
        "publishers": "531141406"   # Aba Lista de Publishers
    }
    
    # Inicializar serviço
    sheets_service = GoogleSheetsService()
    
    if not sheets_service.is_configured():
        print("❌ Google Sheets não configurado")
        return None
    
    try:
        # Ler dados de todas as abas
        all_data = {}
        
        for tab_name, gid in gids.items():
            print(f"📊 Lendo aba: {tab_name} (GID: {gid})")
            # Tentar acessar pela aba específica
            if tab_name == "publishers":
                df = sheets_service.read_sheet_data(sheet_id, sheet_name="Lista de Publishers")
            elif tab_name == "contract":
                df = sheets_service.read_sheet_data(sheet_id, sheet_name="Informações de Contrato")
            elif tab_name == "strategies":
                df = sheets_service.read_sheet_data(sheet_id, sheet_name="Estratégias")
            elif tab_name == "daily_data":
                df = sheets_service.read_sheet_data(sheet_id, sheet_name="Report ")
            else:
                df = sheets_service.read_sheet_data(sheet_id, gid=gid)
            
            if df is not None:
                print(f"✅ Aba {tab_name}: {len(df)} linhas")
                print(f"Colunas: {list(df.columns)}")
                all_data[tab_name] = df
            else:
                print(f"⚠️ Aba {tab_name}: Nenhum dado encontrado")
                all_data[tab_name] = None
        
        # Processar dados específicos do SEBRAE
        sebrae_data = process_sebrae_data(all_data)
        
        # Salvar dados processados
        output_file = "sebrae_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sebrae_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados salvos em {output_file}")
        return sebrae_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return None

def extract_contract_data(df):
    """Extrair dados de contratação da aba contract"""
    if df is None:
        return {
            "client": "SEBRAE PR",
            "campaign": "Institucional Setembro",
            "channel": "Prográmatica",
            "creative_type": "Video",
            "investment": 31000.00,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "period_start": "15/09/2025",
            "period_end": "30/09/2025"
        }
    
    contract_data = {
        "client": "SEBRAE PR",
        "campaign": "Institucional Setembro",
        "channel": "Prográmatica",
        "creative_type": "Video",
        "investment": 31000.00,
        "cpv_contracted": 0.16,
        "complete_views_contracted": 193750,
        "period_start": "15/09/2025",
        "period_end": "30/09/2025"
    }
    
    # Processar dados de contratação da planilha
    if not df.empty:
        for _, row in df.iterrows():
            # Verificar se a linha tem dados
            row_values = [str(val).strip() for val in row if str(val).strip() and str(val).strip() != 'nan']
            if len(row_values) >= 2:
                key = row_values[0].lower()
                value = row_values[1]
                
                if 'cliente' in key:
                    contract_data["client"] = value
                elif 'campanha' in key:
                    contract_data["campaign"] = value
                elif 'canal' in key:
                    contract_data["channel"] = value
                elif 'tipo de criativo' in key:
                    contract_data["creative_type"] = value
                elif 'investimento' in key:
                    # Extrair valor numérico
                    numeric_value = float(pd.to_numeric(
                        value.replace('R$ ', '').replace('.', '').replace(',', '.')
                        .replace(r'[^\d.]', ''), 
                        errors='coerce'
                    ) or 0)
                    contract_data["investment"] = numeric_value
                elif 'cpv' in key:
                    # Extrair CPV
                    numeric_value = float(pd.to_numeric(
                        value.replace('R$ ', '').replace(',', '.')
                        .replace(r'[^\d.]', ''), 
                        errors='coerce'
                    ) or 0)
                    contract_data["cpv_contracted"] = numeric_value
                elif 'complete' in key:
                    # Extrair VC contratado
                    numeric_value = int(pd.to_numeric(
                        value.replace(r'[^\d]', ''), 
                        errors='coerce'
                    ) or 0)
                    contract_data["complete_views_contracted"] = numeric_value
                elif 'periodo' in key and len(row_values) >= 3:
                    # Extrair período
                    contract_data["period_start"] = row_values[1]
                    contract_data["period_end"] = row_values[2]
    
    return contract_data

def extract_strategies_data(df):
    """Extrair dados de estratégias da aba strategies"""
    if df is None:
        return {
            "segmentation": [
                "Microempreendedores",
                "Jovens Empreendedores em Ascensão"
            ],
            "objectives": [
                "Maximizar alcance qualificado",
                "Eficiência de conversão"
            ]
        }
    
    strategies_data = {
        "segmentation": [],
        "objectives": []
    }
    
    # Processar estratégias da planilha
    if not df.empty:
        for _, row in df.iterrows():
            # Verificar se a linha tem dados
            row_values = [str(val).strip() for val in row if str(val).strip() and str(val).strip() != 'nan']
            if len(row_values) >= 2:
                key = row_values[0].lower()
                value = row_values[1]
                
                if 'segmentações' in key:
                    # Adicionar segmentação
                    if 'microempreendedor' in value.lower():
                        strategies_data["segmentation"].append("Microempreendedores")
                    if 'jovem' in value.lower() and 'empreendedor' in value.lower():
                        strategies_data["segmentation"].append("Jovens Empreendedores em Ascensão")
                elif 'praças' in key:
                    # Adicionar localização
                    strategies_data["objectives"].append(f"Alcance em {value}")
                elif 'white list' in key:
                    # Adicionar objetivo
                    strategies_data["objectives"].append("White list para grandes portais")
    
    return strategies_data

def extract_publishers_data(df):
    """Extrair lista de publishers da aba publishers"""
    if df is None:
        return [
            {"name": "YouTube", "type": "Plataforma principal de vídeo"},
            {"name": "Google Display Network", "type": "Rede de display do Google"},
            {"name": "Facebook/Meta", "type": "Rede social e vídeo"},
            {"name": "Instagram", "type": "Stories e Reels"},
            {"name": "TikTok", "type": "Vídeos curtos"},
            {"name": "LinkedIn", "type": "Rede profissional"}
        ]
    
    publishers_data = []
    
    # Processar publishers da planilha
    if not df.empty:
        for _, row in df.iterrows():
            publisher_info = {}
            for col in df.columns:
                value = str(row[col]).strip()
                if value and value != 'nan':
                    if col.lower() in ['nome', 'name']:
                        publisher_info["name"] = value
                    elif col.lower() in ['app/url', 'url', 'website']:
                        publisher_info["type"] = f"Site: {value}"
            
            if publisher_info.get("name"):
                publishers_data.append(publisher_info)
    
    return publishers_data

def process_sebrae_data(all_data):
    """Processar dados específicos do SEBRAE de múltiplas abas"""
    
    # Extrair dados de contratação da aba contract
    contract_data = extract_contract_data(all_data.get("contract"))
    
    # Extrair dados de estratégias da aba strategies
    strategies_data = extract_strategies_data(all_data.get("strategies"))
    
    # Extrair lista de publishers da aba publishers
    publishers_data = extract_publishers_data(all_data.get("publishers"))
    
    # Dados da campanha
    campaign_data = {
        "campaign_name": f"{contract_data.get('client', 'SEBRAE PR')} - {contract_data.get('campaign', 'Institucional Setembro')}",
        "dashboard_title": f"Dashboard {contract_data.get('client', 'SEBRAE PR')} - {contract_data.get('campaign', 'Institucional Setembro')}",
        "channel": contract_data.get('channel', 'Prográmatica'),
        "creative_type": contract_data.get('creative_type', 'Video'),
        "period": f"{contract_data.get('period_start', '15/09/2025')} - {contract_data.get('period_end', '30/09/2025')}",
        "contract": contract_data,
        "strategies": strategies_data,
        "publishers": publishers_data,
        "metrics": {},
        "daily_data": [],
        "per_data": []
    }
    
    # Usar dados de contratação para métricas base
    campaign_data["budget_contracted"] = contract_data["investment"]
    campaign_data["vc_contracted"] = contract_data["complete_views_contracted"]
    
    # Processar dados diários da aba daily_data
    df = all_data.get("daily_data")
    if df is None:
        print("⚠️ Nenhum dado diário encontrado")
        return campaign_data
    
    # Mapear colunas do SEBRAE baseado na planilha
    column_mapping = {
        'Day': 'date',
        'Creative': 'creative',
        'Imps': 'impressions',
        'Clicks': 'clicks',
        'CTR %': 'ctr',
        'Video Completion Rate %': 'vtr',
        'Video Skip Rate %': 'skip_rate',
        'Video Start Rate %': 'start_rate',
        '25% Video Complete': 'q25',
        '50% Video Complete': 'q50',
        '75% Video Complete': 'q75',
        '100% Complete': 'q100',
        'Video Starts': 'starts',
        'Valor Investido': 'spend',
        'CPV': 'cpv'
    }
    
    # Encontrar colunas na planilha
    available_columns = {}
    for col in df.columns:
        for key, value in column_mapping.items():
            if key.lower() in col.lower():
                available_columns[value] = col
                break
    
    print(f"Colunas mapeadas: {available_columns}")
    
    # Calcular totais
    total_metrics = {}
    for metric, column in available_columns.items():
        if column in df.columns and metric not in ['date', 'creative']:
            # Converter para numérico, tratando valores como "R$ 1.087,36"
            if metric == 'spend':
                # Remover "R$ " e converter vírgula para ponto
                numeric_values = pd.to_numeric(
                    df[column].astype(str).str.replace('R$ ', '', regex=False)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .str.replace(r'[^\d.]', '', regex=True), 
                    errors='coerce'
                )
            else:
                numeric_values = pd.to_numeric(
                    df[column].astype(str).str.replace(r'[^\d.,]', '', regex=True)
                    .str.replace(',', '.', regex=True), 
                    errors='coerce'
                )
            total_metrics[metric] = int(numeric_values.sum())
        else:
            total_metrics[metric] = 0
    
    # Calcular métricas derivadas
    if total_metrics.get('impressions', 0) > 0:
        if total_metrics.get('clicks', 0) > 0:
            total_metrics['ctr'] = (total_metrics['clicks'] / total_metrics['impressions']) * 100
        if total_metrics.get('spend', 0) > 0:
            total_metrics['cpm'] = (total_metrics['spend'] / (total_metrics['impressions'] / 1000))
            if total_metrics.get('clicks', 0) > 0:
                total_metrics['cpc'] = total_metrics['spend'] / total_metrics['clicks']
        if total_metrics.get('q100', 0) > 0:
            total_metrics['vtr'] = (total_metrics['q100'] / total_metrics['starts']) * 100
            total_metrics['cpv'] = total_metrics['spend'] / total_metrics['q100']
    
    # Calcular pacing
    total_metrics['pacing'] = (total_metrics['spend'] / campaign_data['budget_contracted']) * 100
    
    campaign_data["metrics"] = total_metrics
    
    # Processar dados diários
    if 'date' in available_columns and available_columns['date'] in df.columns:
        daily_rows = []
        for _, row in df.iterrows():
            # Processar data
            date_value = str(row.get(available_columns['date'], ''))
            
            # Processar spend
            spend_value = 0
            if available_columns.get('spend') and available_columns['spend'] in df.columns:
                spend_str = str(row.get(available_columns['spend'], '0'))
                spend_value = float(pd.to_numeric(
                    spend_str.replace('R$ ', '').replace('.', '').replace(',', '.')
                    .replace(r'[^\d.]', ''), 
                    errors='coerce'
                ) or 0)
            
            daily_row = {
                "date": date_value,
                "creative": str(row.get(available_columns.get('creative', ''), '')),
                "spend": spend_value,
                "impressions": int(pd.to_numeric(str(row.get(available_columns.get('impressions', '0'), '0')), errors='coerce') or 0),
                "clicks": int(pd.to_numeric(str(row.get(available_columns.get('clicks', '0'), '0')), errors='coerce') or 0),
                "starts": int(pd.to_numeric(str(row.get(available_columns.get('starts', '0'), '0')), errors='coerce') or 0),
                "q25": int(pd.to_numeric(str(row.get(available_columns.get('q25', '0'), '0')), errors='coerce') or 0),
                "q50": int(pd.to_numeric(str(row.get(available_columns.get('q50', '0'), '0')), errors='coerce') or 0),
                "q75": int(pd.to_numeric(str(row.get(available_columns.get('q75', '0'), '0')), errors='coerce') or 0),
                "q100": int(pd.to_numeric(str(row.get(available_columns.get('q100', '0'), '0')), errors='coerce') or 0),
                "ctr": float(pd.to_numeric(str(row.get(available_columns.get('ctr', '0'), '0')), errors='coerce') or 0),
                "vtr": float(pd.to_numeric(str(row.get(available_columns.get('vtr', '0'), '0')), errors='coerce') or 0),
                "cpv": float(pd.to_numeric(str(row.get(available_columns.get('cpv', '0'), '0')), errors='coerce') or 0)
            }
            
            # Só adicionar se tiver data válida
            if date_value and date_value != 'nan' and date_value != '':
                daily_rows.append(daily_row)
        
        campaign_data["daily_data"] = daily_rows
    
    # Criar dados PER (por criativo)
    if campaign_data["daily_data"]:
        creative_data = {}
        for row in campaign_data["daily_data"]:
            creative = row.get('creative', 'N/A')
            if creative not in creative_data:
                creative_data[creative] = {
                    'spend': 0,
                    'impressions': 0,
                    'clicks': 0,
                    'starts': 0,
                    'q25': 0,
                    'q50': 0,
                    'q75': 0,
                    'q100': 0
                }
            
            creative_data[creative]['spend'] += row['spend']
            creative_data[creative]['impressions'] += row['impressions']
            creative_data[creative]['clicks'] += row['clicks']
            creative_data[creative]['starts'] += row['starts']
            creative_data[creative]['q25'] += row['q25']
            creative_data[creative]['q50'] += row['q50']
            creative_data[creative]['q75'] += row['q75']
            creative_data[creative]['q100'] += row['q100']
        
        # Converter para formato PER
        per_data = []
        for creative, data in creative_data.items():
            if data['impressions'] > 0:
                ctr = (data['clicks'] / data['impressions']) * 100
                vtr = (data['q100'] / data['starts']) * 100 if data['starts'] > 0 else 0
                cpv = data['spend'] / data['q100'] if data['q100'] > 0 else 0
                cpm = (data['spend'] / (data['impressions'] / 1000)) if data['impressions'] > 0 else 0
                
                per_data.append({
                    "creative": creative,
                    "spend": data['spend'],
                    "impressions": data['impressions'],
                    "clicks": data['clicks'],
                    "starts": data['starts'],
                    "q25": data['q25'],
                    "q50": data['q50'],
                    "q75": data['q75'],
                    "q100": data['q100'],
                    "ctr": ctr,
                    "vtr": vtr,
                    "cpv": cpv,
                    "cpm": cpm
                })
        
        campaign_data["per_data"] = per_data
    
    return campaign_data

if __name__ == "__main__":
    extract_sebrae_data()
