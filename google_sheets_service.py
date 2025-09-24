#!/usr/bin/env python3
"""
Google Sheets Service - Integração real com Google Sheets API
Sem fallbacks, sem dados simulados - apenas dados reais
"""

import os
import json
from typing import Dict, List, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

class GoogleSheetsService:
    """Serviço para integração real com Google Sheets"""
    
    # Escopo necessário para acessar planilhas
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.is_configured_flag = False
        
        # Tentar inicializar o serviço
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar o serviço do Google Sheets"""
        try:
            # Verificar se estamos no Google Cloud Run
            if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                # Usar Service Account no Cloud Run
                self.service = build('sheets', 'v4')
                self.is_configured_flag = True
                print("✅ Google Sheets Service Account configurado (Cloud Run)")
                return
            
            # Verificar se temos credenciais OAuth
            if os.path.exists('credentials.json'):
                self.credentials = self._get_credentials()
                if self.credentials:
                    self.service = build('sheets', 'v4', credentials=self.credentials)
                    self.is_configured_flag = True
                    print("✅ Google Sheets OAuth configurado (Local)")
                    return
            
            print("❌ Google Sheets não configurado - credenciais não encontradas")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar Google Sheets: {e}")
    
    def _get_credentials(self):
        """Obter credenciais OAuth"""
        creds = None
        
        # Verificar se já temos token salvo
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # Se não temos credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima execução
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def is_configured(self) -> bool:
        """Verificar se o serviço está configurado"""
        return self.is_configured_flag and self.service is not None
    
    def test_connection(self) -> str:
        """Testar conexão com Google Sheets"""
        if not self.is_configured():
            return "not_configured"
        
        try:
            # Testar com uma planilha pública conhecida
            test_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=test_sheet_id,
                range="Class Data!A1:E1"
            ).execute()
            
            return "connected"
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return "error"
    
    def validate_sheet_access(self, sheet_id: str, gid: Optional[str] = None) -> bool:
        """Validar se podemos acessar uma planilha específica"""
        if not self.is_configured():
            return False
        
        try:
            # Tentar acessar a planilha
            result = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            return True
        except HttpError as e:
            if e.resp.status == 403:
                print(f"❌ Acesso negado à planilha {sheet_id}")
            elif e.resp.status == 404:
                print(f"❌ Planilha {sheet_id} não encontrada")
            else:
                print(f"❌ Erro ao acessar planilha {sheet_id}: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao validar planilha {sheet_id}: {e}")
            return False
    
    def read_sheet_data(self, sheet_id: str, sheet_name: str = None, gid: str = None) -> Optional[pd.DataFrame]:
        """Ler dados de uma planilha específica"""
        if not self.is_configured():
            raise Exception("Google Sheets não configurado")
        
        try:
            # Determinar o range
            if gid and sheet_name:
                range_name = f"{sheet_name}!A:Z"
            elif sheet_name:
                range_name = f"{sheet_name}!A:Z"
            else:
                range_name = "A:Z"
            
            # Fazer a requisição
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
            
            # Converter para DataFrame
            # Garantir que todas as linhas tenham o mesmo número de colunas
            max_cols = len(values[0]) if values else 0
            normalized_values = []
            
            for row in values:
                # Preencher com strings vazias se a linha tiver menos colunas
                while len(row) < max_cols:
                    row.append('')
                # Truncar se a linha tiver mais colunas
                if len(row) > max_cols:
                    row = row[:max_cols]
                normalized_values.append(row)
            
            df = pd.DataFrame(normalized_values[1:], columns=normalized_values[0])
            return df
            
        except HttpError as e:
            print(f"❌ Erro ao ler planilha {sheet_id}: {e}")
            raise
        except Exception as e:
            print(f"❌ Erro inesperado ao ler planilha {sheet_id}: {e}")
            raise
    
    def get_campaign_data(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Obter dados de uma campanha específica"""
        if not self.is_configured():
            raise Exception("Google Sheets não configurado")
        
        campaign_data = {
            "campaign_id": campaign.get("id"),
            "campaign_name": campaign.get("name"),
            "channels": {}
        }
        
        # Processar cada canal da campanha
        for channel in campaign.get("channels", []):
            channel_name = channel.get("name")
            sheet_id = channel.get("sheet_id")
            gid = channel.get("gid")
            
            try:
                # Ler dados da planilha
                df = self.read_sheet_data(sheet_id, gid=gid)
                if df is None:
                    raise Exception(f"Nenhum dado encontrado na planilha {sheet_id}")
                
                # Processar dados específicos do canal
                channel_data = self._process_channel_data(df, channel_name)
                campaign_data["channels"][channel_name] = channel_data
                
            except Exception as e:
                print(f"❌ Erro ao processar canal {channel_name}: {e}")
                raise Exception(f"Erro ao processar dados do canal {channel_name}: {e}")
        
        return campaign_data
    
    def _process_channel_data(self, df: pd.DataFrame, channel_name: str) -> Dict[str, Any]:
        """Processar dados específicos de um canal"""
        channel_name_lower = channel_name.lower()
        
        if 'youtube' in channel_name_lower:
            return self._process_youtube_data(df)
        elif 'programatica' in channel_name_lower and 'video' in channel_name_lower:
            return self._process_programmatic_video_data(df)
        elif 'programatica' in channel_name_lower and 'display' in channel_name_lower:
            return self._process_programmatic_display_data(df)
        else:
            raise Exception(f"Tipo de canal não suportado: {channel_name}")
    
    def _process_youtube_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processar dados do YouTube"""
        # Mapear colunas do YouTube
        column_mapping = {
            'Impressões': 'impressions',
            'Visualizações': 'views',
            'Cliques': 'clicks',
            'Gasto': 'spend',
            'CTR': 'ctr',
            'CPV': 'cpv',
            'Video assistido 100%': 'completion_100'
        }
        
        # Encontrar colunas na planilha
        available_columns = {}
        for col in df.columns:
            for key, value in column_mapping.items():
                if key.lower() in col.lower():
                    available_columns[value] = col
                    break
        
        # Calcular totais
        data = {}
        for metric, column in available_columns.items():
            if column in df.columns:
                # Converter para numérico, removendo caracteres não numéricos
                numeric_values = pd.to_numeric(df[column].astype(str).str.replace(r'[^\d.,]', '', regex=True).str.replace(',', '.'), errors='coerce')
                data[metric] = numeric_values.sum()
            else:
                data[metric] = 0
        
        # Calcular métricas derivadas
        if data.get('impressions', 0) > 0:
            data['ctr'] = (data.get('clicks', 0) / data['impressions']) * 100
            data['cpv'] = data.get('spend', 0) / data.get('views', 1)
        
        return data
    
    def _process_programmatic_video_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processar dados de Programática Video"""
        # Mapear colunas de Programática Video
        column_mapping = {
            'Impressões': 'impressions',
            'Cliques': 'clicks',
            'Gasto': 'spend',
            'CTR': 'ctr',
            'CPV': 'cpv',
            '100% Complete': 'completion_100'
        }
        
        # Encontrar colunas na planilha
        available_columns = {}
        for col in df.columns:
            for key, value in column_mapping.items():
                if key.lower() in col.lower():
                    available_columns[value] = col
                    break
        
        # Calcular totais
        data = {}
        for metric, column in available_columns.items():
            if column in df.columns:
                # Converter para numérico
                numeric_values = pd.to_numeric(df[column].astype(str).str.replace(r'[^\d.,]', '', regex=True).str.replace(',', '.'), errors='coerce')
                data[metric] = numeric_values.sum()
            else:
                data[metric] = 0
        
        # Calcular métricas derivadas
        if data.get('impressions', 0) > 0:
            data['ctr'] = (data.get('clicks', 0) / data['impressions']) * 100
            data['cpv'] = data.get('spend', 0) / data.get('completion_100', 1)
        
        return data
    
    def _process_programmatic_display_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processar dados de Programática Display"""
        # Similar ao video, mas com métricas específicas de display
        return self._process_programmatic_video_data(df)
