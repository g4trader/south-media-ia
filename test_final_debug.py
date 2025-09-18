#!/usr/bin/env python3
"""
Teste Final de Debug
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

def test_final_debug():
    """Teste final de debug"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        logging.info("🔍 Teste final de debug...")
        
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
        
        # Testar página de usuários
        logging.info("🧪 Testando página de usuários...")
        driver.get("https://dash.iasouth.tech/users.html")
        time.sleep(5)
        
        current_url = driver.current_url
        logging.info(f"🔗 URL da página de usuários: {current_url}")
        
        # Verificar se há elementos na página
        try:
            create_btn = driver.find_element(By.ID, "createUserBtn")
            logging.info("✅ Botão createUserBtn encontrado")
        except Exception as e:
            logging.error(f"❌ Botão createUserBtn não encontrado: {e}")
        
        # Verificar se há modal
        try:
            modal = driver.find_element(By.ID, "userModal")
            logging.info("✅ Modal userModal encontrado")
        except Exception as e:
            logging.error(f"❌ Modal userModal não encontrado: {e}")
        
        # Testar clique no botão
        try:
            create_btn = driver.find_element(By.ID, "createUserBtn")
            create_btn.click()
            time.sleep(2)
            
            modal = driver.find_element(By.ID, "userModal")
            modal_classes = modal.get_attribute("class")
            logging.info(f"🎨 Classes do modal: {modal_classes}")
            
            if "show" in modal_classes:
                logging.info("✅ Modal abriu com sucesso")
                
                # Fechar modal
                close_btn = driver.find_element(By.CLASS_NAME, "close")
                close_btn.click()
                time.sleep(1)
                
                logging.info("✅ Modal fechado com sucesso")
                return True
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
    success = test_final_debug()
    if success:
        logging.info("🎉 Teste final passou!")
    else:
        logging.error("❌ Teste final falhou!")
