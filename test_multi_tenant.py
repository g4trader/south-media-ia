#!/usr/bin/env python3
"""
Teste do Sistema Multi-Tenant
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

def test_multi_tenant_system():
    """Teste completo do sistema multi-tenant"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🏢 Teste do Sistema Multi-Tenant")
        
        # Teste 1: Super Admin vê todas as empresas
        logger.info("👑 Teste 1: Super Admin - Todas as empresas")
        success = test_super_admin_access(driver)
        if not success:
            return False
        
        # Teste 2: Manager da IA South Tech
        logger.info("👔 Teste 2: Manager IA South Tech")
        success = test_company_manager(driver, "manager", "manager2025", "IA South Tech")
        if not success:
            return False
        
        # Teste 3: Manager da Sonho Digital
        logger.info("🎯 Teste 3: Manager Sonho Digital")
        success = test_company_manager(driver, "sonho_manager", "sonho2025", "Sonho Digital")
        if not success:
            return False
        
        # Teste 4: Viewer da Analytics Pro
        logger.info("📊 Teste 4: Viewer Analytics Pro")
        success = test_company_viewer(driver, "analytics_viewer", "analytics2025", "Analytics Pro")
        if not success:
            return False
        
        logger.info("🎉 SISTEMA MULTI-TENANT FUNCIONANDO PERFEITAMENTE!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        return False
    finally:
        driver.quit()

def test_super_admin_access(driver):
    """Testar acesso do super admin"""
    try:
        # Login como super admin
        if not login_user(driver, "admin", "dashboard2025"):
            return False
        
        # Verificar se vê todas as empresas
        company_info = driver.find_element(By.ID, "userCompany")
        if "Todas as Empresas" not in company_info.text:
            logger.error(f"❌ Super admin não vê 'Todas as Empresas': {company_info.text}")
            return False
        
        # Verificar se vê todos os dashboards
        dashboards = driver.execute_script("return window.authSystem.getDashboardsForUser();")
        if len(dashboards) < 5:  # Deve ver pelo menos 5 dashboards
            logger.error(f"❌ Super admin não vê todos os dashboards: {len(dashboards)}")
            return False
        
        logger.info(f"✅ Super admin vê {len(dashboards)} dashboards de todas as empresas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do super admin: {e}")
        return False

def test_company_manager(driver, username, password, expected_company):
    """Testar manager de empresa específica"""
    try:
        # Login como manager
        if not login_user(driver, username, password):
            return False
        
        # Verificar empresa
        company_info = driver.find_element(By.ID, "userCompany")
        if expected_company not in company_info.text:
            logger.error(f"❌ Manager não vê empresa correta: {company_info.text}")
            return False
        
        # Verificar dashboards da empresa
        dashboards = driver.execute_script("return window.authSystem.getDashboardsForUser();")
        if len(dashboards) == 0:
            logger.error(f"❌ Manager não vê dashboards da empresa")
            return False
        
        # Verificar se todos os dashboards são da empresa correta
        user = driver.execute_script("return window.authSystem.getCurrentUser();")
        company_id = user['company_id']
        
        for dashboard in dashboards:
            if dashboard['company_id'] != company_id:
                logger.error(f"❌ Dashboard de empresa diferente encontrado: {dashboard['name']}")
                return False
        
        logger.info(f"✅ Manager {expected_company} vê {len(dashboards)} dashboards da empresa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do manager: {e}")
        return False

def test_company_viewer(driver, username, password, expected_company):
    """Testar viewer de empresa específica"""
    try:
        # Login como viewer
        if not login_user(driver, username, password):
            return False
        
        # Verificar empresa
        company_info = driver.find_element(By.ID, "userCompany")
        if expected_company not in company_info.text:
            logger.error(f"❌ Viewer não vê empresa correta: {company_info.text}")
            return False
        
        # Verificar dashboards da empresa
        dashboards = driver.execute_script("return window.authSystem.getDashboardsForUser();")
        if len(dashboards) == 0:
            logger.error(f"❌ Viewer não vê dashboards da empresa")
            return False
        
        # Verificar se todos os dashboards são da empresa correta
        user = driver.execute_script("return window.authSystem.getCurrentUser();")
        company_id = user['company_id']
        
        for dashboard in dashboards:
            if dashboard['company_id'] != company_id:
                logger.error(f"❌ Dashboard de empresa diferente encontrado: {dashboard['name']}")
                return False
        
        logger.info(f"✅ Viewer {expected_company} vê {len(dashboards)} dashboards da empresa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste do viewer: {e}")
        return False

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
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

if __name__ == "__main__":
    success = test_multi_tenant_system()
    if success:
        print("\n🎉 SISTEMA MULTI-TENANT FUNCIONANDO PERFEITAMENTE!")
        print("✅ Todos os testes passaram com sucesso")
        print("\n🏢 Funcionalidades implementadas:")
        print("   • Sistema de empresas multi-tenant")
        print("   • Associação de usuários a empresas")
        print("   • Associação de dashboards a empresas")
        print("   • Filtragem por empresa no painel")
        print("   • Super admin vê todas as empresas")
        print("   • Usuários veem apenas sua empresa")
        print("\n👥 Empresas configuradas:")
        print("   • IA South Tech (manager, viewer)")
        print("   • Sonho Digital (sonho_manager)")
        print("   • Analytics Pro (analytics_viewer)")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔍 Verifique os logs para mais detalhes")
    
    exit(0 if success else 1)
