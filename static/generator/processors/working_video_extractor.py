#!/usr/bin/env python3
"""
Extrator Funcional para Dados de Campanha de Vídeo
Versão que realmente funciona
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import re

from unidecode import unidecode

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google_sheets_service import GoogleSheetsService
from numeric_parsers import safe_float as parse_safe_float, safe_int as parse_safe_int

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

DAY_COLUMN_CANDIDATES = [
    "day",
    "date",
    "data",
]

CREATIVE_COLUMN_CANDIDATES = [
    "creative",
    "criativo",
    "ad",
    "ad name",
    "ad_name",
]

SPEND_COLUMN_CANDIDATES = [
    "valor investido",
    "valor investido (r$)",
    "investimento",
    "budget",
    "spend",
]

IMPRESSIONS_COLUMN_CANDIDATES = [
    "imps",
    "impressions",
    "impressões",
    "impressoes",
]

CLICKS_COLUMN_CANDIDATES = [
    "clicks",
    "cliques",
]

CPV_COLUMN_CANDIDATES = [
    "cpv",
    "cost per view",
]

CTR_COLUMN_CANDIDATES = [
    "ctr",
    "ctr ",
    "click-through rate",
]

VIDEO_STARTS_COLUMN_CANDIDATES = [
    "video starts",
    "starts",
    "video start",
    "inícios de vídeo",
    "inicios de video",
]

VIDEO_COMPLETIONS_COLUMN_CANDIDATES = [
    "100%  video complete",
    "100% video complete",
    "video completions",
    "video assistido 100%",
    "complete views",
    "completed views",
]


def _normalize_sheet_value(value) -> Optional[str]:
    """Return a stripped string representation for sheet values."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def _extract_row_value(
    row: pd.Series,
    candidates,
    normalized_columns: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Retrieve the first non-empty value from the provided candidate columns."""

    if not isinstance(row, pd.Series):
        return None

    normalized_columns = normalized_columns or {
        str(col).strip().lower(): col for col in row.index
    }

    for candidate in candidates:
        normalized_candidate = str(candidate).strip().lower()
        source_column = normalized_columns.get(normalized_candidate)
        if source_column is None:
            continue

        value = _normalize_sheet_value(row.get(source_column))
        if value is not None:
            return value

    return None


def _extract_candidate_value(
    row: pd.Series,
    normalized_columns: Dict[str, str],
    candidates: List[str],
):
    """Return the first non-null value for any of the candidate columns."""

    if not isinstance(row, pd.Series) or not normalized_columns:
        return None

    for candidate in candidates:
        normalized_candidate = str(candidate).strip().lower()
        source_column = normalized_columns.get(normalized_candidate)
        if source_column is None:
            continue

        value = row.get(source_column)
        if value is None:
            continue

        if isinstance(value, float) and pd.isna(value):
            continue

        if isinstance(value, str) and not value.strip():
            continue

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
            daily_data = self._extract_daily_data_real() or []
            if not daily_data:
                logger.warning("⚠️ Nenhum dado diário encontrado - retornando estrutura padrão")

            # 3. Extrair dados de contrato
            contract_data = self._extract_contract_data_real()

            # 4. Calcular métricas totais
            total_metrics = self._calculate_total_metrics(daily_data, contract_data)

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
                "metrics": total_metrics,
                "publishers": self._get_publishers(daily_data),
                "strategies": self._extract_strategies_data_real(),
            }
            
            logger.info(f"✅ Extração REAL concluída: {len(daily_data)} registros diários")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None

    def _get_tab_gid(self, tab_key: str) -> Optional[str]:
        """Recupera o GID configurado para uma aba específica."""

        tabs = getattr(self.config, "tabs", None) or {}
        if not isinstance(tabs, dict):
            return None

        gid = tabs.get(tab_key)
        if gid is None:
            return None

        gid_str = str(gid).strip()
        return gid_str or None

    def _read_tab_dataframe(
        self,
        tab_key: str,
        default_sheet_name: Optional[str],
    ) -> pd.DataFrame:
        """Lê uma aba da planilha utilizando o GID configurado."""

        gid = self._get_tab_gid(tab_key)
        if gid:
            logger.info("📄 Lendo aba '%s' usando GID %s", tab_key, gid)
            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id,
                gid=gid,
            )

            if not df.empty or default_sheet_name is None:
                return df

            logger.warning(
                "⚠️ Aba '%s' (gid %s) vazia ou não encontrada; tentando nome padrão '%s'",
                tab_key,
                gid,
                default_sheet_name,
            )

        if default_sheet_name:
            logger.info(
                "ℹ️ Utilizando fallback para aba '%s' com nome '%s'",
                tab_key,
                default_sheet_name,
            )
            return self.sheets_service.read_sheet_data(
                self.config.sheet_id,
                sheet_name=default_sheet_name,
            )

        return pd.DataFrame()

    def _extract_strategies_data_real(self) -> Dict[str, List[str]]:
        """Extrai dados de estratégias convertendo linhas da planilha em listas."""

        empty_strategies = {
            "segmentation": [],
            "creative_strategy": [],
            "objectives": [],
            "highlights": [],
            "formats": [],
            "channels": [],
            "insights": [],
        }

        try:
            df = self._read_tab_dataframe("strategies", "Estratégias")
        except Exception as error:
            logger.warning("⚠️ Erro ao ler aba de estratégias: %s", error)
            return empty_strategies

        if df is None or df.empty:
            return empty_strategies

        strategies_data = {key: list(values) for key, values in empty_strategies.items()}

        for _, row in df.iterrows():
            row_values = [
                str(value).strip()
                for value in row
                if value is not None and not (isinstance(value, float) and pd.isna(value)) and str(value).strip()
            ]

            if len(row_values) < 2:
                continue

            category = row_values[0].lower()
            values = row_values[1:]

            if "segment" in category:
                target_key = "segmentation"
            elif "criativo" in category or "creative" in category:
                target_key = "creative_strategy"
            elif "objetivo" in category or "objective" in category:
                target_key = "objectives"
            elif "destaque" in category or "highlight" in category:
                target_key = "highlights"
            elif "formato" in category or "format" in category:
                target_key = "formats"
            elif "canal" in category or "channel" in category:
                target_key = "channels"
            elif "insight" in category:
                target_key = "insights"
            else:
                continue

            for value in values:
                cleaned_value = value.strip()
                if cleaned_value and cleaned_value.lower() != "nan":
                    strategies_data[target_key].append(cleaned_value)

        return strategies_data

    def _extract_daily_data_real(self) -> list:
        """Extrair dados diários da aba Report - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados diários REAIS...")
            
            # Usar o método correto do GoogleSheetsService
            df = self._read_tab_dataframe("daily_data", "Report")
            
            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Report")
                return []
            
            logger.info(f"✅ DataFrame carregado: {len(df)} linhas, {len(df.columns)} colunas")
            logger.info(f"📊 Colunas disponíveis: {list(df.columns)}")
            
            daily_records = []
            for index, row in df.iterrows():
                try:
                    normalized_columns = {
                        str(col).strip().lower(): col for col in row.index
                    }

                    # Extrair dados básicos com tratamento de erro
                    date_value = _extract_candidate_value(
                        row, normalized_columns, DAY_COLUMN_CANDIDATES
                    )
                    date_str = str(date_value or "").strip()
                    if not date_str or date_str == 'nan' or date_str == '':
                        continue

                    creative_value = _extract_candidate_value(
                        row, normalized_columns, CREATIVE_COLUMN_CANDIDATES
                    )
                    creative = _normalize_sheet_value(creative_value) or ''
                    publisher_name = (
                        _extract_row_value(
                            row,
                            PUBLISHER_COLUMN_CANDIDATES,
                            normalized_columns,
                        )
                        or creative
                        or "Desconhecido"
                    )
                    publisher_type = _extract_row_value(
                        row, PUBLISHER_TYPE_COLUMN_CANDIDATES, normalized_columns
                    )
                    spend_value = _extract_candidate_value(
                        row, normalized_columns, SPEND_COLUMN_CANDIDATES
                    )
                    spend = (
                        self._safe_float(spend_value)
                        if spend_value is not None
                        else 0.0
                    )
                    impressions_value = _extract_candidate_value(
                        row, normalized_columns, IMPRESSIONS_COLUMN_CANDIDATES
                    )
                    impressions = (
                        self._safe_int(impressions_value)
                        if impressions_value is not None
                        else 0
                    )
                    clicks_value = _extract_candidate_value(
                        row, normalized_columns, CLICKS_COLUMN_CANDIDATES
                    )
                    clicks = (
                        self._safe_int(clicks_value)
                        if clicks_value is not None
                        else 0
                    )
                    cpv_value = _extract_candidate_value(
                        row, normalized_columns, CPV_COLUMN_CANDIDATES
                    )
                    cpv = (
                        self._safe_float(cpv_value)
                        if cpv_value is not None
                        else None
                    )
                    ctr_value = _extract_candidate_value(
                        row, normalized_columns, CTR_COLUMN_CANDIDATES
                    )
                    ctr = (
                        self._safe_float(ctr_value)
                        if ctr_value is not None
                        else None
                    )
                    starts_value = _extract_candidate_value(
                        row, normalized_columns, VIDEO_STARTS_COLUMN_CANDIDATES
                    )
                    starts = (
                        self._safe_int(starts_value)
                        if starts_value is not None
                        else 0
                    )
                    q100_value = _extract_candidate_value(
                        row, normalized_columns, VIDEO_COMPLETIONS_COLUMN_CANDIDATES
                    )
                    q100 = (
                        self._safe_int(q100_value)
                        if q100_value is not None
                        else 0
                    )

                    # Calcular métricas derivadas e preencher CTR/CPV quando possível
                    impressions_available = impressions_value is not None
                    clicks_available = clicks_value is not None
                    spend_available = spend_value is not None
                    starts_available = starts_value is not None
                    q100_available = q100_value is not None

                    if ctr is None and clicks_available and impressions_available and impressions > 0:
                        ctr = (clicks / impressions) * 100

                    if cpv is None and spend_available:
                        if q100_available and q100 > 0:
                            cpv = spend / q100
                        elif starts_available and starts > 0:
                            cpv = spend / starts

                    cpm = (
                        (spend / impressions * 1000)
                        if impressions_available and impressions > 0
                        else None
                    )
                    if starts_available and starts > 0 and q100_available:
                        vtr = (q100 / starts) * 100
                    else:
                        vtr = None
                    
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
            df = self._read_tab_dataframe("contract", "Informações de contrato")

            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Informações de contrato")
                return self._get_default_contract()

            logger.info(f"✅ DataFrame de contrato carregado: {len(df)} linhas")
            logger.info(f"📊 Colunas de contrato: {list(df.columns)}")

            def _normalize_contract_key(key: Optional[str]) -> Optional[str]:
                if key is None:
                    return None

                normalized = unidecode(str(key))
                normalized = normalized.strip().lower()
                normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
                normalized = re.sub(r"\s+", " ", normalized).strip()
                return normalized or None

            normalized_key_map: Dict[str, str] = {}
            # Converter para dicionário
            contract_dict = {}
            for index, row in df.iterrows():
                try:
                    if len(row) >= 2:
                        raw_key = row.iloc[0]
                        raw_value = row.iloc[1]
                        key = _normalize_sheet_value(raw_key)
                        value = _normalize_sheet_value(raw_value)
                        if key and value and value != 'nan':
                            contract_dict[key] = value
                            normalized_key = _normalize_contract_key(key)
                            if normalized_key and normalized_key not in normalized_key_map:
                                normalized_key_map[normalized_key] = key
                            logger.info(f"✅ Contrato: {key} = {value}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha de contrato {index}: {e}")
                    continue

            def _get_contract_value(candidates: List[str]) -> Optional[str]:
                for candidate in candidates:
                    candidate_slug = _normalize_contract_key(candidate)
                    if not candidate_slug:
                        continue

                    original_key = normalized_key_map.get(candidate_slug)
                    if not original_key:
                        # Tentar correspondência parcial (casos com sufixos adicionais)
                        for slug, mapped_key in normalized_key_map.items():
                            if slug.startswith(candidate_slug):
                                original_key = mapped_key
                                break

                    if original_key:
                        return contract_dict.get(original_key)

                return None

            default_contract = self._get_default_contract()

            investment_value = _get_contract_value(["valor investido", "investimento total"])
            if investment_value is None:
                logger.warning("⚠️ Valor investido não encontrado na planilha. Usando valor padrão.")
            investment = (
                self._safe_float(investment_value)
                if investment_value is not None
                else self._safe_float(default_contract.get("investment"))
            )

            cpv_value = _get_contract_value(["cpv"])
            if cpv_value is None:
                logger.warning("⚠️ CPV não encontrado na planilha. Usando valor padrão.")
            cpv_contracted = (
                self._safe_float(cpv_value)
                if cpv_value is not None
                else self._safe_float(default_contract.get("cpv_contracted"))
            )

            complete_views_value = _get_contract_value(["visualizacoes completas", "vc contratadas"])
            if complete_views_value is None:
                logger.warning("⚠️ Visualizações completas contratadas não encontradas. Usando valor padrão.")
            complete_views_contracted = (
                self._safe_int(complete_views_value)
                if complete_views_value is not None
                else self._safe_int(default_contract.get("complete_views_contracted"))
            )

            impressions_value = _get_contract_value(["impressoes contratadas"])
            if impressions_value is None:
                logger.warning("⚠️ Impressões contratadas não encontradas. Usando valor padrão.")
            impressions_contracted = (
                self._safe_int(impressions_value)
                if impressions_value is not None
                else self._safe_int(default_contract.get("impressions_contracted"))
            )

            period_value = _get_contract_value(["periodo de veiculacao", "período de veiculação"])
            if period_value is None:
                logger.warning("⚠️ Período de veiculação não encontrado. Usando valor padrão.")
            period = period_value or default_contract.get("period")

            # Processar dados de contrato
            result = {
                "client": self.config.client,
                "campaign": self.config.campaign,
                "investment": investment,
                "cpv_contracted": cpv_contracted,
                "complete_views_contracted": complete_views_contracted,
                "impressions_contracted": impressions_contracted,
                "period": period,
                "status": "Em andamento"
            }
            
            logger.info("✅ Dados de contrato extraídos com SUCESSO")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados de contrato REAIS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return self._get_default_contract()
    
    def _calculate_total_metrics(
        self,
        daily_data: list,
        contract_data: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Calcular métricas totais dos dados diários"""
        zero_metrics = {
            "spend": 0,
            "impressions": 0,
            "clicks": 0,
            "starts": 0,
            "q100": 0,
            "ctr": 0,
            "cpm": 0,
            "vtr": 0,
            "cpv": 0,
            "pacing": 0,
            "vc_pacing": 0,
        }

        try:
            contract_data = contract_data or {}
            default_contract = self._get_default_contract()

            budget_contracted_raw = contract_data.get("investment")
            if budget_contracted_raw in (None, "", 0):
                budget_contracted_raw = default_contract.get("investment")
            budget_contracted = self._safe_float(budget_contracted_raw)

            complete_views_target_raw = contract_data.get("complete_views_contracted")
            if complete_views_target_raw in (None, "", 0):
                complete_views_target_raw = default_contract.get("complete_views_contracted")
            complete_views_target = self._safe_int(complete_views_target_raw)

            if not daily_data:
                # Sem dados entregues, manter estrutura padrão com métricas zeradas
                zero_metrics["pacing"] = 0
                zero_metrics["vc_pacing"] = 0
                return zero_metrics

            # Somar todas as métricas
            total_spend = sum(record.get("spend", 0) for record in daily_data)
            total_impressions = sum(record.get("impressions", 0) for record in daily_data)
            total_clicks = sum(record.get("clicks", 0) for record in daily_data)
            total_starts = sum(record.get("starts", 0) for record in daily_data)
            total_q100 = sum(record.get("q100", 0) for record in daily_data)

            # Calcular métricas derivadas
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            vtr = (total_q100 / total_starts * 100) if total_starts > 0 else 0
            cpv = (total_spend / total_q100) if total_q100 > 0 else 0

            # Calcular pacing
            pacing = (total_spend / budget_contracted * 100) if budget_contracted > 0 else 0
            vc_pacing = (total_q100 / complete_views_target * 100) if complete_views_target > 0 else 0

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
            return zero_metrics
    
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

        if hasattr(pd, "isna") and pd.isna(value):
            return 0.0
        return parse_safe_float(value)

    def _safe_int(self, value) -> int:
        """Converter valor para int de forma segura"""

        if hasattr(pd, "isna") and pd.isna(value):
            return 0
        return parse_safe_int(value)

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
