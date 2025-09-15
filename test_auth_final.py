#!/usr/bin/env python3
"""
Teste Final do Sistema de Autenticação Robusto
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

def test_auth_final():
    """Teste final do sistema de autenticação"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🔐 Teste Final do Sistema de Autenticação Robusto")
        
        # Teste 1: Login com admin
        logger.info("👑 Teste 1: Login com admin")
        success = test_login(driver, "admin", "dashboard2025", "Administrador do Sistema", "SUPER")
        if not success:
            return False
        
        # Teste 2: Verificar sistema funcionando
        logger.info("✅ Teste 2: Verificar sistema funcionando")
        
        # Verificar se authSystem está disponível
        auth_system_available = driver.execute_script("return typeof window.authSystem !== 'undefined';")
        auth_system_authenticated = driver.execute_script("return window.authSystem ? window.authSystem.isAuthenticated() : false;")
        
        logger.info(f"✅ authSystem disponível: {auth_system_available}")
        logger.info(f"✅ authSystem autenticado: {auth_system_authenticated}")
        
        if not (auth_system_available and auth_system_authenticated):
            logger.error("❌ Sistema de autenticação não está funcionando corretamente")
            return False
        
        # Verificar dados do usuário
        current_user = driver.execute_script("return window.authSystem.getCurrentUser();")
        logger.info(f"✅ Usuário atual: {current_user['profile']['full_name']}")
        logger.info(f"✅ Role: {current_user['role']}")
        logger.info(f"✅ Permissões: {current_user['permissions']}")
        
        # Verificar se tem todas as permissões (super admin)
        if '*' not in current_user['permissions']:
            logger.error("❌ Admin não tem todas as permissões")
            return False
        
        logger.info("🎉 SISTEMA DE AUTENTICAÇÃO ROBUSTO FUNCIONANDO PERFEITAMENTE!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        return False
    finally:
        driver.quit()

def test_login(driver, username, password, expected_name, expected_role):
    """Testar login com credenciais específicas"""
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
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard-protected" in d.current_url
        )
        
        # Verificar informações do usuário
        user_name = driver.find_element(By.ID, "userName")
        user_role = driver.find_element(By.ID, "userRole")
        
        if expected_name not in user_name.text:
            logger.error(f"❌ Nome esperado '{expected_name}' não encontrado em '{user_name.text}'")
            return False
        
        if expected_role not in user_role.text:
            logger.error(f"❌ Role esperado '{expected_role}' não encontrado em '{user_role.text}'")
            return False
        
        logger.info(f"✅ Login bem-sucedido: {user_name.text} ({user_role.text})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_final()
    if success:
        print("\n🎉 SISTEMA DE AUTENTICAÇÃO ROBUSTO FUNCIONANDO PERFEITAMENTE!")
        print("✅ Todos os testes passaram com sucesso")
        print("\n🔐 Funcionalidades implementadas:")
        print("   • Sistema de usuários e roles")
        print("   • Controle de acesso baseado em permissões")
        print("   • Gerenciamento de sessões seguro")
        print("   • Middleware de proteção de rotas")
        print("   • Interface de gerenciamento de usuários")
        print("\n👥 Usuários disponíveis:")
        print("   • admin / dashboard2025 (Super Admin)")
        print("   • manager / manager2025 (Gerente)")
        print("   • viewer / viewer2025 (Visualizador)")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔍 Verifique os logs para mais detalhes")
    
    exit(0 if success else 1)
