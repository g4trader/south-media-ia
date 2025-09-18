#!/usr/bin/env python3
"""
Debug do erro JavaScript específico
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_js_error():
    """Debug detalhado do erro JavaScript"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🔍 Acessando página para debug...")
        driver.get("https://dash.iasouth.tech")
        time.sleep(5)
        
        # Capturar todos os logs
        logs = driver.get_log('browser')
        
        logging.info(f"📊 Total de logs: {len(logs)}")
        
        for log in logs:
            level = log['level']
            message = log['message']
            timestamp = log['timestamp']
            
            if 'localhost:8081' in message:
                logging.error(f"🚨 ERRO LOCALHOST:8081:")
                logging.error(f"   Nível: {level}")
                logging.error(f"   Mensagem: {message}")
                logging.error(f"   Timestamp: {timestamp}")
            elif level == 'SEVERE':
                logging.warning(f"⚠️ OUTRO ERRO SEVERO:")
                logging.warning(f"   Mensagem: {message}")
        
        # Verificar se há código específico que ainda está executando
        current_js = driver.execute_script("return document.documentElement.outerHTML;")
        
        if 'localhost:8081' in current_js:
            logging.error("🚨 Código localhost:8081 encontrado no HTML!")
            
            # Encontrar onde está
            lines = current_js.split('\n')
            for i, line in enumerate(lines):
                if 'localhost:8081' in line:
                    logging.error(f"   Linha {i+1}: {line.strip()}")
        else:
            logging.info("✅ Nenhum código localhost:8081 encontrado no HTML")
        
    except Exception as e:
        logging.error(f"❌ Erro no debug: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_js_error()
