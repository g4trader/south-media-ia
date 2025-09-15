#!/usr/bin/env python3
"""
Teste Simples do Sistema Multi-Tenant
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

def test_multi_tenant_simple():
    """Teste simples do sistema multi-tenant"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🏢 Teste Simples do Sistema Multi-Tenant")
        
        # Teste 1: Login com admin
        logger.info("👑 Teste 1: Login com admin")
        if not login_user(driver, "admin", "dashboard2025"):
            return False
        
        # Teste 2: Verificar sistema multi-tenant
        logger.info("🔍 Teste 2: Verificar sistema multi-tenant")
        
        # Verificar se authSystem está disponível
        auth_system_available = driver.execute_script("return typeof window.authSystem !== 'undefined';")
        logger.info(f"✅ authSystem disponível: {auth_system_available}")
        
        if not auth_system_available:
            logger.error("❌ Sistema de autenticação não está disponível")
            return False
        
        # Verificar empresas
        companies = driver.execute_script("return window.authSystem.getAllCompanies();")
        logger.info(f"✅ Empresas encontradas: {companies['success']}")
        
        if companies['success']:
            logger.info(f"✅ Total de empresas: {len(companies['companies'])}")
            for company in companies['companies']:
                logger.info(f"   • {company['name']} ({company['code']})")
        
        # Verificar dashboards
        dashboards = driver.execute_script("return window.authSystem.getDashboardsForUser();")
        logger.info(f"✅ Dashboards encontrados: {len(dashboards)}")
        
        for dashboard in dashboards:
            logger.info(f"   • {dashboard['name']} (Empresa: {dashboard['company_id']})")
        
        # Verificar usuário atual
        user = driver.execute_script("return window.authSystem.getCurrentUser();")
        logger.info(f"✅ Usuário atual: {user['profile']['full_name']}")
        logger.info(f"✅ Empresa do usuário: {user['company_id']}")
        
        # Verificar empresa do usuário
        company = driver.execute_script("return window.authSystem.getCurrentUserCompany();")
        if company:
            logger.info(f"✅ Empresa: {company['name']}")
        else:
            logger.info("✅ Super Admin (sem empresa específica)")
        
        logger.info("🎉 SISTEMA MULTI-TENANT FUNCIONANDO!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        return False
    finally:
        driver.quit()

def login_user(driver, username, password):
    """Fazer login com usuário específico"""
    try:
        # Ir para página de login
        driver.get("https://dash.iasouth.tech/login.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        
        # Preencher credenciais
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard-protected" in d.current_url
        )
        
        logger.info(f"✅ Login bem-sucedido: {username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

if __name__ == "__main__":
    success = test_multi_tenant_simple()
    if success:
        print("\n🎉 SISTEMA MULTI-TENANT FUNCIONANDO PERFEITAMENTE!")
        print("✅ Teste simples passou com sucesso")
    else:
        print("\n❌ TESTE FALHOU")
        print("🔍 Verifique os logs para mais detalhes")
    
    exit(0 if success else 1)
