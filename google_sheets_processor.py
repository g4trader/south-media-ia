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
            import json
            
            # Se está no Cloud Run (variável de ambiente definida), usa service account
            if os.environ.get('GOOGLE_CREDENTIALS_FILE'):
                logger.info("🔐 Usando autenticação por Service Account (Cloud Run)")
                
                # No Cloud Run, GOOGLE_CREDENTIALS_FILE pode conter o JSON diretamente ou o caminho
                credentials_path = os.environ.get('GOOGLE_CREDENTIALS_FILE')
                
                # Verifica se é um JSON válido (começa com {)
                if credentials_path.strip().startswith('{'):
                    logger.info("📁 Credenciais em formato JSON detectadas")
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
                # Modo local - prioriza Application Default Credentials (gcloud)
                logger.info("🔐 Modo local: tentando usar Application Default Credentials (gcloud)")
                try:
                    from google.auth import default
                    creds, project = default(scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
                    logger.info("✅ Usando Application Default Credentials")
                except Exception as adc_error:
                    logger.warning(f"⚠️ Application Default Credentials não disponível: {adc_error}")
                    # Fallback: tenta usar arquivo de credenciais local
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(f"Arquivo de credenciais {self.credentials_file} não encontrado e Application Default Credentials não disponível")
                    
                    # Lê o arquivo para detectar o tipo
                    try:
                        with open(self.credentials_file, 'r') as f:
                            creds_data = json.load(f)
                        
                        # Verifica se é service account
                        if creds_data.get('type') == 'service_account':
                            logger.info("🔐 Usando autenticação por Service Account (arquivo local)")
                            creds = service_account.Credentials.from_service_account_file(
                                self.credentials_file,
                                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                            )
                        else:
                            # É OAuth client secrets
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
                                    flow = InstalledAppFlow.from_client_secrets_file(
                                        self.credentials_file, SCOPES)
                                    creds = flow.run_local_server(port=0)
                                
                                # Salva as credenciais para próxima execução
                                with open('token.pickle', 'wb') as token:
                                    pickle.dump(creds, token)
                    except json.JSONDecodeError:
                        # Se não é JSON válido, tenta OAuth
                        logger.info("🔐 Arquivo não é JSON válido, tentando OAuth")
                        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                        creds = None
                        
                        if os.path.exists('token.pickle'):
                            with open('token.pickle', 'rb') as token:
                                creds = pickle.load(token)
                        
                        if not creds or not creds.valid:
                            if creds and creds.expired and creds.refresh_token:
                                creds.refresh(Request())
                            else:
                                flow = InstalledAppFlow.from_client_secrets_file(
                                    self.credentials_file, SCOPES)
                                creds = flow.run_local_server(port=0)
                            
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
                # Log das primeiras 10 linhas para debug
                for i in range(min(10, len(values))):
                    if values[i]:
                        logger.info(f"🔍 Linha {i+1}: {values[i][:5]}")  # Primeiras 5 colunas
            
            # Procura pelo cabeçalho real (linha com nomes de colunas válidos)
            header_row = None
            data_start_row = None
            
            for i, row in enumerate(values):
                if row and len(row) > 0:
                    # Verifica se a linha contém palavras-chave de cabeçalho (independente da primeira coluna)
                    if (len(row) > 3 and  # Tem várias colunas
                        any('Video' in str(cell) or 'Creative' in str(cell) or 'Valor' in str(cell) or 
                            'Impressions' in str(cell) or 'Clicks' in str(cell) or 'Day' in str(cell) 
                            for cell in row[:8])):  # Contém palavras-chave de cabeçalho
                        # Verifica se não é uma linha de dados (não começa com data)
                        first_cell = str(row[0]).strip() if row[0] else ''
                        if not (first_cell and first_cell.replace('/', '').replace('-', '').replace(' ', '').isdigit()):
                            header_row = i
                            data_start_row = i + 1
                            logger.info(f"🔧 Cabeçalho encontrado na linha {i + 1}: {row[:5]}")
                            break
            
            if header_row is not None:
                # Usa o cabeçalho encontrado, mas alinha número de colunas entre header e dados.
                # Algumas planilhas (ex: Netflix) podem ter colunas extras em linhas de dados.
                header = list(values[header_row])
                data_rows = values[data_start_row:]

                # Descobrir o maior número de colunas observado
                max_cols = max(
                    len(header),
                    max((len(r) for r in data_rows if r), default=0)
                )

                # Ajustar header para max_cols
                if len(header) < max_cols:
                    header = header + [f"Coluna_Extra_{i}" for i in range(len(header), max_cols)]
                elif len(header) > max_cols:
                    header = header[:max_cols]

                # Ajustar cada linha de dados para max_cols
                aligned_data = []
                for r in data_rows:
                    if not r:
                        continue
                    row = list(r)
                    if len(row) < max_cols:
                        row = row + [''] * (max_cols - len(row))
                    else:
                        row = row[:max_cols]
                    aligned_data.append(row)

                df = pd.DataFrame(aligned_data, columns=header)
                logger.info(f"✅ Usando linha {header_row + 1} como cabeçalho (alinhado: {len(header)} colunas)")
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
            
            # Tratamento especial para Footfall Data (dados geográficos estáticos)
            if channel_name == "Footfall Data":
                for _, row in df.iterrows():
                    try:
                        # Processa dados geográficos
                        lat = self.parse_number(row.get(columns['lat'], 0))
                        lon = self.parse_number(row.get(columns['lon'], 0))
                        proximity = self.parse_number(row.get(columns['proximity'], 0))
                        name = str(row.get(columns['name'], ''))
                        users = self.parse_number(row.get(columns['users'], 0))
                        rate = self.parse_number(row.get(columns['rate'], 0))
                        
                        if not name or users == 0:
                            logger.warning(f"⚠️ Pulando linha Footfall: name='{name}', users={users}")
                            continue
                        
                        daily_data.append({
                            'lat': lat,
                            'lon': lon,
                            'proximity': proximity,
                            'name': name,
                            'users': users,
                            'rate': rate
                        })
                    except Exception as e:
                        logger.error(f"⚠️ Erro ao processar linha do Footfall Data: {e}")
                        continue
                
                logger.info(f"✅ {len(daily_data)} registros processados para {channel_name}")
                return daily_data
            
            # Detecção automática de data se a coluna date não estiver configurada
            date_column = None
            configured_date_col = columns.get('date', '').strip()
            
            if not configured_date_col:
                # Tenta encontrar coluna de data automaticamente
                for col in df.columns:
                    col_str = str(col).strip()
                    # Verifica se a coluna parece ser uma data (primeira coluna ou contém palavras-chave)
                    if col_str == '' or col_str.lower() in ['date', 'day', 'dia', 'data']:
                        date_column = col
                        logger.info(f"🔍 Coluna de data detectada automaticamente: '{col}' (índice {list(df.columns).index(col)})")
                        break
                # Se não encontrou, usa a primeira coluna
                if date_column is None and len(df.columns) > 0:
                    date_column = df.columns[0]
                    logger.info(f"🔍 Usando primeira coluna como data: '{date_column}'")
            else:
                # Tenta usar a coluna configurada
                if configured_date_col in df.columns:
                    date_column = configured_date_col
                    logger.info(f"🔍 Usando coluna de data configurada: '{date_column}'")
                else:
                    # Se a coluna configurada não existe, tenta detectar automaticamente
                    logger.warning(f"⚠️ Coluna de data configurada '{configured_date_col}' não encontrada. Tentando detecção automática...")
                    for col in df.columns:
                        col_str = str(col).strip()
                        if col_str.lower() in ['date', 'day', 'dia', 'data']:
                            date_column = col
                            logger.info(f"🔍 Coluna de data detectada automaticamente: '{col}'")
                            break
                    # Se ainda não encontrou, usa a primeira coluna
                    if date_column is None and len(df.columns) > 0:
                        date_column = df.columns[0]
                        logger.info(f"🔍 Usando primeira coluna como data: '{date_column}'")
            
            # Detecção automática de TrueViews ou Video Starts para YouTube
            starts_column = None
            q25_col = None
            q50_col = None
            q75_col = None
            q100_col = None
            
            if channel_name == "YouTube":
                # Verifica se existe TrueViews (prioridade para True View)
                for col in df.columns:
                    col_str = str(col).strip()
                    if col_str.lower() == 'trueviews':
                        starts_column = col
                        logger.info(f"🔍 TrueViews detectado para YouTube: '{col}'")
                        break
                
                # Se não encontrou TrueViews, tenta Video Starts ou Starts (Video)
                if starts_column is None:
                    for col in df.columns:
                        col_str = str(col).strip().lower()
                        if 'starts' in col_str or 'video starts' in col_str:
                            starts_column = col
                            logger.info(f"🔍 Video Starts detectado para YouTube: '{col}'")
                            break
                
                # Se ainda não encontrou, usa a coluna configurada
                if starts_column is None and columns.get('starts'):
                    starts_column = columns['starts']
                    logger.info(f"🔍 Usando coluna configurada para starts: '{starts_column}'")
                
                # Detecção automática de colunas de quartis para YouTube (True View)
                # Primeiro tenta usar as colunas configuradas
                q25_col = columns.get('q25', '')
                q50_col = columns.get('q50', '')
                q75_col = columns.get('q75', '')
                q100_col = columns.get('q100', '')
                
                # Se não encontrou as colunas configuradas, tenta detectar automaticamente
                # Suporta múltiplos formatos: "25% Video Complete", "First-Quartile Views (Video)", etc.
                if not q25_col or q25_col not in df.columns:
                    for col in df.columns:
                        col_str = str(col).strip().lower()
                        if ('25%' in col_str or 'first-quartile' in col_str or 'first quartile' in col_str) and \
                           ('video' in col_str or 'complete' in col_str or 'views' in col_str):
                            q25_col = col
                            logger.info(f"🔍 Coluna Q25 detectada automaticamente: '{col}'")
                            break
                
                if not q50_col or q50_col not in df.columns:
                    for col in df.columns:
                        col_str = str(col).strip().lower()
                        if ('50%' in col_str or 'midpoint' in col_str or 'mid point' in col_str) and \
                           ('video' in col_str or 'complete' in col_str or 'views' in col_str):
                            q50_col = col
                            logger.info(f"🔍 Coluna Q50 detectada automaticamente: '{col}'")
                            break
                
                if not q75_col or q75_col not in df.columns:
                    for col in df.columns:
                        col_str = str(col).strip().lower()
                        if ('75%' in col_str or 'third-quartile' in col_str or 'third quartile' in col_str) and \
                           ('video' in col_str or 'complete' in col_str or 'views' in col_str):
                            q75_col = col
                            logger.info(f"🔍 Coluna Q75 detectada automaticamente: '{col}'")
                            break
                
                if not q100_col or q100_col not in df.columns:
                    for col in df.columns:
                        col_str = str(col).strip().lower()
                        if ('100%' in col_str or 'complete views' in col_str or 'complete' in col_str) and \
                           ('video' in col_str or 'views' in col_str or 'complete' in col_str):
                            q100_col = col
                            logger.info(f"🔍 Coluna Q100 detectada automaticamente: '{col}'")
                            break
            else:
                # Para outros canais, usa as colunas configuradas
                q25_col = columns.get('q25', '')
                q50_col = columns.get('q50', '')
                q75_col = columns.get('q75', '')
                q100_col = columns.get('q100', '')
            
            skipped_count = 0
            skip_reasons = {}
            
            for idx, row in df.iterrows():
                try:
                    # Processa data
                    date_str = str(row.get(date_column, ''))
                    if not date_str or date_str == 'nan' or date_str.strip() == '':
                        skipped_count += 1
                        reason = "Data vazia"
                        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                        continue
                    
                    formatted_date = self.format_date(date_str)
                    
                    if not formatted_date:
                        skipped_count += 1
                        reason = f"Data inválida: '{date_str}'"
                        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                        if idx < 3:  # Log apenas as primeiras 3 para não poluir
                            logger.warning(f"⚠️ Linha {idx + 1}: Data não formatada: '{date_str}'")
                        continue
                    
                    # Processa valor investido (detecção automática se não configurado)
                    spend_key = columns.get('spend', '')
                    if not spend_key or spend_key not in df.columns:
                        # Tenta detectar automaticamente
                        for col in df.columns:
                            col_str = str(col).strip().lower()
                            if 'valor investido' in col_str or 'spend' in col_str or 'investido' in col_str:
                                spend_key = col
                                break
                    spend_str = str(row.get(spend_key, '0')) if spend_key else '0'
                    spend = self.parse_currency(spend_str)
                    
                    # Processa outros campos (detecção automática de creative)
                    creative_key = columns.get('creative', '')
                    if not creative_key or creative_key not in df.columns:
                        # Tenta detectar automaticamente
                        for col in df.columns:
                            col_str = str(col).strip().lower()
                            if 'creative' in col_str or 'criativo' in col_str:
                                creative_key = col
                                break
                    creative = str(row.get(creative_key, '')) if creative_key else ''
                    
                    # Impressions e clicks podem não existir em alguns canais (ex: Netflix)
                    impressions_key = columns.get('impressions', '')
                    if impressions_key and impressions_key not in df.columns:
                        # Tenta detectar automaticamente
                        for col in df.columns:
                            col_str = str(col).strip().lower()
                            if 'impressions' in col_str or 'imps' in col_str:
                                impressions_key = col
                                break
                    impressions = self.parse_number(row.get(impressions_key, 0)) if impressions_key else 0
                    
                    clicks_key = columns.get('clicks', '')
                    if clicks_key and clicks_key not in df.columns:
                        # Tenta detectar automaticamente
                        for col in df.columns:
                            col_str = str(col).strip().lower()
                            if 'clicks' in col_str:
                                clicks_key = col
                                break
                    clicks = self.parse_number(row.get(clicks_key, 0)) if clicks_key else 0
                    
                    visits_key = columns.get('visits', '')
                    visits = str(row.get(visits_key, '')) if visits_key else ''
                    
                    # Processa campos específicos do YouTube e Netflix
                    # Para YouTube, usa TrueViews se disponível, senão usa Video Starts
                    if channel_name == "YouTube" and starts_column:
                        starts = self.parse_number(row.get(starts_column, 0))
                    else:
                        starts = self.parse_number(row.get(columns.get('starts', ''), 0))
                    
                    # Usa as colunas de quartis detectadas (já foram detectadas antes do loop)
                    q25 = self.parse_number(row.get(q25_col, 0)) if q25_col else 0
                    q50 = self.parse_number(row.get(q50_col, 0)) if q50_col else 0
                    q75 = self.parse_number(row.get(q75_col, 0)) if q75_col else 0
                    q100 = self.parse_number(row.get(q100_col, 0)) if q100_col else 0
                    
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
                    skipped_count += 1
                    reason = f"Erro: {str(e)[:50]}"
                    skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                    logger.warning(f"⚠️ Erro ao processar linha {idx + 1} do {channel_name}: {e}")
                    continue
            
            # Log de resumo
            if skipped_count > 0:
                logger.warning(f"⚠️ {skipped_count} linhas puladas para {channel_name} / Motivos: {skip_reasons}")
            
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
            
            # Se tem vírgula e ponto, assume formato brasileiro (1.234,56 ou 1.234,5678)
            if ',' in clean_str and '.' in clean_str:
                # Formato brasileiro: ponto para milhares, vírgula para decimais
                clean_str = clean_str.replace('.', '').replace(',', '.')
            elif ',' in clean_str and '.' not in clean_str:
                # Se só tem vírgula, verificar se é decimal brasileiro
                parts = clean_str.split(',')
                if len(parts) == 2:
                    decimal_part = parts[1]
                    # Se a parte decimal tem até 4 dígitos, é decimal brasileiro
                    # (alguns valores podem ter mais de 2 casas decimais na planilha)
                    if len(decimal_part) <= 4:
                        clean_str = clean_str.replace(',', '.')
                    else:
                        # Mais de 4 dígitos após vírgula provavelmente é separador de milhares
                        clean_str = clean_str.replace(',', '')
                else:
                    # Múltiplas vírgulas ou sem parte decimal clara
                    clean_str = clean_str.replace(',', '')
            
            result = float(clean_str)
            
            # Validação: se o resultado for muito grande (mais de 10 milhões), 
            # provavelmente houve erro de parsing
            if result > 10000000:
                logger.warning(f"⚠️ Valor monetário suspeitamente alto: {value_str} -> {result}")
                # Tentar novamente assumindo formato brasileiro com vírgula decimal
                if ',' in str(value_str) and '.' not in str(value_str):
                    parts = str(value_str).replace('R$', '').replace(' ', '').strip().split(',')
                    if len(parts) == 2:
                        result = float(parts[0].replace('.', '') + '.' + parts[1])
            
            return result
            
        except (ValueError, AttributeError, IndexError) as e:
            logger.warning(f"⚠️ Erro ao converter valor monetário: {value_str} - {e}")
            return 0.0
    
    def parse_number(self, value):
        """Converte string numérica para int"""
        try:
            if not value or str(value).lower() in ['nan', 'none', '']:
                return 0
            
            clean_str = str(value).strip()
            
            # Se tem vírgula e ponto, assume formato brasileiro (1.234,56)
            # Para números inteiros, precisamos remover a parte decimal
            if ',' in clean_str and '.' in clean_str:
                # Formato brasileiro: ponto para milhares, vírgula para decimais
                # Para inteiros, usar apenas a parte inteira antes da vírgula
                clean_str = clean_str.replace('.', '').split(',')[0]
            elif ',' in clean_str and '.' not in clean_str:
                # Se só tem vírgula, pode ser decimal brasileiro
                parts = clean_str.split(',')
                if len(parts) == 2:
                    decimal_part = parts[1]
                    # Se a parte decimal tem até 4 dígitos, é decimal brasileiro
                    # Para inteiros, usar apenas a parte inteira
                    if len(decimal_part) <= 4:
                        clean_str = parts[0]
                    else:
                        # Mais de 4 dígitos provavelmente é separador de milhares
                        clean_str = clean_str.replace(',', '')
                else:
                    # Múltiplas vírgulas - usar apenas primeira parte
                    clean_str = parts[0] if parts else clean_str.replace(',', '')
            else:
                # Remover pontos de milhares se houver
                if '.' in clean_str:
                    # Verificar se é formato numérico com pontos de milhares
                    parts = clean_str.split('.')
                    # Se a última parte tem mais de 3 dígitos, provavelmente não é separador de milhares
                    if len(parts) > 1 and len(parts[-1]) <= 3:
                        clean_str = clean_str.replace('.', '')
            
            return int(float(clean_str))
            
        except (ValueError, AttributeError, IndexError) as e:
            logger.warning(f"⚠️ Erro ao converter número: {value} - {e}")
            return 0
    
    def get_all_channels_data(self):
        """Obtém dados de todos os canais"""
        logger.info("🚀 Iniciando coleta de dados de todos os canais...")
        
        all_daily_data = []
        successful_channels = 0
        failed_channels = []
        
        for channel_name, channel_config in GOOGLE_SHEETS_CONFIG.items():
            try:
                # Verificar se sheet_id está configurado
                sheet_id = channel_config.get('sheet_id', '').strip()
                if not sheet_id:
                    logger.warning(f"⚠️ Canal {channel_name} não tem sheet_id configurado, pulando...")
                    failed_channels.append(f"{channel_name} (sem sheet_id)")
                    continue
                
                logger.info(f"📊 Processando canal: {channel_name} (sheet_id: {sheet_id[:20]}...)")
                channel_data = self.process_channel_data(channel_name, channel_config)
                
                if channel_data:
                    all_daily_data.extend(channel_data)
                    successful_channels += 1
                    logger.info(f"✅ Canal {channel_name}: {len(channel_data)} registros coletados")
                else:
                    logger.warning(f"⚠️ Canal {channel_name}: nenhum dado coletado")
                    failed_channels.append(f"{channel_name} (sem dados)")
                    
            except Exception as e:
                logger.error(f"❌ Erro no canal {channel_name}: {e}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                failed_channels.append(f"{channel_name} (erro: {str(e)[:50]})")
                continue
        
        logger.info(f"✅ Coleta concluída: {successful_channels}/{len(GOOGLE_SHEETS_CONFIG)} canais processados com sucesso")
        if failed_channels:
            logger.warning(f"⚠️ Canais com problemas: {', '.join(failed_channels)}")
        logger.info(f"📊 Total de registros coletados: {len(all_daily_data)}")
        
        return all_daily_data

    def validate_sheet_access(self, sheet_id, gid=None):
        """Validar se podemos acessar uma planilha específica"""
        try:
            if not self.service:
                logger.error("❌ Serviço Google Sheets não inicializado")
                return False
            
            # Tentar acessar a planilha
            result = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            logger.info(f"✅ Acesso validado para planilha {sheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar acesso à planilha {sheet_id}: {e}")
            return False

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
