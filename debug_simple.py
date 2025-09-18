#!/usr/bin/env python3
"""
Debug simples do erro JavaScript
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_simple():
    """Debug simples"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🔍 Debug simples...")
        driver.get("https://dash.iasouth.tech")
        time.sleep(5)
        
        # Capturar logs
        logs = driver.get_log('browser')
        
        localhost_errors = [log for log in logs if 'localhost:8081' in log['message']]
        
        logging.info(f"📊 Total de logs: {len(logs)}")
        logging.info(f"🚨 Erros localhost:8081: {len(localhost_errors)}")
        
        for error in localhost_errors:
            logging.error(f"   - {error['message']}")
        
        return len(localhost_errors) == 0
        
    except Exception as e:
        logging.error(f"❌ Erro: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_simple()
    logging.info(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ AINDA HÁ ERROS'}")
