#!/usr/bin/env python3
"""
Debug do Sistema Multi-Tenant
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

def debug_multi_tenant():
    """Debug do sistema multi-tenant"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🔍 Debug do Sistema Multi-Tenant")
        
        # Teste 1: Verificar página de login
        logger.info("📄 Teste 1: Verificar página de login")
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
        
        # Teste 2: Verificar se authSystem está disponível
        logger.info("🔧 Teste 2: Verificar authSystem")
        
        # Aguardar um pouco para o JavaScript carregar
        time.sleep(2)
        
        auth_system_available = driver.execute_script("return typeof window.authSystem !== 'undefined';")
        logger.info(f"✅ authSystem disponível: {auth_system_available}")
        
        if not auth_system_available:
            # Verificar se há erros no console
            logs = driver.get_log('browser')
            for log in logs:
                if log['level'] == 'SEVERE':
                    logger.error(f"❌ Erro no console: {log['message']}")
            
            logger.error("❌ authSystem não está disponível")
            return False
        
        # Teste 3: Verificar dados do sistema
        logger.info("📊 Teste 3: Verificar dados do sistema")
        system_data = driver.execute_script("return window.authSystem.getSystemData();")
        logger.info(f"✅ Dados do sistema carregados: {'Sim' if system_data else 'Não'}")
        
        if system_data:
            logger.info(f"✅ Empresas: {len(system_data.companies) if system_data.companies else 0}")
            logger.info(f"✅ Usuários: {len(system_data.users) if system_data.users else 0}")
            logger.info(f"✅ Dashboards: {len(system_data.dashboards) if system_data.dashboards else 0}")
        
        # Teste 4: Tentar login
        logger.info("🔑 Teste 4: Tentar login")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        login_button.click()
        
        # Aguardar um pouco
        time.sleep(3)
        
        # Verificar se houve redirecionamento
        current_url = driver.current_url
        logger.info(f"✅ URL atual: {current_url}")
        
        if "dashboard-protected" in current_url:
            logger.info("✅ Redirecionamento bem-sucedido")
            
            # Verificar dados do usuário
            user = driver.execute_script("return window.authSystem.getCurrentUser();")
            if user:
                logger.info(f"✅ Usuário logado: {user['profile']['full_name']}")
                logger.info(f"✅ Empresa: {user['company_id']}")
                
                # Verificar dashboards
                dashboards = driver.execute_script("return window.authSystem.getDashboardsForUser();")
                logger.info(f"✅ Dashboards disponíveis: {len(dashboards)}")
                
                for dashboard in dashboards:
                    logger.info(f"   • {dashboard['name']} (Empresa: {dashboard['company_id']})")
            else:
                logger.error("❌ Usuário não encontrado após login")
                return False
        else:
            logger.error("❌ Redirecionamento falhou")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_multi_tenant()
    if success:
        print("\n🔍 DEBUG CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ ERRO NO DEBUG")
    
    exit(0 if success else 1)
