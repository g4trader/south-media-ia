#!/usr/bin/env python3

import csv
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardAutomation:
    def __init__(self):
        self.staging_url = "https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app"
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configurar o driver do Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Executar sem interface gráfica
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("✅ Driver do Selenium configurado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def read_csv_data(self, csv_file="dashboards.csv"):
        """Ler dados do arquivo CSV"""
        try:
            dashboards = []
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Extrair ID da planilha da URL
                    sheet_url = row['planilha']
                    sheet_id = sheet_url.split('/d/')[1].split('/')[0] if '/d/' in sheet_url else sheet_url
                    
                    dashboard_data = {
                        'cliente': row['cliente'].strip(),
                        'campanha': row['campanha'].strip(),
                        'planilha': sheet_id,
                        'canal': row['canal'].strip(),
                        'kpi': row['kpi'].strip().upper()
                    }
                    dashboards.append(dashboard_data)
            
            logger.info(f"📊 {len(dashboards)} dashboards carregados do CSV")
            return dashboards
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler CSV: {e}")
            return []
    
    def generate_dashboard_via_api(self, dashboard_data):
        """Gerar dashboard via API (mais rápido e confiável)"""
        try:
            # Gerar campaign_key
            campaign_key = f"{dashboard_data['cliente'].lower().replace(' ', '_')}_{dashboard_data['campanha'].lower().replace(' ', '_').replace(' ', '_')}"
            campaign_key = ''.join(c for c in campaign_key if c.isalnum() or c in ['_', '-'])[:100]  # Limitar tamanho
            
            # Preparar dados para API
            api_data = {
                "campaign_key": campaign_key,
                "client": dashboard_data['cliente'],
                "campaign_name": dashboard_data['campanha'],
                "sheet_id": dashboard_data['planilha'],
                "channel": dashboard_data['canal'],
                "kpi": dashboard_data['kpi']
            }
            
            logger.info(f"🚀 Gerando dashboard: {dashboard_data['cliente']} - {dashboard_data['campanha']}")
            
            # Chamar API
            response = requests.post(
                f"{self.staging_url}/api/generate-dashboard",
                json=api_data,
                timeout=300  # 5 minutos timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    dashboard_url = result.get('dashboard_url', 'N/A')
                    logger.info(f"✅ Dashboard criado: {dashboard_url}")
                    return True, dashboard_url
                else:
                    logger.error(f"❌ Erro na API: {result.get('message', 'Erro desconhecido')}")
                    return False, None
            else:
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dashboard: {e}")
            return False, None
    
    def generate_dashboard_via_web(self, dashboard_data):
        """Gerar dashboard via interface web (fallback)"""
        try:
            logger.info(f"🌐 Acessando interface web: {dashboard_data['cliente']} - {dashboard_data['campanha']}")
            
            # Acessar página do gerador
            self.driver.get(f"{self.staging_url}/dash-generator-pro")
            
            # Aguardar página carregar
            self.wait.until(EC.presence_of_element_located((By.ID, "campaign-key")))
            
            # Preencher formulário
            campaign_key = f"{dashboard_data['cliente'].lower().replace(' ', '_')}_{dashboard_data['campanha'].lower().replace(' ', '_').replace(' ', '_')}"
            campaign_key = ''.join(c for c in campaign_key if c.isalnum() or c in ['_', '-'])[:100]
            
            # Campo campaign-key
            campaign_key_input = self.driver.find_element(By.ID, "campaign-key")
            campaign_key_input.clear()
            campaign_key_input.send_keys(campaign_key)
            
            # Campo client
            client_input = self.driver.find_element(By.ID, "client")
            client_input.clear()
            client_input.send_keys(dashboard_data['cliente'])
            
            # Campo campaign-name
            campaign_name_input = self.driver.find_element(By.ID, "campaign-name")
            campaign_name_input.clear()
            campaign_name_input.send_keys(dashboard_data['campanha'])
            
            # Campo sheet-id
            sheet_id_input = self.driver.find_element(By.ID, "sheet-id")
            sheet_id_input.clear()
            sheet_id_input.send_keys(dashboard_data['planilha'])
            
            # Campo channel
            channel_input = self.driver.find_element(By.ID, "channel")
            channel_input.clear()
            channel_input.send_keys(dashboard_data['canal'])
            
            # Campo kpi
            kpi_input = self.driver.find_element(By.ID, "kpi")
            kpi_input.clear()
            kpi_input.send_keys(dashboard_data['kpi'])
            
            # Clicar em gerar
            generate_button = self.driver.find_element(By.ID, "generate-dashboard")
            generate_button.click()
            
            # Aguardar geração
            self.wait.until(EC.presence_of_element_located((By.ID, "generation-result")))
            
            # Verificar resultado
            result_element = self.driver.find_element(By.ID, "generation-result")
            if "success" in result_element.get_attribute("class"):
                logger.info(f"✅ Dashboard criado via web: {dashboard_data['cliente']} - {dashboard_data['campanha']}")
                return True
            else:
                logger.error(f"❌ Erro na geração via web: {result_element.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na geração via web: {e}")
            return False
    
    def run_automation(self):
        """Executar automação completa"""
        try:
            logger.info("🤖 INICIANDO AUTOMAÇÃO DE CRIAÇÃO DE DASHBOARDS")
            logger.info("=" * 60)
            
            # Ler dados do CSV
            dashboards = self.read_csv_data()
            if not dashboards:
                logger.error("❌ Nenhum dashboard encontrado no CSV")
                return False
            
            # Configurar driver (para fallback web)
            self.setup_driver()
            
            # Estatísticas
            total = len(dashboards)
            success_count = 0
            failed_count = 0
            failed_dashboards = []
            
            logger.info(f"📊 Total de dashboards para criar: {total}")
            
            # Gerar cada dashboard
            for i, dashboard_data in enumerate(dashboards, 1):
                logger.info(f"\\n🔄 [{i}/{total}] Processando: {dashboard_data['cliente']} - {dashboard_data['campanha']}")
                
                # Tentar API primeiro (mais rápido)
                success, dashboard_url = self.generate_dashboard_via_api(dashboard_data)
                
                if success:
                    success_count += 1
                    logger.info(f"✅ Sucesso: {dashboard_url}")
                else:
                    logger.warning(f"⚠️ API falhou, tentando via web...")
                    
                    # Fallback para interface web
                    success = self.generate_dashboard_via_web(dashboard_data)
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ Sucesso via web")
                    else:
                        failed_count += 1
                        failed_dashboards.append(dashboard_data)
                        logger.error(f"❌ Falhou: {dashboard_data['cliente']} - {dashboard_data['campanha']}")
                
                # Pausa entre requests
                if i < total:
                    time.sleep(2)
            
            # Relatório final
            logger.info("\\n" + "=" * 60)
            logger.info("📊 RELATÓRIO FINAL")
            logger.info("=" * 60)
            logger.info(f"✅ Dashboards criados com sucesso: {success_count}")
            logger.info(f"❌ Dashboards que falharam: {failed_count}")
            logger.info(f"📊 Taxa de sucesso: {(success_count/total)*100:.1f}%")
            
            if failed_dashboards:
                logger.info("\\n❌ DASHBOARDS QUE FALHARAM:")
                for dashboard in failed_dashboards:
                    logger.info(f"  - {dashboard['cliente']} - {dashboard['campanha']}")
            
            return success_count == total
            
        except Exception as e:
            logger.error(f"❌ Erro na automação: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()

def main():
    automation = DashboardAutomation()
    success = automation.run_automation()
    
    if success:
        logger.info("\\n🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("✅ Todos os dashboards foram criados")
    else:
        logger.info("\\n⚠️ AUTOMAÇÃO CONCLUÍDA COM ALGUNS ERROS")
        logger.info("🔍 Verifique os logs acima para detalhes")

if __name__ == "__main__":
    main()
