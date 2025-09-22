#!/usr/bin/env python3
"""
Teste de Debug do Menu de Navegação
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

def test_menu_debug():
    """Teste de debug do menu"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        logging.info("🔍 Testando menu de navegação...")
        
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
        
        # Verificar se está na página protegida
        current_url = driver.current_url
        logging.info(f"🔗 URL atual: {current_url}")
        
        if "dashboard-protected.html" not in current_url:
            logging.error("❌ Não conseguiu fazer login")
            return False
        
        # Verificar se o menu está presente
        try:
            menu_toggle = wait.until(EC.presence_of_element_located((By.ID, "navToggle")))
            logging.info("✅ Botão do menu encontrado")
        except Exception as e:
            logging.error(f"❌ Botão do menu não encontrado: {e}")
            return False
        
        # Verificar se o menu está presente no DOM
        menu_present = driver.execute_script("return document.getElementById('navigationMenu') !== null;")
        logging.info(f"📋 Menu no DOM: {menu_present}")
        
        if not menu_present:
            logging.error("❌ Menu não está no DOM")
            return False
        
        # Tentar clicar no menu
        try:
            menu_toggle.click()
            time.sleep(2)
            
            # Verificar se o menu abriu
            menu = driver.find_element(By.ID, "navigationMenu")
            menu_classes = menu.get_attribute("class")
            logging.info(f"🎨 Classes do menu: {menu_classes}")
            
            if "open" in menu_classes:
                logging.info("✅ Menu abriu com sucesso")
                
                # Verificar links do menu
                menu_links = driver.find_elements(By.CLASS_NAME, "nav-link")
                logging.info(f"🔗 Links encontrados: {len(menu_links)}")
                
                for link in menu_links:
                    logging.info(f"   - {link.text}")
                
                return True
            else:
                logging.error("❌ Menu não abriu")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro ao clicar no menu: {e}")
            return False
        
        finally:
            driver.quit()
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    success = test_menu_debug()
    if success:
        logging.info("🎉 Teste do menu passou!")
    else:
        logging.error("❌ Teste do menu falhou!")
