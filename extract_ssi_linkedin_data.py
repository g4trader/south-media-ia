#!/usr/bin/env python3
"""
Extrator de dados para campanha SSI - Linkedin - PGR
"""

import json
import pandas as pd
from google_sheets_service import GoogleSheetsService

def extract_ssi_linkedin_data():
    """Extrair dados da campanha SSI - Linkedin - PGR"""
    
    # Configuração da campanha
    sheet_id = "1F8rq-7S6npEMNRgXHpsjOW8t5-LkvO7MrR9y_akan-c"
    gid = "2035261685"
    
    # Inicializar serviço
    sheets_service = GoogleSheetsService()
    
    if not sheets_service.is_configured():
        print("❌ Google Sheets não configurado")
        return None
    
    try:
        # Ler dados da planilha
        df = sheets_service.read_sheet_data(sheet_id, gid=gid)
        
        if df is None:
            print("❌ Nenhum dado encontrado na planilha")
            return None
        
        print(f"✅ Dados lidos da planilha: {len(df)} linhas")
        print(f"Colunas disponíveis: {list(df.columns)}")
        
        # Processar dados específicos do LinkedIn
        linkedin_data = process_linkedin_data(df)
        
        # Salvar dados processados
        output_file = "ssi_linkedin_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(linkedin_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dados salvos em {output_file}")
        return linkedin_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return None

def process_linkedin_data(df):
    """Processar dados específicos do LinkedIn"""
    
    # Dados da campanha
    campaign_data = {
        "campaign_name": "SSI - Linkedin - PGR",
        "channel": "Linkedin",
        "period": "01/09/2025 a 30/10/2025",
        "budget_contracted": 12000.00,
        "cpm": 36.00,
        "impressions_contracted": 333333,
        "strategy": "Praça: Paraná",
        "metrics": {},
        "daily_data": []
    }
    
    # Mapear colunas do LinkedIn
    column_mapping = {
        'Impressões': 'impressions',
        'Cliques': 'clicks', 
        'Gasto': 'spend',
        'CTR': 'ctr',
        'CPM': 'cpm',
        'CPC': 'cpc',
        'Data': 'date',
        'Criativo': 'creative'
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
        if column in df.columns and metric != 'date' and metric != 'creative':
            # Converter para numérico
            numeric_values = pd.to_numeric(
                df[column].astype(str).str.replace(r'[^\d.,]', '', regex=True).str.replace(',', '.'), 
                errors='coerce'
            )
            total_metrics[metric] = numeric_values.sum()
        else:
            total_metrics[metric] = 0
    
    # Calcular métricas derivadas
    if total_metrics.get('impressions', 0) > 0:
        if total_metrics.get('clicks', 0) > 0:
            total_metrics['ctr'] = (total_metrics['clicks'] / total_metrics['impressions']) * 100
        if total_metrics.get('spend', 0) > 0:
            total_metrics['cpm'] = (total_metrics['spend'] / total_metrics['impressions']) * 1000
            if total_metrics.get('clicks', 0) > 0:
                total_metrics['cpc'] = total_metrics['spend'] / total_metrics['clicks']
    
    campaign_data["metrics"] = total_metrics
    
    # Processar dados diários
    if 'date' in available_columns and available_columns['date'] in df.columns:
        daily_rows = []
        for _, row in df.iterrows():
            daily_row = {
                "date": str(row.get(available_columns['date'], '')),
                "creative": str(row.get(available_columns.get('creative', ''), '')),
                "spend": float(pd.to_numeric(str(row.get(available_columns.get('spend', ''), '')).replace(',', '.'), errors='coerce') or 0),
                "impressions": int(pd.to_numeric(str(row.get(available_columns.get('impressions', ''), '')).replace(',', '.'), errors='coerce') or 0),
                "clicks": int(pd.to_numeric(str(row.get(available_columns.get('clicks', ''), '')).replace(',', '.'), errors='coerce') or 0)
            }
            daily_rows.append(daily_row)
        
        campaign_data["daily_data"] = daily_rows
    
    return campaign_data

if __name__ == "__main__":
    extract_ssi_linkedin_data()
