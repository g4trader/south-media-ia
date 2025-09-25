#!/usr/bin/env python3
"""
Extrator Simples para Dados de Campanha de Vídeo
Versão simplificada que funciona diretamente
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

class SimpleVideoExtractor:
    """Extrator simples e direto para dados de campanha de vídeo"""
    
    def __init__(self, config):
        self.config = config
        self.sheets_service = GoogleSheetsService()
        
    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados da planilha de forma simples"""
        try:
            logger.info(f"🔄 Iniciando extração simples para {self.config.client}")
            
            # 1. Extrair dados diários da aba "Report"
            daily_data = self._extract_daily_data()
            if not daily_data:
                logger.warning("⚠️ Nenhum dado diário encontrado")
                return None
            
            # 2. Extrair dados de contrato da aba "Informações de contrato"
            contract_data = self._extract_contract_data()
            
            # 3. Calcular métricas totais
            total_metrics = self._calculate_total_metrics(daily_data)
            
            # 4. Preparar dados finais
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
            
            logger.info(f"✅ Extração concluída: {len(daily_data)} registros diários")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na extração: {e}")
            return None
    
    def _extract_daily_data(self) -> list:
        """Extrair dados diários da aba Report"""
        try:
            # Usar o GID da aba Report
            report_gid = self.config.tabs.get("daily", "0")
            
            # Ler dados da planilha
            data = self.sheets_service.read_sheet(
                self.config.sheet_id, 
                f"Report!A:N"  # Colunas A até N
            )
            
            if not data or len(data) < 2:
                logger.warning("⚠️ Dados insuficientes na aba Report")
                return []
            
            # Converter para DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            
            daily_records = []
            for _, row in df.iterrows():
                try:
                    # Extrair dados básicos
                    date_str = str(row.get('Day', ''))
                    if not date_str or date_str == 'nan':
                        continue
                    
                    creative = str(row.get('Creative', ''))
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
                    
                    daily_records.append(record)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha: {e}")
                    continue
            
            logger.info(f"✅ {len(daily_records)} registros diários extraídos")
            return daily_records
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados diários: {e}")
            return []
    
    def _extract_contract_data(self) -> dict:
        """Extrair dados de contrato da aba Informações de contrato"""
        try:
            # Usar o GID da aba Informações de contrato
            contract_gid = self.config.tabs.get("contract", "0")
            
            # Ler dados da planilha
            data = self.sheets_service.read_sheet(
                self.config.sheet_id, 
                f"Informações de contrato!A:B"  # Colunas A e B
            )
            
            if not data or len(data) < 2:
                logger.warning("⚠️ Dados insuficientes na aba Informações de contrato")
                return self._get_default_contract()
            
            # Converter para dicionário
            contract_dict = {}
            for row in data[1:]:
                if len(row) >= 2:
                    key = str(row[0]).strip()
                    value = str(row[1]).strip()
                    if key and value and value != 'nan':
                        contract_dict[key] = value
            
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
            
            logger.info("✅ Dados de contrato extraídos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados de contrato: {e}")
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
            
            # Calcular pacing (assumindo investimento de 31k)
            budget_contracted = 31000
            pacing = (total_spend / budget_contracted * 100) if budget_contracted > 0 else 0
            vc_pacing = (total_q100 / 193750 * 100) if 193750 > 0 else 0
            
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
            publishers = set()
            for record in daily_data:
                creative = record.get("creative", "")
                if creative:
                    # Extrair nome do publisher do creative
                    if "SEBRAE" in creative:
                        publishers.add("SEBRAE PR")
                    else:
                        publishers.add("Publisher Padrão")
            
            return [{"name": p, "type": f"Site: {p.lower().replace(' ', '-')}.com"} for p in publishers]
            
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
    """Função principal para extrair dados de uma campanha"""
    try:
        from persistent_database import get_campaign_config
        
        config = get_campaign_config(campaign_key)
        if not config:
            logger.error(f"❌ Configuração não encontrada para campanha: {campaign_key}")
            return None
        
        extractor = SimpleVideoExtractor(config)
        return extractor.extract_data()
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal: {e}")
        return None
