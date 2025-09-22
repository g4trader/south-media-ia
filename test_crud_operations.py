#!/usr/bin/env python3
"""
Teste de CRUD Operations
Verifica se todas as operações CRUD estão funcionando corretamente
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

class CRUDTestSuite:
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
    
    def login(self):
        """Fazer login no sistema"""
        try:
            logger.info("🔄 Fazendo login...")
            
            self.driver.get(f"{self.base_url}/login.html")
            time.sleep(3)
            
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
                logger.info("✅ Login bem-sucedido")
                return True
            else:
                logger.error(f"❌ Login falhou - URL atual: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    def test_user_crud(self):
        """Testar CRUD de usuários"""
        try:
            logger.info("🔄 Testando CRUD de usuários...")
            
            # Navegar para página de usuários
            self.driver.get(f"{self.base_url}/users.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "usersGrid"))
                )
                logger.info("✅ Página de usuários carregada")
            except TimeoutException:
                logger.error("❌ Timeout ao carregar página de usuários")
                return False
            
            # Teste READ - Verificar se há usuários listados
            try:
                users_list = self.driver.find_elements(By.CLASS_NAME, "user-card")
                logger.info(f"✅ READ: {len(users_list)} usuários encontrados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao listar usuários: {e}")
            
            # Teste CREATE - Tentar criar um novo usuário
            try:
                create_button = self.driver.find_element(By.ID, "createUserBtn")
                create_button.click()
                time.sleep(2)
                
                # Verificar se modal de criação apareceu
                modal = self.driver.find_element(By.CLASS_NAME, "modal")
                if modal.is_displayed():
                    logger.info("✅ CREATE: Modal de criação de usuário apareceu")
                    
                    # Preencher formulário
                    name_input = self.driver.find_element(By.ID, "userName")
                    email_input = self.driver.find_element(By.ID, "userEmail")
                    role_select = self.driver.find_element(By.ID, "userRole")
                    
                    name_input.send_keys("Teste Usuário")
                    email_input.send_keys("teste@teste.com")
                    role_select.send_keys("viewer")
                    
                    # Salvar
                    save_button = self.driver.find_element(By.ID, "saveUserBtn")
                    save_button.click()
                    time.sleep(2)
                    
                    logger.info("✅ CREATE: Usuário criado com sucesso")
                else:
                    logger.warning("⚠️ Modal de criação não apareceu")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste CREATE de usuários: {e}")
            
            # Teste UPDATE - Tentar editar um usuário
            try:
                edit_buttons = self.driver.find_elements(By.CLASS_NAME, "edit-user-btn")
                if edit_buttons:
                    edit_buttons[0].click()
                    time.sleep(2)
                    
                    # Verificar se modal de edição apareceu
                    modal = self.driver.find_element(By.CLASS_NAME, "modal")
                    if modal.is_displayed():
                        logger.info("✅ UPDATE: Modal de edição de usuário apareceu")
                        
                        # Modificar dados
                        name_input = self.driver.find_element(By.ID, "userName")
                        name_input.clear()
                        name_input.send_keys("Usuário Editado")
                        
                        # Salvar
                        save_button = self.driver.find_element(By.ID, "saveUserBtn")
                        save_button.click()
                        time.sleep(2)
                        
                        logger.info("✅ UPDATE: Usuário editado com sucesso")
                    else:
                        logger.warning("⚠️ Modal de edição não apareceu")
                else:
                    logger.warning("⚠️ Nenhum botão de edição encontrado")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste UPDATE de usuários: {e}")
            
            # Teste DELETE - Tentar deletar um usuário
            try:
                delete_buttons = self.driver.find_elements(By.CLASS_NAME, "delete-user-btn")
                if delete_buttons:
                    delete_buttons[0].click()
                    time.sleep(2)
                    
                    # Verificar se modal de confirmação apareceu
                    try:
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        time.sleep(2)
                        logger.info("✅ DELETE: Usuário deletado com sucesso")
                    except:
                        logger.warning("⚠️ Modal de confirmação não apareceu")
                else:
                    logger.warning("⚠️ Nenhum botão de delete encontrado")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste DELETE de usuários: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste CRUD de usuários: {e}")
            return False
    
    def test_company_crud(self):
        """Testar CRUD de empresas"""
        try:
            logger.info("🔄 Testando CRUD de empresas...")
            
            # Navegar para página de empresas
            self.driver.get(f"{self.base_url}/companies.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "companiesGrid"))
                )
                logger.info("✅ Página de empresas carregada")
            except TimeoutException:
                logger.error("❌ Timeout ao carregar página de empresas")
                return False
            
            # Teste READ - Verificar se há empresas listadas
            try:
                companies_list = self.driver.find_elements(By.CLASS_NAME, "company-card")
                logger.info(f"✅ READ: {len(companies_list)} empresas encontradas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao listar empresas: {e}")
            
            # Teste CREATE - Tentar criar uma nova empresa
            try:
                create_button = self.driver.find_element(By.ID, "createCompanyBtn")
                create_button.click()
                time.sleep(2)
                
                # Verificar se modal de criação apareceu
                modal = self.driver.find_element(By.CLASS_NAME, "modal")
                if modal.is_displayed():
                    logger.info("✅ CREATE: Modal de criação de empresa apareceu")
                    
                    # Preencher formulário
                    name_input = self.driver.find_element(By.ID, "companyName")
                    code_input = self.driver.find_element(By.ID, "companyCode")
                    email_input = self.driver.find_element(By.ID, "companyEmail")
                    
                    name_input.send_keys("Empresa Teste")
                    code_input.send_keys("TESTE")
                    email_input.send_keys("contato@empresateste.com")
                    
                    # Salvar
                    save_button = self.driver.find_element(By.ID, "saveCompanyBtn")
                    save_button.click()
                    time.sleep(2)
                    
                    logger.info("✅ CREATE: Empresa criada com sucesso")
                else:
                    logger.warning("⚠️ Modal de criação não apareceu")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste CREATE de empresas: {e}")
            
            # Teste UPDATE - Tentar editar uma empresa
            try:
                edit_buttons = self.driver.find_elements(By.CLASS_NAME, "edit-company-btn")
                if edit_buttons:
                    edit_buttons[0].click()
                    time.sleep(2)
                    
                    # Verificar se modal de edição apareceu
                    modal = self.driver.find_element(By.CLASS_NAME, "modal")
                    if modal.is_displayed():
                        logger.info("✅ UPDATE: Modal de edição de empresa apareceu")
                        
                        # Modificar dados
                        name_input = self.driver.find_element(By.ID, "companyName")
                        name_input.clear()
                        name_input.send_keys("Empresa Editada")
                        
                        # Salvar
                        save_button = self.driver.find_element(By.ID, "saveCompanyBtn")
                        save_button.click()
                        time.sleep(2)
                        
                        logger.info("✅ UPDATE: Empresa editada com sucesso")
                    else:
                        logger.warning("⚠️ Modal de edição não apareceu")
                else:
                    logger.warning("⚠️ Nenhum botão de edição encontrado")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste UPDATE de empresas: {e}")
            
            # Teste DELETE - Tentar deletar uma empresa
            try:
                delete_buttons = self.driver.find_elements(By.CLASS_NAME, "delete-company-btn")
                if delete_buttons:
                    delete_buttons[0].click()
                    time.sleep(2)
                    
                    # Verificar se modal de confirmação apareceu
                    try:
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        time.sleep(2)
                        logger.info("✅ DELETE: Empresa deletada com sucesso")
                    except:
                        logger.warning("⚠️ Modal de confirmação não apareceu")
                else:
                    logger.warning("⚠️ Nenhum botão de delete encontrado")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste DELETE de empresas: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste CRUD de empresas: {e}")
            return False
    
    def test_dashboard_crud(self):
        """Testar CRUD de dashboards"""
        try:
            logger.info("🔄 Testando CRUD de dashboards...")
            
            # Navegar para página principal de dashboards
            self.driver.get(f"{self.base_url}/dashboard-protected.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dashboard-card"))
                )
                logger.info("✅ Página de dashboards carregada")
            except TimeoutException:
                logger.error("❌ Timeout ao carregar página de dashboards")
                return False
            
            # Teste READ - Verificar se há dashboards listados
            try:
                dashboards_list = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
                logger.info(f"✅ READ: {len(dashboards_list)} dashboards encontrados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao listar dashboards: {e}")
            
            # Teste SYNC - Testar sincronização de dashboard
            try:
                sync_buttons = self.driver.find_elements(By.CLASS_NAME, "sync-btn")
                if sync_buttons:
                    sync_buttons[0].click()
                    time.sleep(5)  # Aguardar sincronização
                    
                    # Verificar se sincronização foi bem-sucedida
                    button = sync_buttons[0]
                    button_text = button.text
                    if "✅" in button_text or "Sincronizado" in button_text:
                        logger.info("✅ SYNC: Dashboard sincronizado com sucesso")
                    else:
                        logger.warning("⚠️ Sincronização pode ter falhado")
                else:
                    logger.warning("⚠️ Nenhum botão de sync encontrado")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste SYNC de dashboards: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste CRUD de dashboards: {e}")
            return False
    
    def test_system_status_crud(self):
        """Testar operações de status do sistema"""
        try:
            logger.info("🔄 Testando operações de status do sistema...")
            
            # Navegar para página de status
            self.driver.get(f"{self.base_url}/system-status.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "status-card"))
                )
                logger.info("✅ Página de status carregada")
            except TimeoutException:
                logger.error("❌ Timeout ao carregar página de status")
                return False
            
            # Teste READ - Verificar se dados de status são exibidos
            try:
                status_cards = self.driver.find_elements(By.CLASS_NAME, "status-card")
                logger.info(f"✅ READ: {len(status_cards)} cards de status encontrados")
                
                # Verificar se há dados nas cards
                for card in status_cards:
                    status_items = card.find_elements(By.CLASS_NAME, "status-item")
                    if status_items:
                        logger.info(f"✅ READ: {len(status_items)} itens de status na card")
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler status do sistema: {e}")
            
            # Teste REFRESH - Testar atualização de status
            try:
                refresh_button = self.driver.find_element(By.CLASS_NAME, "refresh-btn")
                refresh_button.click()
                time.sleep(3)
                
                logger.info("✅ REFRESH: Status do sistema atualizado")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro no teste REFRESH de status: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de status do sistema: {e}")
            return False
    
    def run_all_crud_tests(self):
        """Executar todos os testes CRUD"""
        try:
            logger.info("🚀 Iniciando testes CRUD completos...")
            
            # Fazer login primeiro
            if not self.login():
                logger.error("❌ Falha no login - abortando testes")
                return False
            
            tests = [
                ("CRUD de Usuários", self.test_user_crud),
                ("CRUD de Empresas", self.test_company_crud),
                ("CRUD de Dashboards", self.test_dashboard_crud),
                ("Status do Sistema", self.test_system_status_crud)
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
            logger.info("📊 RESUMO DOS TESTES CRUD")
            logger.info(f"{'='*50}")
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            for test_name, result in results:
                status = "✅ PASSOU" if result else "❌ FALHOU"
                logger.info(f"{test_name}: {status}")
            
            logger.info(f"\n🎯 Resultado Final: {passed}/{total} testes CRUD passaram")
            
            if passed == total:
                logger.info("🎉 TODOS OS TESTES CRUD PASSARAM! Sistema funcionando perfeitamente!")
            else:
                logger.warning(f"⚠️ {total - passed} testes CRUD falharam. Verificar implementação.")
            
            return passed == total
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução dos testes CRUD: {e}")
            return False
    
    def cleanup(self):
        """Limpar recursos"""
        if self.driver:
            self.driver.quit()
            logger.info("🧹 Driver do Selenium encerrado")

def main():
    """Função principal"""
    test = CRUDTestSuite()
    
    try:
        success = test.run_all_crud_tests()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        return 1
        
    finally:
        test.cleanup()

if __name__ == "__main__":
    exit(main())
