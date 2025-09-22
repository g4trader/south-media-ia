#!/usr/bin/env python3
"""
Debug dos dashboards
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_dashboards():
    """Debug dos dashboards"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🔍 Debug dos dashboards...")
        driver.get("https://dash.iasouth.tech")
        time.sleep(5)
        
        # Verificar se dashboards carregaram
        dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
        logging.info(f"📊 Dashboards encontrados: {len(dashboard_cards)}")
        
        if len(dashboard_cards) > 0:
            first_card = dashboard_cards[0]
            
            # Verificar atributos
            dashboard_file = first_card.get_attribute('data-dashboard-file')
            logging.info(f"🎯 Data-dashboard-file: {dashboard_file}")
            
            # Verificar HTML do card
            html_content = first_card.get_attribute('outerHTML')
            logging.info(f"📄 HTML do primeiro card:\n{html_content[:200]}...")
            
            # Verificar se tem cursor pointer
            style = first_card.get_attribute('style')
            logging.info(f"🎨 Style: {style}")
            
            # Verificar se tem onclick
            onclick = first_card.get_attribute('onclick')
            logging.info(f"🖱️ Onclick: {onclick}")
        
        # Verificar se há erro na console
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if len(js_errors) > 0:
            logging.error(f"🚨 {len(js_errors)} erros JavaScript:")
            for error in js_errors:
                logging.error(f"   - {error['message']}")
        
        return len(dashboard_cards) > 0
        
    except Exception as e:
        logging.error(f"❌ Erro: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_dashboards()
    logging.info(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ FALHOU'}")
