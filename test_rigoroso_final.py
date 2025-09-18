#!/usr/bin/env python3
"""
Teste Rigoroso Final - Verificação das Correções
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TesteRigorosoFinal:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': 0,
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
            self.wait = WebDriverWait(self.driver, 15)
            
            logging.info("✅ Driver do Selenium configurado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def run_test(self, test_name, test_function, is_critical=False):
        """Executar um teste individual"""
        self.results['total_tests'] += 1
        start_time = time.time()
        
        try:
            logging.info(f"🔍 TESTE RIGOROSO: {test_name}")
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
                'critical': is_critical
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
                'critical': is_critical
            })
    
    def test_homepage_js_errors(self):
        """Teste 1: Verificar se erros JavaScript foram corrigidos"""
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(5)
            
            # Verificar erros JavaScript
            logs = self.driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            # Contar apenas erros críticos (não favicon 404)
            critical_errors = [error for error in js_errors if 'favicon.ico' not in error['message']]
            
            if len(critical_errors) == 0:
                logging.info("✅ Nenhum erro JavaScript crítico encontrado")
                return True
            else:
                logging.error(f"❌ {len(critical_errors)} erros JavaScript críticos encontrados")
                for error in critical_errors:
                    logging.error(f"   - {error['message']}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de JavaScript: {e}")
            return False
    
    def test_dashboard_clickability(self):
        """Teste 2: Verificar se dashboards são clicáveis"""
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(5)
            
            # Encontrar dashboards
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if len(dashboard_cards) == 0:
                logging.error("❌ Nenhum dashboard encontrado")
                return False
            
            # Testar clicabilidade do primeiro dashboard
            first_card = dashboard_cards[0]
            
            # Verificar se tem data-dashboard-file
            dashboard_file = first_card.get_attribute('data-dashboard-file')
            if not dashboard_file:
                logging.error("❌ Dashboard não tem data-dashboard-file")
                return False
            
            # Verificar se tem cursor pointer
            cursor_style = first_card.get_attribute('style')
            if 'cursor: pointer' not in cursor_style:
                logging.error("❌ Dashboard não tem cursor pointer")
                return False
            
            # Testar clique
            original_url = self.driver.current_url
            first_card.click()
            time.sleep(3)
            
            # Verificar se abriu nova aba ou redirecionou
            if len(self.driver.window_handles) > 1:
                logging.info("✅ Dashboard abriu em nova aba")
                return True
            elif self.driver.current_url != original_url:
                logging.info("✅ Dashboard redirecionou")
                return True
            else:
                logging.error("❌ Dashboard clicado mas não abriu/redirecionou")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de clicabilidade: {e}")
            return False
    
    def test_login_functionality(self):
        """Teste 3: Verificar funcionalidade de login"""
        try:
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(3)
            
            # Verificar elementos
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            # Testar login
            username_field.send_keys("admin")
            password_field.send_keys("dashboard2025")
            login_button.click()
            time.sleep(5)
            
            # Verificar redirecionamento
            if "dashboard-protected.html" in self.driver.current_url:
                logging.info("✅ Login funcionando corretamente")
                return True
            else:
                logging.error("❌ Login não redirecionou corretamente")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de login: {e}")
            return False
    
    def test_protected_pages_no_alerts(self):
        """Teste 4: Verificar se páginas protegidas não geram alertas"""
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
            
            # Testar páginas protegidas
            protected_pages = [
                "https://dash.iasouth.tech/users.html",
                "https://dash.iasouth.tech/companies.html"
            ]
            
            for page in protected_pages:
                self.driver.get(page)
                time.sleep(3)
                
                # Verificar se há alertas
                try:
                    alert = Alert(self.driver)
                    alert_text = alert.text
                    alert.accept()
                    logging.error(f"❌ Alerta encontrado em {page}: {alert_text}")
                    return False
                except:
                    # Nenhum alerta encontrado - isso é bom
                    pass
                
                # Verificar se a página carregou
                if "login.html" in self.driver.current_url:
                    logging.error(f"❌ Página {page} redirecionou para login")
                    return False
            
            logging.info("✅ Páginas protegidas funcionando sem alertas")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no teste de páginas protegidas: {e}")
            return False
    
    def test_performance(self):
        """Teste 5: Verificar performance"""
        try:
            pages = [
                "https://dash.iasouth.tech",
                "https://dash.iasouth.tech/login.html",
                "https://dash.iasouth.tech/dashboard-protected.html"
            ]
            
            load_times = []
            for page in pages:
                start_time = time.time()
                self.driver.get(page)
                time.sleep(2)
                end_time = time.time()
                load_times.append(end_time - start_time)
            
            avg_load_time = sum(load_times) / len(load_times)
            
            if avg_load_time < 3:
                logging.info(f"✅ Performance excelente: {avg_load_time:.2f}s")
                return True
            else:
                logging.error(f"❌ Performance lenta: {avg_load_time:.2f}s")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro no teste de performance: {e}")
            return False
    
    def calculate_quality_score(self):
        """Calcular pontuação de qualidade"""
        if self.results['total_tests'] == 0:
            return 0
        
        # Penalizar falhas críticas mais severamente
        critical_penalty = self.results['critical_failures'] * 0.3
        passed_ratio = self.results['passed_tests'] / self.results['total_tests']
        
        final_score = (passed_ratio - critical_penalty) * 100
        return max(0, round(final_score, 1))
    
    def generate_report(self):
        """Gerar relatório final"""
        quality_score = self.calculate_quality_score()
        
        print("\n" + "="*100)
        print("🔍 RELATÓRIO DE TESTE RIGOROSO FINAL")
        print("="*100)
        print(f"🎯 Pontuação de Qualidade: {quality_score}%")
        print(f"📈 Testes Executados: {self.results['total_tests']}")
        print(f"✅ Testes Aprovados: {self.results['passed_tests']}")
        print(f"❌ Testes Falharam: {self.results['failed_tests']}")
        print(f"🚨 Falhas Críticas: {self.results['critical_failures']}")
        
        print(f"\n📋 Detalhes dos Testes:")
        for test in self.results['test_details']:
            critical_mark = "🚨" if test.get('critical', False) else ""
            print(f"   {test['status']} {critical_mark} {test['name']} ({test['duration']}s)")
        
        # Classificação rigorosa
        if quality_score >= 95 and self.results['critical_failures'] == 0:
            grade = "🏆 EXCELENTE - CONVICÇÃO ABSOLUTA"
            conviction = "SIM"
        elif quality_score >= 90:
            grade = "🥇 MUITO BOM - ALTA CONVICÇÃO"
            conviction = "SIM"
        elif quality_score >= 80:
            grade = "🥈 BOM - CONVICÇÃO MODERADA"
            conviction = "PARCIAL"
        else:
            grade = "⚠️ PRECISA MELHORAR - SEM CONVICÇÃO"
            conviction = "NÃO"
        
        print(f"\n🏅 Classificação Rigorosa: {grade}")
        print(f"🎯 CONVICÇÃO ABSOLUTA: {conviction}")
        print("="*100)
    
    def run_rigorous_tests(self):
        """Executar testes rigorosos"""
        if not self.setup_driver():
            return False
        
        try:
            logging.info("🚀 INICIANDO TESTES RIGOROSOS FINAIS...")
            
            # Executar todos os testes críticos
            self.run_test("Erros JavaScript Corrigidos", self.test_homepage_js_errors, True)
            self.run_test("Dashboards Clicáveis", self.test_dashboard_clickability, True)
            self.run_test("Login Funcionando", self.test_login_functionality, True)
            self.run_test("Páginas Protegidas Sem Alertas", self.test_protected_pages_no_alerts, True)
            self.run_test("Performance Adequada", self.test_performance, True)
            
            # Gerar relatório
            self.generate_report()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro durante testes rigorosos: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🧹 Driver encerrado")

def main():
    """Função principal"""
    tester = TesteRigorosoFinal()
    success = tester.run_rigorous_tests()
    
    if success:
        logging.info("🎉 Testes rigorosos finalizados!")
    else:
        logging.error("❌ Testes rigorosos falharam!")

if __name__ == "__main__":
    main()
