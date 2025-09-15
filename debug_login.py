#!/usr/bin/env python3
"""
Script para debugar problemas na página de login
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_login():
    """Debugar página de login"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar para login
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(2)
        
        # Verificar se elementos existem
        logger.info("=== VERIFICANDO ELEMENTOS ===")
        try:
            form = driver.find_element(By.ID, "loginForm")
            logger.info("✅ Formulário encontrado")
        except:
            logger.error("❌ Formulário não encontrado")
        
        try:
            username = driver.find_element(By.ID, "username")
            logger.info("✅ Campo username encontrado")
        except:
            logger.error("❌ Campo username não encontrado")
        
        try:
            password = driver.find_element(By.ID, "password")
            logger.info("✅ Campo password encontrado")
        except:
            logger.error("❌ Campo password não encontrado")
        
        try:
            button = driver.find_element(By.ID, "loginButton")
            logger.info("✅ Botão de login encontrado")
        except:
            logger.error("❌ Botão de login não encontrado")
        
        # Verificar JavaScript
        logger.info("=== VERIFICANDO JAVASCRIPT ===")
        js_errors = driver.get_log('browser')
        if js_errors:
            logger.warning("⚠️ Erros JavaScript encontrados:")
            for error in js_errors:
                logger.warning(f"  {error['message']}")
        else:
            logger.info("✅ Nenhum erro JavaScript")
        
        # Tentar preencher e clicar
        logger.info("=== TESTANDO INTERAÇÃO ===")
        username.send_keys("admin")
        password.send_keys("dashboard2025")
        
        logger.info("📝 Campos preenchidos")
        
        # Verificar se há event listeners
        has_submit_listener = driver.execute_script("""
            var form = document.getElementById('loginForm');
            return form && form.onsubmit !== null;
        """)
        logger.info(f"📋 Event listener de submit: {has_submit_listener}")
        
        # Clicar no botão
        button.click()
        logger.info("🖱️ Botão clicado")
        
        # Aguardar e verificar mudanças
        time.sleep(3)
        
        # Verificar URL atual
        current_url = driver.current_url
        logger.info(f"🌐 URL atual: {current_url}")
        
        # Verificar mensagens
        try:
            error_msg = driver.find_element(By.CLASS_NAME, "error-message")
            if error_msg.is_displayed():
                logger.info(f"❌ Mensagem de erro: {error_msg.text}")
        except:
            logger.info("ℹ️ Nenhuma mensagem de erro")
        
        try:
            success_msg = driver.find_element(By.CLASS_NAME, "success-message")
            if success_msg.is_displayed():
                logger.info(f"✅ Mensagem de sucesso: {success_msg.text}")
        except:
            logger.info("ℹ️ Nenhuma mensagem de sucesso")
        
        # Verificar localStorage
        logger.info("=== VERIFICANDO LOCALSTORAGE ===")
        session_data = driver.execute_script("return localStorage.getItem('dashboard_session');")
        if session_data:
            logger.info(f"💾 Sessão encontrada: {session_data[:100]}...")
        else:
            logger.info("💾 Nenhuma sessão no localStorage")
        
        # Verificar se botão mudou de estado
        button_state = driver.execute_script("""
            var button = document.getElementById('loginButton');
            return {
                disabled: button.disabled,
                text: button.textContent.trim(),
                className: button.className
            };
        """)
        logger.info(f"🔘 Estado do botão: {button_state}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login()
