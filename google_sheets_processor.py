#!/usr/bin/env python3
"""
Processador de dados do Google Sheets para automação do dashboard
"""

import pandas as pd
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime
import logging
from config import GOOGLE_SHEETS_CONFIG

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleSheetsProcessor:
    """Classe para processar dados do Google Sheets"""
    
    def __init__(self, credentials_file=None):
        # No Cloud Run, usa a variável de ambiente, senão usa o arquivo local
        if credentials_file is None:
            self.credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        else:
            self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Autentica com a API do Google Sheets"""
        try:
            from google.oauth2 import service_account
            
            # Se está no Cloud Run (variável de ambiente definida), usa service account
            if os.environ.get('GOOGLE_CREDENTIALS_FILE'):
                logger.info("🔐 Usando autenticação por Service Account (Cloud Run)")
                
                # No Cloud Run, GOOGLE_CREDENTIALS_FILE pode conter o JSON diretamente ou o caminho
                credentials_path = os.environ.get('GOOGLE_CREDENTIALS_FILE')
                
                # Verifica se é um JSON válido (começa com {)
                if credentials_path.strip().startswith('{'):
                    logger.info("📁 Credenciais em formato JSON detectadas")
                    import json
                    credentials_dict = json.loads(credentials_path)
                    creds = service_account.Credentials.from_service_account_info(
                        credentials_dict,
                        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                    )
                else:
                    logger.info(f"📁 Caminho das credenciais: {credentials_path}")
                    # Carrega as credenciais do arquivo montado pelo secret
                    creds = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                    )
            else:
                # Modo local - usa OAuth flow
                logger.info("🔐 Usando autenticação OAuth (modo local)")
                SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                creds = None
                
                # Verifica se já existe token salvo
                if os.path.exists('token.pickle'):
                    with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                
                # Se não há credenciais válidas, faz login
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        if not os.path.exists(self.credentials_file):
                            raise FileNotFoundError(f"Arquivo de credenciais {self.credentials_file} não encontrado")
                        
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # Salva as credenciais para próxima execução
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
            
            self.service = build('sheets', 'v4', credentials=creds)
            logger.info("✅ Autenticação com Google Sheets realizada com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            raise
    
    def get_sheet_name_by_gid(self, sheet_id, gid):
        """Converte GID para nome da aba"""
        try:
            # Obter metadados da planilha
            metadata = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheets = metadata.get('sheets', [])
            
            # Procurar pela aba com o GID correspondente
            for sheet in sheets:
                if str(sheet['properties']['sheetId']) == str(gid):
                    return sheet['properties']['title']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar nome da aba por GID {gid}: {e}")
            return None
    
    def read_sheet_data(self, sheet_id, sheet_name=None, gid=None, range_name=None):
        """Lê dados de uma planilha específica"""
        try:
            # Se tem GID, precisa converter para nome da aba primeiro
            if gid:
                sheet_name = self.get_sheet_name_by_gid(sheet_id, gid)
                if not sheet_name:
                    logger.warning(f"⚠️ Não foi possível encontrar aba com GID {gid}")
                    return None
                range_name = f"'{sheet_name}'!A:Z"
            elif not range_name:
                range_name = f"'{sheet_name}'!A:Z" if sheet_name else "A:Z"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning(f"⚠️ Nenhum dado encontrado na planilha {sheet_name or gid}")
                return pd.DataFrame()
            
            # Log dos dados brutos para debug
            logger.info(f"🔍 Dados brutos - {len(values)} linhas encontradas")
            if len(values) > 0:
                logger.info(f"🔍 Cabeçalho: {values[0]}")
                logger.info(f"🔍 Primeira linha de dados: {values[1] if len(values) > 1 else 'Nenhuma'}")
            
            # Procura pelo cabeçalho real (linha com nomes de colunas válidos)
            header_row = None
            data_start_row = None
            
            for i, row in enumerate(values):
                if row and len(row) > 0 and row[0]:
                    # Verifica se a primeira coluna parece ser um cabeçalho (não é data)
                    first_cell = str(row[0]).strip()
                    if (first_cell and 
                        not first_cell.replace('/', '').replace('-', '').replace(' ', '').isdigit() and  # Não é data
                        len(row) > 3 and  # Tem várias colunas
                        any('Video' in str(cell) or 'Creative' in str(cell) or 'Valor' in str(cell) for cell in row[:5])):  # Contém palavras-chave de cabeçalho
                        header_row = i
                        data_start_row = i + 1
                        logger.info(f"🔧 Cabeçalho encontrado na linha {i + 1}: {row[:5]}")
                        break
            
            if header_row is not None:
                # Usa o cabeçalho encontrado
                df = pd.DataFrame(values[data_start_row:], columns=values[header_row])
                logger.info(f"✅ Usando linha {header_row + 1} como cabeçalho")
            else:
                # Fallback: tenta usar primeira linha como cabeçalho normalmente
                if len(values) > 0 and values[0]:
                    df = pd.DataFrame(values[1:], columns=values[0])
                    logger.info("✅ Usando primeira linha como cabeçalho (fallback)")
                else:
                    logger.warning("⚠️ Não foi possível encontrar cabeçalho válido")
                    return pd.DataFrame()
            logger.info(f"✅ {len(df)} registros lidos da planilha {sheet_name or gid}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler planilha {sheet_name or gid}: {e}")
            return pd.DataFrame()
    
    def process_channel_data(self, channel_name, channel_config):
        """Processa dados de um canal específico"""
        try:
            logger.info(f"📊 Processando dados do canal: {channel_name}")
            logger.info(f"🔍 Configuração: {channel_config}")
            
            # Lê dados da planilha
            df = self.read_sheet_data(
                channel_config['sheet_id'],
                sheet_name=channel_config.get('sheet_name'),
                gid=channel_config.get('gid')
            )
            
            if df.empty:
                logger.warning(f"⚠️ Nenhum dado encontrado para {channel_name}")
                return []
            
            logger.info(f"📋 Colunas encontradas: {list(df.columns)}")
            logger.info(f"📊 {len(df)} linhas encontradas")
            logger.info(f"🔍 Primeiras 3 linhas: {df.head(3).to_dict()}")
            
            # Mapeia colunas
            columns = channel_config['columns']
            daily_data = []
            
            for _, row in df.iterrows():
                try:
                    # Processa data
                    date_str = str(row.get(columns['date'], ''))
                    formatted_date = self.format_date(date_str)
                    
                    if not formatted_date:
                        continue
                    
                    # Processa valor investido
                    spend_str = str(row.get(columns['spend'], '0'))
                    spend = self.parse_currency(spend_str)
                    
                    # Processa outros campos
                    creative = str(row.get(columns['creative'], ''))
                    impressions = self.parse_number(row.get(columns['impressions'], 0))
                    clicks = self.parse_number(row.get(columns['clicks'], 0))
                    visits = str(row.get(columns['visits'], ''))
                    
                    # Processa campos específicos do YouTube e Netflix
                    starts = self.parse_number(row.get(columns.get('starts', ''), 0))
                    q25 = self.parse_number(row.get(columns.get('q25', ''), 0))
                    q50 = self.parse_number(row.get(columns.get('q50', ''), 0))
                    q75 = self.parse_number(row.get(columns.get('q75', ''), 0))
                    q100 = self.parse_number(row.get(columns.get('q100', ''), 0))
                    
                    # Cria registro
                    record = {
                        'date': formatted_date,
                        'channel': channel_name,
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
                    logger.warning(f"⚠️ Erro ao processar linha do {channel_name}: {e}")
                    continue
            
            logger.info(f"✅ {len(daily_data)} registros processados para {channel_name}")
            return daily_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar canal {channel_name}: {e}")
            return []
    
    def format_date(self, date_str):
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
            
            logger.warning(f"⚠️ Formato de data não reconhecido: {date_str}")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao formatar data {date_str}: {e}")
            return None
    
    def parse_currency(self, value_str):
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
            logger.warning(f"⚠️ Erro ao converter valor monetário: {value_str}")
            return 0.0
    
    def parse_number(self, value):
        """Converte string numérica para int"""
        try:
            if not value or str(value).lower() in ['nan', 'none', '']:
                return 0
            
            # Remove caracteres não numéricos
            clean_str = str(value).replace(',', '').replace('.', '').strip()
            return int(float(clean_str))
            
        except (ValueError, AttributeError):
            logger.warning(f"⚠️ Erro ao converter número: {value}")
            return 0
    
    def get_all_channels_data(self):
        """Obtém dados de todos os canais"""
        logger.info("🚀 Iniciando coleta de dados de todos os canais...")
        
        all_daily_data = []
        successful_channels = 0
        
        for channel_name, channel_config in GOOGLE_SHEETS_CONFIG.items():
            try:
                channel_data = self.process_channel_data(channel_name, channel_config)
                all_daily_data.extend(channel_data)
                
                if channel_data:
                    successful_channels += 1
                    
            except Exception as e:
                logger.error(f"❌ Erro no canal {channel_name}: {e}")
                continue
        
        logger.info(f"✅ Coleta concluída: {successful_channels}/{len(GOOGLE_SHEETS_CONFIG)} canais processados")
        logger.info(f"📊 Total de registros coletados: {len(all_daily_data)}")
        
        return all_daily_data

def test_connection():
    """Testa conexão com Google Sheets"""
    try:
        processor = GoogleSheetsProcessor()
        
        # Testa com um canal
        test_channel = list(GOOGLE_SHEETS_CONFIG.keys())[0]
        test_config = GOOGLE_SHEETS_CONFIG[test_channel]
        
        logger.info(f"🧪 Testando conexão com canal: {test_channel}")
        
        df = processor.read_sheet_data(
            test_config['sheet_id'],
            test_config['sheet_name']
        )
        
        if not df.empty:
            logger.info(f"✅ Teste bem-sucedido! {len(df)} linhas encontradas")
            logger.info(f"📋 Colunas: {list(df.columns)}")
            return True
        else:
            logger.warning("⚠️ Nenhum dado encontrado no teste")
            return False
            
    except Exception as e:
        logger.error(f"❌ Teste de conexão falhou: {e}")
        return False

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Testar conexão
    if test_connection():
        logger.info("🎉 Conexão com Google Sheets funcionando!")
    else:
        logger.error("❌ Problemas na conexão com Google Sheets")
