#!/usr/bin/env python3
"""
Teste para verificar se o cache está causando problemas
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_cache_clear():
    """Testar com cache limpo"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-cache')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-offline-load-stale-cache')
    chrome_options.add_argument('--disk-cache-size=0')
    chrome_options.add_argument('--media-cache-size=0')
    chrome_options.add_argument('--disable-background-timer-throttling')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🧹 Limpando cache e acessando página...")
        
        # Limpar completamente
        driver.delete_all_cookies()
        driver.execute_script("localStorage.clear();")
        driver.execute_script("sessionStorage.clear();")
        
        # Forçar refresh
        driver.get("https://dash.iasouth.tech")
        driver.refresh()
        time.sleep(5)
        
        # Verificar erros JavaScript
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        critical_errors = [error for error in js_errors if 'favicon.ico' not in error['message']]
        
        logging.info(f"📊 Total de erros: {len(js_errors)}")
        logging.info(f"🚨 Erros críticos: {len(critical_errors)}")
        
        for error in critical_errors:
            logging.error(f"   - {error['message']}")
        
        # Verificar dashboards
        dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
        logging.info(f"📊 Dashboards encontrados: {len(dashboard_cards)}")
        
        if len(dashboard_cards) > 0:
            first_card = dashboard_cards[0]
            dashboard_file = first_card.get_attribute('data-dashboard-file')
            logging.info(f"🎯 Data-dashboard-file: {dashboard_file}")
            
            # Verificar HTML gerado
            html_content = first_card.get_attribute('outerHTML')
            logging.info(f"📄 HTML do primeiro card:\n{html_content[:200]}...")
        
        return len(critical_errors) == 0
        
    except Exception as e:
        logging.error(f"❌ Erro no teste: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_cache_clear()
    logging.info(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")
