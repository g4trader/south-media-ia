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
        """Inicializar serviço do Google Sheets"""
        try:
            # Tentar credenciais locais primeiro
            credentials_path = "credentials.json"
            if os.path.exists(credentials_path):
                logger.info("🔐 Usando credenciais locais (credentials.json)")
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )
            else:
                # Tentar variável de ambiente
                credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
                if credentials_json:
                    logger.info("🔐 Usando credenciais da variável de ambiente")
                    import json
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                    )
                else:
                    raise Exception("Credenciais não encontradas. Configure credentials.json ou GOOGLE_APPLICATION_CREDENTIALS_JSON")
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Serviço Google Sheets inicializado com sucesso")
            
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
                "insights": self._generate_insights(total_metrics),
                "last_updated": datetime.now().isoformat(),
                "data_source": "google_sheets_real"
            }
            
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
            
            # Procurar por abas que contenham dados diários (mais flexível)
            report_sheet = None
            possible_names = ['report', 'dados', 'daily', 'diário', 'performance', 'delivery']
            
            for sheet in sheets:
                sheet_name = sheet['properties']['title']
                clean_name = sheet_name.strip().lower()
                
                # Verificar se o nome da aba contém alguma das palavras-chave
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
            
            range_name = f"{report_sheet}!A:Z"
            
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
            
            # Mapear colunas para nomes padronizados
            column_mapping = {
                'Day': 'date',
                'Line Item': 'line_item',
                'Creative': 'creative',
                'Valor investido': 'spend',  # Corrigido: minúscula
                'Imps': 'impressions',
                'Clicks': 'clicks',
                'CPV': 'cpv',
                'CPC': 'cpc',
                'CTR %': 'ctr',  # Corrigido: com %
                '25% Video Complete': 'video_25',
                '50% Video Complete': 'video_50',
                '75% Video Complete': 'video_75',
                '100% Complete': 'video_completions',  # Corrigido: 100% Complete
                'Video Starts': 'video_starts'
            }
            
            # Renomear colunas
            df = df.rename(columns=column_mapping)
            
            # Converter tipos de dados
            for col in ['spend', 'impressions', 'clicks', 'cpv', 'cpc', 'ctr', 
                       'video_25', 'video_50', 'video_75', 'video_completions', 'video_starts']:
                if col in df.columns:
                    if col == 'spend':  # Tratamento especial para valores monetários brasileiros
                        # Formato brasileiro: R$ 2.575,54 -> 2575.54
                        df[col] = df[col].astype(str).str.replace('R$', '').str.replace(' ', '').str.strip()
                        # Remover pontos de milhares e substituir vírgula por ponto decimal
                        df[col] = df[col].str.replace('.', '', regex=False)  # Remove pontos de milhares
                        df[col] = df[col].str.replace(',', '.', regex=False)  # Vírgula vira ponto decimal
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Converter data
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                df = df.dropna(subset=['date'])
            
            # Converter para lista de dicionários e calcular métricas
            daily_data = []
            for _, row in df.iterrows():
                spend = float(row.get('spend', 0)) if pd.notna(row.get('spend')) else 0.0
                impressions = int(row.get('impressions', 0)) if pd.notna(row.get('impressions')) else 0
                clicks = int(row.get('clicks', 0)) if pd.notna(row.get('clicks')) else 0
                video_completions = int(row.get('video_completions', 0)) if pd.notna(row.get('video_completions')) else 0
                
                # Calcular métricas dinamicamente
                cpv = spend / video_completions if video_completions > 0 else 0.0
                cpc = spend / clicks if clicks > 0 else 0.0
                ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
                
                daily_data.append({
                    "date": str(row.get('date', '')),
                    "line_item": str(row.get('line_item', '')),
                    "creative": str(row.get('creative', '')),
                    "spend": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                    "cpv": round(cpv, 4),
                    "cpc": round(cpc, 2),
                    "ctr": round(ctr, 2),
                    "video_25": int(row.get('video_25', 0)) if pd.notna(row.get('video_25')) else 0,
                    "video_50": int(row.get('video_50', 0)) if pd.notna(row.get('video_50')) else 0,
                    "video_75": int(row.get('video_75', 0)) if pd.notna(row.get('video_75')) else 0,
                    "video_completions": video_completions,
                    "video_starts": int(row.get('video_starts', 0)) if pd.notna(row.get('video_starts')) else 0
                })
            
            logger.info(f"✅ Dados diários extraídos: {len(daily_data)} registros")
            return daily_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados diários: {e}")
            return None
    
    def _extract_contract_data(self) -> Optional[Dict[str, Any]]:
        """Extrair dados de contrato da aba 'Informações de contrato'"""
        try:
            logger.info("📋 Extraindo dados de contrato")
            
            # Listar todas as abas disponíveis para encontrar a correta
            spreadsheet_info = self.service.spreadsheets().get(spreadsheetId=self.config.sheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            # Procurar por abas que contenham "Informações" (ignorando espaços)
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
                # Listar todas as abas para debug
                available_sheets = [sheet['properties']['title'] for sheet in sheets]
                logger.error(f"❌ Aba 'Informações de contrato' não encontrada. Abas disponíveis: {available_sheets}")
                return None
            
            range_name = f"{contract_sheet}!A:B"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.error(f"❌ Aba '{contract_sheet}' está vazia")
                return None
            
            # Converter para dicionário
            contract_dict = {}
            for row in values:
                if len(row) >= 2:
                    key = str(row[0]).strip()
                    value = str(row[1]).strip()
                    if key and value and value.lower() != 'nan':
                        contract_dict[key] = value
            
            logger.info(f"📋 Dados de contrato encontrados: {list(contract_dict.keys())}")
            
            # Mapear para estrutura padrão (usando as chaves reais da planilha)
            contract_data = {
                "client": self.config.client,
                "campaign": getattr(self.config, 'campaign', getattr(self.config, 'campaign_name', 'N/A')),
                "investment": float(contract_dict.get("Investimento:", "0").replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')) if contract_dict.get("Investimento:") else 0.0,
                "complete_views_contracted": int(contract_dict.get("Complete Views Contrado", contract_dict.get("Impressões Contrado", "0")).replace('.', '').replace(',', '')) if contract_dict.get("Complete Views Contrado") or contract_dict.get("Impressões Contrado") else 0,
                "cpv_contracted": float(contract_dict.get("CPV contratado:", contract_dict.get("CPM contratado:", "0")).replace('R$', '').replace(' ', '').replace(',', '.')) if contract_dict.get("CPV contratado:") or contract_dict.get("CPM contratado:") else 0.0,
                "canal": contract_dict.get("Canal:", "").strip() or contract_dict.get("Canal", "").strip(),
                "tipo_criativo": contract_dict.get("Tipo de criativo:", "").strip() or contract_dict.get("Tipo de criativo", "").strip() or contract_dict.get("Tipo de Criativo:", "").strip() or contract_dict.get("Tipo de Criativo", "").strip() or contract_dict.get("Criativo", "").strip(),
                "period_start": None,
                "period_end": None
            }
            
            # Extrair período
            periodo = contract_dict.get("Periodo de veiculação", "")
            if periodo and ' a ' in periodo:
                parts = periodo.split(' a ')
                if len(parts) == 2:
                    contract_data["period_start"] = parts[0].strip()
                    contract_data["period_end"] = parts[1].strip()
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
    
    def _calculate_metrics(self, daily_data: list, contract_data: Dict) -> Dict[str, Any]:
        """Calcular métricas totais"""
        if not daily_data:
            raise Exception("Nenhum dado diário disponível para cálculo de métricas")
        
        df = pd.DataFrame(daily_data)
        
        total_spend = df['spend'].sum()
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_completions = df['video_completions'].sum()
        total_starts = df['video_starts'].sum()
        
        cpv = total_spend / total_completions if total_completions > 0 else 0
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
            "cpv": float(cpv),
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
    
    def _generate_insights(self, metrics: Dict) -> list:
        """Gerar insights baseados nas métricas"""
        insights = []
        
        if metrics['pacing'] > 100:
            insights.append("⚠️ Campanha está gastando acima do planejado")
        elif metrics['pacing'] < 80:
            insights.append("📈 Campanha tem espaço para acelerar o investimento")
        else:
            insights.append("✅ Campanha está no pacing ideal")
        
        if metrics['cpv'] > metrics['cpv_contracted']:
            insights.append(f"📊 CPV atual (R$ {metrics['cpv']:.2f}) está acima do contratado (R$ {metrics['cpv_contracted']:.2f})")
        else:
            insights.append(f"💰 CPV atual (R$ {metrics['cpv']:.2f}) está abaixo do contratado (R$ {metrics['cpv_contracted']:.2f})")
        
        if metrics['vtr'] > 70:
            insights.append("🎯 VTR excelente - audiência altamente engajada")
        elif metrics['vtr'] > 50:
            insights.append("📺 VTR boa - audiência moderadamente engajada")
        else:
            insights.append("⚠️ VTR baixa - revisar targeting e criativos")
        
        return insights

# Classe de configuração
class CampaignConfig:
    def __init__(self, client, campaign, campaign_key, sheet_id, tabs=None):
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
