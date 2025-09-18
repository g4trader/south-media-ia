#!/usr/bin/env python3
"""
Teste de Debug da Página de Empresas
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

def test_companies_debug():
    """Teste de debug da página de empresas"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        logging.info("🔍 Teste de debug da página de empresas...")
        
        # Fazer login primeiro
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(3)
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        login_button.click()
        time.sleep(5)
        
        # Verificar se está logado
        current_url = driver.current_url
        logging.info(f"🔗 URL após login: {current_url}")
        
        if "dashboard-protected.html" not in current_url:
            logging.error("❌ Login falhou")
            return False
        
        # Testar página de empresas
        logging.info("🧪 Testando página de empresas...")
        driver.get("https://dash.iasouth.tech/companies.html")
        time.sleep(5)
        
        current_url = driver.current_url
        logging.info(f"🔗 URL da página de empresas: {current_url}")
        
        # Verificar se há elementos na página
        try:
            create_btn = driver.find_element(By.ID, "createCompanyBtn")
            logging.info("✅ Botão createCompanyBtn encontrado")
        except Exception as e:
            logging.error(f"❌ Botão createCompanyBtn não encontrado: {e}")
            return False
        
        # Verificar se há modal
        try:
            modal = driver.find_element(By.ID, "companyModal")
            logging.info("✅ Modal companyModal encontrado")
        except Exception as e:
            logging.error(f"❌ Modal companyModal não encontrado: {e}")
            return False
        
        # Testar clique no botão
        try:
            create_btn = driver.find_element(By.ID, "createCompanyBtn")
            create_btn.click()
            time.sleep(2)
            
            modal = driver.find_element(By.ID, "companyModal")
            modal_display = modal.get_attribute("style")
            logging.info(f"🎨 Style do modal: {modal_display}")
            
            if "display: block" in modal_display:
                logging.info("✅ Modal abriu com sucesso")
                
                # Testar criação de empresa
                try:
                    nome_field = driver.find_element(By.ID, "companyName")
                    codigo_field = driver.find_element(By.ID, "companyCode")
                    salvar_btn = driver.find_element(By.ID, "saveCompanyBtn")
                    
                    nome_field.send_keys("Empresa Teste")
                    codigo_field.send_keys("TEST001")
                    salvar_btn.click()
                    time.sleep(2)
                    
                    # Verificar se empresa foi criada
                    empresas_grid = driver.find_element(By.ID, "companiesGrid")
                    if "Empresa Teste" in empresas_grid.text:
                        logging.info("✅ Empresa criada com sucesso")
                        return True
                    else:
                        logging.error("❌ Empresa não foi criada")
                        return False
                        
                except Exception as e:
                    logging.error(f"❌ Erro ao criar empresa: {e}")
                    return False
                
            else:
                logging.error("❌ Modal não abriu")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro ao testar modal: {e}")
            return False
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_companies_debug()
    if success:
        logging.info("🎉 Teste de empresas passou!")
    else:
        logging.error("❌ Teste de empresas falhou!")
