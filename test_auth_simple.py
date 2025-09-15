#!/usr/bin/env python3
"""
Teste simples do sistema de autenticação
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_auth_simple():
    """Teste simples de autenticação"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Teste 1: Acessar área protegida sem login
        logger.info("🔒 Teste 1: Acessar área protegida sem login")
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        time.sleep(2)
        
        if "login.html" in driver.current_url:
            logger.info("✅ Redirecionado para login (proteção funcionando)")
        else:
            logger.error("❌ Acesso não foi bloqueado")
            return False
        
        # Teste 2: Login com credenciais válidas
        logger.info("🔑 Teste 2: Login com credenciais válidas")
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username.send_keys("admin")
        password.send_keys("dashboard2025")
        login_button.click()
        
        # Aguardar redirecionamento
        time.sleep(3)
        
        if "dashboard-protected.html" in driver.current_url:
            logger.info("✅ Login bem-sucedido - Acesso à área protegida")
        else:
            logger.error("❌ Login falhou")
            return False
        
        # Teste 3: Verificar elementos da área protegida
        logger.info("🔐 Teste 3: Verificar área protegida")
        try:
            protected_badge = driver.find_element(By.CLASS_NAME, "protected-badge")
            user_name = driver.find_element(By.ID, "userName")
            logger.info(f"✅ Área protegida carregada - Usuário: {user_name.text}")
        except:
            logger.error("❌ Elementos da área protegida não encontrados")
            return False
        
        # Teste 4: Verificar dashboards
        logger.info("📊 Teste 4: Verificar dashboards")
        time.sleep(2)  # Aguardar carregamento
        try:
            dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
            logger.info(f"✅ {len(dashboard_cards)} dashboards encontrados")
        except:
            logger.error("❌ Dashboards não encontrados")
            return False
        
        # Teste 5: Logout
        logger.info("🚪 Teste 5: Logout")
        try:
            logout_button = driver.find_element(By.CLASS_NAME, "logout-button")
            logout_button.click()
            time.sleep(2)
            
            if "login.html" in driver.current_url:
                logger.info("✅ Logout bem-sucedido")
            else:
                logger.error("❌ Logout falhou")
                return False
        except:
            logger.error("❌ Botão de logout não encontrado")
            return False
        
        logger.info("🎉 Todos os testes de autenticação passaram!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_auth_simple()
    exit(0 if success else 1)
