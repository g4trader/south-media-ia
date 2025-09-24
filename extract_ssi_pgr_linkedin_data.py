#!/usr/bin/env python3
"""
Script para extrair dados da campanha SSI - PGR - NativeAds (LinkedIn)
Planilha: https://docs.google.com/spreadsheets/d/1NyChr0Gi3p6K8uuIVFz4H_wtB-ZwALeIuQFZUqlHQKo/edit?gid=255869630#gid=255869630
"""

import os
import json
from datetime import datetime
from google_sheets_processor import GoogleSheetsProcessor

def extract_ssi_pgr_linkedin_data():
    """Extrair dados da campanha SSI - PGR - NativeAds"""
    
    # Configuração da planilha
    sheet_id = "1NyChr0Gi3p6K8uuIVFz4H_wtB-ZwALeIuQFZUqlHQKo"
    gid = "255869630"  # GID da aba de dados
    
    print("🚀 Iniciando extração de dados da campanha SSI - PGR - NativeAds (LinkedIn)")
    print(f"📊 Planilha: {sheet_id}")
    print(f"📋 GID: {gid}")
    
    try:
        # Inicializar processador
        processor = GoogleSheetsProcessor()
        
        # Validar acesso à planilha
        if not processor.validate_sheet_access(sheet_id, gid):
            print("❌ Não foi possível acessar a planilha")
            return None
        
        # Ler dados da planilha
        df = processor.read_sheet_data(sheet_id, gid=gid)
        
        if df.empty:
            print("❌ Nenhum dado encontrado na planilha")
            return None
        
        print(f"✅ {len(df)} linhas encontradas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Processar dados específicos do LinkedIn
        linkedin_data = process_linkedin_data(df)
        
        # Salvar dados processados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ssi_pgr_linkedin_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(linkedin_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados salvos em: {filename}")
        return linkedin_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados: {e}")
        return None

def process_linkedin_data(df):
    """Processar dados específicos do LinkedIn"""
    
    # Configuração da campanha
    campaign_data = {
        "campaign_name": "SSI - PGR - NativeAds",
        "channel": "LinkedIn",
        "period": {
            "start": "01/09/2025",
            "end": "30/10/2025"
        },
        "contract": {
            "budget": 8000.00,
            "cpm": 4.20,
            "impressions_contracted": 1904762
        },
        "strategy": {
            "location": "Paraná",
            "sites_list_url": "https://docs.google.com/spreadsheets/d/1NyChr0Gi3p6K8uuIVFz4H_wtB-ZwALeIuQFZUqlHQKo/edit?gid=1304614939#gid=1304614939"
        }
    }
    
    # Mapear colunas (ajustar conforme estrutura real da planilha)
    column_mapping = {
        'date': ['Data', 'Date', 'Dia'],
        'creative': ['Criativo', 'Creative', 'Anúncio'],
        'spend': ['Gasto', 'Spend', 'Investimento', 'Valor'],
        'impressions': ['Impressões', 'Impressions', 'Views'],
        'clicks': ['Cliques', 'Clicks', 'Cliques únicos'],
        'ctr': ['CTR', 'Taxa de cliques'],
        'cpm': ['CPM', 'Custo por mil impressões'],
        'cpc': ['CPC', 'Custo por clique']
    }
    
    # Encontrar colunas reais
    actual_columns = {}
    for metric, possible_names in column_mapping.items():
        for col in df.columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    actual_columns[metric] = col
                    break
            if metric in actual_columns:
                break
    
    print(f"🔍 Colunas mapeadas: {actual_columns}")
    
    # Processar dados diários
    daily_data = []
    total_spend = 0
    total_impressions = 0
    total_clicks = 0
    
    for _, row in df.iterrows():
        try:
            # Processar data
            date_str = str(row.get(actual_columns.get('date', ''), ''))
            formatted_date = processor.format_date(date_str)
            
            if not formatted_date:
                continue
            
            # Processar outros campos
            creative = str(row.get(actual_columns.get('creative', ''), ''))
            spend = processor.parse_currency(str(row.get(actual_columns.get('spend', ''), '0')))
            impressions = processor.parse_number(row.get(actual_columns.get('impressions', ''), 0))
            clicks = processor.parse_number(row.get(actual_columns.get('clicks', ''), 0))
            
            # Calcular métricas derivadas
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpm = (spend / impressions * 1000) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            
            record = {
                'date': formatted_date,
                'creative': creative,
                'spend': spend,
                'impressions': impressions,
                'clicks': clicks,
                'ctr': ctr,
                'cpm': cpm,
                'cpc': cpc
            }
            
            daily_data.append(record)
            
            # Acumular totais
            total_spend += spend
            total_impressions += impressions
            total_clicks += clicks
            
        except Exception as e:
            print(f"⚠️ Erro ao processar linha: {e}")
            continue
    
    # Calcular métricas consolidadas
    total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    total_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    total_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    pacing = (total_spend / campaign_data['contract']['budget'] * 100) if campaign_data['contract']['budget'] > 0 else 0
    
    # Dados consolidados
    consolidated_data = {
        "Budget Contratado (R$)": campaign_data['contract']['budget'],
        "Budget Utilizado (R$)": total_spend,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (%)": total_ctr,
        "CPM (R$)": total_cpm,
        "CPC (R$)": total_cpc,
        "Pacing (%)": pacing
    }
    
    # Dados por canal (LinkedIn)
    channel_data = {
        "Canal": "LINKEDIN",
        "Budget Contratado (R$)": campaign_data['contract']['budget'],
        "Budget Utilizado (R$)": total_spend,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (%)": total_ctr,
        "CPM (R$)": total_cpm,
        "CPC (R$)": total_cpc,
        "Pacing (%)": pacing,
        "Criativos Únicos": len(set([d['creative'] for d in daily_data if d['creative']]))
    }
    
    return {
        "campaign_info": campaign_data,
        "consolidated": consolidated_data,
        "channels": [channel_data],
        "daily_data": daily_data
    }

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Extrair dados
    data = extract_ssi_pgr_linkedin_data()
    
    if data:
        print("🎉 Extração concluída com sucesso!")
        print(f"📊 Total de registros diários: {len(data['daily_data'])}")
        print(f"💰 Budget utilizado: R$ {data['consolidated']['Budget Utilizado (R$)']:.2f}")
        print(f"📈 Impressões: {data['consolidated']['Impressões']:,}")
        print(f"👆 Cliques: {data['consolidated']['Cliques']:,}")
        print(f"📊 CTR: {data['consolidated']['CTR (%)']:.2f}%")
        print(f"⏱️ Pacing: {data['consolidated']['Pacing (%)']:.1f}%")
    else:
        print("❌ Falha na extração dos dados")
