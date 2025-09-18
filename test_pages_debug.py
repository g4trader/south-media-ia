#!/usr/bin/env python3
"""
Teste de Debug das Páginas de Usuários e Empresas
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

def test_pages_debug():
    """Teste de debug das páginas"""
    try:
        # Configurar driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        logging.info("🔍 Testando páginas de usuários e empresas...")
        
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
        
        if "login.html" in current_url:
            logging.error("❌ Página de usuários redirecionou para login")
            return False
        
        # Verificar elementos da página de usuários
        try:
            novo_usuario_btn = driver.find_element(By.ID, "novoUsuarioBtn")
            logging.info("✅ Botão novo usuário encontrado")
        except Exception as e:
            logging.error(f"❌ Botão novo usuário não encontrado: {e}")
            return False
        
        # Testar página de empresas
        logging.info("🧪 Testando página de empresas...")
        driver.get("https://dash.iasouth.tech/companies.html")
        time.sleep(5)
        
        current_url = driver.current_url
        logging.info(f"🔗 URL da página de empresas: {current_url}")
        
        if "login.html" in current_url:
            logging.error("❌ Página de empresas redirecionou para login")
            return False
        
        # Verificar elementos da página de empresas
        try:
            nova_empresa_btn = driver.find_element(By.ID, "novaEmpresaBtn")
            logging.info("✅ Botão nova empresa encontrado")
        except Exception as e:
            logging.error(f"❌ Botão nova empresa não encontrado: {e}")
            return False
        
        logging.info("✅ Ambas as páginas funcionando corretamente")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro geral: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_pages_debug()
    if success:
        logging.info("🎉 Teste das páginas passou!")
    else:
        logging.error("❌ Teste das páginas falhou!")
