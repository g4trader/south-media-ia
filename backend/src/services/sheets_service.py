"""
Serviço para integração com Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class SheetsService:
    """Serviço para operações com Google Sheets"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        
        # Configuração das planilhas por canal (IDs reais)
        self.sheets_config = {
            "CTV": {
                "spreadsheet_id": os.getenv("CTV_SPREADSHEET_ID", "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U"),
                "sheet_name": "Entrega Diária",
                "gid": None,
                "url": "https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit"
            },
            "Disney": {
                "spreadsheet_id": os.getenv("DISNEY_SPREADSHEET_ID", "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o"),
                "sheet_name": "Entrega Diária",
                "gid": None,
                "url": "https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit"
            },
            "Footfall Display": {
                "spreadsheet_id": os.getenv("FOOTFALL_DISPLAY_SPREADSHEET_ID", "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA"),
                "sheet_name": "Entrega Diária",
                "gid": "1743413064",
                "url": "https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064"
            },
            "Netflix": {
                "spreadsheet_id": os.getenv("NETFLIX_SPREADSHEET_ID", "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo"),
                "sheet_name": "Entrega Diária",
                "gid": None,
                "url": "https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit"
            },
            "TikTok": {
                "spreadsheet_id": os.getenv("TIKTOK_SPREADSHEET_ID", "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM"),
                "sheet_name": "Entrega Diária",
                "gid": None,
                "url": "https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true"
            },
            "YouTube": {
                "spreadsheet_id": os.getenv("YOUTUBE_SPREADSHEET_ID", "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo"),
                "sheet_name": "Entrega Diária",
                "gid": "1863167182",
                "url": "https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182"
            }
        }
    
    def _initialize_client(self):
        """Inicializa o cliente do Google Sheets"""
        try:
            # Caminho para o arquivo de credenciais
            credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
            
            if not os.path.exists(credentials_path):
                logger.warning(f"Arquivo de credenciais não encontrado: {credentials_path}")
                return
            
            # Definir escopos necessários
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            # Carregar credenciais
            credentials = Credentials.from_service_account_file(
                credentials_path, 
                scopes=scopes
            )
            
            # Inicializar cliente
            self.client = gspread.authorize(credentials)
            logger.info("Cliente Google Sheets inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Google Sheets: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.client is not None
    
    def get_sheet_data(self, channel: str) -> Optional[List[Dict[str, Any]]]:
        """Obtém dados de uma planilha específica"""
        if not self.is_available():
            logger.error("Cliente Google Sheets não disponível")
            return None
        
        config = self.sheets_config.get(channel)
        if not config:
            logger.error(f"Configuração não encontrada para o canal: {channel}")
            return None
        
        try:
            # Abrir planilha
            spreadsheet = self.client.open_by_key(config["spreadsheet_id"])
            worksheet = spreadsheet.worksheet(config["sheet_name"])
            
            # Obter dados
            data = worksheet.get_all_records()
            
            logger.info(f"Dados obtidos do canal {channel}: {len(data)} registros")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do canal {channel}: {e}")
            return None
    
    def process_channel_data(self, channel: str) -> List[Dict[str, Any]]:
        """Processa dados de um canal específico com mapeamento correto"""
        raw_data = self.get_sheet_data(channel)
        if not raw_data:
            return []
        
        processed_data = []
        
        for row in raw_data:
            try:
                # Mapear dados baseado na estrutura específica do canal
                mapped_data = self._map_channel_specific_data(channel, row)
                
                if mapped_data and self._safe_spend_validation(mapped_data.get("spend")):
                    processed_data.append(mapped_data)
                
            except Exception as e:
                logger.error(f"Erro ao processar linha do canal {channel}: {e}")
                continue
        
        logger.info(f"Processados {len(processed_data)} registros para o canal {channel}")
        return processed_data
    
    def _map_channel_specific_data(self, channel: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia dados brutos para estrutura padrão baseado no canal"""
        
        base_record = {
            "date": None,
            "channel": channel,
            "creative": "",
            "spend": 0,
            "starts": None,
            "q25": None,
            "q50": None,
            "q75": None,
            "q100": None,
            "impressions": None,
            "clicks": None,
            "visits": None
        }
        
        if channel == "CTV":
            # Estrutura: Data, Creative, Starts, Skips, Q25, Q50, Q75, Q100, Active Views, Valor investido
            base_record.update({
                "date": str(row.get("Data") or row.get("Date") or ""),
                "creative": str(row.get("Creative") or ""),
                "starts": self._safe_float(row.get("Starts (Video)") or row.get("Starts")),
                "q25": self._safe_float(row.get("First-Quartile Views (Video)") or row.get("Q25")),
                "q50": self._safe_float(row.get("Midpoint Views (Video)") or row.get("Q50")),
                "q75": self._safe_float(row.get("Third-Quartile Views (Video)") or row.get("Q75")),
                "q100": self._safe_float(row.get("Complete Views (Video)") or row.get("Q100")),
                "spend": self._safe_float(row.get("Valor investido") or row.get("Spend"))
            })
        
        elif channel in ["Disney", "Netflix"]:
            # Estrutura: Day, Completion Rate, Q25, Q50, Q75, Q100, Starts, Valor investido, Criativo
            base_record.update({
                "date": str(row.get("Day") or row.get("Date") or ""),
                "creative": str(row.get("Criativo") or row.get("Creative") or ""),
                "starts": self._safe_float(row.get("Video Starts") or row.get("Starts")),
                "q25": self._safe_float(row.get("25% Video Complete") or row.get("Q25")),
                "q50": self._safe_float(row.get("50% Video Complete") or row.get("Q50")),
                "q75": self._safe_float(row.get("75% Video Complete") or row.get("Q75")),
                "q100": self._safe_float(row.get("100% Complete") or row.get("Q100")),
                "spend": self._safe_float(row.get("Valor investido") or row.get("Spend"))
            })
        
        elif channel == "TikTok":
            # Estrutura: Ad name, By Day, Valor Investido, CPC, CPM, Impressions, Clicks, CTR
            base_record.update({
                "date": str(row.get("By Day") or row.get("Date") or ""),
                "creative": str(row.get("Ad name") or row.get("Creative") or ""),
                "spend": self._safe_float(row.get("Valor Investido") or row.get("Spend")),
                "impressions": self._safe_float(row.get("Impressions")),
                "clicks": self._safe_float(row.get("Clicks"))
            })
        
        elif channel == "YouTube":
            # Estrutura: Date, Starts, Q25, Q50, Q75, Q100, Active Views, criativo, Valor investido
            base_record.update({
                "date": str(row.get("Date") or ""),
                "creative": str(row.get("criativo") or row.get("Creative") or ""),
                "starts": self._safe_float(row.get("Starts (Video)") or row.get("Starts")),
                "q25": self._safe_float(row.get("First-Quartile Views (Video)") or row.get("Q25")),
                "q50": self._safe_float(row.get("Midpoint Views (Video)") or row.get("Q50")),
                "q75": self._safe_float(row.get("Third-Quartile Views (Video)") or row.get("Q75")),
                "q100": self._safe_float(row.get("Complete Views (Video)") or row.get("Q100")),
                "spend": self._safe_float(row.get("Valor investido") or row.get("Spend"))
            })
        
        elif channel == "Footfall Display":
            # Estrutura: Date, Creative, Impressions, Clicks, CTR, VALOR DO INVESTIMENTO, CPM
            base_record.update({
                "date": str(row.get("Date") or ""),
                "creative": str(row.get("Creative") or ""),
                "impressions": self._safe_float(row.get("Impressions")),
                "clicks": self._safe_float(row.get("Clicks")),
                "spend": self._safe_float(row.get("VALOR DO INVESTIMENTO") or row.get("Spend"))
            })
        
        return base_record
    
    def get_all_channels_data(self) -> List[Dict[str, Any]]:
        """Obtém dados de todos os canais"""
        all_data = []
        
        for channel in self.sheets_config.keys():
            try:
                channel_data = self.process_channel_data(channel)
                all_data.extend(channel_data)
            except Exception as e:
                logger.error(f"Erro ao processar canal {channel}: {e}")
                continue
        
        logger.info(f"Total de registros obtidos: {len(all_data)}")
        return all_data
    
    def _safe_float(self, value) -> Optional[float]:
        """Converte valor para float de forma segura"""
        if value is None or value == "":
            return None
        
        try:
            # Se já é numérico
            if isinstance(value, (int, float)):
                return float(value)
            
            # Converter string
            clean_value = str(value).replace(',', '.').replace('R$', '').replace(' ', '')
            clean_value = clean_value.replace('%', '')
            
            if clean_value == '' or clean_value == '-':
                return None
                
            return float(clean_value)
        except (ValueError, TypeError):
            return None
    
    def _safe_spend_validation(self, spend_value) -> bool:
        """Valida se o valor de spend é válido"""
        if spend_value is None:
            return False
        
        spend = self._safe_float(spend_value)
        if spend is None:
            return False
        
        # Filtrar valores muito altos (provavelmente erros)
        if spend > 10000:
            return False
        
        return spend > 0
    
    def get_contract_data(self) -> Dict[str, Dict[str, Any]]:
        """Obtém dados contratados (mock por enquanto)"""
        # Por enquanto, retorna dados mock
        # Em uma implementação real, isso viria de uma planilha de contrato
        return {
            "CTV": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": None,
                "Cliques": None,
                "CTR": None,
                "VC (100%)": 14718.0,
                "VTR (100%)": 0.8329,
                "CPV (R$)": 0.2,
                "CPM (R$)": None,
                "Pacing (%)": 0.247
            },
            "Disney": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": None,
                "Cliques": None,
                "CTR": None,
                "VC (100%)": 14718.0,
                "VTR (100%)": 0.8329,
                "CPV (R$)": 0.2,
                "CPM (R$)": None,
                "Pacing (%)": 0.247
            },
            "Footfall Display": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": 14718.0,
                "Cliques": 147.0,
                "CTR": 0.01,
                "VC (100%)": None,
                "VTR (100%)": None,
                "CPV (R$)": None,
                "CPM (R$)": 0.2,
                "Pacing (%)": 0.247
            },
            "Netflix": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": None,
                "Cliques": None,
                "CTR": None,
                "VC (100%)": 14718.0,
                "VTR (100%)": 0.8329,
                "CPV (R$)": 0.2,
                "CPM (R$)": None,
                "Pacing (%)": 0.247
            },
            "TikTok": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": 14718.0,
                "Cliques": 147.0,
                "CTR": 0.01,
                "VC (100%)": 14718.0,
                "VTR (100%)": 0.8329,
                "CPV (R$)": 0.2,
                "CPM (R$)": 0.2,
                "Pacing (%)": 0.247
            },
            "YouTube": {
                "Budget Contratado (R$)": 11895.55,
                "Budget Utilizado (R$)": 2943.6,
                "Impressões": None,
                "Cliques": None,
                "CTR": None,
                "VC (100%)": 14718.0,
                "VTR (100%)": 0.8329,
                "CPV (R$)": 0.2,
                "CPM (R$)": None,
                "Pacing (%)": 0.247
            }
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com Google Sheets"""
        if not self.is_available():
            return {
                "status": "error",
                "message": "Cliente Google Sheets não disponível",
                "details": "Verifique as credenciais e configurações"
            }
        
        results = {}
        
        for channel, config in self.sheets_config.items():
            try:
                if not config["spreadsheet_id"]:
                    results[channel] = {
                        "status": "warning",
                        "message": "Spreadsheet ID não configurado"
                    }
                    continue
                
                # Tentar acessar a planilha
                spreadsheet = self.client.open_by_key(config["spreadsheet_id"])
                worksheet = spreadsheet.worksheet(config["sheet_name"])
                
                # Obter algumas linhas para teste
                test_data = worksheet.get_all_values()[:5]
                
                results[channel] = {
                    "status": "success",
                    "message": f"Conectado com sucesso",
                    "rows_found": len(test_data),
                    "spreadsheet_title": spreadsheet.title
                }
                
            except Exception as e:
                results[channel] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
