#!/usr/bin/env python3
"""
Extrator Funcional para Dados de Campanha de Vídeo
Versão que realmente funciona
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import re

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)


PUBLISHER_COLUMN_CANDIDATES = [
    "publisher",
    "publisher name",
    "publisher_name",
    "publisher/ exchange",
    "publisher / exchange",
    "publisher label",
    "exchange",
    "inventory",
    "inventory source",
    "inventory_source",
    "site",
    "site name",
    "site_name",
    "channel",
    "channel name",
    "canal",
    "veículo",
    "veiculo",
    "vehicle",
    "placement",
    "placement name",
    "placement_name",
    "publisher id",
    "publisher_id"
]

PUBLISHER_TYPE_COLUMN_CANDIDATES = [
    "type",
    "publisher type",
    "publisher_type",
    "site type",
    "site_type",
    "channel type",
    "channel_type"
]


def _normalize_sheet_value(value) -> Optional[str]:
    """Return a stripped string representation for sheet values."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def _extract_row_value(row: pd.Series, candidates) -> Optional[str]:
    """Retrieve the first non-empty value from the provided candidate columns."""

    if not isinstance(row, pd.Series):
        return None

    normalized_columns = {str(col).strip().lower(): col for col in row.index}

    for candidate in candidates:
        normalized_candidate = str(candidate).strip().lower()
        source_column = normalized_columns.get(normalized_candidate)
        if source_column is None:
            continue

        value = _normalize_sheet_value(row.get(source_column))
        if value is not None:
            return value

    return None


def _slugify_publisher(name: str) -> str:
    """Create a simple slug for publisher descriptions."""

    if not name:
        return "publisher"

    slug = "-".join(
        part for part in re.split(r"[^a-z0-9]+", name.lower()) if part
    )
    return slug or "publisher"

