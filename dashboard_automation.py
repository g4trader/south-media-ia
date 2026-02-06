#!/usr/bin/env python3
"""
Script principal de automação do dashboard
Atualiza dados do dashboard a cada 3 horas usando Google Sheets
"""

import os
import json
import re
import shutil
import subprocess
from datetime import datetime
import logging
import schedule
import time
import requests
from google_sheets_processor import GoogleSheetsProcessor
from config import AUTOMATION_CONFIG

# Configuração de logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DashboardAutomation:
    """Classe principal para automação do dashboard"""
    
    def __init__(self):
        # Suportar múltiplos arquivos de dashboard
        try:
            self.dashboard_files = AUTOMATION_CONFIG.get('dashboard_files', ['static/dash_sonho.html'])
        except:
            # Se AUTOMATION_CONFIG não estiver definido, usar lista padrão
            self.dashboard_files = ['static/dash_sonho.html', 'static/dash_sonho_v2.html', 'static/dash_sonho_v3.html']
        
        # Se for uma string única, converter para lista para compatibilidade
        if isinstance(self.dashboard_files, str):
            self.dashboard_files = [self.dashboard_files]
        
        # Manter compatibilidade com código existente
        self.dashboard_file = self.dashboard_files[0]
        
        try:
            self.backup_enabled = AUTOMATION_CONFIG['backup_enabled']
            self.backup_dir = AUTOMATION_CONFIG['backup_dir']
        except:
            self.backup_enabled = True
            self.backup_dir = 'backups'
        
        self.processor = None
        
        # Criar diretório de backup se necessário
        if self.backup_enabled:
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def download_dashboard_from_github(self):
        """Baixa os arquivos do dashboard do GitHub antes de fazer atualizações"""
        try:
            success_count = 0
            
            for dashboard_file in self.dashboard_files:
                # Extrair nome do arquivo (sem o diretório)
                filename = os.path.basename(dashboard_file)
                github_url = f"https://raw.githubusercontent.com/g4trader/south-media-ia/main/static/{filename}"
                
                logger.info(f"📥 Baixando dashboard atualizado de: {github_url}")
                
                response = requests.get(github_url, timeout=30)
                response.raise_for_status()
                
                # Criar diretório static se não existir
                os.makedirs("static", exist_ok=True)
                
                # Salvar arquivo
                with open(dashboard_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                logger.info(f"✅ Dashboard {filename} baixado com sucesso do GitHub")
                success_count += 1
            
            if success_count == len(self.dashboard_files):
                logger.info(f"✅ Todos os dashboards ({success_count}) baixados com sucesso")
                return True
            else:
                logger.warning(f"⚠️ Apenas {success_count}/{len(self.dashboard_files)} dashboards foram baixados")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar dashboards do GitHub: {e}")
            return False
    
    def create_backup(self):
        """Cria backup dos dashboards atuais"""
        if not self.backup_enabled:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for dashboard_file in self.dashboard_files:
                if not os.path.exists(dashboard_file):
                    continue
                
                filename = os.path.basename(dashboard_file)
                backup_filename = f"{filename.replace('.html', '')}_backup_{timestamp}.html"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                
                shutil.copy2(dashboard_file, backup_path)
                logger.info(f"✅ Backup criado: {backup_filename}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
    
    def format_js_value(self, value):
        """Formata valor para JavaScript"""
        if isinstance(value, (int, float)):
            if value == float('inf'):
                return 'null'
            elif value != value:  # NaN check
                return 'null'
            else:
                return str(value)
        elif value is None:
            return 'null'
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            return 'null'
    
    def update_dashboard_data(self, daily_data):
        """Atualiza apenas dados de canais (DAILY) dos dashboards, preservando FOOTFALL_POINTS e dados existentes"""
        try:
            logger.info(f"🔧 Atualizando dados de canais de {len(self.dashboard_files)} dashboards (preservando footfall e dados existentes)...")
            
            # Identificar canais que foram processados com sucesso
            processed_channels = set(item['channel'] for item in daily_data)
            logger.info(f"📊 Canais processados com sucesso: {', '.join(sorted(processed_channels))}")
            
            # Atualizar cada arquivo de dashboard
            success_count = 0
            for dashboard_file in self.dashboard_files:
                if not os.path.exists(dashboard_file):
                    logger.warning(f"⚠️ Arquivo não encontrado: {dashboard_file}, pulando...")
                    continue
                
                try:
                    # Ler HTML atual
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Extrair dados existentes do DAILY
                    # Usar padrão que captura tudo até encontrar o próximo const ou ; seguido de quebra de linha
                    daily_pattern = r'const DAILY = \[(.*?)\];'
                    existing_match = re.search(daily_pattern, html_content, re.DOTALL)
                    
                    existing_daily_data = []
                    if existing_match:
                        try:
                            # Tentar parsear dados existentes
                            existing_js = existing_match.group(1).strip()
                            if existing_js:
                                # O formato já é JSON válido (array de objetos)
                                # Adicionar colchetes se necessário
                                existing_data_str = '[' + existing_js + ']'
                                try:
                                    # Usar json.loads para parsear
                                    existing_daily_data = json.loads(existing_data_str)
                                    logger.info(f"📋 Extraídos {len(existing_daily_data)} registros existentes de {os.path.basename(dashboard_file)}")
                                    
                                    # Estatísticas dos canais existentes
                                    existing_channels = set(item.get('channel', '') for item in existing_daily_data)
                                    logger.info(f"   Canais existentes: {', '.join(sorted(existing_channels))}")
                                except json.JSONDecodeError as je:
                                    logger.warning(f"⚠️ Erro ao parsear dados existentes como JSON: {je}")
                                    logger.warning(f"   Usando apenas dados novos (erro na linha {je.lineno}, coluna {je.colno})")
                                    existing_daily_data = []
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao extrair dados existentes: {e}")
                            existing_daily_data = []
                    else:
                        logger.info(f"⚠️ Array DAILY não encontrado no arquivo {os.path.basename(dashboard_file)}, criando novo")
                    
                    # Criar mapa de dados novos por canal e data
                    new_data_map = {}
                    for item in daily_data:
                        channel = item.get('channel', '')
                        date = item.get('date', '')
                        key = f"{channel}_{date}"
                        new_data_map[key] = item
                    
                    # Mesclar dados: substituir dados de canais processados, preservar os demais
                    merged_daily_data = []
                    preserved_channels = set()
                    
                    # Adicionar dados existentes de canais NÃO processados
                    for item in existing_daily_data:
                        channel = item.get('channel', '')
                        if channel not in processed_channels:
                            merged_daily_data.append(item)
                            preserved_channels.add(channel)
                    
                    # Adicionar dados novos (substituindo dados antigos dos canais processados)
                    merged_daily_data.extend(daily_data)
                    
                    if preserved_channels:
                        logger.info(f"✅ Preservados dados de canais não processados: {', '.join(sorted(preserved_channels))}")
                    
                    # Criar string JavaScript para DAILY mesclado
                    daily_items = []
                    for item in merged_daily_data:
                        item_js = "{"
                        item_pairs = []
                        for key, value in item.items():
                            item_pairs.append(f'"{key}": {self.format_js_value(value)}')
                        item_js += ", ".join(item_pairs) + "}"
                        daily_items.append(item_js)
                    
                    new_daily_js = "const DAILY = [" + ", ".join(daily_items) + "];"
                    
                    # Substituir apenas a seção DAILY, preservando FOOTFALL_POINTS
                    html_content = re.sub(daily_pattern, new_daily_js, html_content, flags=re.DOTALL)
                    
                    # Salvar HTML atualizado
                    with open(dashboard_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    logger.info(f"✅ Dados de canais atualizados em {os.path.basename(dashboard_file)}: {len(merged_daily_data)} registros totais ({len(daily_data)} novos + {len(existing_daily_data) - len(daily_data) if existing_daily_data else 0} preservados)")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao atualizar {dashboard_file}: {e}")
                    import traceback
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    continue
            
            if success_count == len(self.dashboard_files):
                logger.info(f"✅ Dados de canais atualizados com {len(daily_data)} registros novos em todos os dashboards (dados existentes preservados)")
                return True
            elif success_count > 0:
                logger.warning(f"⚠️ Dados atualizados em apenas {success_count}/{len(self.dashboard_files)} dashboards")
                return True
            else:
                logger.error("❌ Nenhum dashboard foi atualizado")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dados de canais: {e}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def calculate_cons_data(self, daily_data):
        """Calcula dados consolidadas (CONS) baseados nos dados diários"""
        try:
            logger.info("📊 Calculando dados consolidados...")
            
            # Valores de orçamento contratado por canal (valores corretos das planilhas)
            budget_contratado = {
                "YouTube": 19333.32,
                "TikTok": 13655.27,
                "Netflix": 18643.04,
                "Disney": 18516.65,
                "CTV": 10332.96,
                "Footfall Display": 8470.59,
                "Bonificação Ifood": 5000.00
            }
            
            # Agrupar por canal
            channels = {}
            for item in daily_data:
                if 'channel' not in item:
                    logger.warning(f"⚠️ Item sem chave 'channel': {item}")
                    continue
                channel = item['channel']
                if channel not in channels:
                    channels[channel] = {
                        'spend': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'visits': 0,
                        'starts': 0,
                        'q25': 0,
                        'q50': 0,
                        'q75': 0,
                        'q100': 0
                    }
                
                # Garantir que spend seja sempre numérico
                try:
                    spend_val = float(item.get('spend', 0)) if item.get('spend', 0) else 0
                    channels[channel]['spend'] += spend_val
                except (ValueError, TypeError):
                    logger.warning(f"⚠️ Erro ao converter spend: {item.get('spend')}")
                
                # Garantir que impressões e cliques sejam sempre numéricos
                try:
                    channels[channel]['impressions'] += int(item.get('impressions', 0) or 0)
                    channels[channel]['clicks'] += int(item.get('clicks', 0) or 0)
                except (ValueError, TypeError):
                    pass
                
                # Garantir que valores de vídeo sejam sempre numéricos (converter strings para números)
                starts_val = item.get('starts', '')
                if starts_val != '' and starts_val is not None:
                    try:
                        starts_num = int(float(starts_val))
                        channels[channel]['starts'] += starts_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter starts: {starts_val} para número")
                
                q25_val = item.get('q25', '')
                if q25_val != '' and q25_val is not None:
                    try:
                        q25_num = int(float(q25_val))
                        channels[channel]['q25'] += q25_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q25: {q25_val} para número")
                
                q50_val = item.get('q50', '')
                if q50_val != '' and q50_val is not None:
                    try:
                        q50_num = int(float(q50_val))
                        channels[channel]['q50'] += q50_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q50: {q50_val} para número")
                
                q75_val = item.get('q75', '')
                if q75_val != '' and q75_val is not None:
                    try:
                        q75_num = int(float(q75_val))
                        channels[channel]['q75'] += q75_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q75: {q75_val} para número")
                
                q100_val = item.get('q100', '')
                if q100_val != '' and q100_val is not None:
                    try:
                        q100_num = int(float(q100_val))
                        channels[channel]['q100'] += q100_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q100: {q100_val} para número")
                
                if item.get('visits') and str(item['visits']).isdigit():
                    channels[channel]['visits'] += int(item['visits'])
            
            # Calcular totais
            total_spend = sum(ch['spend'] for ch in channels.values())
            total_impressions = sum(ch['impressions'] for ch in channels.values())
            total_clicks = sum(ch['clicks'] for ch in channels.values())
            total_visits = sum(ch['visits'] for ch in channels.values())
            total_starts = sum(ch['starts'] for ch in channels.values())
            total_q100 = sum(ch['q100'] for ch in channels.values())
            
            # Calcular totais de orçamento contratado
            total_budget_contratado = sum(budget_contratado.get(channel, 0) for channel in channels.keys())
            
            # Calcular métricas consolidadas
            ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
            vtr = (total_q100 / total_starts) * 100 if total_starts > 0 else 0
            cpv = (total_spend / total_q100) if total_q100 > 0 else 0
            cpm = (total_spend / (total_impressions / 1000)) if total_impressions > 0 else 0
            pacing = (total_spend / total_budget_contratado) * 100 if total_budget_contratado > 0 else 0
            
            # Criar dados CONS
            cons_data = {
                "Budget Contratado (R$)": total_budget_contratado,
                "Budget Utilizado (R$)": total_spend,
                "Impressões": total_impressions,
                "Cliques": total_clicks,
                "CTR (%)": ctr,
                "VC (100%)": total_q100,
                "VTR (100%)": vtr / 100,  # Converter para decimal para o dashboard
                "CPV (R$)": cpv,
                "CPM (R$)": cpm,
                "Pacing (%)": pacing
            }
            
            logger.info(f"✅ Dados CONS calculados:")
            logger.info(f"  - Budget Contratado: R$ {total_budget_contratado:.2f}")
            logger.info(f"  - Budget Utilizado: R$ {total_spend:.2f}")
            logger.info(f"  - Impressões: {total_impressions:,}")
            logger.info(f"  - Cliques: {total_clicks:,}")
            logger.info(f"  - CTR: {ctr:.2f}%")
            logger.info(f"  - VC (100%): {total_q100:,}")
            logger.info(f"  - VTR: {vtr:.2f}%")
            logger.info(f"  - CPV: R$ {cpv:.2f}")
            logger.info(f"  - CPM: R$ {cpm:.2f}")
            logger.info(f"  - Pacing: {pacing:.2f}%")
            
            return cons_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular dados CONS: {e}")
            return {}
    
    def calculate_per_data(self, daily_data):
        """Calcula dados por canal (PER) baseados nos dados diários"""
        try:
            logger.info("📊 Calculando dados por canal...")
            
            # Valores de orçamento contratado por canal (valores corretos das planilhas)
            budget_contratado = {
                "YouTube": 19333.32,
                "TikTok": 13655.27,
                "Netflix": 18643.04,
                "Disney": 18516.65,
                "CTV": 10332.96,
                "Footfall Display": 8470.59,
                "Bonificação Ifood": 5000.00
            }
            
            # Agrupar por canal
            channels = {}
            for item in daily_data:
                if 'channel' not in item:
                    logger.warning(f"⚠️ Item sem chave 'channel': {item}")
                    continue
                channel = item['channel']
                if channel not in channels:
                    channels[channel] = {
                        'spend': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'visits': 0,
                        'starts': 0,
                        'q25': 0,
                        'q50': 0,
                        'q75': 0,
                        'q100': 0,
                        'creatives': set()
                    }
                
                # Garantir que spend seja sempre numérico
                try:
                    spend_val = float(item.get('spend', 0)) if item.get('spend', 0) else 0
                    channels[channel]['spend'] += spend_val
                except (ValueError, TypeError):
                    logger.warning(f"⚠️ Erro ao converter spend: {item.get('spend')}")
                
                # Garantir que impressões e cliques sejam sempre numéricos
                try:
                    channels[channel]['impressions'] += int(item.get('impressions', 0) or 0)
                    channels[channel]['clicks'] += int(item.get('clicks', 0) or 0)
                except (ValueError, TypeError):
                    pass
                
                # Garantir que valores de vídeo sejam sempre numéricos (converter strings para números)
                starts_val = item.get('starts', '')
                if starts_val != '' and starts_val is not None:
                    try:
                        starts_num = int(float(starts_val))
                        channels[channel]['starts'] += starts_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter starts: {starts_val} para número")
                
                q25_val = item.get('q25', '')
                if q25_val != '' and q25_val is not None:
                    try:
                        q25_num = int(float(q25_val))
                        channels[channel]['q25'] += q25_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q25: {q25_val} para número")
                
                q50_val = item.get('q50', '')
                if q50_val != '' and q50_val is not None:
                    try:
                        q50_num = int(float(q50_val))
                        channels[channel]['q50'] += q50_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q50: {q50_val} para número")
                
                q75_val = item.get('q75', '')
                if q75_val != '' and q75_val is not None:
                    try:
                        q75_num = int(float(q75_val))
                        channels[channel]['q75'] += q75_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q75: {q75_val} para número")
                
                q100_val = item.get('q100', '')
                if q100_val != '' and q100_val is not None:
                    try:
                        q100_num = int(float(q100_val))
                        channels[channel]['q100'] += q100_num
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Erro ao converter q100: {q100_val} para número")
                
                if item.get('visits') and str(item['visits']).isdigit():
                    channels[channel]['visits'] += int(item['visits'])
                
                creative = item.get('creative', '')
                if creative:
                    channels[channel]['creatives'].add(creative)
            
            # Criar dados PER
            per_data = []
            for channel_name, data in channels.items():
                try:
                    # Calcular métricas
                    budget_contratado_val = budget_contratado.get(channel_name, data['spend'] * 1.2)
                    pacing = (data['spend'] / budget_contratado_val) * 100 if budget_contratado_val > 0 else 0
                    
                    # CTR = Clicks / Impressions * 100
                    ctr = (data['clicks'] / data['impressions']) * 100 if data['impressions'] > 0 else 0
                    
                    # VTR = Video Completions / Video Starts * 100 (apenas para canais de vídeo)
                    vtr = 0
                    if channel_name in ["YouTube", "Netflix", "Disney", "CTV"] and data['starts'] > 0:
                        vtr = (data['q100'] / data['starts']) * 100
                    elif channel_name == "TikTok" and data['starts'] > 0:
                        # TikTok não tem quartis, usar starts como completions
                        vtr = (data['starts'] / data['starts']) * 100
                    
                    # CPV = Spend / Video Completions (apenas para canais de vídeo)
                    cpv = 0
                    if channel_name in ["YouTube", "Netflix", "Disney", "CTV"] and data['q100'] > 0:
                        cpv = data['spend'] / data['q100']
                    elif channel_name == "TikTok" and data['starts'] > 0:
                        # TikTok usa starts como completions
                        cpv = data['spend'] / data['starts']
                    
                    # CPM = Spend / (Impressions / 1000)
                    cpm = (data['spend'] / (data['impressions'] / 1000)) if data['impressions'] > 0 else 0
                    
                    # Garantir que creatives seja um set válido
                    creatives_count = len(data.get('creatives', set()))
                    
                    channel_data = {
                        "Canal": channel_name,
                        "Budget Contratado (R$)": budget_contratado_val,
                        "Budget Utilizado (R$)": data['spend'],
                        "Impressões": data['impressions'],
                        "Cliques": data['clicks'],
                        "CTR (%)": ctr / 100,  # Converter para decimal para o dashboard
                        "VC (100%)": data['q100'] if channel_name in ["YouTube", "Netflix", "Disney", "CTV"] else data['starts'] if channel_name == "TikTok" else 0,
                        "VTR (100%)": vtr / 100,  # Converter para decimal para o dashboard
                        "CPV (R$)": cpv,
                        "CPM (R$)": cpm,
                        "Pacing (%)": pacing / 100,  # Converter para decimal para o dashboard
                        "Criativos Únicos": creatives_count
                    }
                    
                    per_data.append(channel_data)
                except Exception as e:
                    logger.error(f"❌ Erro ao processar canal {channel_name} no PER: {e}")
                    logger.error(f"   Dados do canal: {data}")
                    continue
            
            # Garantir que canais esperados apareçam mesmo sem dados (com valores zerados)
            # Isso evita problemas no dashboard quando um canal não tem dados
            expected_channels = ["YouTube", "TikTok", "Netflix", "Disney", "CTV", "Footfall Display"]
            existing_channel_names = {item["Canal"] for item in per_data}
            
            for expected_channel in expected_channels:
                if expected_channel not in existing_channel_names:
                    logger.warning(f"⚠️ Canal {expected_channel} não encontrado nos dados, adicionando entrada zerada")
                    budget_contratado_val = budget_contratado.get(expected_channel, 0)
                    
                    # Determinar se é canal de vídeo
                    is_video = expected_channel in ["YouTube", "Netflix", "Disney", "CTV"]
                    is_tiktok = expected_channel == "TikTok"
                    
                    channel_data = {
                        "Canal": expected_channel,
                        "Budget Contratado (R$)": budget_contratado_val,
                        "Budget Utilizado (R$)": 0,
                        "Impressões": 0,
                        "Cliques": 0,
                        "CTR (%)": 0,
                        "VC (100%)": 0,
                        "VTR (100%)": 0,
                        "CPV (R$)": 0,
                        "CPM (R$)": 0,
                        "Pacing (%)": 0,
                        "Criativos Únicos": 0
                    }
                    
                    per_data.append(channel_data)
            
            logger.info(f"✅ Dados PER calculados para {len(per_data)} canais (incluindo canais sem dados)")
            return per_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular dados PER: {e}")
            return []
    
    def update_cons_and_per_data(self, daily_data):
        """Atualiza dados CONS e PER nos dashboards, preservando FOOTFALL_POINTS"""
        try:
            logger.info(f"🔧 Atualizando dados CONS e PER em {len(self.dashboard_files)} dashboards (preservando footfall)...")
            
            # Calcular dados (uma vez para todos os arquivos)
            cons_data = self.calculate_cons_data(daily_data)
            per_data = self.calculate_per_data(daily_data)
            
            if not cons_data or not per_data:
                logger.error("❌ Erro ao calcular dados CONS/PER")
                return False
            
            # Preparar strings JavaScript
            cons_js = "const CONS = " + json.dumps(cons_data, indent=2, ensure_ascii=False) + ";"
            per_js = "const PER = " + json.dumps(per_data, indent=2, ensure_ascii=False) + ";"
            
            # Atualizar cada arquivo de dashboard
            success_count = 0
            for dashboard_file in self.dashboard_files:
                if not os.path.exists(dashboard_file):
                    logger.warning(f"⚠️ Arquivo não encontrado: {dashboard_file}, pulando...")
                    continue
                
                try:
                    # Ler HTML atual
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Atualizar CONS
                    cons_pattern = r'const CONS = \{.*?\};'
                    html_content = re.sub(cons_pattern, cons_js, html_content, flags=re.DOTALL)
                    
                    # Atualizar PER
                    per_pattern = r'const PER = \[.*?\];'
                    html_content = re.sub(per_pattern, per_js, html_content, flags=re.DOTALL)
                    
                    # Salvar HTML atualizado
                    with open(dashboard_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    logger.info(f"✅ Dados CONS e PER atualizados em {os.path.basename(dashboard_file)}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao atualizar {dashboard_file}: {e}")
                    continue
            
            if success_count == len(self.dashboard_files):
                logger.info("✅ Dados CONS e PER atualizados em todos os dashboards (FOOTFALL_POINTS preservado)")
                return True
            elif success_count > 0:
                logger.warning(f"⚠️ Dados atualizados em apenas {success_count}/{len(self.dashboard_files)} dashboards")
                return True
            else:
                logger.error("❌ Nenhum dashboard foi atualizado")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dados CONS/PER: {e}")
            return False
    
    def commit_and_push_to_github(self):
        """Faz commit e push das alterações para o GitHub usando API com validação"""
        try:
            logger.info(f"📤 Fazendo commit e push de {len(self.dashboard_files)} dashboards para o GitHub...")
            
            # Configurar token do GitHub
            token = os.getenv('GITHUB_TOKEN')
            if not token:
                logger.error("❌ Token do GitHub não configurado")
                return False
            
            import base64
            import requests
            
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Fazer commit de cada arquivo
            success_count = 0
            for dashboard_file in self.dashboard_files:
                if not os.path.exists(dashboard_file):
                    logger.warning(f"⚠️ Arquivo não encontrado: {dashboard_file}, pulando commit...")
                    continue
                
                try:
                    # Ler o arquivo atualizado
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Validação simplificada - verificar se arquivo não está vazio
                    if not content.strip():
                        logger.error(f"❌ Arquivo vazio: {dashboard_file}, commit cancelado")
                        continue
                    
                    # Extrair nome do arquivo (sem o diretório)
                    filename = os.path.basename(dashboard_file)
                    
                    # URL do arquivo no GitHub
                    url = f"https://api.github.com/repos/g4trader/south-media-ia/contents/static/{filename}"
                    
                    # Obter SHA do arquivo atual
                    response = requests.get(url, headers=headers)
                    if response.status_code != 200:
                        logger.error(f"❌ Erro ao obter SHA do arquivo {filename}: {response.status_code}")
                        continue
                    
                    current_sha = response.json()["sha"]
                    
                    # Fazer commit
                    data = {
                        "message": f"🤖 Atualização automática do dashboard {filename} - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                        "sha": current_sha
                    }
                    
                    response = requests.put(url, headers=headers, json=data)
                    if response.status_code == 200:
                        logger.info(f"✅ Dashboard {filename} atualizado no GitHub com sucesso")
                        success_count += 1
                    else:
                        logger.error(f"❌ Erro no commit de {filename}: {response.status_code} - {response.text}")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao fazer commit de {dashboard_file}: {e}")
                    continue
            
            if success_count == len(self.dashboard_files):
                logger.info(f"✅ Todos os dashboards ({success_count}) atualizados no GitHub com sucesso")
                return True
            elif success_count > 0:
                logger.warning(f"⚠️ Apenas {success_count}/{len(self.dashboard_files)} dashboards foram atualizados no GitHub")
                return True
            else:
                logger.error("❌ Nenhum dashboard foi atualizado no GitHub")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit/push via GitHub API: {e}")
            return False
    
    def trigger_footfall_update(self):
        """Chama a atualização de footfall após atualização dos canais"""
        try:
            logger.info("🔄 Acionando atualização de footfall após atualização dos canais...")
            
            # URL do serviço de footfall
            footfall_url = "https://footfall-automation-609095880025.us-central1.run.app/trigger"
            reset_url = "https://footfall-automation-609095880025.us-central1.run.app/reset"
            
            # Headers com autenticação
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('GCLOUD_ACCESS_TOKEN', '')}"
            }
            
            # Dados da requisição
            data = {"test_mode": False}
            
            # Fazer chamada para o serviço de footfall
            response = requests.post(footfall_url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("✅ Atualização de footfall acionada com sucesso")
                    return True
                else:
                    logger.error(f"❌ Erro na atualização de footfall: {result.get('message', 'Erro desconhecido')}")
                    return False
            elif response.status_code == 409:
                logger.warning("⚠️ Footfall já está em execução, tentando resetar...")
                
                # Tentar resetar o footfall
                try:
                    reset_response = requests.post(reset_url, headers=headers, timeout=30)
                    if reset_response.status_code == 200:
                        logger.info("✅ Footfall resetado com sucesso, tentando novamente...")
                        
                        # Aguardar um pouco e tentar novamente
                        import time
                        time.sleep(2)
                        
                        # Segunda tentativa
                        retry_response = requests.post(footfall_url, headers=headers, json=data, timeout=120)
                        if retry_response.status_code == 200:
                            result = retry_response.json()
                            if result.get('success'):
                                logger.info("✅ Atualização de footfall acionada com sucesso após reset")
                                return True
                            else:
                                logger.error(f"❌ Erro na segunda tentativa: {result.get('message', 'Erro desconhecido')}")
                                return False
                        else:
                            logger.error(f"❌ Erro na segunda tentativa: {retry_response.status_code} - {retry_response.text}")
                            return False
                    else:
                        logger.error(f"❌ Erro ao resetar footfall: {reset_response.status_code} - {reset_response.text}")
                        return False
                        
                except Exception as reset_error:
                    logger.error(f"❌ Erro ao tentar resetar footfall: {reset_error}")
                    return False
            else:
                logger.error(f"❌ Erro ao acionar footfall: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao acionar atualização de footfall: {e}")
            return False
    
    def run_update(self):
        """Executa uma atualização completa do dashboard"""
        try:
            logger.info("🚀 Iniciando atualização automática do dashboard...")
            
            # Baixar arquivo atualizado do GitHub primeiro
            logger.info("📥 Baixando versão mais recente do dashboard do GitHub...")
            if not self.download_dashboard_from_github():
                logger.error("❌ Falha ao baixar dashboard do GitHub")
                return False
            
            # Criar backup
            self.create_backup()
            
            # Inicializar processador se necessário
            if not self.processor:
                self.processor = GoogleSheetsProcessor()
            
            # Obter dados de todos os canais
            daily_data = self.processor.get_all_channels_data()
            
            if not daily_data:
                logger.error("❌ Nenhum dado foi coletado")
                return False
            
            # Atualizar dashboard
            success = self.update_dashboard_data(daily_data)
            if not success:
                return False
            
            # Atualizar dados CONS e PER
            success = self.update_cons_and_per_data(daily_data)
            if not success:
                return False
            
            logger.info("🎉 Atualização automática concluída com sucesso!")
            
            # Estatísticas finais
            channels = set(item['channel'] for item in daily_data)
            total_spend = sum(item['spend'] for item in daily_data)
            total_impressions = sum(item['impressions'] for item in daily_data)
            total_clicks = sum(item['clicks'] for item in daily_data)
            
            logger.info(f"📊 Estatísticas da atualização:")
            logger.info(f"  - Canais processados: {len(channels)}")
            logger.info(f"  - Registros totais: {len(daily_data)}")
            
            # Acionar atualização de footfall após atualização dos canais
            logger.info("🔄 Iniciando atualização de footfall...")
            footfall_success = self.trigger_footfall_update()
            if footfall_success:
                logger.info("✅ Processo completo: Canais + Footfall atualizados com sucesso!")
            else:
                logger.warning("⚠️ Canais atualizados, mas footfall falhou. Verifique logs.")
            logger.info(f"  - Total investido: R$ {total_spend:.2f}")
            logger.info(f"  - Total impressões: {total_impressions:,}")
            logger.info(f"  - Total cliques: {total_clicks:,}")
            
            # Fazer commit e push para o GitHub
            github_success = self.commit_and_push_to_github()
            if github_success:
                logger.info("🌐 Dashboard atualizado no GitHub e disponível via Vercel")
            else:
                logger.warning("⚠️ Dashboard atualizado localmente, mas falhou o push para GitHub")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante atualização: {e}")
            return False
    
    def start_scheduler(self):
        """Inicia o agendador de atualizações"""
        try:
            interval_hours = AUTOMATION_CONFIG['update_interval_hours']
            
            logger.info(f"⏰ Configurando atualização a cada {interval_hours} horas...")
            
            # Agendar atualização
            schedule.every(interval_hours).hours.do(self.run_update)
            
            # Executar uma vez imediatamente
            logger.info("🔄 Executando primeira atualização...")
            self.run_update()
            
            logger.info("✅ Agendador iniciado! Pressione Ctrl+C para parar.")
            
            # Loop principal
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
                
        except KeyboardInterrupt:
            logger.info("🛑 Agendador interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no agendador: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando automação do dashboard...")
    
    try:
        automation = DashboardAutomation()
        automation.start_scheduler()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()
