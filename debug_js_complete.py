#!/usr/bin/env python3
"""
Debug completo do erro JavaScript
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_js_complete():
    """Debug completo do erro JavaScript"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--disable-cache')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🔍 Debug completo do erro JavaScript...")
        
        # Limpar tudo
        driver.delete_all_cookies()
        driver.execute_script("localStorage.clear();")
        driver.execute_script("sessionStorage.clear();")
        
        driver.get("https://dash.iasouth.tech")
        time.sleep(8)  # Aguardar mais tempo
        
        # Capturar todos os logs
        logs = driver.get_log('browser')
        
        logging.info(f"📊 Total de logs: {len(logs)}")
        
        localhost_errors = []
        for log in logs:
            level = log['level']
            message = log['message']
            timestamp = log['timestamp']
            
            if 'localhost:8081' in message:
                localhost_errors.append({
                    'level': level,
                    'message': message,
                    'timestamp': timestamp
                })
                logging.error(f"🚨 ERRO LOCALHOST:8081:")
                logging.error(f"   Nível: {level}")
                logging.error(f"   Mensagem: {message}")
                logging.error(f"   Timestamp: {timestamp}")
        
        if len(localhost_errors) == 0:
            logging.info("✅ Nenhum erro localhost:8081 encontrado!")
            return True
        else:
            logging.error(f"❌ {len(localhost_errors)} erros localhost:8081 encontrados")
            
            # Verificar se há código no HTML
            html_content = driver.execute_script("return document.documentElement.outerHTML;")
            
            localhost_count = html_content.count('localhost:8081')
            logging.info(f"📄 Ocorrências de localhost:8081 no HTML: {localhost_count}")
            
            if localhost_count > 0:
                # Encontrar linhas específicas
                lines = html_content.split('\n')
                for i, line in enumerate(lines):
                    if 'localhost:8081' in line:
                        logging.error(f"   Linha {i+1}: {line.strip()}")
            
            return False
        
    except Exception as e:
        logging.error(f"❌ Erro no debug: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_js_complete()
    logging.info(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ AINDA HÁ ERROS'}")
