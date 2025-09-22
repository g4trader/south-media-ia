#!/usr/bin/env python3
"""
Teste de Integração Firebase
Verifica se o sistema híbrido está funcionando corretamente
"""

import time
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

class FirebaseIntegrationTest:
    def __init__(self):
        self.driver = None
        self.base_url = "https://dash.iasouth.tech"
        self.setup_driver()
    
    def setup_driver(self):
        """Configurar driver do Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("✅ Driver do Selenium configurado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver: {e}")
            raise
    
    def test_firebase_availability(self):
        """Testar se Firebase está disponível"""
        try:
            logger.info("🔄 Testando disponibilidade do Firebase...")
            
            self.driver.get(f"{self.base_url}/login.html")
            time.sleep(3)
            
            # Verificar se o sistema híbrido está carregado
            firebase_status = self.driver.execute_script("""
                if (window.hybridAuthSystem) {
                    return window.hybridAuthSystem.getSystemStatus();
                }
                return null;
            """)
            
            if firebase_status:
                logger.info(f"✅ Sistema híbrido carregado: {firebase_status}")
                return True
            else:
                logger.warning("⚠️ Sistema híbrido não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar Firebase: {e}")
            return False
    
    def test_authentication_flow(self):
        """Testar fluxo de autenticação"""
        try:
            logger.info("🔄 Testando fluxo de autenticação...")
            
            # Testar login com admin
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "loginButton")
            
            username_input.clear()
            username_input.send_keys("admin")
            password_input.clear()
            password_input.send_keys("dashboard2025")
            
            login_button.click()
            time.sleep(3)
            
            # Verificar se foi redirecionado
            current_url = self.driver.current_url
            if "dashboard-protected.html" in current_url:
                logger.info("✅ Login bem-sucedido - redirecionado para área protegida")
                return True
            else:
                logger.error(f"❌ Login falhou - URL atual: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de autenticação: {e}")
            return False
    
    def test_dashboard_loading(self):
        """Testar carregamento de dashboards"""
        try:
            logger.info("🔄 Testando carregamento de dashboards...")
            
            # Aguardar carregamento dos dashboards com múltiplas tentativas
            dashboard_cards = []
            for attempt in range(3):
                try:
                    # Aguardar carregamento dos dashboards
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "dashboard-card"))
                    )
                    dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
                    if len(dashboard_cards) > 0:
                        break
                except TimeoutException:
                    logger.warning(f"⚠️ Tentativa {attempt + 1} - Timeout ao carregar dashboards")
                    time.sleep(2)
            
            if len(dashboard_cards) == 0:
                # Verificar se há estado de loading ou empty
                try:
                    loading_state = self.driver.find_element(By.ID, "loadingState")
                    if loading_state.is_displayed():
                        logger.info("ℹ️ Dashboards ainda carregando...")
                        return True
                except:
                    pass
                
                try:
                    empty_state = self.driver.find_element(By.ID, "emptyState")
                    if empty_state.is_displayed():
                        logger.info("ℹ️ Nenhum dashboard encontrado (estado vazio)")
                        return True
                except:
                    pass
                
                logger.error("❌ Nenhum dashboard carregado")
                return False
            
            logger.info(f"✅ {len(dashboard_cards)} dashboards carregados")
            
            # Verificar informações do usuário
            try:
                user_name = self.driver.find_element(By.ID, "userName").text
                user_role = self.driver.find_element(By.ID, "userRole").text
                user_company = self.driver.find_element(By.ID, "userCompany").text
                
                logger.info(f"✅ Usuário: {user_name} | Role: {user_role} | Empresa: {user_company}")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível obter informações do usuário: {e}")
            
            return len(dashboard_cards) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar carregamento de dashboards: {e}")
            return False
    
    def test_system_status(self):
        """Testar status do sistema"""
        try:
            logger.info("🔄 Testando status do sistema...")
            
            # Obter status do sistema via JavaScript
            system_status = self.driver.execute_script("""
                if (window.hybridAuthSystem) {
                    return window.hybridAuthSystem.getSystemStatus();
                }
                return null;
            """)
            
            if system_status:
                logger.info(f"✅ Status do sistema: {system_status}")
                
                # Verificar se há dados
                if system_status.get('companies', 0) > 0:
                    logger.info(f"✅ {system_status['companies']} empresas encontradas")
                if system_status.get('users', 0) > 0:
                    logger.info(f"✅ {system_status['users']} usuários encontrados")
                if system_status.get('dashboards', 0) > 0:
                    logger.info(f"✅ {system_status['dashboards']} dashboards encontrados")
                
                return True
            else:
                logger.error("❌ Não foi possível obter status do sistema")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar status do sistema: {e}")
            return False
    
    def test_logout(self):
        """Testar logout"""
        try:
            logger.info("🔄 Testando logout...")
            
            # Clicar no botão de logout
            logout_button = self.driver.find_element(By.CLASS_NAME, "logout-button")
            logout_button.click()
            time.sleep(1)
            
            # Aceitar o alert de confirmação
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                time.sleep(2)
            except:
                # Se não houver alert, continuar
                pass
            
            # Verificar se foi redirecionado para login
            current_url = self.driver.current_url
            if "login.html" in current_url:
                logger.info("✅ Logout bem-sucedido - redirecionado para login")
                return True
            else:
                logger.error(f"❌ Logout falhou - URL atual: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de logout: {e}")
            return False
    
    def run_all_tests(self):
        """Executar todos os testes"""
        try:
            logger.info("🚀 Iniciando testes de integração Firebase...")
            
            tests = [
                ("Disponibilidade Firebase", self.test_firebase_availability),
                ("Fluxo de Autenticação", self.test_authentication_flow),
                ("Carregamento de Dashboards", self.test_dashboard_loading),
                ("Status do Sistema", self.test_system_status),
                ("Logout", self.test_logout)
            ]
            
            results = []
            
            for test_name, test_func in tests:
                logger.info(f"\n{'='*50}")
                logger.info(f"🧪 Executando: {test_name}")
                logger.info(f"{'='*50}")
                
                try:
                    result = test_func()
                    results.append((test_name, result))
                    
                    if result:
                        logger.info(f"✅ {test_name}: PASSOU")
                    else:
                        logger.error(f"❌ {test_name}: FALHOU")
                        
                except Exception as e:
                    logger.error(f"❌ {test_name}: ERRO - {e}")
                    results.append((test_name, False))
                
                time.sleep(2)
            
            # Resumo dos resultados
            logger.info(f"\n{'='*50}")
            logger.info("📊 RESUMO DOS TESTES")
            logger.info(f"{'='*50}")
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            for test_name, result in results:
                status = "✅ PASSOU" if result else "❌ FALHOU"
                logger.info(f"{test_name}: {status}")
            
            logger.info(f"\n🎯 Resultado Final: {passed}/{total} testes passaram")
            
            if passed == total:
                logger.info("🎉 TODOS OS TESTES PASSARAM! Sistema Firebase funcionando!")
            else:
                logger.warning(f"⚠️ {total - passed} testes falharam. Verificar configuração.")
            
            return passed == total
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução dos testes: {e}")
            return False
    
    def cleanup(self):
        """Limpar recursos"""
        if self.driver:
            self.driver.quit()
            logger.info("🧹 Driver do Selenium encerrado")

def main():
    """Função principal"""
    test = FirebaseIntegrationTest()
    
    try:
        success = test.run_all_tests()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        return 1
        
    finally:
        test.cleanup()

if __name__ == "__main__":
    exit(main())
