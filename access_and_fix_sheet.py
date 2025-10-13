#!/usr/bin/env python3
"""
Script para acessar e corrigir datas na planilha Google Sheets
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def access_google_sheet():
    """Acessar planilha Google Sheets diretamente"""
    
    # ID da planilha da campanha Semana do Pescado
    sheet_id = "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg"
    
    logger.info("🔍 Acessando planilha Google Sheets...")
    logger.info(f"📊 Sheet ID: {sheet_id}")
    
    try:
        # Tentar importar as bibliotecas do Google
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Configurar credenciais
        credentials_file = 'service-account-key.json'
        
        if not os.path.exists(credentials_file):
            logger.error(f"❌ Arquivo de credenciais não encontrado: {credentials_file}")
            return False
        
        # Carregar credenciais
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Construir serviço
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        logger.info("✅ Conexão com Google Sheets estabelecida")
        
        # Ler dados da aba Report
        range_name = "Report!A:Z"
        logger.info(f"📊 Lendo dados da aba: {range_name}")
        
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        logger.info(f"📊 Encontradas {len(values)} linhas na planilha")
        
        if not values:
            logger.error("❌ Nenhum dado encontrado na planilha")
            return False
        
        # Analisar primeira linha (cabeçalhos)
        headers = values[0]
        logger.info(f"📊 Cabeçalhos: {headers}")
        
        # Procurar coluna de data
        date_column_index = None
        for i, header in enumerate(headers):
            if 'date' in header.lower() or 'dia' in header.lower() or 'data' in header.lower():
                date_column_index = i
                break
        
        if date_column_index is None:
            logger.error("❌ Coluna de data não encontrada")
            return False
        
        logger.info(f"📊 Coluna de data encontrada no índice: {date_column_index}")
        logger.info(f"📊 Nome da coluna: {headers[date_column_index]}")
        
        # Analisar algumas datas para entender o formato
        logger.info("🔍 Analisando formato das datas...")
        
        sample_dates = []
        for i, row in enumerate(values[1:6]):  # Primeiras 5 linhas de dados
            if len(row) > date_column_index:
                date_value = row[date_column_index]
                sample_dates.append(date_value)
                logger.info(f"   Linha {i+2}: {date_value}")
        
        # Verificar se as datas estão no formato brasileiro (DD/MM/YYYY)
        logger.info("🔍 Verificando formato das datas...")
        
        # Se as datas estão no formato brasileiro, vamos convertê-las para o formato que a API espera
        # A API está interpretando DD/MM/YYYY como MM/DD/YYYY, então vamos corrigir isso
        
        # Primeiro, vamos ver quantas linhas temos de dados
        data_rows = values[1:]  # Excluir cabeçalho
        logger.info(f"📊 Total de linhas de dados: {len(data_rows)}")
        
        # Analisar o problema: a API está retornando apenas 11 dias
        # Vamos verificar se há mais dados na planilha
        logger.info("🔍 Verificando se há mais dados na planilha...")
        
        # Ler uma faixa maior para ter certeza
        extended_range = "Report!A1:Z100"
        extended_result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=extended_range
        ).execute()
        
        extended_values = extended_result.get('values', [])
        logger.info(f"📊 Faixa estendida tem {len(extended_values)} linhas")
        
        if len(extended_values) > len(values):
            logger.info(f"📊 Encontradas {len(extended_values) - len(values)} linhas adicionais!")
        
        # Agora vamos corrigir as datas
        logger.info("🔧 Iniciando correção das datas...")
        
        # Estratégia: vamos alterar as datas para o formato que a API está interpretando corretamente
        # Se a API está interpretando DD/MM/YYYY como MM/DD/YYYY, vamos inverter
        
        corrected_dates = []
        for i, row in enumerate(data_rows):
            if len(row) > date_column_index:
                original_date = row[date_column_index]
                
                # Tentar parsear a data original
                try:
                    # Se está no formato DD/MM/YYYY, vamos converter para MM/DD/YYYY
                    if '/' in original_date:
                        parts = original_date.split('/')
                        if len(parts) == 3:
                            day, month, year = parts
                            # Inverter dia e mês para que a API interprete corretamente
                            corrected_date = f"{month}/{day}/{year}"
                            corrected_dates.append((i + 2, original_date, corrected_date))
                            logger.info(f"   Linha {i + 2}: {original_date} → {corrected_date}")
                except Exception as e:
                    logger.warning(f"   Linha {i + 2}: Erro ao processar data {original_date}: {e}")
        
        logger.info(f"📊 {len(corrected_dates)} datas para corrigir")
        
        # Agora vamos aplicar as correções na planilha
        if corrected_dates:
            logger.info("🔧 Aplicando correções na planilha...")
            
            # Preparar dados para atualização
            updates = []
            for row_num, original, corrected in corrected_dates:
                # Criar range para a célula específica
                cell_range = f"Report!{chr(65 + date_column_index)}{row_num}"
                
                # Adicionar à lista de updates
                updates.append({
                    'range': cell_range,
                    'values': [[corrected]]
                })
            
            # Aplicar updates em lotes
            batch_update_request = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            # Executar atualização
            result = sheet.values().batchUpdate(
                spreadsheetId=sheet_id,
                body=batch_update_request
            ).execute()
            
            logger.info(f"✅ {len(updates)} datas corrigidas na planilha")
            logger.info("🎉 Correção concluída com sucesso!")
            
            return True
        else:
            logger.info("ℹ️ Nenhuma correção necessária")
            return True
            
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        logger.error("💡 Certifique-se de que as bibliotecas do Google estão instaladas")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao acessar planilha: {e}")
        return False

if __name__ == "__main__":
    success = access_google_sheet()
    if success:
        print("\n🎉 CORREÇÃO DA PLANILHA CONCLUÍDA!")
        print("📊 Agora teste a API de produção para verificar se os dados estão corretos")
    else:
        print("\n❌ ERRO NA CORREÇÃO DA PLANILHA")
        print("💡 Verifique as credenciais e permissões")

