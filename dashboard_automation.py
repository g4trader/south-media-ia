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
        self.dashboard_file = AUTOMATION_CONFIG['dashboard_file']
        self.backup_enabled = AUTOMATION_CONFIG['backup_enabled']
        self.backup_dir = AUTOMATION_CONFIG['backup_dir']
        self.processor = None
        
        # Criar diretório de backup se necessário
        if self.backup_enabled:
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Cria backup do dashboard atual"""
        if not self.backup_enabled:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"dash_sonho_backup_{timestamp}.html"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.dashboard_file, backup_path)
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
        """Atualiza dados do dashboard"""
        try:
            logger.info("🔧 Atualizando dados do dashboard...")
            
            # Ler HTML atual
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Criar string JavaScript para DAILY
            daily_items = []
            for item in daily_data:
                item_js = "{"
                item_pairs = []
                for key, value in item.items():
                    item_pairs.append(f'"{key}": {self.format_js_value(value)}')
                item_js += ", ".join(item_pairs) + "}"
                daily_items.append(item_js)
            
            new_daily_js = "const DAILY = [" + ", ".join(daily_items) + "];"
            
            # Substituir no HTML
            daily_pattern = r'const DAILY = \[(.*?)\];'
            html_content = re.sub(daily_pattern, new_daily_js, html_content, flags=re.DOTALL)
            
            # Salvar HTML atualizado
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Dashboard atualizado com {len(daily_data)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dashboard: {e}")
            return False
    
    def calculate_cons_data(self, daily_data):
        """Calcula dados consolidadas (CONS) baseados nos dados diários"""
        try:
            logger.info("📊 Calculando dados consolidados...")
            
            # Valores de orçamento contratado por canal
            budget_contratado = {
                "YouTube": 25000.00,
                "TikTok": 25000.00,
                "Netflix": 25000.00,
                "Disney": 25000.00,
                "CTV": 12000.00,
                "Footfall Display": 10000.00
            }
            
            # Agrupar por canal
            channels = {}
            for item in daily_data:
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
                
                channels[channel]['spend'] += item['spend']
                channels[channel]['impressions'] += item['impressions']
                channels[channel]['clicks'] += item['clicks']
                channels[channel]['starts'] += item.get('starts', 0) if item.get('starts', '') != '' else 0
                channels[channel]['q25'] += item.get('q25', 0) if item.get('q25', '') != '' else 0
                channels[channel]['q50'] += item.get('q50', 0) if item.get('q50', '') != '' else 0
                channels[channel]['q75'] += item.get('q75', 0) if item.get('q75', '') != '' else 0
                channels[channel]['q100'] += item.get('q100', 0) if item.get('q100', '') != '' else 0
                if item['visits'] and str(item['visits']).isdigit():
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
            
            # Valores de orçamento contratado por canal
            budget_contratado = {
                "YouTube": 25000.00,
                "TikTok": 25000.00,
                "Netflix": 25000.00,
                "Disney": 25000.00,
                "CTV": 12000.00,
                "Footfall Display": 10000.00
            }
            
            # Agrupar por canal
            channels = {}
            for item in daily_data:
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
                
                channels[channel]['spend'] += item['spend']
                channels[channel]['impressions'] += item['impressions']
                channels[channel]['clicks'] += item['clicks']
                channels[channel]['starts'] += item.get('starts', 0) if item.get('starts', '') != '' else 0
                channels[channel]['q25'] += item.get('q25', 0) if item.get('q25', '') != '' else 0
                channels[channel]['q50'] += item.get('q50', 0) if item.get('q50', '') != '' else 0
                channels[channel]['q75'] += item.get('q75', 0) if item.get('q75', '') != '' else 0
                channels[channel]['q100'] += item.get('q100', 0) if item.get('q100', '') != '' else 0
                if item['visits'] and str(item['visits']).isdigit():
                    channels[channel]['visits'] += int(item['visits'])
                channels[channel]['creatives'].add(item['creative'])
            
            # Criar dados PER
            per_data = []
            for channel_name, data in channels.items():
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
                
                channel_data = {
                    "Canal": channel_name,
                    "Budget Contratado (R$)": budget_contratado_val,
                    "Budget Utilizado (R$)": data['spend'],
                    "Impressões": data['impressions'],
                    "Cliques": data['clicks'],
                    "CTR (%)": ctr,
                    "VC (100%)": data['q100'] if channel_name in ["YouTube", "Netflix", "Disney", "CTV"] else data['starts'] if channel_name == "TikTok" else 0,
                    "VTR (100%)": vtr / 100,  # Converter para decimal para o dashboard
                    "CPV (R$)": cpv,
                    "CPM (R$)": cpm,
                    "Pacing (%)": pacing,
                    "Criativos Únicos": len(data['creatives'])
                }
                
                per_data.append(channel_data)
            
            logger.info(f"✅ Dados PER calculados para {len(per_data)} canais com métricas completas")
            return per_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular dados PER: {e}")
            return []
    
    def update_cons_and_per_data(self, daily_data):
        """Atualiza dados CONS e PER no dashboard"""
        try:
            logger.info("🔧 Atualizando dados CONS e PER...")
            
            # Calcular dados
            cons_data = self.calculate_cons_data(daily_data)
            per_data = self.calculate_per_data(daily_data)
            
            if not cons_data or not per_data:
                logger.error("❌ Erro ao calcular dados CONS/PER")
                return False
            
            # Ler HTML atual
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Atualizar CONS
            cons_js = "const CONS = " + json.dumps(cons_data, indent=2, ensure_ascii=False) + ";"
            cons_pattern = r'const CONS = \{.*?\};'
            html_content = re.sub(cons_pattern, cons_js, html_content, flags=re.DOTALL)
            
            # Atualizar PER
            per_js = "const PER = " + json.dumps(per_data, indent=2, ensure_ascii=False) + ";"
            per_pattern = r'const PER = \[.*?\];'
            html_content = re.sub(per_pattern, per_js, html_content, flags=re.DOTALL)
            
            # Salvar HTML atualizado
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("✅ Dados CONS e PER atualizados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dados CONS/PER: {e}")
            return False
    
    def commit_and_push_to_github(self):
        """Faz commit e push das alterações para o GitHub usando API"""
        try:
            logger.info("📤 Fazendo commit e push para o GitHub...")
            
            # Ler o arquivo atualizado
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Usar GitHub API para atualizar o arquivo
            import requests
            import base64
            
            # Configurações do GitHub
            repo_owner = "g4trader"  # Seu username do GitHub
            repo_name = "south-media-ia"  # Nome do repositório
            file_path = "static/dash_sonho.html"
            github_token = os.environ.get('GITHUB_TOKEN')  # Token do GitHub
            
            if not github_token:
                logger.warning("⚠️ GITHUB_TOKEN não configurado, pulando push para GitHub")
                return False
            
            # Limpar quebras de linha do token
            github_token = github_token.strip()
            
            # Obter SHA do arquivo atual
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
            
            # Log para debug
            logger.info(f"🔍 Token GitHub configurado: {github_token[:10]}...")
            logger.info(f"🔍 URL da requisição: {url}")
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Fazer requisição para obter SHA atual
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"❌ Erro ao obter SHA do arquivo: {response.status_code}")
                return False
            
            current_sha = response.json()["sha"]
            
            # Preparar dados para atualização
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            commit_message = f"🤖 Atualização automática do dashboard - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            data = {
                "message": commit_message,
                "content": content_b64,
                "sha": current_sha
            }
            
            # Fazer commit via API
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                logger.info("✅ Commit e push realizados com sucesso via GitHub API")
                return True
            else:
                logger.error(f"❌ Erro ao fazer commit via GitHub API: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit/push via GitHub API: {e}")
            return False
    
    def run_update(self):
        """Executa uma atualização completa do dashboard"""
        try:
            logger.info("🚀 Iniciando atualização automática do dashboard...")
            
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
