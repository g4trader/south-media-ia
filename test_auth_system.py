#!/usr/bin/env python3
"""
Teste do Sistema de Autenticação
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

def test_auth_system():
    """Teste do sistema de autenticação"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        logging.info("🔍 Testando sistema de autenticação...")
        
        # Acessar página de login
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(5)  # Aguardar mais tempo para carregar
        
        # Verificar se o sistema de autenticação está disponível
        auth_system_available = driver.execute_script("return typeof window.authSystem !== 'undefined';")
        logging.info(f"🔐 Sistema de autenticação disponível: {auth_system_available}")
        
        if auth_system_available:
            # Verificar se está inicializado
            is_initialized = driver.execute_script("return window.authSystem.isInitialized;")
            logging.info(f"🔄 Sistema inicializado: {is_initialized}")
            
            # Verificar se há usuários disponíveis
            users_available = driver.execute_script("return window.authSystem.users && window.authSystem.users.length > 0;")
            logging.info(f"👥 Usuários disponíveis: {users_available}")
            
            if users_available:
                users_count = driver.execute_script("return window.authSystem.users.length;")
                logging.info(f"📊 Número de usuários: {users_count}")
        
        # Tentar fazer login
        try:
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "loginButton")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            login_button.click()
            
            time.sleep(5)  # Aguardar mais tempo
            
            current_url = driver.current_url
            logging.info(f"🔗 URL após login: {current_url}")
            
            if "dashboard-protected.html" in current_url:
                logging.info("✅ Login bem-sucedido!")
                return True
            else:
                logging.info("❌ Login falhou - não redirecionou")
                
                # Verificar se há mensagens de erro
                try:
                    error_message = driver.find_element(By.ID, "errorMessage")
                    if error_message.is_displayed():
                        logging.info(f"🚨 Mensagem de erro: {error_message.text}")
                except:
                    pass
                
                return False
                
        except Exception as e:
            logging.error(f"❌ Erro durante login: {e}")
            return False
        
        finally:
            driver.quit()
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_system()
    if success:
        logging.info("🎉 Teste de autenticação passou!")
    else:
        logging.error("❌ Teste de autenticação falhou!")