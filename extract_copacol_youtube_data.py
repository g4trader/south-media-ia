#!/usr/bin/env python3
"""
Script para extrair dados da campanha COPACOL REMARKETING YOUTUBE
Planilha: https://docs.google.com/spreadsheets/d/1nDp-VgoMn5En3k40PN4Z-7QgmVrxOGnYo3RkSqNaz_o/edit?gid=406306010#gid=406306010
"""

import pandas as pd
import json
from datetime import datetime
from google_sheets_processor import GoogleSheetsProcessor
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_copacol_youtube_data():
    """Extrair dados da campanha COPACOL REMARKETING YOUTUBE"""
    
    # Configuração da planilha COPACOL
    sheet_config = {
        'sheet_id': '1nDp-VgoMn5En3k40PN4Z-7QgmVrxOGnYo3RkSqNaz_o',
        'gid': '406306010',
        'sheet_name': None  # Será determinado pelo GID
    }
    
    # Configuração das colunas (baseado no padrão das outras campanhas)
    columns_config = {
        'date': 'Data',
        'creative': 'Criativo',
        'spend': 'Investimento (R$)',
        'impressions': 'Impressões',
        'clicks': 'Cliques',
        'starts': 'Starts',
        'q25': '25%',
        'q50': '50%',
        'q75': '75%',
        'q100': '100%',
        'visits': 'Visitas'
    }
    
    try:
        # Inicializar o processador (usar o mesmo método que funciona)
        from google_sheets_service import GoogleSheetsService
        service = GoogleSheetsService()
        
        # Ler dados da planilha
        logger.info("📊 Lendo dados da planilha COPACOL...")
        df = processor.read_sheet_data(
            sheet_id=sheet_config['sheet_id'],
            gid=sheet_config['gid']
        )
        
        if df.empty:
            logger.warning("⚠️ Nenhum dado encontrado na planilha")
            return None
        
        logger.info(f"✅ {len(df)} linhas encontradas")
        logger.info(f"📋 Colunas: {list(df.columns)}")
        
        # Processar dados diários
        daily_data = []
        for _, row in df.iterrows():
            try:
                # Processar data
                date_str = str(row.get(columns_config['date'], ''))
                formatted_date = processor.format_date(date_str)
                
                if not formatted_date:
                    continue
                
                # Processar outros campos
                creative = str(row.get(columns_config['creative'], ''))
                spend = processor.parse_currency(str(row.get(columns_config['spend'], '0')))
                impressions = processor.parse_number(row.get(columns_config['impressions'], 0))
                clicks = processor.parse_number(row.get(columns_config['clicks'], 0))
                starts = processor.parse_number(row.get(columns_config['starts'], 0))
                q25 = processor.parse_number(row.get(columns_config['q25'], 0))
                q50 = processor.parse_number(row.get(columns_config['q50'], 0))
                q75 = processor.parse_number(row.get(columns_config['q75'], 0))
                q100 = processor.parse_number(row.get(columns_config['q100'], 0))
                visits = str(row.get(columns_config['visits'], ''))
                
                # Criar registro
                record = {
                    'date': formatted_date,
                    'channel': 'YOUTUBE',
                    'creative': creative,
                    'spend': spend,
                    'starts': starts if starts > 0 else '',
                    'q25': q25 if q25 > 0 else '',
                    'q50': q50 if q50 > 0 else '',
                    'q75': q75 if q75 > 0 else '',
                    'q100': q100 if q100 > 0 else '',
                    'impressions': impressions,
                    'clicks': clicks,
                    'visits': visits
                }
                
                daily_data.append(record)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar linha: {e}")
                continue
        
        logger.info(f"✅ {len(daily_data)} registros processados")
        
        # Calcular métricas consolidadas
        total_spend = sum(record['spend'] for record in daily_data)
        total_impressions = sum(record['impressions'] for record in daily_data)
        total_clicks = sum(record['clicks'] for record in daily_data)
        total_starts = sum(record['starts'] for record in daily_data if record['starts'])
        total_q100 = sum(record['q100'] for record in daily_data if record['q100'])
        
        # Calcular métricas derivadas
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        vtr = (total_q100 / total_starts * 100) if total_starts > 0 else 0
        cpv = (total_spend / total_q100) if total_q100 > 0 else 0
        cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        
        # Dados consolidadas (CONS)
        cons_data = {
            "Budget Contratado (R$)": 21000.00,
            "Budget Utilizado (R$)": total_spend,
            "Impressões": total_impressions,
            "Cliques": total_clicks,
            "CTR (%)": ctr,
            "VC (100%)": total_q100,
            "VTR (100%)": vtr / 100,
            "CPV (R$)": cpv,
            "CPM (R$)": cpm,
            "Pacing (%)": (total_spend / 21000.00) * 100
        }
        
        # Dados por canal (PER)
        per_data = [{
            "Canal": "YOUTUBE",
            "Budget Contratado (R$)": 21000.00,
            "Budget Utilizado (R$)": total_spend,
            "Impressões": total_impressions,
            "Cliques": total_clicks,
            "CTR (%)": ctr,
            "VC (100%)": total_q100,
            "VTR (100%)": vtr / 100,
            "CPV (R$)": cpv,
            "CPM (R$)": cpm,
            "Pacing (%)": (total_spend / 21000.00) * 100,
            "Criativos Únicos": len(set(record['creative'] for record in daily_data if record['creative']))
        }]
        
        # Salvar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Dados para o dashboard
        dashboard_data = {
            'CONS': cons_data,
            'PER': per_data,
            'DAILY': daily_data
        }
        
        filename = f"copacol_youtube_data_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Dados salvos em {filename}")
        
        # Log resumo
        logger.info("📊 RESUMO DOS DADOS:")
        logger.info(f"💰 Budget Utilizado: R$ {total_spend:,.2f}")
        logger.info(f"📺 Impressões: {total_impressions:,}")
        logger.info(f"👆 Cliques: {total_clicks:,}")
        logger.info(f"🎬 Video Completions (100%): {total_q100:,}")
        logger.info(f"📈 CTR: {ctr:.2f}%")
        logger.info(f"📊 VTR: {vtr:.2f}%")
        logger.info(f"💰 CPV: R$ {cpv:.2f}")
        logger.info(f"💰 CPM: R$ {cpm:.2f}")
        logger.info(f"⏱️ Pacing: {(total_spend/21000.00)*100:.1f}%")
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair dados: {e}")
        return None

if __name__ == "__main__":
    extract_copacol_youtube_data()
