#!/usr/bin/env python3
"""
Extrator genérico de dados para campanhas de vídeo programática
Substitui os extratores específicos por cliente
"""

import json
import pandas as pd
import sys
import os
import math
import numpy as np
from typing import Dict, List, Optional, Any

def safe_int_convert(value, default=0):
    """Converter valor para inteiro com segurança, tratando NaN"""
    try:
        numeric_val = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric_val) or np.isnan(numeric_val):
            return default
        return int(numeric_val)
    except:
        return default

def convert_nan_to_null(obj):
    """Converter NaN para null para compatibilidade com JSON"""
    if isinstance(obj, dict):
        return {key: convert_nan_to_null(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_null(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    else:
        return obj

# Adicionar diretório raiz ao path para importar google_sheets_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from google_sheets_service import GoogleSheetsService

# Mapeamento padrão de colunas
DEFAULT_COLUMN_MAPPING = {
    'date': 'Day',
    'creative': 'Creative',
    'impressions': 'Imps',
    'clicks': 'Clicks',
    'ctr': 'CTR %',
    'vtr': 'Video Completion Rate %',
    'starts': 'Video Starts',
    'spend': 'Valor investido',
    'cpv': 'CPV',
    'cpc': 'CPC',
    'q25': '25% Video Complete',
    'q50': '50% Video Complete',
    'q75': '75% Video Complete',
    'q100': '100% Complete'
}

# Mapeamento padrão de contrato
DEFAULT_CONTRACT_MAPPING = {
    'client': 'Cliente',
    'campaign': 'Campanha',
    'investment': 'Investimento',
    'cpv_contracted': 'CPV Contratado',
    'complete_views_contracted': 'Views Completas Contratadas',
    'period_start': 'Início',
    'period_end': 'Fim'
}

class VideoCampaignDataExtractor:
    """Extrator genérico para campanhas de vídeo programática"""
    
    def __init__(self, campaign_config):
        self.config = campaign_config
        self.sheets_service = GoogleSheetsService()
        
    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados da campanha"""
        try:
            print(f"📊 Extraindo dados da campanha: {self.config.client} - {self.config.campaign}")
            
            # Ler dados de todas as abas
            all_data = {}
            
            for tab_name, gid in self.config.tabs.items():
                print(f"📊 Lendo aba: {tab_name} (GID: {gid})")
                
                # Mapear nome da aba para nome real na planilha
                sheet_name = self._get_sheet_name(tab_name)
                df = self.sheets_service.read_sheet_data(self.config.sheet_id, sheet_name=sheet_name)
                
                if df is not None:
                    print(f"✅ Aba {tab_name}: {len(df)} linhas")
                    print(f"Colunas: {list(df.columns)}")
                    all_data[tab_name] = df
                else:
                    print(f"⚠️ Aba {tab_name}: Nenhum dado encontrado")
                    all_data[tab_name] = None
            
            # Processar dados específicos da campanha
            campaign_data = self._process_campaign_data(all_data)
            
            # Salvar dados processados
            output_file = f"{self.config.get_slug()}_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(campaign_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dados salvos em {output_file}")
            
            # Converter NaN para null para compatibilidade com JSON
            campaign_data = convert_nan_to_null(campaign_data)
            return campaign_data
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados: {e}")
            return None
    
    def _get_sheet_name(self, tab_name: str) -> str:
        """Mapear nome interno da aba para nome real na planilha"""
        sheet_name_mapping = {
            "daily_data": "Report",
            "contract": "Informações de contrato",
            "strategies": "Estratégias",
            "publishers": "Lista de publishers"
        }
        return sheet_name_mapping.get(tab_name, tab_name)
    
    def _process_campaign_data(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Processar dados específicos da campanha"""
        
        # Extrair dados de contratação
        contract_data = self._extract_contract_data(all_data.get("contract"))
        
        # Extrair dados de estratégias
        strategies_data = self._extract_strategies_data(all_data.get("strategies"))
        
        # Extrair lista de publishers
        publishers_data = self._extract_publishers_data(all_data.get("publishers"))
        
        # Dados da campanha
        campaign_data = {
            "campaign_name": f"{contract_data.get('client', self.config.client)} - {contract_data.get('campaign', self.config.campaign)}",
            "dashboard_title": f"Dashboard {contract_data.get('client', self.config.client)} - {contract_data.get('campaign', self.config.campaign)}",
            "channel": contract_data.get('channel', 'Prográmatica'),
            "creative_type": contract_data.get('creative_type', 'Video'),
            "period": f"{contract_data.get('period_start', '15/09/2025')} - {contract_data.get('period_end', '30/09/2025')}",
            "contract": contract_data,
            "strategies": strategies_data,
            "publishers": publishers_data,
            "metrics": {},
            "daily_data": [],
            "per_data": []
        }
        
        # Usar dados de contratação para métricas base
        campaign_data["budget_contracted"] = contract_data.get("investment", 0)
        campaign_data["vc_contracted"] = contract_data.get("complete_views_contracted", 0)
        
        # Processar dados diários
        df = all_data.get("daily_data")
        if df is not None:
            campaign_data.update(self._process_daily_data(df))
        
        return campaign_data
    
    def _extract_contract_data(self, df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Extrair dados de contratação"""
        default_contract = {
            "client": self.config.client,
            "campaign": self.config.campaign,
            "channel": "Prográmatica",
            "creative_type": "Video",
            "investment": 31000.00,
            "cpv_contracted": 0.16,
            "complete_views_contracted": 193750,
            "period_start": "15/09/2025",
            "period_end": "30/09/2025"
        }
        
        if df is None or df.empty:
            return default_contract
        
        contract_data = default_contract.copy()
        
        # Processar dados de contratação da planilha
        for _, row in df.iterrows():
            row_values = [str(val).strip() for val in row if str(val).strip() and str(val).strip() != 'nan']
            if len(row_values) >= 2:
                key = row_values[0].lower()
                value = row_values[1]
                
                # Mapear campos usando configuração padrão
                for planilha_key, data_key in DEFAULT_CONTRACT_MAPPING.items():
                    if planilha_key in key:
                        if data_key == 'investment':
                            numeric_value = float(pd.to_numeric(
                                value.replace('R$ ', '').replace('.', '').replace(',', '.')
                                .replace(r'[^\d.]', ''), 
                                errors='coerce'
                            ) or 0)
                            contract_data[data_key] = numeric_value
                        elif data_key == 'cpv_contracted':
                            numeric_value = float(pd.to_numeric(
                                value.replace('R$ ', '').replace(',', '.')
                                .replace(r'[^\d.]', ''), 
                                errors='coerce'
                            ) or 0)
                            contract_data[data_key] = numeric_value
                        elif data_key == 'complete_views_contracted':
                            numeric_value = int(pd.to_numeric(
                                value.replace(r'[^\d]', ''), 
                                errors='coerce'
                            ) or 0)
                            contract_data[data_key] = numeric_value
                        elif data_key == 'period' and len(row_values) >= 3:
                            contract_data["period_start"] = row_values[1]
                            contract_data["period_end"] = row_values[2]
                        else:
                            contract_data[data_key] = value
        
        return contract_data
    
    def _extract_strategies_data(self, df: Optional[pd.DataFrame]) -> Dict[str, List[str]]:
        """Extrair dados de estratégias"""
        default_strategies = {
            "segmentation": ["Microempreendedores", "Jovens Empreendedores em Ascensão"],
            "objectives": ["Alcance em PARANÁ", "White list para grandes portais"]
        }
        
        if df is None or df.empty:
            return default_strategies
        
        strategies_data = {
            "segmentation": [],
            "objectives": []
        }
        
        # Processar estratégias da planilha
        for _, row in df.iterrows():
            row_values = [str(val).strip() for val in row if str(val).strip() and str(val).strip() != 'nan']
            if len(row_values) >= 2:
                key = row_values[0].lower()
                value = row_values[1]
                
                if 'segmentações' in key:
                    if 'microempreendedor' in value.lower():
                        strategies_data["segmentation"].append("Microempreendedores")
                    if 'jovem' in value.lower() and 'empreendedor' in value.lower():
                        strategies_data["segmentation"].append("Jovens Empreendedores em Ascensão")
                elif 'praças' in key:
                    strategies_data["objectives"].append(f"Alcance em {value}")
                elif 'white list' in key:
                    strategies_data["objectives"].append("White list para grandes portais")
        
        return strategies_data
    
    def _extract_publishers_data(self, df: Optional[pd.DataFrame]) -> List[Dict[str, str]]:
        """Extrair lista de publishers"""
        default_publishers = [
            {"name": "Gazeta do Povo", "type": "Site: gazetadopovo.com.br"},
            {"name": "Bem Paraná", "type": "Site: bemparana.com.br"},
            {"name": "Tribuna PR", "type": "Site: tribunapr.com.br"},
            {"name": "Bonde", "type": "Site: bonde.com.br"},
            {"name": "Massa News", "type": "Site: massanews.com"}
        ]
        
        if df is None or df.empty:
            return default_publishers
        
        publishers_data = []
        
        # Processar publishers da planilha
        for _, row in df.iterrows():
            row_values = [str(val).strip() for val in row if str(val).strip() and str(val).strip() != 'nan']
            if len(row_values) >= 2:
                name = row_values[0]
                url = row_values[1]
                if name and url:
                    publishers_data.append({
                        "name": name,
                        "type": f"Site: {url}"
                    })
        
        return publishers_data
    
    def _process_daily_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processar dados diários e calcular métricas"""
        
        # Mapear colunas
        available_columns = {}
        for standard_col, sheet_col in DEFAULT_COLUMN_MAPPING.items():
            if sheet_col in df.columns:
                available_columns[standard_col] = sheet_col
        
        print(f"Colunas mapeadas: {available_columns}")
        
        # Calcular métricas totais
        total_metrics = {}
        for metric, column in available_columns.items():
            if column in df.columns:
                if metric == 'spend':
                    # Remover "R$ " e converter vírgula para ponto
                    numeric_values = pd.to_numeric(
                        df[column].astype(str).str.replace('R$ ', '')
                        .str.replace('.', '')
                        .str.replace(',', '.')
                        .str.replace(r'[^\d.]', ''), 
                        errors='coerce'
                    )
                else:
                    numeric_values = pd.to_numeric(
                        df[column].astype(str).str.replace(r'[^\d.,]', '')
                        .str.replace(',', '.'), 
                        errors='coerce'
                    )
                total_metrics[metric] = int(numeric_values.sum())
            else:
                total_metrics[metric] = 0
        
        # Calcular métricas derivadas
        if total_metrics.get('impressions', 0) > 0:
            total_metrics['ctr'] = (total_metrics.get('clicks', 0) / total_metrics['impressions']) * 100
            total_metrics['cpm'] = (total_metrics.get('spend', 0) / total_metrics['impressions']) * 1000
            total_metrics['cpc'] = total_metrics.get('spend', 0) / max(total_metrics.get('clicks', 1), 1)
        
        if total_metrics.get('starts', 0) > 0:
            total_metrics['vtr'] = (total_metrics.get('q100', 0) / total_metrics['starts']) * 100
        
        # Calcular pacing
        budget_contracted = 31000  # Valor padrão, pode ser sobrescrito
        total_metrics['pacing'] = (total_metrics.get('spend', 0) / budget_contracted) * 100
        
        # Processar dados diários
        daily_data = []
        for _, row in df.iterrows():
            date_value = str(row.get(available_columns.get('date', ''), ''))
            if not date_value or date_value == 'nan':
                continue
            
            # Processar spend
            spend_value = 0
            if available_columns.get('spend') and available_columns['spend'] in df.columns:
                spend_str = str(row.get(available_columns['spend'], '0'))
                spend_value = float(pd.to_numeric(
                    spend_str.replace('R$ ', '').replace('.', '').replace(',', '.')
                    .replace(r'[^\d.]', ''), 
                    errors='coerce'
                ) or 0)
            
            daily_row = {
                "date": date_value,
                "creative": str(row.get(available_columns.get('creative', ''), '')),
                "spend": spend_value,
                "impressions": safe_int_convert(row.get(available_columns.get('impressions', 0), 0)),
                "clicks": safe_int_convert(row.get(available_columns.get('clicks', 0), 0)),
                "starts": safe_int_convert(row.get(available_columns.get('starts', 0), 0)),
                "q25": safe_int_convert(row.get(available_columns.get('q25', 0), 0)),
                "q50": safe_int_convert(row.get(available_columns.get('q50', 0), 0)),
                "q75": safe_int_convert(row.get(available_columns.get('q75', 0), 0)),
                "q100": safe_int_convert(row.get(available_columns.get('q100', 0), 0)),
                "ctr": float(pd.to_numeric(row.get(available_columns.get('ctr', 0), 0), errors='coerce') or 0),
                "vtr": float(pd.to_numeric(row.get(available_columns.get('vtr', 0), 0), errors='coerce') or 0),
                "cpv": float(pd.to_numeric(row.get(available_columns.get('cpv', 0), 0), errors='coerce') or 0)
            }
            daily_data.append(daily_row)
        
        return {
            "metrics": total_metrics,
            "daily_data": daily_data,
            "per_data": []  # Pode ser implementado posteriormente
        }

def extract_campaign_data(campaign_key: str) -> Optional[Dict[str, Any]]:
    """Função principal para extrair dados de uma campanha"""
    from campaign_config import get_campaign_config
    
    config = get_campaign_config(campaign_key)
    if not config:
        print(f"❌ Configuração não encontrada para campanha: {campaign_key}")
        return None
    
    extractor = VideoCampaignDataExtractor(config)
    return extractor.extract_data()

if __name__ == "__main__":
    # Teste com campanha SEBRAE
    print("🧪 Testando extrator genérico...")
    data = extract_campaign_data("sebrae_pr")
    
    if data:
        print("✅ Extração bem-sucedida!")
        print(f"📊 Cliente: {data.get('contract', {}).get('client', 'N/A')}")
        print(f"📊 Campanha: {data.get('contract', {}).get('campaign', 'N/A')}")
        print(f"📊 Publishers: {len(data.get('publishers', []))}")
    else:
        print("❌ Falha na extração")
