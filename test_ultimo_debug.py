#!/usr/bin/env python3
"""
Último debug para identificar o erro JavaScript
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ultimo_debug():
    """Último debug"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-cache')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-offline-load-stale-cache')
    chrome_options.add_argument('--disk-cache-size=0')
    chrome_options.add_argument('--media-cache-size=0')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logging.info("🔍 Último debug - verificando erro JavaScript...")
        
        driver.get("https://dash.iasouth.tech")
        time.sleep(8)
        
        # Capturar logs
        logs = driver.get_log('browser')
        
        logging.info(f"📊 Total de logs: {len(logs)}")
        
        for log in logs:
            level = log['level']
            message = log['message']
            
            if level == 'SEVERE':
                logging.error(f"🚨 ERRO SEVERO: {message}")
            elif level == 'WARNING':
                logging.warning(f"⚠️ AVISO: {message}")
            else:
                logging.info(f"ℹ️ INFO: {message}")
        
        # Verificar se há código localhost:8081 no HTML
        html_content = driver.execute_script("return document.documentElement.outerHTML;")
        
        localhost_count = html_content.count('localhost:8081')
        logging.info(f"📄 Ocorrências de localhost:8081 no HTML: {localhost_count}")
        
        if localhost_count > 0:
            lines = html_content.split('\n')
            for i, line in enumerate(lines):
                if 'localhost:8081' in line:
                    logging.error(f"   Linha {i+1}: {line.strip()}")
        
        # Verificar se dashboards carregaram
        dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
        logging.info(f"📊 Dashboards encontrados: {len(dashboard_cards)}")
        
        if len(dashboard_cards) > 0:
            first_card = dashboard_cards[0]
            dashboard_file = first_card.get_attribute('data-dashboard-file')
            logging.info(f"🎯 Data-dashboard-file: {dashboard_file}")
        
        return localhost_count == 0
        
    except Exception as e:
        logging.error(f"❌ Erro: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = ultimo_debug()
    logging.info(f"🎯 Resultado: {'✅ SUCESSO' if success else '❌ AINDA HÁ ERROS'}")