class WorkingVideoExtractor:
    """Extrator que realmente funciona"""
    
    def __init__(self, config):
        self.config = config
        self.sheets_service = GoogleSheetsService()
        
    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados da planilha - VERSÃO QUE FUNCIONA"""
        try:
            logger.info(f"🔄 Iniciando extração REAL para {self.config.client}")
            
            # 1. Verificar se o serviço está configurado
            if not self.sheets_service.is_configured():
                logger.error("❌ Google Sheets não configurado")
                return None
            
            # 2. Extrair dados diários da aba "Report"
            daily_data = self._extract_daily_data_real()
            if not daily_data:
                logger.warning("⚠️ Nenhum dado diário encontrado")
                return None
            
            # 3. Extrair dados de contrato
            contract_data = self._extract_contract_data_real()
            
            # 4. Calcular métricas totais
            total_metrics = self._calculate_total_metrics(daily_data)
            
            # 5. Preparar dados finais
            result = {
                "campaign_name": f"{self.config.client} - {self.config.campaign}",
                "dashboard_title": f"Dashboard {self.config.client} - {self.config.campaign}",
                "channel": "Prográmatica",
                "creative_type": "Video",
                "period": contract_data.get("period", "15/09/2025 - 30/09/2025"),
                "contract": contract_data,
                "daily_data": daily_data,
                "total_metrics": total_metrics,
                "publishers": self._get_publishers(daily_data),
                "strategies": {
                    "segmentation": ["Lookalike", "Interesse", "Retargeting"],
                    "objectives": ["Brand Awareness", "Video Views", "Engagement"]
                }
            }
            
            logger.info(f"✅ Extração REAL concluída: {len(daily_data)} registros diários")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    def _extract_daily_data_real(self) -> list:
        """Extrair dados diários da aba Report - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados diários REAIS...")
            
            # Usar o método correto do GoogleSheetsService
            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id, 
                sheet_name="Report"
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Report")
                return []
            
            logger.info(f"✅ DataFrame carregado: {len(df)} linhas, {len(df.columns)} colunas")
            logger.info(f"📊 Colunas disponíveis: {list(df.columns)}")
            
            daily_records = []
            for index, row in df.iterrows():
                try:
                    # Extrair dados básicos com tratamento de erro
                    date_str = str(row.get('Day', ''))
                    if not date_str or date_str == 'nan' or date_str == '':
                        continue
                    
                    creative = _normalize_sheet_value(row.get('Creative')) or ''
                    publisher_name = _extract_row_value(row, PUBLISHER_COLUMN_CANDIDATES) or creative or "Desconhecido"
                    publisher_type = _extract_row_value(row, PUBLISHER_TYPE_COLUMN_CANDIDATES)
                    spend = self._safe_float(row.get('Valor investido', 0))
                    impressions = self._safe_int(row.get('Imps', 0))
                    clicks = self._safe_int(row.get('Clicks', 0))
                    cpv = self._safe_float(row.get('CPV', 0))
                    ctr = self._safe_float(row.get('CTR ', 0))
                    starts = self._safe_int(row.get('Video Starts', 0))
                    q100 = self._safe_int(row.get('Video Completions', 0))
                    
                    # Calcular métricas derivadas
                    cpm = (spend / impressions * 1000) if impressions > 0 else 0
                    vtr = (starts / impressions * 100) if impressions > 0 else 0
                    
                    record = {
                        "date": date_str,
                        "creative": creative,
                        "publisher": publisher_name,
                        "spend": spend,
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                        "cpv": cpv,
                        "cpm": cpm,
                        "starts": starts,
                        "q100": q100,
                        "vtr": vtr
                    }

                    if publisher_type:
                        record["publisher_type"] = publisher_type

                    daily_records.append(record)
                    logger.info(f"✅ Registro {index + 1}: {date_str} - {creative} - R$ {spend}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha {index}: {e}")
                    continue
            
            logger.info(f"✅ {len(daily_records)} registros diários extraídos com SUCESSO")
            return daily_records
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados diários REAIS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    def _extract_contract_data_real(self) -> dict:
        """Extrair dados de contrato - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados de contrato REAIS...")
            
            # Usar o método correto do GoogleSheetsService
            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id, 
                sheet_name="Informações de contrato"
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Informações de contrato")
                return self._get_default_contract()
            
            logger.info(f"✅ DataFrame de contrato carregado: {len(df)} linhas")
            logger.info(f"📊 Colunas de contrato: {list(df.columns)}")
            
            # Converter para dicionário
            contract_dict = {}
            for index, row in df.iterrows():
                try:
                    if len(row) >= 2:
                        key = str(row.iloc[0]).strip()
                        value = str(row.iloc[1]).strip()
                        if key and value and value != 'nan':
                            contract_dict[key] = value
                            logger.info(f"✅ Contrato: {key} = {value}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha de contrato {index}: {e}")
                    continue
            
            # Processar dados de contrato
            result = {
                "client": self.config.client,
                "campaign": self.config.campaign,
                "investment": self._safe_float(contract_dict.get("Valor investido", 31000)),
                "cpv_contracted": self._safe_float(contract_dict.get("CPV", 0.16)),
                "complete_views_contracted": self._safe_int(contract_dict.get("Visualizações completas", 193750)),
                "impressions_contracted": self._safe_int(contract_dict.get("Impressões", 193750)),
                "period": contract_dict.get("Periodo de veiculação", "15/09/2025 - 30/09/2025"),
                "status": "Em andamento"
            }
            
            logger.info("✅ Dados de contrato extraídos com SUCESSO")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados de contrato REAIS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return self._get_default_contract()
    
    def _calculate_total_metrics(self, daily_data: list) -> dict:
        """Calcular métricas totais dos dados diários"""
        try:
            if not daily_data:
                return {}
            
            # Somar todas as métricas
            total_spend = sum(record.get("spend", 0) for record in daily_data)
            total_impressions = sum(record.get("impressions", 0) for record in daily_data)
            total_clicks = sum(record.get("clicks", 0) for record in daily_data)
            total_starts = sum(record.get("starts", 0) for record in daily_data)
            total_q100 = sum(record.get("q100", 0) for record in daily_data)
            
            # Calcular métricas derivadas
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            vtr = (total_starts / total_impressions * 100) if total_impressions > 0 else 0
            cpv = (total_spend / total_q100) if total_q100 > 0 else 0
            
            # Calcular pacing
            budget_contracted = 31000
            pacing = (total_spend / budget_contracted * 100) if budget_contracted > 0 else 0
            vc_pacing = (total_q100 / 193750 * 100) if 193750 > 0 else 0
            
            logger.info(f"✅ Métricas calculadas: R$ {total_spend}, {total_impressions} impressões")
            
            return {
                "spend": total_spend,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "starts": total_starts,
                "q100": total_q100,
                "ctr": ctr,
                "cpm": cpm,
                "vtr": vtr,
                "cpv": cpv,
                "pacing": pacing,
                "vc_pacing": vc_pacing
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas totais: {e}")
            return {}
    
    def _get_publishers(self, daily_data: list) -> list:
        """Extrair publishers únicos dos dados diários"""
        try:
            publishers_list = []
            seen_names = set()

            for record in daily_data:
                raw_name = record.get("publisher") or record.get("site") or record.get("channel") or record.get("creative")
                publisher_name = _normalize_sheet_value(raw_name) or "Desconhecido"
                normalized_name = publisher_name.lower()

                if normalized_name in seen_names:
                    continue

                seen_names.add(normalized_name)

                entry = {"name": publisher_name}
                publisher_type = record.get("publisher_type")
                if publisher_type:
                    entry["type"] = publisher_type
                else:
                    entry["type"] = f"Site: {_slugify_publisher(publisher_name)}.com"

                publishers_list.append(entry)

            if not publishers_list:
                publishers_list.append({"name": "Publisher Padrão", "type": "Site: publisher-padrao.com"})

            logger.info(f"✅ Publishers extraídos: {len(publishers_list)}")
            return publishers_list

        except Exception as e:
            logger.error(f"❌ Erro ao extrair publishers: {e}")
            return [{"name": "Publisher Padrão", "type": "Site: publisher-padrao.com"}]
    
    def _get_default_contract(self) -> dict:
        """Retornar dados de contrato padrão"""
        return {
            "client": self.config.client,
            "campaign": self.config.campaign,
            "investment": 31000,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "impressions_contracted": 193750,
            "period": "15/09/2025 - 30/09/2025",
            "status": "Em andamento"
        }
    
    def _safe_float(self, value) -> float:
        """Converter valor para float de forma segura"""
        try:
            if pd.isna(value) or value == '' or value == 'nan':
                return 0.0
            return float(str(value).replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value) -> int:
        """Converter valor para int de forma segura"""
        try:
            if pd.isna(value) or value == '' or value == 'nan':
                return 0
            return int(float(str(value).replace(',', '.')))
        except (ValueError, TypeError):
            return 0

def extract_campaign_data(campaign_key: str) -> Optional[Dict[str, Any]]:
    """Função principal para extrair dados de uma campanha - VERSÃO QUE FUNCIONA"""
    try:
        from persistent_database import get_campaign_config
        
        config = get_campaign_config(campaign_key)
        if not config:
            logger.error(f"❌ Configuração não encontrada para campanha: {campaign_key}")
            return None
        
        extractor = WorkingVideoExtractor(config)
        return extractor.extract_data()
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

"""
Extrator Funcional para Dados de Campanha de Vídeo
Versão que realmente funciona
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)

