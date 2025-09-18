#!/usr/bin/env python3
"""
Teste completo das funcionalidades CRUD implementadas
- Testa página de usuários
- Testa página de empresas
- Verifica modais, formulários e interações
"""

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CRUDFunctionalityTests(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://dash.iasouth.tech"
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        logger.info("✅ Driver do Selenium configurado com sucesso")

    def tearDown(self):
        self.driver.quit()
        logger.info("🧹 Driver do Selenium encerrado")

    def login_admin(self):
        """Fazer login como admin"""
        self.driver.get(f"{self.base_url}/login.html")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys("admin")
        self.driver.find_element(By.ID, "password").send_keys("dashboard2025")
        self.driver.find_element(By.ID, "loginButton").click()
        time.sleep(2)
        
        if "dashboard-protected.html" in self.driver.current_url:
            logger.info("✅ Login bem-sucedido")
            return True
        else:
            logger.error(f"❌ Login falhou - URL atual: {self.driver.current_url}")
            return False

    def test_users_page_crud_elements(self):
        """Testar elementos CRUD na página de usuários"""
        logger.info("🔄 Testando elementos CRUD na página de usuários...")
        
        if not self.login_admin():
            self.fail("Não foi possível fazer login")
        
        # Navegar para página de usuários
        self.driver.get(f"{self.base_url}/users.html")
        time.sleep(2)
        
        try:
            # Verificar botões de ação
            create_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "createUserBtn"))
            )
            refresh_btn = self.driver.find_element(By.ID, "refreshUsersBtn")
            
            logger.info("✅ Botões de ação encontrados na página de usuários")
            
            # Testar abertura do modal
            create_btn.click()
            time.sleep(1)
            
            modal = self.driver.find_element(By.ID, "userModal")
            if modal.is_displayed():
                logger.info("✅ Modal de criação de usuário aberto com sucesso")
                
                # Verificar campos do formulário
                required_fields = [
                    "userName", "userEmail", "userUsername", 
                    "userPassword", "userRole", "userStatus"
                ]
                
                for field_id in required_fields:
                    field = self.driver.find_element(By.ID, field_id)
                    if field.is_displayed():
                        logger.info(f"✅ Campo {field_id} encontrado")
                    else:
                        logger.warning(f"⚠️ Campo {field_id} não encontrado")
                
                # Fechar modal
                close_btn = self.driver.find_element(By.ID, "closeModal")
                close_btn.click()
                time.sleep(1)
                
                if not modal.is_displayed():
                    logger.info("✅ Modal fechado com sucesso")
                else:
                    logger.warning("⚠️ Modal não foi fechado")
            else:
                logger.error("❌ Modal não foi aberto")
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar página de usuários: {e}")
            self.fail(f"Erro ao testar página de usuários: {e}")

    def test_companies_page_crud_elements(self):
        """Testar elementos CRUD na página de empresas"""
        logger.info("🔄 Testando elementos CRUD na página de empresas...")
        
        if not self.login_admin():
            self.fail("Não foi possível fazer login")
        
        # Navegar para página de empresas
        self.driver.get(f"{self.base_url}/companies.html")
        time.sleep(2)
        
        try:
            # Verificar botões de ação
            create_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "createCompanyBtn"))
            )
            refresh_btn = self.driver.find_element(By.ID, "refreshCompaniesBtn")
            
            logger.info("✅ Botões de ação encontrados na página de empresas")
            
            # Testar abertura do modal
            create_btn.click()
            time.sleep(1)
            
            modal = self.driver.find_element(By.ID, "companyModal")
            if modal.is_displayed():
                logger.info("✅ Modal de criação de empresa aberto com sucesso")
                
                # Verificar campos do formulário
                required_fields = [
                    "companyName", "companyCode", "companyEmail",
                    "companyTheme", "companyTimezone", "companyLanguage", "companyStatus"
                ]
                
                for field_id in required_fields:
                    field = self.driver.find_element(By.ID, field_id)
                    if field.is_displayed():
                        logger.info(f"✅ Campo {field_id} encontrado")
                    else:
                        logger.warning(f"⚠️ Campo {field_id} não encontrado")
                
                # Fechar modal
                close_btn = self.driver.find_element(By.ID, "closeModal")
                close_btn.click()
                time.sleep(1)
                
                if not modal.is_displayed():
                    logger.info("✅ Modal fechado com sucesso")
                else:
                    logger.warning("⚠️ Modal não foi fechado")
            else:
                logger.error("❌ Modal não foi aberto")
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar página de empresas: {e}")
            self.fail(f"Erro ao testar página de empresas: {e}")

    def test_navigation_menu(self):
        """Testar menu de navegação"""
        logger.info("🔄 Testando menu de navegação...")
        
        if not self.login_admin():
            self.fail("Não foi possível fazer login")
        
        try:
            # Verificar se o menu de navegação está presente
            nav_menu = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "nav-menu"))
            )
            
            if nav_menu.is_displayed():
                logger.info("✅ Menu de navegação encontrado")
                
                # Verificar links do menu
                menu_links = nav_menu.find_elements(By.TAG_NAME, "a")
                expected_links = ["Dashboard", "Usuários", "Empresas"]
                
                for expected_link in expected_links:
                    found = False
                    for link in menu_links:
                        if expected_link in link.text:
                            found = True
                            logger.info(f"✅ Link '{expected_link}' encontrado no menu")
                            break
                    
                    if not found:
                        logger.warning(f"⚠️ Link '{expected_link}' não encontrado no menu")
            else:
                logger.error("❌ Menu de navegação não está visível")
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar menu de navegação: {e}")
            self.fail(f"Erro ao testar menu de navegação: {e}")

    def test_user_interface_consistency(self):
        """Testar consistência da interface"""
        logger.info("🔄 Testando consistência da interface...")
        
        if not self.login_admin():
            self.fail("Não foi possível fazer login")
        
        pages_to_test = [
            ("users.html", "Usuários"),
            ("companies.html", "Empresas")
        ]
        
        for page_url, page_name in pages_to_test:
            try:
                self.driver.get(f"{self.base_url}/{page_url}")
                time.sleep(2)
                
                # Verificar elementos comuns
                common_elements = [
                    ("header", "Cabeçalho"),
                    ("user-info", "Informações do usuário"),
                    ("page-title", "Título da página"),
                    ("btn-primary", "Botão primário")
                ]
                
                for element_class, element_name in common_elements:
                    try:
                        element = self.driver.find_element(By.CLASS_NAME, element_class)
                        if element.is_displayed():
                            logger.info(f"✅ {element_name} encontrado em {page_name}")
                        else:
                            logger.warning(f"⚠️ {element_name} não visível em {page_name}")
                    except NoSuchElementException:
                        logger.warning(f"⚠️ {element_name} não encontrado em {page_name}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao testar {page_name}: {e}")

    def test_responsive_design(self):
        """Testar design responsivo"""
        logger.info("🔄 Testando design responsivo...")
        
        if not self.login_admin():
            self.fail("Não foi possível fazer login")
        
        # Testar em diferentes tamanhos de tela
        screen_sizes = [
            (1920, 1080, "Desktop"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        for width, height, device_name in screen_sizes:
            try:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Testar página de usuários
                self.driver.get(f"{self.base_url}/users.html")
                time.sleep(2)
                
                # Verificar se elementos principais estão visíveis
                create_btn = self.driver.find_element(By.ID, "createUserBtn")
                if create_btn.is_displayed():
                    logger.info(f"✅ Botão de criar usuário visível em {device_name}")
                else:
                    logger.warning(f"⚠️ Botão de criar usuário não visível em {device_name}")
                
                # Testar página de empresas
                self.driver.get(f"{self.base_url}/companies.html")
                time.sleep(2)
                
                create_btn = self.driver.find_element(By.ID, "createCompanyBtn")
                if create_btn.is_displayed():
                    logger.info(f"✅ Botão de criar empresa visível em {device_name}")
                else:
                    logger.warning(f"⚠️ Botão de criar empresa não visível em {device_name}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao testar {device_name}: {e}")
        
        # Restaurar tamanho original
        self.driver.maximize_window()

if __name__ == "__main__":
    # Executar testes
    unittest.main(verbosity=2)


