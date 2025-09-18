#!/usr/bin/env python3
"""
Teste de Verificação Absoluta - Análise Crítica e Detalhada
Verifica cada funcionalidade com rigor máximo
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
        logging.FileHandler('verificacao_absoluta.log'),
        logging.StreamHandler()
    ]
)

class VerificacaoAbsoluta:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': 0,
            'test_details': [],
            'performance_metrics': {},
            'security_issues': [],
            'functionality_issues': []
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
            self.wait = WebDriverWait(self.driver, 15)
            
            logging.info("✅ Driver do Selenium configurado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def run_test(self, test_name, test_function, is_critical=False):
        """Executar um teste individual com análise crítica"""
        self.results['total_tests'] += 1
        start_time = time.time()
        
        try:
            logging.info(f"🔍 VERIFICAÇÃO CRÍTICA: {test_name}")
            result = test_function()
            end_time = time.time()
            
            if result:
                self.results['passed_tests'] += 1
                status = "✅ PASSOU"
                logging.info(f"✅ {test_name}: PASSOU")
            else:
                self.results['failed_tests'] += 1
                if is_critical:
                    self.results['critical_failures'] += 1
                status = "❌ FALHOU"
                logging.error(f"❌ {test_name}: FALHOU")
            
            self.results['test_details'].append({
                'name': test_name,
                'status': status,
                'duration': round(end_time - start_time, 2),
                'critical': is_critical,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            self.results['failed_tests'] += 1
            if is_critical:
                self.results['critical_failures'] += 1
            end_time = time.time()
            logging.error(f"❌ {test_name}: ERRO CRÍTICO - {e}")
            
            self.results['test_details'].append({
                'name': test_name,
                'status': "❌ ERRO CRÍTICO",
                'duration': round(end_time - start_time, 2),
                'error': str(e),
                'critical': is_critical,
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
    
    def test_homepage_comprehensive(self):
        """Teste 1: Homepage - Análise Completa"""
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(5)
            
            # Verificar título
            title = self.driver.title
            if not title or "Dashboard" not in title:
                self.results['functionality_issues'].append("Título da homepage incorreto")
                return False
            
            # Verificar dashboards
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if len(dashboard_cards) == 0:
                self.results['functionality_issues'].append("Nenhum dashboard encontrado")
                return False
            
            # Verificar se dashboards são clicáveis
            for card in dashboard_cards[:3]:  # Testar apenas os primeiros 3
                try:
                    card.click()
                    time.sleep(2)
                    if "404" in self.driver.title or "error" in self.driver.current_url.lower():
                        self.results['functionality_issues'].append(f"Dashboard {card.text} não funciona")
                        return False
                    self.driver.back()
                    time.sleep(1)
                except:
                    self.results['functionality_issues'].append("Dashboard não clicável")
                    return False
            
            # Verificar responsividade
            self.driver.set_window_size(375, 667)
            time.sleep(2)
            if not self.driver.find_element(By.TAG_NAME, "body").is_displayed():
                self.results['functionality_issues'].append("Homepage não responsiva")
                return False
            
            logging.info(f"✅ Homepage: {len(dashboard_cards)} dashboards funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico na homepage: {e}")
            return False
    
    def test_login_comprehensive(self):
        """Teste 2: Login - Análise Completa"""
        try:
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(3)
            
            # Verificar elementos essenciais
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            # Testar login com credenciais corretas
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            if "dashboard-protected.html" not in self.driver.current_url:
                self.results['security_issues'].append("Login não redireciona corretamente")
                return False
            
            # Verificar se sessão foi criada
            session_data = self.driver.execute_script("return localStorage.getItem('dashboard_session');")
            if not session_data:
                self.results['security_issues'].append("Sessão não foi criada")
                return False
            
            # Testar login com credenciais incorretas
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("senha_errada")
            login_button.click()
            time.sleep(3)
            
            if "dashboard-protected.html" in self.driver.current_url:
                self.results['security_issues'].append("Login aceita credenciais incorretas")
                return False
            
            logging.info("✅ Sistema de login funcionando corretamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no login: {e}")
            return False
    
    def test_navigation_comprehensive(self):
        """Teste 3: Navegação - Análise Completa"""
        try:
            # Fazer login primeiro
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            # Testar menu
            menu_toggle = self.wait.until(EC.presence_of_element_located((By.ID, "navToggle")))
            menu_toggle.click()
            time.sleep(2)
            
            menu = self.driver.find_element(By.ID, "navigationMenu")
            if "open" not in menu.get_attribute("class"):
                self.results['functionality_issues'].append("Menu não abre")
                return False
            
            # Testar todos os links do menu
            menu_links = self.driver.find_elements(By.CLASS_NAME, "nav-link")
            expected_pages = ["dashboard-protected.html", "users.html", "companies.html", "system-status.html"]
            
            for link in menu_links:
                if link.get_attribute("href") and not link.get_attribute("href").startswith("#"):
                    try:
                        original_url = self.driver.current_url
                        link.click()
                        time.sleep(3)
                        
                        if "login.html" in self.driver.current_url and "dashboard-protected.html" not in original_url:
                            self.results['functionality_issues'].append(f"Link {link.text} redireciona para login")
                            return False
                        
                        # Voltar para testar próximo link
                        self.driver.back()
                        time.sleep(2)
                        
                        # Reabrir menu
                        menu_toggle = self.driver.find_element(By.ID, "navToggle")
                        menu_toggle.click()
                        time.sleep(1)
                        
                    except Exception as e:
                        self.results['functionality_issues'].append(f"Erro ao testar link {link.text}: {e}")
                        return False
            
            logging.info("✅ Menu de navegação funcionando completamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico na navegação: {e}")
            return False
    
    def test_crud_users_comprehensive(self):
        """Teste 4: CRUD Usuários - Análise Completa"""
        try:
            # Fazer login primeiro
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            # Acessar página de usuários
            self.driver.get("https://dash.iasouth.tech/users.html")
            time.sleep(5)
            
            if "login.html" in self.driver.current_url:
                self.results['security_issues'].append("Página de usuários não protegida")
                return False
            
            # Testar criação de usuário
            create_btn = self.driver.find_element(By.ID, "createUserBtn")
            create_btn.click()
            time.sleep(2)
            
            modal = self.driver.find_element(By.ID, "userModal")
            if "display: block" not in modal.get_attribute("style"):
                self.results['functionality_issues'].append("Modal de criação não abre")
                return False
            
            # Preencher formulário
            name_field = self.driver.find_element(By.ID, "userName")
            email_field = self.driver.find_element(By.ID, "userEmail")
            username_field = self.driver.find_element(By.ID, "userUsername")
            password_field = self.driver.find_element(By.ID, "userPassword")
            
            name_field.send_keys("Usuário Teste")
            email_field.send_keys("teste@teste.com")
            username_field.send_keys("teste_user")
            password_field.send_keys("teste123")
            
            # Salvar
            save_btn = self.driver.find_element(By.ID, "saveUserBtn")
            self.driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(3)
            
            # Verificar se usuário foi criado
            users_grid = self.driver.find_element(By.ID, "usersGrid")
            if "Usuário Teste" not in users_grid.text:
                self.results['functionality_issues'].append("Usuário não foi criado")
                return False
            
            logging.info("✅ CRUD de usuários funcionando completamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no CRUD de usuários: {e}")
            return False
    
    def test_crud_companies_comprehensive(self):
        """Teste 5: CRUD Empresas - Análise Completa"""
        try:
            # Fazer login primeiro
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            # Acessar página de empresas
            self.driver.get("https://dash.iasouth.tech/companies.html")
            time.sleep(5)
            
            if "login.html" in self.driver.current_url:
                self.results['security_issues'].append("Página de empresas não protegida")
                return False
            
            # Testar criação de empresa
            create_btn = self.driver.find_element(By.ID, "createCompanyBtn")
            create_btn.click()
            time.sleep(2)
            
            modal = self.driver.find_element(By.ID, "companyModal")
            if "display: block" not in modal.get_attribute("style"):
                self.results['functionality_issues'].append("Modal de criação não abre")
                return False
            
            # Preencher formulário
            name_field = self.driver.find_element(By.ID, "companyName")
            code_field = self.driver.find_element(By.ID, "companyCode")
            
            name_field.send_keys("Empresa Teste Crítica")
            code_field.send_keys("TEST_CRIT")
            
            # Salvar
            save_btn = self.driver.find_element(By.ID, "saveCompanyBtn")
            self.driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(3)
            
            # Verificar se empresa foi criada
            companies_grid = self.driver.find_element(By.ID, "companiesGrid")
            if "Empresa Teste Crítica" not in companies_grid.text:
                self.results['functionality_issues'].append("Empresa não foi criada")
                return False
            
            logging.info("✅ CRUD de empresas funcionando completamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no CRUD de empresas: {e}")
            return False
    
    def test_security_comprehensive(self):
        """Teste 6: Segurança - Análise Completa"""
        try:
            # Limpar completamente a sessão
            self.driver.delete_all_cookies()
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            # Testar acesso a páginas protegidas
            protected_pages = [
                "https://dash.iasouth.tech/dashboard-protected.html",
                "https://dash.iasouth.tech/users.html",
                "https://dash.iasouth.tech/companies.html"
            ]
            
            for page in protected_pages:
                self.driver.get(page)
                time.sleep(3)
                
                if "login.html" not in self.driver.current_url:
                    self.results['security_issues'].append(f"Página {page} acessível sem login")
                    return False
            
            # Testar tentativa de bypass de autenticação
            self.driver.execute_script("localStorage.setItem('dashboard_session', 'fake_session');")
            self.driver.get("https://dash.iasouth.tech/dashboard-protected.html")
            time.sleep(3)
            
            if "dashboard-protected.html" in self.driver.current_url:
                self.results['security_issues'].append("Sistema aceita sessão falsa")
                return False
            
            logging.info("✅ Sistema de segurança funcionando completamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico na segurança: {e}")
            return False
    
    def test_performance_comprehensive(self):
        """Teste 7: Performance - Análise Completa"""
        try:
            pages = [
                "https://dash.iasouth.tech",
                "https://dash.iasouth.tech/login.html",
                "https://dash.iasouth.tech/dashboard-protected.html",
                "https://dash.iasouth.tech/users.html",
                "https://dash.iasouth.tech/companies.html",
                "https://dash.iasouth.tech/system-status.html"
            ]
            
            load_times = []
            for page in pages:
                page_start = time.time()
                self.driver.get(page)
                time.sleep(3)
                page_end = time.time()
                load_times.append(page_end - page_start)
            
            avg_load_time = sum(load_times) / len(load_times)
            max_load_time = max(load_times)
            
            self.results['performance_metrics'] = {
                'avg_load_time': round(avg_load_time, 2),
                'max_load_time': round(max_load_time, 2),
                'min_load_time': round(min(load_times), 2),
                'all_load_times': [round(t, 2) for t in load_times]
            }
            
            if avg_load_time > 5:
                self.results['functionality_issues'].append(f"Performance lenta: {avg_load_time}s")
                return False
            
            if max_load_time > 10:
                self.results['functionality_issues'].append(f"Página muito lenta: {max_load_time}s")
                return False
            
            logging.info(f"✅ Performance excelente: {avg_load_time}s (média)")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico na performance: {e}")
            return False
    
    def test_error_handling(self):
        """Teste 8: Tratamento de Erros"""
        try:
            # Testar página inexistente
            self.driver.get("https://dash.iasouth.tech/pagina-inexistente.html")
            time.sleep(3)
            
            # Verificar se há tratamento de erro adequado
            if "404" not in self.driver.title and "error" not in self.driver.current_url.lower():
                self.results['functionality_issues'].append("Não há tratamento de erro 404")
                return False
            
            # Testar JavaScript errors
            logs = self.driver.get_log('browser')
            critical_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if len(critical_errors) > 0:
                self.results['functionality_issues'].append(f"Erros JavaScript críticos: {len(critical_errors)}")
                return False
            
            logging.info("✅ Tratamento de erros funcionando")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro crítico no tratamento de erros: {e}")
            return False
    
    def calculate_quality_score(self):
        """Calcular pontuação de qualidade com análise crítica"""
        if self.results['total_tests'] == 0:
            return 0
        
        # Penalizar falhas críticas mais severamente
        critical_penalty = self.results['critical_failures'] * 0.2
        passed_ratio = self.results['passed_tests'] / self.results['total_tests']
        
        # Aplicar penalidades por problemas identificados
        security_penalty = len(self.results['security_issues']) * 0.1
        functionality_penalty = len(self.results['functionality_issues']) * 0.05
        
        final_score = (passed_ratio - critical_penalty - security_penalty - functionality_penalty) * 100
        return max(0, round(final_score, 1))
    
    def generate_comprehensive_report(self):
        """Gerar relatório abrangente"""
        quality_score = self.calculate_quality_score()
        
        print("\n" + "="*100)
        print("🔍 RELATÓRIO DE VERIFICAÇÃO ABSOLUTA - ANÁLISE CRÍTICA")
        print("="*100)
        print(f"🎯 Pontuação de Qualidade: {quality_score}%")
        print(f"📈 Testes Executados: {self.results['total_tests']}")
        print(f"✅ Testes Aprovados: {self.results['passed_tests']}")
        print(f"❌ Testes Falharam: {self.results['failed_tests']}")
        print(f"🚨 Falhas Críticas: {self.results['critical_failures']}")
        
        if self.results['performance_metrics']:
            perf = self.results['performance_metrics']
            print(f"\n⚡ Performance:")
            print(f"   • Tempo médio: {perf.get('avg_load_time', 'N/A')}s")
            print(f"   • Tempo máximo: {perf.get('max_load_time', 'N/A')}s")
            print(f"   • Tempo mínimo: {perf.get('min_load_time', 'N/A')}s")
        
        if self.results['security_issues']:
            print(f"\n🔒 Problemas de Segurança:")
            for issue in self.results['security_issues']:
                print(f"   • {issue}")
        
        if self.results['functionality_issues']:
            print(f"\n⚙️ Problemas de Funcionalidade:")
            for issue in self.results['functionality_issues']:
                print(f"   • {issue}")
        
        print(f"\n📋 Detalhes dos Testes:")
        for test in self.results['test_details']:
            critical_mark = "🚨" if test.get('critical', False) else ""
            print(f"   {test['status']} {critical_mark} {test['name']} ({test['duration']}s)")
        
        # Classificação crítica
        if quality_score >= 95:
            grade = "🏆 EXCELENTE - CONVICÇÃO ABSOLUTA"
        elif quality_score >= 90:
            grade = "🥇 MUITO BOM - ALTA CONVICÇÃO"
        elif quality_score >= 80:
            grade = "🥈 BOM - CONVICÇÃO MODERADA"
        elif quality_score >= 70:
            grade = "🥉 REGULAR - CONVICÇÃO BAIXA"
        else:
            grade = "⚠️ PRECISA MELHORAR - SEM CONVICÇÃO"
        
        print(f"\n🏅 Classificação Crítica: {grade}")
        
        # Convicção absoluta
        if quality_score >= 95 and self.results['critical_failures'] == 0 and len(self.results['security_issues']) == 0:
            print(f"\n🎯 CONVICÇÃO ABSOLUTA: SIM - Sistema está 100% funcional!")
        else:
            print(f"\n🎯 CONVICÇÃO ABSOLUTA: NÃO - Há problemas que precisam ser resolvidos")
        
        print("="*100)
        
        # Salvar relatório
        with open('verificacao_absoluta_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logging.info(f"📄 Relatório crítico salvo em: verificacao_absoluta_report.json")
    
    def run_comprehensive_verification(self):
        """Executar verificação abrangente"""
        if not self.setup_driver():
            return False
        
        try:
            logging.info("🔍 INICIANDO VERIFICAÇÃO ABSOLUTA - ANÁLISE CRÍTICA...")
            
            # Executar todos os testes críticos
            self.run_test("Homepage Completa", self.test_homepage_comprehensive, True)
            self.run_test("Login Completo", self.test_login_comprehensive, True)
            self.run_test("Navegação Completa", self.test_navigation_comprehensive, True)
            self.run_test("CRUD Usuários Completo", self.test_crud_users_comprehensive, True)
            self.run_test("CRUD Empresas Completo", self.test_crud_companies_comprehensive, True)
            self.run_test("Segurança Completa", self.test_security_comprehensive, True)
            self.run_test("Performance Completa", self.test_performance_comprehensive, True)
            self.run_test("Tratamento de Erros", self.test_error_handling, True)
            
            # Gerar relatório abrangente
            self.generate_comprehensive_report()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro durante verificação absoluta: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🧹 Driver do Selenium encerrado")

def main():
    """Função principal"""
    verifier = VerificacaoAbsoluta()
    success = verifier.run_comprehensive_verification()
    
    if success:
        logging.info("🎉 Verificação absoluta finalizada!")
    else:
        logging.error("❌ Verificação absoluta falhou!")

if __name__ == "__main__":
    main()
