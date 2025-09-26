#!/usr/bin/env python3
"""
Teste End-to-End do MVP Dashboard Builder na Nuvem
Testa todo o fluxo: gerador -> dashboard -> dados carregando
"""

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudRunE2ETest:
    def __init__(self):
        self.base_url = "https://mvp-dashboard-builder-609095880025.us-central1.run.app"
        self.driver = None
        self.wait = None
        self.test_results = []
        
    def setup_driver(self):
        """Configurar driver do Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar sem interface gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        logger.info("✅ Driver do Selenium configurado")
        
    def teardown_driver(self):
        """Fechar driver"""
        if self.driver:
            self.driver.quit()
            logger.info("✅ Driver do Selenium fechado")
    
    def log_test_result(self, test_name, success, message=""):
        """Registrar resultado do teste"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status}: {test_name} - {message}")
    
    def test_health_check(self):
        """Teste 1: Health Check da API"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test_result("Health Check", True, "API está saudável")
                    return True
                else:
                    self.log_test_result("Health Check", False, "Status não é healthy")
                    return False
            else:
                self.log_test_result("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Health Check", False, f"Erro: {str(e)}")
            return False
    
    def test_generator_interface(self):
        """Teste 2: Interface do Gerador"""
        try:
            self.driver.get(f"{self.base_url}/test-generator")
            
            # Aguardar carregamento da página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Verificar elementos principais
            title = self.driver.find_element(By.TAG_NAME, "h1")
            if "Gerador de Dashboards" in title.text:
                self.log_test_result("Interface do Gerador", True, "Página carregou corretamente")
                
                # Verificar campos do formulário
                campaign_key_field = self.driver.find_element(By.ID, "campaign_key")
                client_field = self.driver.find_element(By.ID, "client")
                campaign_name_field = self.driver.find_element(By.ID, "campaign_name")
                sheet_id_field = self.driver.find_element(By.ID, "sheet_id")
                generate_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                
                if all([campaign_key_field, client_field, campaign_name_field, sheet_id_field, generate_button]):
                    self.log_test_result("Formulário do Gerador", True, "Todos os campos estão presentes")
                    return True
                else:
                    self.log_test_result("Formulário do Gerador", False, "Campos faltando")
                    return False
            else:
                self.log_test_result("Interface do Gerador", False, "Título não encontrado")
                return False
                
        except Exception as e:
            self.log_test_result("Interface do Gerador", False, f"Erro: {str(e)}")
            return False
    
    def test_dashboard_generation(self):
        """Teste 3: Geração de Dashboard via API"""
        try:
            test_data = {
                "campaign_key": f"teste_e2e_{int(time.time())}",
                "client": "Cliente Teste E2E",
                "campaign_name": "Campanha Teste End-to-End",
                "sheet_id": "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8",
                "channel": "Video Programática"
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate-dashboard",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    dashboard_url = data.get("dashboard_url")
                    self.log_test_result("Geração de Dashboard", True, f"Dashboard criado: {dashboard_url}")
                    return data.get("dashboard_url")
                else:
                    self.log_test_result("Geração de Dashboard", False, f"Erro na criação: {data.get('message')}")
                    return None
            else:
                self.log_test_result("Geração de Dashboard", False, f"Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test_result("Geração de Dashboard", False, f"Erro: {str(e)}")
            return None
    
    def test_dashboard_loading(self, dashboard_url):
        """Teste 4: Carregamento do Dashboard"""
        try:
            full_url = f"{self.base_url}{dashboard_url}"
            self.driver.get(full_url)
            
            # Aguardar carregamento da página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Verificar se o título contém o nome da campanha
            title = self.driver.find_element(By.TAG_NAME, "title")
            if "Dashboard" in title.text and "Cliente Teste E2E" in title.text:
                self.log_test_result("Carregamento do Dashboard", True, "Página carregou")
                
                # Verificar se o modal de loading aparece
                try:
                    loading_modal = self.wait.until(
                        EC.presence_of_element_located((By.ID, "loadingModal"))
                    )
                    if loading_modal.is_displayed():
                        self.log_test_result("Modal de Loading", True, "Modal de loading apareceu")
                        
                        # Aguardar o modal desaparecer (dados carregarem)
                        try:
                            self.wait.until_not(
                                EC.visibility_of_element_located((By.ID, "loadingModal"))
                            )
                            self.log_test_result("Carregamento de Dados", True, "Modal desapareceu - dados carregados")
                            return True
                        except TimeoutException:
                            self.log_test_result("Carregamento de Dados", False, "Modal não desapareceu em 30s")
                            return False
                    else:
                        self.log_test_result("Modal de Loading", False, "Modal não está visível")
                        return False
                        
                except TimeoutException:
                    self.log_test_result("Modal de Loading", False, "Modal não apareceu")
                    return False
            else:
                self.log_test_result("Carregamento do Dashboard", False, "Título incorreto")
                return False
                
        except Exception as e:
            self.log_test_result("Carregamento do Dashboard", False, f"Erro: {str(e)}")
            return False
    
    def test_dashboard_data_display(self):
        """Teste 5: Exibição dos Dados no Dashboard"""
        try:
            # Aguardar um pouco para os dados carregarem
            time.sleep(5)
            
            # Verificar se há dados sendo exibidos
            metrics_elements = self.driver.find_elements(By.CSS_SELECTOR, ".metric .value")
            if len(metrics_elements) > 0:
                # Verificar se pelo menos alguns valores não são zero ou vazios
                non_zero_values = 0
                for element in metrics_elements:
                    value_text = element.text.strip()
                    if value_text and value_text != "0" and value_text != "0,00" and value_text != "R$ 0,00":
                        non_zero_values += 1
                
                if non_zero_values > 0:
                    self.log_test_result("Exibição de Dados", True, f"{non_zero_values} valores não-zero encontrados")
                    
                    # Verificar tabs
                    tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab")
                    if len(tabs) >= 4:
                        self.log_test_result("Navegação por Tabs", True, f"{len(tabs)} tabs encontradas")
                        
                        # Testar navegação entre tabs
                        for i, tab in enumerate(tabs[:3]):  # Testar apenas as primeiras 3 tabs
                            try:
                                tab.click()
                                time.sleep(1)
                                if tab.get_attribute("class").find("active") != -1:
                                    self.log_test_result(f"Tab {i+1} Ativa", True, f"Tab {i+1} ativada com sucesso")
                                else:
                                    self.log_test_result(f"Tab {i+1} Ativa", False, f"Tab {i+1} não ficou ativa")
                            except Exception as e:
                                self.log_test_result(f"Tab {i+1} Ativa", False, f"Erro ao clicar: {str(e)}")
                        
                        return True
                    else:
                        self.log_test_result("Navegação por Tabs", False, "Tabs insuficientes")
                        return False
                else:
                    self.log_test_result("Exibição de Dados", False, "Todos os valores são zero")
                    return False
            else:
                self.log_test_result("Exibição de Dados", False, "Elementos de métricas não encontrados")
                return False
                
        except Exception as e:
            self.log_test_result("Exibição de Dados", False, f"Erro: {str(e)}")
            return False
    
    def test_api_data_endpoint(self, campaign_key=None):
        """Teste 6: Endpoint de Dados da API"""
        try:
            # Usar a campanha fornecida ou a campanha copacol_institucional_30s como fallback
            test_campaign = campaign_key or "copacol_institucional_30s"
            response = requests.get(
                f"{self.base_url}/api/{test_campaign}/data",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result_data = data.get("data", {})
                    summary = result_data.get("campaign_summary", {})
                    contract = result_data.get("contract", {})
                    
                    # Verificar se há dados importantes
                    if (summary.get("total_spend", 0) > 0 and 
                        contract.get("investment", 0) > 0 and
                        summary.get("total_video_completions", 0) > 0):
                        
                        self.log_test_result("API Data Endpoint", True, 
                            f"Budget: R$ {contract.get('investment', 0):,.2f}, "
                            f"Spend: R$ {summary.get('total_spend', 0):,.2f}, "
                            f"VC: {summary.get('total_video_completions', 0):,}")
                        return True
                    else:
                        self.log_test_result("API Data Endpoint", False, "Dados insuficientes")
                        return False
                else:
                    self.log_test_result("API Data Endpoint", False, f"API retornou erro: {data.get('message')}")
                    return False
            else:
                self.log_test_result("API Data Endpoint", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("API Data Endpoint", False, f"Erro: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Executar todos os testes"""
        logger.info("🚀 Iniciando Teste End-to-End do MVP Dashboard Builder na Nuvem")
        logger.info(f"🌐 URL Base: {self.base_url}")
        
        try:
            self.setup_driver()
            
            # Executar testes sequencialmente
            tests = [
                ("Health Check", self.test_health_check),
                ("Interface do Gerador", self.test_generator_interface),
                ("Geração de Dashboard", self.test_dashboard_generation),
                ("API Data Endpoint", self.test_api_data_endpoint),
            ]
            
            dashboard_url = None
            campaign_key = None
            for test_name, test_func in tests:
                logger.info(f"🧪 Executando: {test_name}")
                
                if test_name == "Geração de Dashboard":
                    dashboard_url = test_func()
                    # Extrair campaign_key da URL do dashboard
                    if dashboard_url:
                        campaign_key = dashboard_url.split('/')[-1].replace('.html', '').replace('dash_', '')
                elif test_name == "API Data Endpoint":
                    test_func(campaign_key)
                elif test_name in ["Carregamento do Dashboard", "Exibição de Dados"]:
                    if dashboard_url:
                        if test_name == "Carregamento do Dashboard":
                            success = test_func(dashboard_url)
                        else:
                            success = test_func()
                    else:
                        self.log_test_result(test_name, False, "Dashboard URL não disponível")
                else:
                    test_func()
                
                time.sleep(2)  # Pausa entre testes
            
            # Teste adicional: Dashboard existente
            if dashboard_url:
                logger.info("🧪 Testando Dashboard Gerado")
                self.test_dashboard_loading(dashboard_url)
                self.test_dashboard_data_display()
            
        finally:
            self.teardown_driver()
        
        # Relatório final
        self.generate_report()
    
    def generate_report(self):
        """Gerar relatório final"""
        logger.info("\n" + "="*80)
        logger.info("📊 RELATÓRIO FINAL - TESTE END-TO-END")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"📈 Total de Testes: {total_tests}")
        logger.info(f"✅ Testes Passaram: {passed_tests}")
        logger.info(f"❌ Testes Falharam: {failed_tests}")
        logger.info(f"📊 Taxa de Sucesso: {(passed_tests/total_tests*100):.1f}%")
        
        logger.info("\n📋 DETALHES DOS TESTES:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"  {status} {result['test']}: {result['message']}")
        
        logger.info("\n🌐 URLS TESTADAS:")
        logger.info(f"  🏠 Home: {self.base_url}/")
        logger.info(f"  🎯 Gerador: {self.base_url}/test-generator")
        logger.info(f"  🏥 Health: {self.base_url}/health")
        logger.info(f"  📊 API: {self.base_url}/api/generate-dashboard")
        
        if failed_tests == 0:
            logger.info("\n🎉 TODOS OS TESTES PASSARAM! Sistema está funcionando perfeitamente na nuvem!")
        else:
            logger.info(f"\n⚠️ {failed_tests} teste(s) falharam. Verificar logs acima.")
        
        logger.info("="*80)

if __name__ == "__main__":
    test = CloudRunE2ETest()
    test.run_all_tests()