class WorkingVideoExtractor:
    """Extrator que realmente funciona"""
    
    def __init__(self, config):
        self.config = config
        self.sheets_service = GoogleSheetsService()
        
    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados da planilha - VERSÃO QUE FUNCIONA"""
        try:
            logger.info(f"🔄 Iniciando extração REAL para {self.config.client}")
            
            # 1. Verificar se o serviço está configurado
            if not self.sheets_service.is_configured():
                logger.error("❌ Google Sheets não configurado")
                return None
            
            # 2. Extrair dados diários da aba "Report"
            daily_data = self._extract_daily_data_real()
            if not daily_data:
                logger.warning("⚠️ Nenhum dado diário encontrado")
                return None
            
            # 3. Extrair dados de contrato
            contract_data = self._extract_contract_data_real()
            
            # 4. Calcular métricas totais
            total_metrics = self._calculate_total_metrics(daily_data)
            
            # 5. Preparar dados finais
            result = {
                "campaign_name": f"{self.config.client} - {self.config.campaign}",
                "dashboard_title": f"Dashboard {self.config.client} - {self.config.campaign}",
                "channel": "Prográmatica",
                "creative_type": "Video",
                "period": contract_data.get("period", "15/09/2025 - 30/09/2025"),
                "contract": contract_data,
                "daily_data": daily_data,
                "total_metrics": total_metrics,
                "publishers": self._get_publishers(daily_data),
                "strategies": {
                    "segmentation": ["Lookalike", "Interesse", "Retargeting"],
                    "objectives": ["Brand Awareness", "Video Views", "Engagement"]
                }
            }
            
            logger.info(f"✅ Extração REAL concluída: {len(daily_data)} registros diários")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    def _extract_daily_data_real(self) -> list:
        """Extrair dados diários da aba Report - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados diários REAIS...")
            
            # Usar o método correto do GoogleSheetsService
            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id, 
                sheet_name="Report"
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Report")
                return []
            
            logger.info(f"✅ DataFrame carregado: {len(df)} linhas, {len(df.columns)} colunas")
            logger.info(f"📊 Colunas disponíveis: {list(df.columns)}")
            
            daily_records = []
            for index, row in df.iterrows():
                try:
                    # Extrair dados básicos com tratamento de erro
                    date_str = str(row.get('Day', ''))
                    if not date_str or date_str == 'nan' or date_str == '':
                        continue
                    
                    creative = _normalize_sheet_value(row.get('Creative')) or ''
                    publisher_name = _extract_row_value(row, PUBLISHER_COLUMN_CANDIDATES) or creative or "Desconhecido"
                    publisher_type = _extract_row_value(row, PUBLISHER_TYPE_COLUMN_CANDIDATES)
                    spend = self._safe_float(row.get('Valor investido', 0))
                    impressions = self._safe_int(row.get('Imps', 0))
                    clicks = self._safe_int(row.get('Clicks', 0))
                    cpv = self._safe_float(row.get('CPV', 0))
                    ctr = self._safe_float(row.get('CTR ', 0))
                    starts = self._safe_int(row.get('Video Starts', 0))
                    q100 = self._safe_int(row.get('Video Completions', 0))
                    
                    # Calcular métricas derivadas
                    cpm = (spend / impressions * 1000) if impressions > 0 else 0
                    vtr = (starts / impressions * 100) if impressions > 0 else 0
                    
                    record = {
                        "date": date_str,
                        "creative": creative,
                        "publisher": publisher_name,
                        "spend": spend,
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                        "cpv": cpv,
                        "cpm": cpm,
                        "starts": starts,
                        "q100": q100,
                        "vtr": vtr
                    }

                    if publisher_type:
                        record["publisher_type"] = publisher_type

                    daily_records.append(record)
                    logger.info(f"✅ Registro {index + 1}: {date_str} - {creative} - R$ {spend}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha {index}: {e}")
                    continue
            
            logger.info(f"✅ {len(daily_records)} registros diários extraídos com SUCESSO")
            return daily_records
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados diários REAIS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    def _extract_contract_data_real(self) -> dict:
        """Extrair dados de contrato - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados de contrato REAIS...")
            
            # Usar o método correto do GoogleSheetsService
            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id, 
                sheet_name="Informações de contrato"
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Informações de contrato")
                return self._get_default_contract()
            
            logger.info(f"✅ DataFrame de contrato carregado: {len(df)} linhas")
            logger.info(f"📊 Colunas de contrato: {list(df.columns)}")
            
            # Converter para dicionário
            contract_dict = {}
            for index, row in df.iterrows():
                try:
                    if len(row) >= 2:
                        key = str(row.iloc[0]).strip()
                        value = str(row.iloc[1]).strip()
                        if key and value and value != 'nan':
                            contract_dict[key] = value
                            logger.info(f"✅ Contrato: {key} = {value}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha de contrato {index}: {e}")
                    continue
            
            # Processar dados de contrato
            result = {
                "client": self.config.client,
                "campaign": self.config.campaign,
                "investment": self._safe_float(contract_dict.get("Valor investido", 31000)),
                "cpv_contracted": self._safe_float(contract_dict.get("CPV", 0.16)),
                "complete_views_contracted": self._safe_int(contract_dict.get("Visualizações completas", 193750)),
                "impressions_contracted": self._safe_int(contract_dict.get("Impressões", 193750)),
                "period": contract_dict.get("Periodo de veiculação", "15/09/2025 - 30/09/2025"),
                "status": "Em andamento"
            }
            
            logger.info("✅ Dados de contrato extraídos com SUCESSO")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados de contrato REAIS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return self._get_default_contract()
    
    def _calculate_total_metrics(self, daily_data: list) -> dict:
        """Calcular métricas totais dos dados diários"""
        try:
            if not daily_data:
                return {}
            
            # Somar todas as métricas
            total_spend = sum(record.get("spend", 0) for record in daily_data)
            total_impressions = sum(record.get("impressions", 0) for record in daily_data)
            total_clicks = sum(record.get("clicks", 0) for record in daily_data)
            total_starts = sum(record.get("starts", 0) for record in daily_data)
            total_q100 = sum(record.get("q100", 0) for record in daily_data)
            
            # Calcular métricas derivadas
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            vtr = (total_starts / total_impressions * 100) if total_impressions > 0 else 0
            cpv = (total_spend / total_q100) if total_q100 > 0 else 0
            
            # Calcular pacing
            budget_contracted = 31000
            pacing = (total_spend / budget_contracted * 100) if budget_contracted > 0 else 0
            vc_pacing = (total_q100 / 193750 * 100) if 193750 > 0 else 0
            
            logger.info(f"✅ Métricas calculadas: R$ {total_spend}, {total_impressions} impressões")
            
            return {
                "spend": total_spend,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "starts": total_starts,
                "q100": total_q100,
                "ctr": ctr,
                "cpm": cpm,
                "vtr": vtr,
                "cpv": cpv,
                "pacing": pacing,
                "vc_pacing": vc_pacing
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas totais: {e}")
            return {}
    
    def _get_publishers(self, daily_data: list) -> list:
        """Extrair publishers únicos dos dados diários"""
        try:
            publishers_list = []
            seen_names = set()

            for record in daily_data:
                raw_name = record.get("publisher") or record.get("site") or record.get("channel") or record.get("creative")
                publisher_name = _normalize_sheet_value(raw_name) or "Desconhecido"
                normalized_name = publisher_name.lower()

                if normalized_name in seen_names:
                    continue

                seen_names.add(normalized_name)

                entry = {"name": publisher_name}
                publisher_type = record.get("publisher_type")
                if publisher_type:
                    entry["type"] = publisher_type
                else:
                    entry["type"] = f"Site: {_slugify_publisher(publisher_name)}.com"

                publishers_list.append(entry)

            if not publishers_list:
                publishers_list.append({"name": "Publisher Padrão", "type": "Site: publisher-padrao.com"})

            logger.info(f"✅ Publishers extraídos: {len(publishers_list)}")
            return publishers_list
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair publishers: {e}")
            return [{"name": "Publisher Padrão", "type": "Site: publisher-padrao.com"}]
    
    def _get_default_contract(self) -> dict:
        """Retornar dados de contrato padrão"""
        return {
            "client": self.config.client,
            "campaign": self.config.campaign,
            "investment": 31000,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "impressions_contracted": 193750,
            "period": "15/09/2025 - 30/09/2025",
            "status": "Em andamento"
        }
    
    def _safe_float(self, value) -> float:
        """Converter valor para float de forma segura"""
        try:
            if pd.isna(value) or value == '' or value == 'nan':
                return 0.0
            return float(str(value).replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value) -> int:
        """Converter valor para int de forma segura"""
        try:
            if pd.isna(value) or value == '' or value == 'nan':
                return 0
            return int(float(str(value).replace(',', '.')))
        except (ValueError, TypeError):
            return 0

def extract_campaign_data(campaign_key: str) -> Optional[Dict[str, Any]]:
    """Função principal para extrair dados de uma campanha - VERSÃO QUE FUNCIONA"""
    try:
        from persistent_database import get_campaign_config
        
        config = get_campaign_config(campaign_key)
        if not config:
            logger.error(f"❌ Configuração não encontrada para campanha: {campaign_key}")
            return None
        
        extractor = WorkingVideoExtractor(config)
        return extractor.extract_data()
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None
