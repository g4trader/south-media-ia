#!/usr/bin/env python3
"""
Debug do Sistema de Autenticação
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_auth_system():
    """Debug do sistema de autenticação"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🔍 Debug do sistema de autenticação")
        
        # Teste 1: Verificar se login.html carrega o sistema robusto
        logger.info("📄 Teste 1: Verificar login.html")
        driver.get("https://dash.iasouth.tech/login.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        
        # Verificar se os scripts estão carregados
        scripts = driver.find_elements(By.TAG_NAME, "script")
        auth_system_loaded = False
        auth_middleware_loaded = False
        
        for script in scripts:
            src = script.get_attribute("src")
            if src and "auth_system.js" in src:
                auth_system_loaded = True
            if src and "auth_middleware.js" in src:
                auth_middleware_loaded = True
        
        logger.info(f"✅ auth_system.js carregado: {auth_system_loaded}")
        logger.info(f"✅ auth_middleware.js carregado: {auth_middleware_loaded}")
        
        # Teste 2: Fazer login
        logger.info("🔑 Teste 2: Fazer login")
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username.send_keys("admin")
        password.send_keys("dashboard2025")
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard-protected" in d.current_url
        )
        
        logger.info(f"✅ Redirecionado para: {driver.current_url}")
        
        # Teste 3: Verificar elementos na página protegida
        logger.info("🔍 Teste 3: Verificar elementos na página protegida")
        
        try:
            user_name = driver.find_element(By.ID, "userName")
            logger.info(f"✅ Nome do usuário encontrado: {user_name.text}")
        except Exception as e:
            logger.error(f"❌ Erro ao encontrar userName: {e}")
        
        try:
            user_role = driver.find_element(By.ID, "userRole")
            logger.info(f"✅ Role do usuário encontrado: {user_role.text}")
        except Exception as e:
            logger.error(f"❌ Erro ao encontrar userRole: {e}")
        
        try:
            user_avatar = driver.find_element(By.ID, "userAvatar")
            logger.info(f"✅ Avatar do usuário encontrado: {user_avatar.text}")
        except Exception as e:
            logger.error(f"❌ Erro ao encontrar userAvatar: {e}")
        
        # Teste 4: Verificar se há seção de permissões
        logger.info("🔐 Teste 4: Verificar seção de permissões")
        try:
            permissions_section = driver.find_element(By.ID, "permissionsList")
            logger.info(f"✅ Seção de permissões encontrada: {permissions_section.text[:100]}...")
        except Exception as e:
            logger.error(f"❌ Erro ao encontrar permissionsList: {e}")
        
        # Teste 5: Verificar localStorage
        logger.info("💾 Teste 5: Verificar localStorage")
        session_data = driver.execute_script("return localStorage.getItem('dashboard_session');")
        auth_data = driver.execute_script("return localStorage.getItem('dashboard_auth_system');")
        
        logger.info(f"✅ dashboard_session: {session_data[:100] if session_data else 'None'}...")
        logger.info(f"✅ dashboard_auth_system: {auth_data[:100] if auth_data else 'None'}...")
        
        # Teste 6: Verificar se authSystem está disponível
        logger.info("🔧 Teste 6: Verificar authSystem")
        auth_system_available = driver.execute_script("return typeof window.authSystem !== 'undefined';")
        auth_system_authenticated = driver.execute_script("return window.authSystem ? window.authSystem.isAuthenticated() : false;")
        
        logger.info(f"✅ authSystem disponível: {auth_system_available}")
        logger.info(f"✅ authSystem autenticado: {auth_system_authenticated}")
        
        if auth_system_authenticated:
            current_user = driver.execute_script("return window.authSystem.getCurrentUser();")
            logger.info(f"✅ Usuário atual: {current_user}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_auth_system()
    if success:
        print("\n🔍 DEBUG CONCLUÍDO!")
    else:
        print("\n❌ ERRO NO DEBUG")
    
    exit(0 if success else 1)
