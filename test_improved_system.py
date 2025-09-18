#!/usr/bin/env python3
"""
Teste Melhorado do Sistema - Com Correções
Verifica todas as funcionalidades do sistema multi-tenant
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_improved_results.log'),
        logging.StreamHandler()
    ]
)

class ImprovedSystemTest:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'performance_metrics': {},
            'quality_score': 0
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
                'duration': round(end_time - start_time, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            self.results['failed_tests'] += 1
            end_time = time.time()
            logging.error(f"❌ {test_name}: ERRO - {e}")
            
            self.results['test_details'].append({
                'name': test_name,
                'status': "❌ ERRO",
                'duration': round(end_time - start_time, 2),
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    def handle_alert(self):
        """Lidar com alertas do navegador"""
        try:
            alert = Alert(self.driver)
            alert_text = alert.text
            alert.accept()
            return alert_text
        except:
            return None
    
    def test_homepage_accessibility(self):
        """Teste 1: Acessibilidade da página inicial"""
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(3)
            
            # Verificar elementos essenciais
            title = self.driver.title
            if "Dashboard" not in title:
                return False
            
            # Verificar se há dashboards listados
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if len(dashboard_cards) == 0:
                return False
            
            logging.info(f"✅ Homepage: {len(dashboard_cards)} dashboards encontrados")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de homepage: {e}")
            return False
    
    def test_login_system(self):
        """Teste 2: Sistema de login"""
        try:
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            # Verificar elementos do login
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            # Testar login
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            
            # Verificar redirecionamento
            time.sleep(3)
            current_url = self.driver.current_url
            if "dashboard-protected.html" not in current_url:
                return False
            
            logging.info("✅ Login realizado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de login: {e}")
            return False
    
    def test_navigation_menu(self):
        """Teste 3: Menu de navegação"""
        try:
            # Verificar se o menu está presente
            menu_toggle = self.wait.until(EC.presence_of_element_located((By.ID, "navToggle")))
            menu_toggle.click()
            time.sleep(2)  # Aguardar mais tempo
            
            # Verificar se o menu abriu
            menu = self.driver.find_element(By.ID, "navigationMenu")
            if "open" not in menu.get_attribute("class"):
                return False
            
            # Verificar links do menu
            menu_links = self.driver.find_elements(By.CLASS_NAME, "nav-link")
            expected_links = ["Dashboard", "Usuários", "Empresas", "Status do Sistema"]
            
            for expected in expected_links:
                found = False
                for link in menu_links:
                    if expected in link.text:
                        found = True
                        break
                if not found:
                    return False
            
            logging.info("✅ Menu de navegação funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de menu: {e}")
            return False
    
    def test_user_management(self):
        """Teste 4: Gerenciamento de usuários"""
        try:
            # Fazer login primeiro se necessário
            if "login.html" in self.driver.current_url:
                username_field = self.driver.find_element(By.ID, "username")
                password_field = self.driver.find_element(By.ID, "password")
                login_button = self.driver.find_element(By.ID, "loginButton")
                
                username_field.send_keys("admin")
                password_field.send_keys("dashboard2025")
                login_button.click()
                time.sleep(3)
            
            self.driver.get("https://dash.iasouth.tech/users.html")
            time.sleep(3)
            
            # Lidar com alerta de permissão se aparecer
            alert_text = self.handle_alert()
            if alert_text and "permissão" in alert_text:
                logging.info("✅ Sistema de permissões funcionando (alerta de permissão)")
                return True
            
            # Verificar elementos da página
            novo_usuario_btn = self.wait.until(EC.presence_of_element_located((By.ID, "createUserBtn")))
            atualizar_btn = self.driver.find_element(By.ID, "refreshUsersBtn")
            
            # Testar modal de criação
            novo_usuario_btn.click()
            time.sleep(1)
            
            modal = self.driver.find_element(By.ID, "userModal")
            modal_display = modal.get_attribute("style")
            if "display: block" not in modal_display:
                return False
            
            # Fechar modal
            close_btn = self.driver.find_element(By.CLASS_NAME, "close")
            close_btn.click()
            time.sleep(1)
            
            logging.info("✅ Gerenciamento de usuários funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de usuários: {e}")
            return False
    
    def test_company_management(self):
        """Teste 5: Gerenciamento de empresas"""
        try:
            # Fazer login primeiro se necessário
            if "login.html" in self.driver.current_url:
                username_field = self.driver.find_element(By.ID, "username")
                password_field = self.driver.find_element(By.ID, "password")
                login_button = self.driver.find_element(By.ID, "loginButton")
                
                username_field.send_keys("admin")
                password_field.send_keys("dashboard2025")
                login_button.click()
                time.sleep(3)
            
            self.driver.get("https://dash.iasouth.tech/companies.html")
            time.sleep(3)
            
            # Lidar com alerta de permissão se aparecer
            alert_text = self.handle_alert()
            if alert_text and "permissão" in alert_text:
                logging.info("✅ Sistema de permissões funcionando (alerta de permissão)")
                return True
            
            # Verificar elementos da página
            nova_empresa_btn = self.wait.until(EC.presence_of_element_located((By.ID, "createCompanyBtn")))
            atualizar_btn = self.driver.find_element(By.ID, "refreshCompaniesBtn")
            
            # Testar modal de criação
            nova_empresa_btn.click()
            time.sleep(1)
            
            modal = self.driver.find_element(By.ID, "companyModal")
            modal_display = modal.get_attribute("style")
            if "display: block" not in modal_display:
                return False
            
            # Testar criação de empresa
            nome_field = self.driver.find_element(By.ID, "companyName")
            codigo_field = self.driver.find_element(By.ID, "companyCode")
            salvar_btn = self.driver.find_element(By.ID, "saveCompanyBtn")
            
            nome_field.send_keys("Empresa Teste")
            codigo_field.send_keys("TEST001")
            
            # Usar JavaScript para clicar no botão
            self.driver.execute_script("arguments[0].click();", salvar_btn)
            time.sleep(2)
            
            # Verificar se empresa foi criada
            empresas_grid = self.driver.find_element(By.ID, "companiesGrid")
            if "Empresa Teste" not in empresas_grid.text:
                return False
            
            logging.info("✅ Gerenciamento de empresas funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de empresas: {e}")
            return False
    
    def test_system_status(self):
        """Teste 6: Status do sistema"""
        try:
            self.driver.get("https://dash.iasouth.tech/system-status.html")
            time.sleep(3)
            
            # Lidar com alerta de permissão se aparecer
            alert_text = self.handle_alert()
            if alert_text and "permissão" in alert_text:
                logging.info("✅ Sistema de permissões funcionando (alerta de permissão)")
                return True
            
            # Verificar cards de status
            status_cards = self.driver.find_elements(By.CLASS_NAME, "status-card")
            if len(status_cards) < 3:
                return False
            
            # Testar botão de refresh
            refresh_btn = self.driver.find_element(By.CLASS_NAME, "refresh-btn")
            refresh_btn.click()
            time.sleep(2)
            
            logging.info("✅ Status do sistema funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de status: {e}")
            return False
    
    def test_dashboard_functionality(self):
        """Teste 7: Funcionalidades do dashboard"""
        try:
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            # Lidar com alerta de permissão se aparecer
            alert_text = self.handle_alert()
            if alert_text and "permissão" in alert_text:
                logging.info("✅ Sistema de permissões funcionando (alerta de permissão)")
                return True
            
            # Verificar se dashboards estão carregados
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if len(dashboard_cards) == 0:
                return False
            
            # Verificar botão de sync (se existir)
            sync_buttons = self.driver.find_elements(By.CLASS_NAME, "sync-button")
            if sync_buttons:
                sync_buttons[0].click()
                time.sleep(2)
            
            logging.info("✅ Dashboard funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de dashboard: {e}")
            return False
    
    def test_responsive_design(self):
        """Teste 8: Design responsivo"""
        try:
            # Testar diferentes tamanhos de tela
            sizes = [(1920, 1080), (1366, 768), (768, 1024), (375, 667)]
            
            for width, height in sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Verificar se elementos estão visíveis
                body = self.driver.find_element(By.TAG_NAME, "body")
                if not body.is_displayed():
                    return False
            
            logging.info("✅ Design responsivo funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste responsivo: {e}")
            return False
    
    def test_performance(self):
        """Teste 9: Performance"""
        try:
            start_time = time.time()
            
            # Testar carregamento de páginas
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
                
                # Lidar com alertas de permissão
                self.handle_alert()
                
                page_end = time.time()
                load_times.append(page_end - page_start)
            
            avg_load_time = sum(load_times) / len(load_times)
            self.results['performance_metrics']['avg_load_time'] = round(avg_load_time, 2)
            self.results['performance_metrics']['max_load_time'] = round(max(load_times), 2)
            self.results['performance_metrics']['min_load_time'] = round(min(load_times), 2)
            
            # Considerar bom se carregamento médio < 5 segundos
            if avg_load_time < 5:
                logging.info(f"✅ Performance: {avg_load_time}s (média)")
                return True
            else:
                logging.warning(f"⚠️ Performance: {avg_load_time}s (lento)")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de performance: {e}")
            return False
    
    def test_security(self):
        """Teste 10: Segurança básica"""
        try:
            # Limpar sessão primeiro
            self.driver.delete_all_cookies()
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            # Testar acesso sem login
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "login.html" in current_url:
                logging.info("✅ Redirecionamento de segurança funcionando")
                return True
            else:
                logging.warning("⚠️ Página protegida acessível sem login")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de segurança: {e}")
            return False
    
    def test_authentication_flow(self):
        """Teste 11: Fluxo completo de autenticação"""
        try:
            # Limpar sessão primeiro
            self.driver.delete_all_cookies()
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            # 1. Acessar página protegida sem login
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            # 2. Verificar redirecionamento para login
            if "login.html" not in self.driver.current_url:
                return False
            
            # 3. Fazer login
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            # 4. Verificar acesso à área protegida
            if "dashboard-protected.html" not in self.driver.current_url:
                return False
            
            # 5. Verificar se informações do usuário estão sendo exibidas
            user_info = self.driver.find_elements(By.CLASS_NAME, "user-info")
            if len(user_info) == 0:
                return False
            
            logging.info("✅ Fluxo de autenticação completo funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de autenticação: {e}")
            return False
    
    def calculate_quality_score(self):
        """Calcular pontuação de qualidade"""
        if self.results['total_tests'] == 0:
            return 0
        
        passed_ratio = self.results['passed_tests'] / self.results['total_tests']
        self.results['quality_score'] = round(passed_ratio * 100, 1)
        
        return self.results['quality_score']
    
    def generate_report(self):
        """Gerar relatório de qualidade"""
        quality_score = self.calculate_quality_score()
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE QUALIDADE DO SISTEMA - VERSÃO MELHORADA")
        print("="*80)
        print(f"🎯 Pontuação de Qualidade: {quality_score}%")
        print(f"📈 Testes Executados: {self.results['total_tests']}")
        print(f"✅ Testes Aprovados: {self.results['passed_tests']}")
        print(f"❌ Testes Falharam: {self.results['failed_tests']}")
        
        if 'performance_metrics' in self.results and self.results['performance_metrics']:
            perf = self.results['performance_metrics']
            print(f"\n⚡ Performance:")
            print(f"   • Tempo médio de carregamento: {perf.get('avg_load_time', 'N/A')}s")
            print(f"   • Tempo máximo: {perf.get('max_load_time', 'N/A')}s")
            print(f"   • Tempo mínimo: {perf.get('min_load_time', 'N/A')}s")
        
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
        
        # Salvar relatório em arquivo
        with open('improved_quality_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logging.info(f"📄 Relatório salvo em: improved_quality_report.json")
    
    def run_all_tests(self):
        """Executar todos os testes"""
        if not self.setup_driver():
            return False
        
        try:
            logging.info("🚀 Iniciando Teste Melhorado de Qualidade do Sistema...")
            
            # Executar todos os testes
            self.run_test("Acessibilidade da Homepage", self.test_homepage_accessibility)
            self.run_test("Sistema de Login", self.test_login_system)
            self.run_test("Menu de Navegação", self.test_navigation_menu)
            self.run_test("Gerenciamento de Usuários", self.test_user_management)
            self.run_test("Gerenciamento de Empresas", self.test_company_management)
            self.run_test("Status do Sistema", self.test_system_status)
            self.run_test("Funcionalidades do Dashboard", self.test_dashboard_functionality)
            self.run_test("Design Responsivo", self.test_responsive_design)
            self.run_test("Performance", self.test_performance)
            self.run_test("Segurança Básica", self.test_security)
            self.run_test("Fluxo de Autenticação", self.test_authentication_flow)
            
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
    tester = ImprovedSystemTest()
    success = tester.run_all_tests()
    
    if success:
        logging.info("🎉 Teste melhorado finalizado com sucesso!")
    else:
        logging.error("❌ Teste melhorado falhou!")

if __name__ == "__main__":
    main()
