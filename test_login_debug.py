#!/usr/bin/env python3
"""
Teste de Debug do Sistema de Login
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

def test_login_debug():
    """Teste de debug do login"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        logging.info("🔍 Testando página de login...")
        
        # Acessar página de login
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(3)
        
        # Verificar título da página
        title = driver.title
        logging.info(f"📄 Título da página: {title}")
        
        # Verificar se a página carregou
        body = driver.find_element(By.TAG_NAME, "body")
        logging.info(f"📝 Conteúdo do body: {body.text[:200]}...")
        
        # Verificar elementos específicos
        try:
            username_field = driver.find_element(By.ID, "username")
            logging.info("✅ Campo username encontrado")
        except Exception as e:
            logging.error(f"❌ Campo username não encontrado: {e}")
        
        try:
            password_field = driver.find_element(By.ID, "password")
            logging.info("✅ Campo password encontrado")
        except Exception as e:
            logging.error(f"❌ Campo password não encontrado: {e}")
        
        try:
            login_button = driver.find_element(By.ID, "loginButton")
            logging.info("✅ Botão login encontrado")
        except Exception as e:
            logging.error(f"❌ Botão login não encontrado: {e}")
        
        # Verificar se há erros JavaScript
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                logging.error(f"🚨 Erro JavaScript: {log['message']}")
        
        # Tentar fazer login
        try:
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            login_button.click()
            
            time.sleep(3)
            
            current_url = driver.current_url
            logging.info(f"🔗 URL após login: {current_url}")
            
            if "dashboard-protected.html" in current_url:
                logging.info("✅ Login bem-sucedido!")
            else:
                logging.info("❌ Login falhou - não redirecionou")
                
        except Exception as e:
            logging.error(f"❌ Erro durante login: {e}")
        
        driver.quit()
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_login_debug()
