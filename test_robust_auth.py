#!/usr/bin/env python3
"""
Teste do Sistema de Autenticação Robusto
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

def test_robust_auth_system():
    """Teste completo do sistema de autenticação robusto"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info("🔐 Iniciando teste do sistema de autenticação robusto")
        
        # Teste 1: Login com usuário admin
        logger.info("👑 Teste 1: Login com usuário admin")
        if test_admin_login(driver):
            logger.info("✅ Login admin bem-sucedido")
        else:
            logger.error("❌ Falha no login admin")
            return False
        
        # Teste 2: Verificar permissões de admin
        logger.info("🔍 Teste 2: Verificar permissões de admin")
        if test_admin_permissions(driver):
            logger.info("✅ Permissões de admin verificadas")
        else:
            logger.error("❌ Falha na verificação de permissões admin")
            return False
        
        # Teste 3: Testar logout
        logger.info("🚪 Teste 3: Testar logout")
        if test_logout(driver):
            logger.info("✅ Logout bem-sucedido")
        else:
            logger.error("❌ Falha no logout")
            return False
        
        # Teste 4: Login com usuário manager
        logger.info("👔 Teste 4: Login com usuário manager")
        if test_manager_login(driver):
            logger.info("✅ Login manager bem-sucedido")
        else:
            logger.error("❌ Falha no login manager")
            return False
        
        # Teste 5: Verificar permissões limitadas
        logger.info("🔒 Teste 5: Verificar permissões limitadas do manager")
        if test_manager_permissions(driver):
            logger.info("✅ Permissões limitadas verificadas")
        else:
            logger.error("❌ Falha na verificação de permissões manager")
            return False
        
        # Teste 6: Testar acesso negado
        logger.info("🚫 Teste 6: Testar acesso negado")
        if test_access_denied(driver):
            logger.info("✅ Acesso negado funcionando")
        else:
            logger.error("❌ Falha no teste de acesso negado")
            return False
        
        logger.info("🎉 Todos os testes do sistema robusto passaram!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")
        return False
    finally:
        driver.quit()

def test_admin_login(driver):
    """Testar login com usuário admin"""
    try:
        driver.get("https://dash.iasouth.tech/login.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        
        # Preencher credenciais
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
        
        return "dashboard-protected" in driver.current_url
        
    except Exception as e:
        logger.error(f"Erro no teste de login admin: {e}")
        return False

def test_admin_permissions(driver):
    """Verificar permissões de admin"""
    try:
        # Verificar se está na página protegida
        if "dashboard-protected" not in driver.current_url:
            return False
        
        # Verificar se o nome do usuário está correto
        user_name = driver.find_element(By.ID, "userName")
        if "Administrador" not in user_name.text:
            return False
        
        # Verificar se o role está correto
        user_role = driver.find_element(By.ID, "userRole")
        if "SUPER" not in user_role.text:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação de permissões admin: {e}")
        return False

def test_logout(driver):
    """Testar logout"""
    try:
        # Clicar no botão de logout
        logout_button = driver.find_element(By.CSS_SELECTOR, "a[onclick='logout()']")
        logout_button.click()
        
        # Confirmar logout
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        
        # Aguardar redirecionamento para login
        WebDriverWait(driver, 10).until(
            lambda d: "login" in d.current_url
        )
        
        return "login" in driver.current_url
        
    except Exception as e:
        logger.error(f"Erro no teste de logout: {e}")
        return False

def test_manager_login(driver):
    """Testar login com usuário manager"""
    try:
        # Preencher credenciais do manager
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        username.clear()
        password.clear()
        username.send_keys("manager")
        password.send_keys("manager2025")
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard-protected" in d.current_url
        )
        
        return "dashboard-protected" in driver.current_url
        
    except Exception as e:
        logger.error(f"Erro no teste de login manager: {e}")
        return False

def test_manager_permissions(driver):
    """Verificar permissões limitadas do manager"""
    try:
        # Verificar se está na página protegida
        if "dashboard-protected" not in driver.current_url:
            return False
        
        # Verificar se o nome do usuário está correto
        user_name = driver.find_element(By.ID, "userName")
        if "Gerente" not in user_name.text:
            return False
        
        # Verificar se o role está correto
        user_role = driver.find_element(By.ID, "userRole")
        if "Gerente" not in user_role.text:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação de permissões manager: {e}")
        return False

def test_access_denied(driver):
    """Testar acesso negado"""
    try:
        # Tentar acessar página de usuários (requer permissão users:manage)
        driver.get("https://dash.iasouth.tech/users.html")
        
        # Aguardar redirecionamento ou mensagem de erro
        time.sleep(3)
        
        # Se foi redirecionado para unauthorized ou se há alerta, está funcionando
        if "unauthorized" in driver.current_url:
            return True
        
        # Verificar se há alerta de permissão
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return "permissão" in alert_text.lower()
        except:
            pass
        
        return False
        
    except Exception as e:
        logger.error(f"Erro no teste de acesso negado: {e}")
        return False

if __name__ == "__main__":
    success = test_robust_auth_system()
    if success:
        print("\n🎉 SISTEMA DE AUTENTICAÇÃO ROBUSTO FUNCIONANDO PERFEITAMENTE!")
        print("✅ Todos os testes passaram com sucesso")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("🔍 Verifique os logs para mais detalhes")
    
    exit(0 if success else 1)
