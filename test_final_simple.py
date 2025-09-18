#!/usr/bin/env python3
"""
Teste Final Simplificado - Foco no Essencial
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FinalSimpleTest:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
    def setup_driver(self):
        """Configurar o driver do Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logging.info("✅ Driver do Selenium configurado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def run_test(self, test_name, test_function):
        """Executar um teste individual"""
        self.results['total_tests'] += 1
        start_time = time.time()
        
        try:
            logging.info(f"🧪 Executando: {test_name}")
            result = test_function()
            end_time = time.time()
            
            if result:
                self.results['passed_tests'] += 1
                status = "✅ PASSOU"
                logging.info(f"✅ {test_name}: PASSOU")
            else:
                self.results['failed_tests'] += 1
                status = "❌ FALHOU"
                logging.error(f"❌ {test_name}: FALHOU")
            
            self.results['test_details'].append({
                'name': test_name,
                'status': status,
                'duration': round(end_time - start_time, 2)
            })
            
        except Exception as e:
            self.results['failed_tests'] += 1
            end_time = time.time()
            logging.error(f"❌ {test_name}: ERRO - {e}")
            
            self.results['test_details'].append({
                'name': test_name,
                'status': "❌ ERRO",
                'duration': round(end_time - start_time, 2),
                'error': str(e)
            })
    
    def test_homepage(self):
        """Teste 1: Homepage"""
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(3)
            
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            return len(dashboard_cards) > 0
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de homepage: {e}")
            return False
    
    def test_login(self):
        """Teste 2: Login"""
        try:
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(3)
            
            return "dashboard-protected.html" in self.driver.current_url
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de login: {e}")
            return False
    
    def test_menu(self):
        """Teste 3: Menu"""
        try:
            menu_toggle = self.wait.until(EC.presence_of_element_located((By.ID, "navToggle")))
            menu_toggle.click()
            time.sleep(2)
            
            menu = self.driver.find_element(By.ID, "navigationMenu")
            return "open" in menu.get_attribute("class")
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de menu: {e}")
            return False
    
    def test_users_page(self):
        """Teste 4: Página de usuários"""
        try:
            self.driver.get("https://dash.iasouth.tech/users.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            if "login.html" in self.driver.current_url:
                return False
            
            # Verificar se há botão de criar usuário
            create_btn = self.driver.find_element(By.ID, "createUserBtn")
            return create_btn is not None
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de usuários: {e}")
            return False
    
    def test_companies_page(self):
        """Teste 5: Página de empresas"""
        try:
            self.driver.get("https://dash.iasouth.tech/companies.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            if "login.html" in self.driver.current_url:
                return False
            
            # Verificar se há botão de criar empresa
            create_btn = self.driver.find_element(By.ID, "createCompanyBtn")
            return create_btn is not None
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de empresas: {e}")
            return False
    
    def test_system_status(self):
        """Teste 6: Status do sistema"""
        try:
            self.driver.get("https://dash.iasouth.tech/system-status.html")
            time.sleep(3)
            
            status_cards = self.driver.find_elements(By.CLASS_NAME, "status-card")
            return len(status_cards) >= 3
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de status: {e}")
            return False
    
    def test_dashboard(self):
        """Teste 7: Dashboard"""
        try:
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            return len(dashboard_cards) > 0
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de dashboard: {e}")
            return False
    
    def test_responsive(self):
        """Teste 8: Design responsivo"""
        try:
            sizes = [(1920, 1080), (768, 1024), (375, 667)]
            
            for width, height in sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                body = self.driver.find_element(By.TAG_NAME, "body")
                if not body.is_displayed():
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste responsivo: {e}")
            return False
    
    def test_performance(self):
        """Teste 9: Performance"""
        try:
            pages = [
                "https://dash.iasouth.tech",
                "https://dash.iasouth.tech/dashboard-protected.html",
                "https://dash.iasouth.tech/users.html",
                "https://dash.iasouth.tech/companies.html",
                "https://dash.iasouth.tech/system-status.html"
            ]
            
            load_times = []
            for page in pages:
                page_start = time.time()
                self.driver.get(page)
                time.sleep(2)
                page_end = time.time()
                load_times.append(page_end - page_start)
            
            avg_load_time = sum(load_times) / len(load_times)
            return avg_load_time < 5
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de performance: {e}")
            return False
    
    def test_security(self):
        """Teste 10: Segurança"""
        try:
            # Limpar sessão
            self.driver.delete_all_cookies()
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            # Tentar acessar página protegida
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            return "login.html" in self.driver.current_url
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de segurança: {e}")
            return False
    
    def calculate_quality_score(self):
        """Calcular pontuação de qualidade"""
        if self.results['total_tests'] == 0:
            return 0
        
        passed_ratio = self.results['passed_tests'] / self.results['total_tests']
        return round(passed_ratio * 100, 1)
    
    def generate_report(self):
        """Gerar relatório de qualidade"""
        quality_score = self.calculate_quality_score()
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO FINAL DE QUALIDADE DO SISTEMA")
        print("="*80)
        print(f"🎯 Pontuação de Qualidade: {quality_score}%")
        print(f"📈 Testes Executados: {self.results['total_tests']}")
        print(f"✅ Testes Aprovados: {self.results['passed_tests']}")
        print(f"❌ Testes Falharam: {self.results['failed_tests']}")
        
        print(f"\n📋 Detalhes dos Testes:")
        for test in self.results['test_details']:
            print(f"   {test['status']} {test['name']} ({test['duration']}s)")
        
        # Classificação de qualidade
        if quality_score >= 90:
            grade = "🏆 EXCELENTE"
        elif quality_score >= 80:
            grade = "🥇 MUITO BOM"
        elif quality_score >= 70:
            grade = "🥈 BOM"
        elif quality_score >= 60:
            grade = "🥉 REGULAR"
        else:
            grade = "⚠️ PRECISA MELHORAR"
        
        print(f"\n🏅 Classificação: {grade}")
        print("="*80)
    
    def run_all_tests(self):
        """Executar todos os testes"""
        if not self.setup_driver():
            return False
        
        try:
            logging.info("🚀 Iniciando Teste Final Simplificado...")
            
            # Executar todos os testes
            self.run_test("Homepage", self.test_homepage)
            self.run_test("Login", self.test_login)
            self.run_test("Menu", self.test_menu)
            self.run_test("Página de Usuários", self.test_users_page)
            self.run_test("Página de Empresas", self.test_companies_page)
            self.run_test("Status do Sistema", self.test_system_status)
            self.run_test("Dashboard", self.test_dashboard)
            self.run_test("Design Responsivo", self.test_responsive)
            self.run_test("Performance", self.test_performance)
            self.run_test("Segurança", self.test_security)
            
            # Gerar relatório
            self.generate_report()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro durante execução dos testes: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🧹 Driver do Selenium encerrado")

def main():
    """Função principal"""
    tester = FinalSimpleTest()
    success = tester.run_all_tests()
    
    if success:
        logging.info("🎉 Teste final simplificado finalizado com sucesso!")
    else:
        logging.error("❌ Teste final simplificado falhou!")

if __name__ == "__main__":
    main()
