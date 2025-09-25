#!/usr/bin/env python3
"""
Extrator Funcional para Dados de Campanha de Vídeo
Versão que realmente funciona
"""

import os
import sys
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)


class WorkingVideoExtractor:
    """Extrator que realmente funciona"""

    PUBLISHER_COLUMNS = [
        "Publisher",
        "Canal",
        "Canal ",
        "Channel",
        "Channel Name",
        "Publisher Name",
        "Site",
        "Site Name",
        "Placement",
        "Placement Name",
        "Inventory",
    ]

    CHANNEL_COLUMNS = [
        "Channel",
        "Canal",
        "Device",
        "Device Category",
        "Formato",
    ]

    LINE_ITEM_COLUMNS = [
        "Line Item",
        "Line item",
        "LineItem",
        "Pedido",
    ]

    INVESTMENT_COLUMNS = [
        "Investimento",
        "Investment",
        "Budget",
        "Investimento (R$)",
        "Budget (R$)",
        "Valor Investido",
        "Valor investido",
    ]

    def __init__(self, config):
        self.config = config
        self.sheets_service = GoogleSheetsService()

    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados da planilha - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Iniciando extração REAL para %s", self.config.client)

            if not self.sheets_service.is_configured():
                logger.error("❌ Google Sheets não configurado")
                return None

            daily_data = self._extract_daily_data_real()
            if not daily_data:
                logger.warning("⚠️ Nenhum dado diário encontrado")
                return None

            contract_data = self._extract_contract_data_real()
            total_metrics = self._calculate_total_metrics(daily_data, contract_data)
            publishers = self._aggregate_publishers(daily_data, contract_data)

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
                "publishers": publishers,
                "strategies": {
                    "segmentation": ["Lookalike", "Interesse", "Retargeting"],
                    "objectives": ["Brand Awareness", "Video Views", "Engagement"],
                },
            }

            logger.info("✅ Extração REAL concluída: %s registros diários", len(daily_data))
            logger.info("✅ Publishers agregados: %s", len(publishers))
            return result

        except Exception as exc:  # pragma: no cover - logging de segurança
            logger.error("❌ Erro na extração REAL: %s", exc)
            import traceback

            logger.error("❌ Traceback: %s", traceback.format_exc())
            return None

    def _extract_daily_data_real(self) -> List[Dict[str, Any]]:
        """Extrair dados diários da aba Report - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados diários REAIS...")

            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id,
                sheet_name="Report",
            )

            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Report")
                return []

            logger.info("✅ DataFrame carregado: %s linhas, %s colunas", len(df), len(df.columns))
            logger.info("📊 Colunas disponíveis: %s", list(df.columns))

            daily_records: List[Dict[str, Any]] = []
            for index, row in df.iterrows():
                try:
                    date_str = str(row.get("Day", "")).strip()
                    if not date_str or date_str.lower() == "nan":
                        continue

                    creative = str(row.get("Creative", "")).strip()
                    spend = self._safe_float(row.get("Valor investido", 0))
                    impressions = self._safe_int(row.get("Imps", 0))
                    clicks = self._safe_int(row.get("Clicks", 0))
                    cpv = self._safe_float(row.get("CPV", 0))
                    ctr = self._safe_float(row.get("CTR ", row.get("CTR", 0)))
                    starts = self._safe_int(row.get("Video Starts", 0))
                    q100 = self._safe_int(row.get("Video Completions", 0))

                    investment = self._safe_float(self._get_first_nonempty(row, self.INVESTMENT_COLUMNS))
                    if investment == 0:
                        investment = spend

                    publisher_info = self._extract_publisher_info(row, creative)

                    cpm = (spend / impressions * 1000) if impressions > 0 else 0
                    vtr = (starts / impressions * 100) if impressions > 0 else 0
                    if cpv == 0 and q100 > 0:
                        cpv = spend / q100

                    record: Dict[str, Any] = {
                        "date": date_str,
                        "creative": creative,
                        "spend": spend,
                        "investment": investment,
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                        "cpv": cpv,
                        "cpm": cpm,
                        "starts": starts,
                        "q100": q100,
                        "vtr": vtr,
                        "publisher": publisher_info["publisher"],
                        "channel": publisher_info["channel"],
                        "line_item": publisher_info["line_item"],
                        "inventory": publisher_info["inventory"],
                    }

                    daily_records.append(record)
                    logger.debug("✅ Registro %s: %s - %s - R$ %.2f", index + 1, date_str, creative, spend)

                except Exception as exc:  # pragma: no cover - logging preventivo
                    logger.warning("⚠️ Erro ao processar linha %s: %s", index, exc)
                    continue

            logger.info("✅ %s registros diários extraídos com SUCESSO", len(daily_records))
            return daily_records

        except Exception as exc:  # pragma: no cover
            logger.error("❌ Erro ao extrair dados diários REAIS: %s", exc)
            import traceback

            logger.error("❌ Traceback: %s", traceback.format_exc())
            return []

    def _extract_contract_data_real(self) -> Dict[str, Any]:
        """Extrair dados de contrato - VERSÃO QUE FUNCIONA"""
        try:
            logger.info("🔄 Extraindo dados de contrato REAIS...")

            df = self.sheets_service.read_sheet_data(
                self.config.sheet_id,
                sheet_name="Informações de contrato",
            )

            if df is None or df.empty:
                logger.warning("⚠️ DataFrame vazio da aba Informações de contrato")
                return self._get_default_contract()

            logger.info("✅ DataFrame de contrato carregado: %s linhas", len(df))
            logger.info("📊 Colunas de contrato: %s", list(df.columns))

            contract_dict: Dict[str, Any] = {}
            for index, row in df.iterrows():
                try:
                    if len(row) >= 2:
                        key = str(row.iloc[0]).strip()
                        value = str(row.iloc[1]).strip()
                        if key and value and value.lower() != "nan":
                            contract_dict[key] = value
                            logger.debug("✅ Contrato: %s = %s", key, value)
                except Exception as exc:  # pragma: no cover
                    logger.warning("⚠️ Erro ao processar linha de contrato %s: %s", index, exc)
                    continue

            result = {
                "client": self.config.client,
                "campaign": self.config.campaign,
                "investment": self._safe_float(contract_dict.get("Valor investido", 31000)),
                "cpv_contracted": self._safe_float(contract_dict.get("CPV", 0.16)),
                "complete_views_contracted": self._safe_int(contract_dict.get("Visualizações completas", 193750)),
                "impressions_contracted": self._safe_int(contract_dict.get("Impressões", 193750)),
                "period": contract_dict.get("Periodo de veiculação", "15/09/2025 - 30/09/2025"),
                "status": contract_dict.get("Status", "Em andamento"),
            }

            logger.info("✅ Dados de contrato extraídos com SUCESSO")
            return result

        except Exception as exc:  # pragma: no cover
            logger.error("❌ Erro ao extrair dados de contrato REAIS: %s", exc)
            import traceback

            logger.error("❌ Traceback: %s", traceback.format_exc())
            return self._get_default_contract()

    def _calculate_total_metrics(
        self, daily_data: List[Dict[str, Any]], contract_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calcular métricas totais dos dados diários"""
        if not daily_data:
            return {}

        total_spend = sum(record.get("spend", 0) for record in daily_data)
        total_investment = sum(record.get("investment", record.get("spend", 0)) for record in daily_data)
        total_impressions = sum(record.get("impressions", 0) for record in daily_data)
        total_clicks = sum(record.get("clicks", 0) for record in daily_data)
        total_starts = sum(record.get("starts", 0) for record in daily_data)
        total_q100 = sum(record.get("q100", 0) for record in daily_data)

        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        vtr = (total_starts / total_impressions * 100) if total_impressions > 0 else 0
        cpv = (total_spend / total_q100) if total_q100 > 0 else 0

        budget_contracted = None
        impressions_contracted = None
        complete_views_contracted = None
        if contract_data:
            budget_contracted = self._safe_float(contract_data.get("investment"))
            impressions_contracted = self._safe_int(contract_data.get("impressions_contracted"))
            complete_views_contracted = self._safe_int(contract_data.get("complete_views_contracted"))

        pacing = (total_spend / budget_contracted * 100) if budget_contracted else 0
        vc_pacing = (total_q100 / complete_views_contracted * 100) if complete_views_contracted else 0

        logger.info(
            "✅ Métricas totais calculadas: gasto=R$ %.2f, impressões=%s",
            total_spend,
            total_impressions,
        )

        return {
            "spend": total_spend,
            "investment": total_investment,
            "impressions": total_impressions,
            "clicks": total_clicks,
            "starts": total_starts,
            "q100": total_q100,
            "ctr": ctr,
            "cpm": cpm,
            "vtr": vtr,
            "cpv": cpv,
            "pacing": pacing,
            "vc_pacing": vc_pacing,
            "budget_contracted": budget_contracted,
            "impressions_contracted": impressions_contracted,
            "vc_contracted": complete_views_contracted,
        }

    def _aggregate_publishers(
        self,
        daily_data: List[Dict[str, Any]],
        contract_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Agrega dados diários por publisher/canal"""
        if not daily_data:
            return []

        aggregated: Dict[str, Dict[str, Any]] = {}
        total_spend = sum(record.get("spend", 0) for record in daily_data)
        total_budget = self._safe_float(contract_data.get("investment")) if contract_data else 0

        for record in daily_data:
            publisher_name = record.get("publisher") or record.get("channel") or "Publisher Padrão"
            publisher_name = publisher_name.strip() if isinstance(publisher_name, str) else "Publisher Padrão"
            if not publisher_name:
                publisher_name = "Publisher Padrão"

            entry = aggregated.setdefault(
                publisher_name,
                {
                    "name": publisher_name,
                    "channel": record.get("channel") or publisher_name,
                    "type": f"Canal: {record.get('channel') or publisher_name}",
                    "spend": 0.0,
                    "investment": 0.0,
                    "impressions": 0,
                    "clicks": 0,
                    "starts": 0,
                    "q100": 0,
                    "line_items": set(),
                    "inventory": set(),
                    "days": set(),
                },
            )

            entry["spend"] += record.get("spend", 0.0)
            entry["investment"] += record.get("investment", record.get("spend", 0.0))
            entry["impressions"] += record.get("impressions", 0)
            entry["clicks"] += record.get("clicks", 0)
            entry["starts"] += record.get("starts", 0)
            entry["q100"] += record.get("q100", 0)

            if record.get("line_item"):
                entry["line_items"].add(record["line_item"])
            if record.get("inventory"):
                entry["inventory"].add(record["inventory"])
            if record.get("date"):
                entry["days"].add(record["date"])

        publisher_list: List[Dict[str, Any]] = []
        for publisher in aggregated.values():
            impressions = publisher["impressions"]
            q100 = publisher["q100"]
            spend = publisher["spend"]

            ctr = (publisher["clicks"] / impressions * 100) if impressions else 0
            cpm = (spend / impressions * 1000) if impressions else 0
            vtr = (publisher["starts"] / impressions * 100) if impressions else 0
            cpv = (spend / q100) if q100 else 0
            pacing = (spend / total_budget * 100) if total_budget else 0
            share = (spend / total_spend * 100) if total_spend else 0

            publisher_list.append(
                {
                    "name": publisher["name"],
                    "channel": publisher["channel"],
                    "type": publisher["type"],
                    "spend": spend,
                    "investment": publisher["investment"],
                    "impressions": impressions,
                    "clicks": publisher["clicks"],
                    "starts": publisher["starts"],
                    "q100": q100,
                    "ctr": ctr,
                    "cpm": cpm,
                    "vtr": vtr,
                    "cpv": cpv,
                    "pacing": pacing,
                    "share": share,
                    "line_items": sorted(publisher["line_items"]),
                    "inventory": sorted(publisher["inventory"]),
                    "days": sorted(publisher["days"]),
                }
            )

        publisher_list.sort(key=lambda item: item["spend"], reverse=True)
        return publisher_list

    def _extract_publisher_info(self, row: pd.Series, creative: str) -> Dict[str, Optional[str]]:
        """Extrai informações de publisher e canal de uma linha"""
        publisher = self._get_first_nonempty(row, self.PUBLISHER_COLUMNS)
        channel = self._get_first_nonempty(row, self.CHANNEL_COLUMNS)
        line_item = self._get_first_nonempty(row, self.LINE_ITEM_COLUMNS)
        inventory = self._get_first_nonempty(row, ["Inventory", "Inventory Source", "Inventory source"])

        if not publisher:
            publisher = self._parse_publisher_from_creative(creative)
        if not channel:
            channel = publisher

        return {
            "publisher": publisher or "Publisher Padrão",
            "channel": channel or publisher or "Publisher Padrão",
            "line_item": line_item,
            "inventory": inventory,
        }

    def _get_default_contract(self) -> Dict[str, Any]:
        """Retornar dados de contrato padrão"""
        return {
            "client": self.config.client,
            "campaign": self.config.campaign,
            "investment": 31000,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "impressions_contracted": 193750,
            "period": "15/09/2025 - 30/09/2025",
            "status": "Em andamento",
        }

    def _parse_publisher_from_creative(self, creative: str) -> Optional[str]:
        if not creative:
            return None
        clean = creative.replace("_", " ")
        if "-" in clean:
            parts = [part.strip() for part in clean.split("-") if part.strip()]
            if parts:
                return parts[0]
        if "(" in clean:
            before_parentheses = clean.split("(")[0].strip()
            if before_parentheses:
                return before_parentheses
        return clean.strip() or None

    def _get_first_nonempty(self, row: pd.Series, candidates: List[str]) -> Optional[str]:
        for column in candidates:
            if column in row and not pd.isna(row[column]):
                value = str(row[column]).strip()
                if value and value.lower() != "nan":
                    return value
        return None

    def _safe_float(self, value) -> float:
        """Converter valor para float de forma segura"""
        try:
            if pd.isna(value) or value == "" or str(value).lower() == "nan":
                return 0.0
            return float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            return 0.0

    def _safe_int(self, value) -> int:
        """Converter valor para int de forma segura"""
        try:
            if pd.isna(value) or value == "" or str(value).lower() == "nan":
                return 0
            return int(float(str(value).replace(",", ".")))
        except (ValueError, TypeError):
            return 0


def extract_campaign_data(campaign_key: str) -> Optional[Dict[str, Any]]:
    """Função principal para extrair dados de uma campanha - VERSÃO QUE FUNCIONA"""
    try:
        from persistent_database import get_campaign_config

        config = get_campaign_config(campaign_key)
        if not config:
            logger.error("❌ Configuração não encontrada para campanha: %s", campaign_key)
            return None

        extractor = WorkingVideoExtractor(config)
        return extractor.extract_data()

    except Exception as exc:  # pragma: no cover
        logger.error("❌ Erro na função principal: %s", exc)
        import traceback

        logger.error("❌ Traceback: %s", traceback.format_exc())
        return None
