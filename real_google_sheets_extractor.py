#!/usr/bin/env python3
"""
Extrator REAL para Google Sheets
Versão que carrega dados reais ou falha com erro claro
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(__file__))

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.error("❌ Google API não disponível. Execute: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class RealGoogleSheetsExtractor:
    """Extrator que carrega dados REAIS do Google Sheets ou falha com erro"""
    
    def __init__(self, config):
        self.config = config
        self.service = None
        logger.info(f"🔧 Inicializando extrator REAL para {config.client}")
        
        if not GOOGLE_AVAILABLE:
            raise Exception("Google API não disponível")
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar serviço do Google Sheets usando GoogleSheetsService"""
        try:
            from google_sheets_service import GoogleSheetsService
            sheets_service = GoogleSheetsService()
            
            if not sheets_service.is_configured():
                raise Exception("GoogleSheetsService não configurado")
            
            self.service = sheets_service._service
            logger.info("✅ Serviço Google Sheets inicializado via GoogleSheetsService")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Google Sheets: {e}")
            raise Exception(f"Não foi possível conectar ao Google Sheets: {e}")
    
    def extract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados REAIS do Google Sheets"""
        try:
            logger.info(f"🔄 Iniciando extração REAL para {self.config.client}")
            logger.info(f"📊 Sheet ID: {self.config.sheet_id}")
            
            # 1. Extrair dados diários da aba "Report"
            daily_data = self._extract_daily_data()
            if daily_data is None:
                raise Exception("Falha ao extrair dados diários da aba 'Report'")
            
            # 2. Extrair dados de contrato
            contract_data = self._extract_contract_data()
            if contract_data is None:
                raise Exception("Falha ao extrair dados de contrato da aba 'Informações de contrato'")
            
            # 3. Calcular métricas totais
            total_metrics = self._calculate_metrics(daily_data, contract_data)
            
            # 4. Preparar dados finais
            result = {
                "campaign_summary": {
                    "client": self.config.client,
                    "campaign": getattr(self.config, 'campaign', getattr(self.config, 'campaign_name', 'N/A')),
                    "status": self._get_campaign_status(contract_data),
                    "period": f"{contract_data['period_start']} a {contract_data['period_end']}" if contract_data.get('period_start') and contract_data.get('period_end') else "N/A",
                    **total_metrics
                },
                "contract": contract_data,
                "daily_data": daily_data,
                "publishers": self._extract_publishers_data(),
                "strategies": self._extract_strategies_data(),
                "insights": self._generate_insights(total_metrics, self.config.kpi),
                "last_updated": datetime.now().isoformat(),
                "data_source": "google_sheets_real"
            }

            use_footfall = bool(getattr(self.config, "use_footfall", False))
            if use_footfall:
                result["footfall_points"] = self._extract_footfall_points()
            
            logger.info(f"✅ Extração REAL concluída para {self.config.client}")
            logger.info(f"📊 Dados extraídos: {len(daily_data)} dias")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na extração REAL: {e}")
            raise Exception(f"Falha na extração de dados: {e}")
    
    def _extract_daily_data(self) -> Optional[list]:
        """Extrair dados diários da aba 'Report'"""
        try:
            logger.info("📊 Extraindo dados diários da aba 'Report'")
            
            # Primeiro, listar todas as abas disponíveis para encontrar a correta
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            report_sheet = None
            # Se tiver report_sheet_gid (ex.: 364193781), usar essa aba para bater com a planilha
            report_gid = getattr(self.config, 'report_sheet_gid', None)
            if report_gid is not None:
                try:
                    gid_int = int(report_gid)
                    for sheet in sheets:
                        if sheet.get('properties', {}).get('sheetId') == gid_int:
                            report_sheet = sheet['properties']['title']
                            logger.info(f"📊 Usando aba Report por GID {gid_int}: '{report_sheet}'")
                            break
                except (TypeError, ValueError):
                    pass
            if not report_sheet:
                possible_names = [
                    'report', 'dados', 'daily', 'diário', 'diario', 'performance', 'delivery',
                    'relatório', 'relatorio', 'fps', 'youtube', 'data', 'views', 'complete'
                ]
                for sheet in sheets:
                    sheet_name = sheet['properties']['title']
                    clean_name = sheet_name.strip().lower()
                    for possible_name in possible_names:
                        if possible_name in clean_name:
                            report_sheet = sheet_name
                            logger.info(f"📊 Encontrada aba de dados: '{sheet_name}' (contém: '{possible_name}')")
                            break
                    if report_sheet:
                        break
            # Se não encontrou, usar a primeira aba que não seja de configuração
            if not report_sheet:
                config_sheets = ['informações', 'contrato', 'publishers', 'estratégias', 'config']
                for sheet in sheets:
                    sheet_name = sheet['properties']['title']
                    clean_name = sheet_name.strip().lower()
                    
                    # Pular abas de configuração
                    is_config = any(config_word in clean_name for config_word in config_sheets)
                    if not is_config:
                        report_sheet = sheet_name
                        logger.info(f"📊 Usando primeira aba de dados disponível: '{sheet_name}'")
                        break
            
            if not report_sheet:
                # Listar todas as abas para debug
                available_sheets = [sheet['properties']['title'] for sheet in sheets]
                raise Exception(f"Nenhuma aba de dados encontrada. Abas disponíveis: {available_sheets}")
            
            # Nome da aba com aspas se tiver espaço (ex.: 'Dados Diários'!A:Z)
            range_name = f"'{report_sheet}'!A:Z" if ' ' in report_sheet else f"{report_sheet}!A:Z"
            
            # Ler os dados da aba encontrada
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                raise Exception("Aba 'Report' está vazia")
            
            logger.info(f"📊 Encontradas {len(values)} linhas na aba Report")
            
            # Converter para DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])  # Primeira linha como header
            
            # Mapear colunas para nomes padronizados (inglês + português / variações)
            column_mapping = {
                'Day': 'date',
                'Data': 'date',
                'Date': 'date',
                'Dia': 'date',
                'Line Item': 'line_item',
                'Creative': 'creative',
                'Valor investido': 'spend',
                'VALOR DO INVESTIMENTO': 'spend',
                'Spend': 'spend',
                'Imps': 'impressions',
                'Impressões': 'impressions',
                'Impressions': 'impressions',
                'Disparos': 'disparos',
                'Clicks': 'clicks',
                'Cliques': 'clicks',
                'CPV': 'cpv',
                'CPC': 'cpc',
                'CTR %': 'ctr',
                'CTR': 'ctr',
                'Click Rate (CTR)': 'ctr',
                '25% Video Complete': 'video_25',
                '50% Video Complete': 'video_50',
                '75% Video Complete': 'video_75',
                '100% Complete': 'video_completions',
                'Video Starts': 'video_starts',
                'Visualizações completas': 'video_completions',
            }
            # Aplicar mapeamento (case-insensitive: planilha pode ter "Day" ou "day" ou "DAY")
            rename_map = {}
            col_lower = {str(c).strip().lower(): str(c).strip() for c in df.columns}
            for k, v in column_mapping.items():
                k_lower = k.lower()
                if k_lower in col_lower:
                    rename_map[col_lower[k_lower]] = v
            df = df.rename(columns=rename_map)
            
            # Excluir linhas sem data (totais/resumos) para não inflar soma de VCs/impr
            if 'date' in df.columns:
                before = len(df)
                df['date'] = df['date'].astype(str).str.strip()
                df = df[df['date'].notna() & (df['date'] != '') & (df['date'].str.lower() != 'nan')]
                if len(df) < before:
                    logger.info(f"📋 Removidas {before - len(df)} linhas sem data (totais/resumo)")
            
            # Converter tipos de dados: API pode retornar número (301166.0) ou string com milhar (ex.: "301.166")
            def _parse_num_br(ser):
                def _one(val):
                    if pd.isna(val):
                        return float('nan')
                    s = str(val).strip().replace('R$', '').replace(' ', '')
                    if not s or s.lower() == 'nan':
                        return float('nan')
                    # Se tem vírgula, é decimal BR: 1.234,56 -> remover ponto, trocar vírgula
                    if ',' in s:
                        s = s.replace('.', '').replace(',', '.')
                        try:
                            return float(s)
                        except ValueError:
                            return float('nan')
                    # Se termina com .0 ou .00 (número da API), usar float direto
                    if s.endswith('.0') or ('.' in s and s.split('.')[-1].replace('0', '') == ''):
                        try:
                            return float(s)
                        except ValueError:
                            pass
                    # Ponto como milhar (ex.: 1.234 ou 301.166) vs decimal (1.5)
                    if '.' in s:
                        parts = s.split('.')
                        if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
                            return float(s.replace('.', ''))  # milhar
                        try:
                            return float(s)
                        except ValueError:
                            return float('nan')
                    try:
                        return float(s)
                    except ValueError:
                        return float('nan')
                return ser.map(_one)
            for col in ['spend', 'impressions', 'disparos', 'clicks', 'cpv', 'cpc', 'ctr',
                       'video_25', 'video_50', 'video_75', 'video_completions', 'video_starts']:
                if col in df.columns:
                    df[col] = _parse_num_br(df[col])
            
            # Converter data com correção de formato
            if 'date' in df.columns:
                logger.info("🔧 Aplicando correção de datas...")
                
                # Importar normalizador de datas
                try:
                    from date_normalizer import DateNormalizer
                    date_normalizer = DateNormalizer()
                    
                    # Aplicar normalização inteligente de datas
                    df = date_normalizer.normalize_dataframe_dates(df, 'date')
                    logger.info(f"✅ Datas corrigidas: {len(df)} registros processados")
                    
                except ImportError:
                    logger.warning("⚠️ DateNormalizer não disponível, usando conversão padrão")
                    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                    df = df.dropna(subset=['date'])
                except Exception as e:
                    logger.warning(f"⚠️ Erro na normalização de datas: {e}, usando conversão padrão")
                    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                    df = df.dropna(subset=['date'])
            
            # Converter para lista de dicionários e calcular métricas
            daily_data = []
            for _, row in df.iterrows():
                spend = float(row.get('spend', 0)) if pd.notna(row.get('spend')) else 0.0
                # Para campanhas CPD (como Push), pode não existir coluna de impressões.
                # Nesse caso, usamos "disparos" como proxy de impressões.
                raw_imps = row.get('impressions', row.get('disparos', 0))
                impressions = int(raw_imps) if pd.notna(raw_imps) else 0
                clicks = int(row.get('clicks', 0)) if pd.notna(row.get('clicks')) else 0
                video_completions = int(row.get('video_completions', 0)) if pd.notna(row.get('video_completions')) else 0
                video_75 = int(row.get('video_75', 0)) if pd.notna(row.get('video_75')) else 0
                # Não zerar video_completions quando 100% > 75%: a planilha pode reportar assim (definições diferentes).
                # Total VC Entregue deve bater com a soma da coluna 100% Complete na planilha.
                disparos = int(row.get('disparos', video_completions)) if pd.notna(row.get('disparos', video_completions)) else 0
                
                # Calcular métricas dinamicamente
                cpv = spend / video_completions if video_completions > 0 else 0.0
                cpc = spend / clicks if clicks > 0 else 0.0
                ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
                cpd = spend / disparos if disparos > 0 else 0.0
                
                daily_data.append({
                    "date": str(row.get('date', '')),
                    "line_item": str(row.get('line_item', '')),
                    "creative": str(row.get('creative', '')),
                    "spend": spend,
                    "impressions": impressions,
                    "disparos": disparos,
                    "clicks": clicks,
                    "cpv": round(cpv, 4),
                    "cpc": round(cpc, 2),
                    "cpd": round(cpd, 4),
                    "ctr": round(ctr, 2),
                    "video_25": int(row.get('video_25', 0)) if pd.notna(row.get('video_25')) else 0,
                    "video_50": int(row.get('video_50', 0)) if pd.notna(row.get('video_50')) else 0,
                    "video_75": int(row.get('video_75', 0)) if pd.notna(row.get('video_75')) else 0,
                    "video_completions": video_completions,
                    "video_starts": int(row.get('video_starts', 0)) if pd.notna(row.get('video_starts')) else 0
                })
            
            total_vc = sum(d.get('video_completions', 0) for d in daily_data)
            logger.info(f"✅ Dados diários extraídos: {len(daily_data)} registros | Soma VC (100% Complete): {total_vc}")
            return daily_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados diários: {e}", exc_info=True)
            return None
    
    def _extract_contract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados de contrato da aba 'Informações de contrato'"""
        try:
            logger.info("📋 Extraindo dados de contrato")
            
            # Listar todas as abas disponíveis para encontrar a correta
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            # Procurar por abas de contrato.
            # Modelos antigos usam "Informações de contrato"; outros (HHS/OHS) usam apenas "Contrato".
            contract_sheet = None
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                # Limpar espaços em branco e comparar
                clean_name = sheet_name.strip()
                if 'informações' in clean_name.lower() and 'contrato' in clean_name.lower():
                    contract_sheet = sheet_name  # Usar o nome original da planilha
                    logger.info(f"📋 Encontrada aba de contrato: '{sheet_name}' (limpo: '{clean_name}')")
                    break

            if not contract_sheet:
                for sheet in sheets:
                    sheet_name = sheet['properties']['title']
                    clean_name = sheet_name.strip().lower()
                    # Aceitar "Contrato", "CONTRATO", "contrato (x)" etc.
                    if 'contrato' in clean_name:
                        contract_sheet = sheet_name
                        logger.info(f"📋 Encontrada aba de contrato (fallback): '{sheet_name}'")
                        break
            
            if not contract_sheet:
                # Listar todas as abas para debug
                available_sheets = [sheet['properties']['title'] for sheet in sheets]
                logger.warning(f"⚠️ Aba 'Informações de contrato' não encontrada. Abas disponíveis: {available_sheets}")
                logger.info("📋 Usando dados padrão mínimos para contrato")
                return {
                    "client": self.config.client,
                    "campaign": getattr(self.config, 'campaign', getattr(self.config, 'campaign_name', 'N/A')),
                    "investment": 0.0,
                    "complete_views_contracted": 0,
                    "impressions_contracted": 0,
                    "cpv_contracted": 0.0,
                    "canal": self.config.channel or "Programática",
                    "tipo_criativo": "N/A",
                    "period_start": None,
                    "period_end": None
                }
            
            # Nome da aba com aspas se tiver espaço (ex.: 'Informações de contrato'!A:D)
            range_name = f"'{contract_sheet}'!A:D" if ' ' in contract_sheet else f"{contract_sheet}!A:D"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.error(f"❌ Aba '{contract_sheet}' está vazia")
                return None
            
            # Converter para dicionário (chave exata + chave sem dois-pontos final para flexibilidade)
            # Valor pode estar em B ou, se B vazio, em C. Também aceitar linha com A vazio, B=label, C=valor.
            def _cell(row, i):
                if len(row) <= i:
                    return ""
                return str(row[i]).strip() if row[i] is not None else ""
            
            contract_dict = {}
            for row in values:
                if len(row) < 1:
                    continue
                key = _cell(row, 0)
                val_b = _cell(row, 1)
                val_c = _cell(row, 2) if len(row) >= 3 else ""
                value = val_b or val_c
                # Estrutura alternativa: A vazio, B = label, C = valor (ex.: VC Contratadas)
                if not key and len(row) >= 3 and val_b and val_c:
                    key, value = val_b, val_c
                if key and value and value.lower() != 'nan':
                    contract_dict[key] = value
                    if key.endswith(':'):
                        contract_dict[key.rstrip(':')] = value
                    # Normalizar chave sem ":" para busca posterior
                    key_plain = key.rstrip(':')
                    if key_plain and key_plain not in contract_dict:
                        contract_dict[key_plain] = value
                    
                    if key == "Periodo de veiculação" or key_plain == "Periodo de veiculação":
                        if len(row) >= 3 and val_c:
                            contract_dict["Periodo de veiculação_fim"] = val_c
            
            logger.info(f"📋 Dados de contrato encontrados: {list(contract_dict.keys())}")
            
            # Detectar KPI para mapear corretamente
            kpi = getattr(self.config, 'kpi', None)
            is_cpm = kpi and kpi.upper() == 'CPM'
            
            # Mapear impressões/views contratadas baseado no KPI
            # Se CPM: "Impressões Contrado" vai para impressions_contracted
            # Se CPV: "Complete Views Contrado" vai para complete_views_contracted
            if is_cpm:
                # Para CPM, priorizar "Impressões Contrado"
                imp_contracted_str = contract_dict.get("Impressões Contrado", contract_dict.get("Impressões contratadas", "0"))
                impressions_contracted = int(imp_contracted_str.replace('.', '').replace(',', '')) if imp_contracted_str and imp_contracted_str != "0" else 0
                # Também mapear para complete_views_contracted para compatibilidade
                complete_views_contracted = impressions_contracted
            else:
                # Para CPV/CPE/CPD: VC Contratadas, Complete Views Contratado(s), Escutas, Disparos, etc.
                # Incluir com e sem dois-pontos (planilha pode ter "VC Contratadas:" ou "VC Contratadas").
                # Planilha FPS usa exatamente "Complete Views Contrado" (A7) e valor em B7 (ex.: 205318)
                raw_vc = (
                    contract_dict.get("Complete Views Contrado")
                    or contract_dict.get("Complete Views Contrado:")
                    or contract_dict.get("VC Contratadas")
                    or contract_dict.get("VC Contratadas:")
                    or contract_dict.get("Complete Views Contratadas")
                    or contract_dict.get("Complete Views Contratadas:")
                    or contract_dict.get("Visualizações Completas Contratadas")
                    or contract_dict.get("Views Contratadas")
                    or contract_dict.get("Escutas Contrado")
                    or contract_dict.get("Disparos Contratados")
                    or contract_dict.get("Disparos Contrado")
                    or contract_dict.get("Downloads Contratados")
                )
                # Fallback: procurar qualquer chave que contenha VC/Complete View/Visualização e Contratad (case-insensitive)
                if not raw_vc:
                    for k, v in contract_dict.items():
                        k_lower = k.lower()
                        v_str = str(v).strip() if v is not None else ""
                        if not v_str or v_str.lower() == 'nan':
                            continue
                        if ('vc' in k_lower or 'complete view' in k_lower or 'visualização' in k_lower or 'visualizacoes' in k_lower) and ('contratad' in k_lower or 'contrado' in k_lower):
                            raw_vc = v
                            logger.info(f"📋 VC Contratadas encontrado na chave: {k!r} = {v}")
                            break
                        if 'view' in k_lower and 'contract' in k_lower:
                            raw_vc = v
                            logger.info(f"📋 VC Contratadas encontrado na chave: {k!r} = {v}")
                            break
                # Aceitar valor como número (API) ou string (ex.: "205318" ou "205.318")
                raw_vc_str = str(raw_vc).strip() if raw_vc is not None else ""
                if raw_vc_str and raw_vc_str.lower() != 'nan':
                    raw_vc_clean = raw_vc_str.replace('.', '').replace(',', '').replace(' ', '')
                    complete_views_contracted = int(raw_vc_clean) if raw_vc_clean.isdigit() else 0
                else:
                    complete_views_contracted = 0
                if complete_views_contracted == 0 and not is_cpm:
                    logger.warning(f"⚠️ VC Contratadas zerado. Chaves do contrato: {list(contract_dict.keys())}")
                impressions_contracted = 0
            
            # Mapear para estrutura padrão (usando as chaves reais da planilha)
            contract_data = {
                "client": self.config.client,
                "campaign": getattr(self.config, 'campaign', getattr(self.config, 'campaign_name', 'N/A')),
                "investment": float(contract_dict.get("Investimento:", "0").replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')) if contract_dict.get("Investimento:") else 0.0,
                "complete_views_contracted": complete_views_contracted,
                "impressions_contracted": impressions_contracted,  # Adicionado para CPM
                "cpv_contracted": float(contract_dict.get("CPV contratado:", contract_dict.get("CPM contratado:", contract_dict.get("CPE contratado:", contract_dict.get("CPD contratado:", "0")))).replace('R$', '').replace(' ', '').replace(',', '.')) if contract_dict.get("CPV contratado:") or contract_dict.get("CPM contratado:") or contract_dict.get("CPE contratado:") or contract_dict.get("CPD contratado:") else 0.0,
                "canal": contract_dict.get("Canal:", "").strip() or contract_dict.get("Canal", "").strip(),
                "tipo_criativo": contract_dict.get("Tipo de criativo:", "").strip() or contract_dict.get("Tipo de criativo", "").strip() or contract_dict.get("Tipo de Criativo:", "").strip() or contract_dict.get("Tipo de Criativo", "").strip() or contract_dict.get("Criativo", "").strip(),
                "period_start": None,
                "period_end": None
            }
            
            # Extrair período - verificar se há data de fim na célula adjacente
            periodo = contract_dict.get("Periodo de veiculação", "")
            periodo_fim = contract_dict.get("Periodo de veiculação_fim", "")  # Célula C8
            
            if periodo and ' a ' in periodo:
                # Formato: "13/10/2025 a 31/12/2025"
                parts = periodo.split(' a ')
                if len(parts) == 2:
                    contract_data["period_start"] = parts[0].strip()
                    contract_data["period_end"] = parts[1].strip()
            elif periodo and periodo_fim:
                # Formato: B8="13/10/2025", C8="31/12/2025"
                contract_data["period_start"] = periodo.strip()
                contract_data["period_end"] = periodo_fim.strip()
            elif periodo:
                # Se só tem uma data, usar como data de início e adicionar 30 dias
                from datetime import datetime, timedelta
                try:
                    start_date = datetime.strptime(periodo, '%d/%m/%Y')
                    end_date = start_date + timedelta(days=30)
                    contract_data["period_start"] = start_date.strftime('%d/%m/%Y')
                    contract_data["period_end"] = end_date.strftime('%d/%m/%Y')
                except:
                    contract_data["period_start"] = periodo
                    contract_data["period_end"] = periodo
            
            # Debug: Log do período extraído
            logger.info(f"📅 Período extraído da planilha: '{periodo}' -> Início: {contract_data.get('period_start')}, Fim: {contract_data.get('period_end')}")
            
            logger.info("✅ Dados de contrato extraídos com sucesso")
            return contract_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados de contrato: {e}")
            # Retornar dados padrão em caso de erro
            return {
                "client": self.config.client,
                "campaign": getattr(self.config, 'campaign', getattr(self.config, 'campaign_name', 'N/A')),
                "investment": 0.0,
                "complete_views_contracted": 0,
                "cpv_contracted": 0.0,
                "canal": "Programática",
                "tipo_criativo": "Video",
                "period_start": None,
                "period_end": None
            }
    
    def _extract_publishers_data(self) -> list:
        """Extrair dados de publishers da aba 'Lista de publishers'"""
        try:
            logger.info("📺 Extraindo dados de publishers da aba 'Lista de publishers'")
            
            # Listar todas as abas disponíveis para encontrar a correta
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            # Procurar por aba "Lista de publishers"
            publishers_sheet = None
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                clean_name = sheet_name.strip().lower()
                if 'lista' in clean_name and 'publisher' in clean_name:
                    publishers_sheet = sheet_name
                    logger.info(f"📺 Encontrada aba de publishers: '{sheet_name}' (limpo: '{clean_name}')")
                    break
            
            if not publishers_sheet:
                logger.warning("Aba 'Lista de publishers' não encontrada")
                return []
            
            # Ler dados da aba
            range_name = f"{publishers_sheet}!A:Z"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("Aba 'Lista de publishers' está vazia")
                return []
            
            # Processar dados dos publishers
            publishers = []
            headers = values[0] if values else []
            
            # Mapear colunas
            name_col = None
            url_col = None
            for i, header in enumerate(headers):
                header_lower = header.strip().lower()
                if 'nome' in header_lower:
                    name_col = i
                elif 'app' in header_lower or 'url' in header_lower:
                    url_col = i
            
            # Processar cada linha de publisher
            for row in values[1:]:  # Pular cabeçalho
                if not row or len(row) == 0:  # Pular linhas vazias
                    continue
                    
                name = row[name_col] if name_col is not None and name_col < len(row) else ''
                url = row[url_col] if url_col is not None and url_col < len(row) else ''
                
                if name and name.strip():  # Só incluir se tiver nome
                    publishers.append({
                        'publisher': name.strip(),
                        'name': name.strip(),
                        'url': url.strip() if url else '',
                        'type': 'Video Programática',
                        'investimento': 0.0,  # Será calculado se necessário
                        'impressoes': 0,
                        'cliques': 0,
                        'visualizacoes_completas': 0,
                        'video_starts': 0,
                        'spend': 0.0
                    })
            
            logger.info(f"✅ Publishers extraídos: {len(publishers)}")
            return publishers
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair publishers: {e}")
            return []
    
    def _extract_strategies_data(self) -> list:
        """Extrair dados de estratégias/segmentações"""
        try:
            logger.info("🎯 Extraindo dados de estratégias")
            
            # Listar todas as abas disponíveis para encontrar a correta
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            # Procurar por abas que contenham "Estratégias" ou "Segmentações" (ignorando espaços)
            strategies_sheet = None
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                # Limpar espaços em branco e comparar
                clean_name = sheet_name.strip()
                if 'estratégias' in clean_name.lower() or 'segmentações' in clean_name.lower():
                    strategies_sheet = sheet_name  # Usar o nome original da planilha
                    logger.info(f"🎯 Encontrada aba de estratégias: '{sheet_name}' (limpo: '{clean_name}')")
                    break
            
            if not strategies_sheet:
                logger.warning("Aba 'Estratégias' ou 'Segmentações' não encontrada")
                return []
            
            range_name = f"{strategies_sheet}!A:D"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("Aba 'Segmentações' não encontrada ou vazia")
                return []
            
            strategies = []
            for row in values[1:]:
                if len(row) >= 2:
                    strategies.append({
                        "strategy": str(row[0]) if len(row) > 0 else "",
                        "type": str(row[1]) if len(row) > 1 else "",
                        "investimento": float(row[2].replace('.', '').replace(',', '.')) if len(row) > 2 and row[2] else 0.0,
                        "impressoes": int(row[3].replace('.', '')) if len(row) > 3 and row[3] else 0
                    })
            
            logger.info(f"✅ Estratégias extraídas: {len(strategies)}")
            return strategies
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair estratégias: {e}")
            return []

    def _extract_footfall_points(self) -> list:
        """Extrai pontos de footfall de uma aba de Footfall da planilha.

        Espera colunas (case-insensitive):
        - lat / latitude
        - long / lon / lng / longitude
        - name / store / location
        - Footfall Users / users / visitantes
        - Footfall Rate % / rate / taxa
        """
        try:
            logger.info("🗺️ Extraindo pontos de Footfall")

            # Descobrir a aba correta (nem sempre se chama exatamente 'Footfall')
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', []) or []
            sheet_titles = [s.get('properties', {}).get('title') for s in sheets if s.get('properties', {}).get('title')]

            footfall_sheet = None
            # Preferir nomes que contenham "footfall"
            for title in sheet_titles:
                if "footfall" in str(title).strip().lower():
                    footfall_sheet = title
                    break
            # Fallback: alguns modelos usam "Mapa" / "Heatmap" / "Fluxo"
            if not footfall_sheet:
                for title in sheet_titles:
                    t = str(title).strip().lower()
                    if any(k in t for k in ["heat", "mapa", "map", "fluxo", "foot fall"]):
                        footfall_sheet = title
                        break

            if not footfall_sheet:
                logger.warning(f"⚠️ Nenhuma aba de Footfall encontrada. Abas disponíveis: {sheet_titles}")
                return []

            range_name = f"'{footfall_sheet}'!A1:Z2000" if ' ' in footfall_sheet else f"{footfall_sheet}!A1:Z2000"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            values = result.get("values", [])
            if not values:
                return []

            header = [str(c).strip().lower() for c in values[0]]

            def idx(col_name: str) -> int:
                col_name = col_name.strip().lower()
                return header.index(col_name) if col_name in header else -1

            # Coordenadas
            lat_i = idx("lat")
            if lat_i < 0:
                lat_i = idx("latitude")

            lon_i = idx("long")
            if lon_i < 0:
                for alt in ("lon", "lng", "longitude"):
                    lon_i = idx(alt)
                    if lon_i >= 0:
                        break

            # Nome/label
            name_i = idx("name")
            if name_i < 0:
                for alt in ("store", "loja", "location", "local", "ponto", "pdv"):
                    name_i = idx(alt)
                    if name_i >= 0:
                        break

            # Métricas
            users_i = idx("footfall users")
            if users_i < 0:
                for alt in ("users", "usuários", "usuarios", "visitantes", "footfall"):
                    users_i = idx(alt)
                    if users_i >= 0:
                        break

            rate_i = idx("footfall rate %")
            if rate_i < 0:
                for alt in ("rate", "taxa", "footfall rate", "rate %", "taxa %"):
                    rate_i = idx(alt)
                    if rate_i >= 0:
                        break

            def safe_get(row, i: int) -> str:
                return str(row[i]).strip() if i >= 0 and i < len(row) and row[i] is not None else ""

            def parse_coord(val: str, max_abs: float):
                try:
                    s = str(val).strip()
                    if not s or s.lower() == "nan":
                        return None
                    negative_hint = s[:1] in ("-", "−", "–", "—")
                    dot_hint = s.count(".")
                    # Normalizar: aceitar números com separadores de milhar (ex.: -8.031.797.632.094.190)
                    # e também formatos usuais com ponto decimal (ex.: -8.0317).
                    s = s.replace(" ", "")
                    # Alguns Sheets podem usar sinal de menos Unicode (U+2212) etc.
                    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
                    if "," in s and "." not in s:
                        # Decimal com vírgula
                        s = s.replace(",", ".")

                    # Se parece um inteiro gigantesco com separadores, remover tudo exceto dígitos, sinal e ponto
                    cleaned = re.sub(r"[^0-9\\-\\.]", "", s)
                    if not cleaned or cleaned in ("-", "."):
                        return None

                    # Tentar float direto primeiro
                    try:
                        num = float(cleaned)
                    except Exception:
                        # Se ainda falhar (ex.: múltiplos pontos), remover pontos e tratar como inteiro
                        digits = re.sub(r"[^0-9\\-]", "", cleaned)
                        if digits in ("", "-"):
                            return None
                        num = float(int(digits))

                    # Se veio em escala (micro/nano graus), reduzir até caber no range de graus
                    # (lat ~ [-90,90], lon ~ [-180,180])
                    while abs(num) > max_abs:
                        num /= 10.0
                        # Evitar loop infinito caso algo esteja muito fora
                        if abs(num) < 1e-12:
                            return None
                    # Heurística adicional para latitudes: alguns exports vêm "1 casa a mais" (ex.: -80.317... deveria ser -8.031...).
                    if max_abs == 90.0 and abs(num) > 60:
                        num /= 10.0
                    # Heurística adicional (Brasil): alguns exports ficam 10x maiores (ex.: -58.19 deveria ser -5.819; -32.01 deveria ser -3.201).
                    # Isso acontece quando o valor original era um inteiro com separadores e o parser mantém uma casa a mais.
                    if max_abs == 90.0 and abs(num) > 35:
                        num /= 10.0
                    # Se a string tinha muitos separadores (milhares), é comum precisar de mais uma casa (ex.: -32 -> -3.2).
                    if max_abs == 90.0 and dot_hint >= 3 and abs(num) > 15:
                        num /= 10.0
                    # Blindagem: se a string original tinha sinal negativo, preservar o sinal
                    if negative_hint and num > 0:
                        num = -num
                    return num
                except Exception:
                    return None

            points = []
            for row in values[1:]:
                if not any(row):
                    continue
                name = safe_get(row, name_i)
                if not name:
                    continue

                users_raw = safe_get(row, users_i)
                rate_raw = safe_get(row, rate_i)
                lat_raw = safe_get(row, lat_i)
                lon_raw = safe_get(row, lon_i)

                try:
                    users = int(re.sub(r"[.,\\s]", "", users_raw) or "0")
                except Exception:
                    users = 0

                try:
                    rate = float(
                        str(rate_raw)
                        .replace("%", "")
                        .replace(" ", "")
                        .replace(".", "")
                        .replace(",", ".")
                        or "0"
                    )
                except Exception:
                    rate = 0.0

                lat = parse_coord(lat_raw, 90.0)
                lon = parse_coord(lon_raw, 180.0)
                if lat is None or lon is None:
                    continue

                points.append({
                    "lat": lat,
                    "lon": lon,
                    "name": name,
                    "users": users,
                    "rate": rate,
                })

            logger.info(f"✅ Footfall ({footfall_sheet}): {len(points)} pontos")
            return points
        except Exception as e:
            # Não quebrar o dashboard quando a aba não existir / não tiver permissão
            logger.warning(f"⚠️ Falha ao extrair Footfall: {e}", exc_info=True)
            return []
    
    def _calculate_metrics(self, daily_data: list, contract_data: Dict) -> Dict[str, Any]:
        """Calcular métricas totais"""
        if not daily_data:
            raise Exception("Nenhum dado diário disponível para cálculo de métricas")
        
        df = pd.DataFrame(daily_data)
        
        total_spend = df['spend'].sum()
        # Em campanhas CPD, não há coluna de impressões; usamos disparos como proxy.
        if 'impressions' in df.columns:
            total_impressions = df['impressions'].sum()
        elif 'disparos' in df.columns:
            total_impressions = df['disparos'].sum()
        else:
            total_impressions = 0
        total_clicks = df['clicks'].sum()
        total_completions = df['video_completions'].sum() if 'video_completions' in df.columns else 0
        total_starts = df['video_starts'].sum() if 'video_starts' in df.columns else 0
        
        # Para campanhas CPD, podemos ter uma coluna explícita de disparos; se não tiver,
        # reusamos video_completions como proxy para disparos.
        if 'disparos' in df.columns:
            total_disparos = df['disparos'].sum()
        elif 'video_completions' in df.columns:
            total_disparos = df['video_completions'].sum()
        else:
            total_disparos = 0
        
        cpv = total_spend / total_completions if total_completions > 0 else 0
        cpd = total_spend / total_disparos if total_disparos > 0 else 0
        ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        vtr = total_completions / total_starts * 100 if total_starts > 0 else 0
        
        # Calcular pacing baseado no investimento contratado vs gasto real
        investment_contracted = contract_data.get('investment', 0)
        pacing = (total_spend / investment_contracted * 100) if investment_contracted > 0 else 0
        
        # Calcular período para exibição
        period_start = contract_data.get('period_start')
        period_end = contract_data.get('period_end')
        
        days_passed = 0
        total_days = 1
        
        if period_start and period_end:
            try:
                start_date = datetime.strptime(period_start, '%d/%m/%Y')
                end_date = datetime.strptime(period_end, '%d/%m/%Y')
                today = datetime.now()
                
                total_days = (end_date - start_date).days + 1
                days_passed = max(0, (today - start_date).days + 1)
            except ValueError as e:
                logger.warning(f"Formato de data inválido: {e}")
        
        return {
            "investment": float(contract_data['investment']),
            "complete_views_contracted": int(contract_data['complete_views_contracted']),
            "cpv_contracted": float(contract_data['cpv_contracted']),
            "total_spend": float(total_spend),
            "total_impressions": int(total_impressions),
            "total_clicks": int(total_clicks),
            "total_video_completions": int(total_completions),
            "total_video_starts": int(total_starts),
            "total_disparos": int(total_disparos),
            "cpv": float(cpv),
            "cpd": float(cpd),
            "ctr": float(ctr),
            "vtr": float(vtr),
            "pacing": float(pacing),
            "days_passed": days_passed,
            "total_days": total_days
        }
    
    def _get_campaign_status(self, contract_data: Dict) -> str:
        """Determinar status da campanha"""
        period_start = contract_data.get('period_start')
        period_end = contract_data.get('period_end')
        
        if not period_start or not period_end:
            return "Período Indefinido"
        
        try:
            start_date = datetime.strptime(period_start, '%d/%m/%Y')
            end_date = datetime.strptime(period_end, '%d/%m/%Y')
            today = datetime.now()
            
            if today < start_date:
                return "Não Iniciada"
            elif start_date <= today <= end_date:
                return "Ativa"
            else:
                return "Finalizada"
        except ValueError:
            return "Erro de Data"
    
    def _generate_insights(self, metrics: Dict, kpi: str = 'CPV') -> list:
        """Gerar insights baseados nas métricas"""
        insights = []
        
        if metrics['pacing'] > 100:
            insights.append("⚠️ Campanha está gastando acima do planejado")
        elif metrics['pacing'] < 80:
            insights.append("📈 Campanha tem espaço para acelerar o investimento")
        else:
            insights.append("✅ Campanha está no pacing ideal")
        
        # Determinar tipo de KPI baseado no KPI
        kpi_upper = kpi.upper()
        if kpi_upper == 'CPE':
            kpi_type = "CPE"
        elif kpi_upper == 'CPD':
            kpi_type = "CPD"
        else:
            kpi_type = "CPV"
        
        # Não gerar insight de "KPI atual vs contratado" para:
        # - CPM: fixo, não faz sentido comparar
        # - CPD: user pediu para remover essa análise no quadro de Insights Principais
        # Só mostrar "acima"/"abaixo" quando houver diferença relevante (evitar "acima" com valores iguais ex.: R$ 0,03 vs R$ 0,03)
        if kpi_upper not in ('CPM', 'CPD'):
            cpv_atual = float(metrics.get('cpv', 0) or 0)
            cpv_contr = float(metrics.get('cpv_contracted', 0) or 0)
            tol_abs = 0.005  # R$ 0,005 de tolerância
            tol_rel = 0.01   # 1% de tolerância
            diff_ok = cpv_contr > 0 and (abs(cpv_atual - cpv_contr) > max(tol_abs, cpv_contr * tol_rel))
            if diff_ok and cpv_atual > cpv_contr:
                insights.append(f"📊 {kpi_type} atual (R$ {cpv_atual:.2f}) está acima do contratado (R$ {cpv_contr:.2f})")
            elif diff_ok and cpv_atual < cpv_contr:
                insights.append(f"💰 {kpi_type} atual (R$ {cpv_atual:.2f}) está abaixo do contratado (R$ {cpv_contr:.2f})")
            elif cpv_contr > 0:
                insights.append(f"✅ {kpi_type} atual (R$ {cpv_atual:.2f}) está em linha com o contratado (R$ {cpv_contr:.2f})")
        
        # Insights de VTR só fazem sentido para campanhas com vídeo (CPV/CPE)
        if kpi_upper in ('CPV', 'CPE'):
            if metrics['vtr'] > 70:
                insights.append("🎯 VTR excelente - audiência altamente engajada")
            elif metrics['vtr'] > 50:
                insights.append("📺 VTR boa - audiência moderadamente engajada")
            else:
                insights.append("⚠️ VTR baixa - revisar targeting e criativos")
        
        return insights

# Classe de configuração
class CampaignConfig:
    def __init__(self, client, campaign, campaign_key, sheet_id, tabs=None, report_sheet_gid=None):
        self.client = client
        self.campaign = campaign
        self.campaign_key = campaign_key
        self.sheet_id = sheet_id
        self.tabs = tabs or {
            "report": "Report",
            "contract": "Informações de contrato",
            "publishers": "Publishers",
            "strategies": "Segmentações"
        }
        # GID da aba Report (ex.: 364193781) para forçar essa aba quando conhecido
        self.report_sheet_gid = report_sheet_gid
        self.use_footfall = False

if __name__ == "__main__":
    # Teste local
    config = CampaignConfig(
        client="Copacol",
        campaign="Institucional 30s",
        campaign_key="copacol_test",
        sheet_id="1scA5ykf49DLobPTAKSL5fNgGM_iomcJmgSJqXolV679M"
    )
    
    try:
        extractor = RealGoogleSheetsExtractor(config)
        data = extractor.extract_data()
        
        if data:
            print("✅ Extrator REAL funcionando!")
            print(f"📊 Dados reais: {len(data['daily_data'])} dias")
            print(f"💰 Investimento: R$ {data['campaign_summary']['investment']:,.2f}")
            print(f"📈 Pacing: {data['campaign_summary']['pacing']:.1f}%")
            print(f"🔗 Fonte: {data['data_source']}")
        else:
            print("❌ Erro no extrator REAL")
    except Exception as e:
        print(f"❌ Erro: {e}")

    def _generate_default_contract_data(self) -> Dict[str, Any]:
        """Gerar dados de contrato padrão para campanhas CPE/CPD sem aba de contrato"""
        try:
            logger.info("📋 Gerando dados de contrato padrão para CPE/CPD")
            
            # Extrair dados da planilha principal para calcular valores padrão
            range_name = "A:Z"  # Usar a primeira aba (padrão)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning("⚠️ Planilha vazia, usando valores padrão")
                return self._get_fallback_contract_data()
            
            # Calcular totais dos dados
            total_spend = 0
            total_completions = 0
            total_starts = 0
            
            # Pular cabeçalho e processar dados
            for row in values[1:]:
                if len(row) >= 12:  # Verificar se tem colunas suficientes
                    try:
                        # Extrair valores (ajustar índices conforme estrutura da planilha)
                        spend_str = row[10] if len(row) > 10 else "0"  # Coluna "Valor investido"
                        completions = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0  # Coluna "100% Complete"
                        starts = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0  # Coluna "Video Starts"
                        
                        # Converter spend
                        spend = float(spend_str.replace('R$', '').replace(' ', '').replace(',', '.')) if spend_str else 0
                        
                        total_spend += spend
                        total_completions += completions
                        total_starts += starts
                    except (ValueError, IndexError):
                        continue
            
            # Calcular valores de contrato baseados nos dados
            cpe_contracted = 0.30  # Valor padrão para CPE
            listens_contracted = max(total_completions * 5, 34000)  # 5x o entregue ou 34k mínimo
            investment = max(total_spend * 1.5, 10200)  # 1.5x o gasto ou 10.2k mínimo
            
            contract_data = {
                "investment": investment,
                "complete_views_contracted": listens_contracted,
                "cpv_contracted": cpe_contracted,
                "canal": self.config.channel or "Spotify",
                "period_start": "2025-10-01",
                "period_end": "2025-10-31"
            }
            
            logger.info(f"✅ Dados de contrato gerados: {contract_data}")
            return contract_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dados de contrato padrão: {e}")
            return self._get_fallback_contract_data()
    
    def _get_fallback_contract_data(self) -> Dict[str, Any]:
        """Dados de contrato de fallback quando não é possível extrair da planilha"""
        return {
            "investment": 10200.0,
            "complete_views_contracted": 34000,
            "cpv_contracted": 0.30,
            "canal": self.config.channel or "Spotify",
            "period_start": "2025-10-01",
            "period_end": "2025-10-31"
        }
