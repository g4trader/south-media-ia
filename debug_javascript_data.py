#!/usr/bin/env python3
"""
Debug específico para verificar os dados JavaScript
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_javascript_data():
    """Debug específico dos dados JavaScript"""
    print("🔍 DEBUG DOS DADOS JAVASCRIPT")
    print("=" * 50)
    
    # Setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        print("📊 Acessando dashboard...")
        driver.get("http://localhost:5000/static/dash_sebrae_programatica_video_sync.html")
        time.sleep(10)  # Aguardar carregamento
        
        # Verificar dados JavaScript
        print("\n🔧 Verificando dados JavaScript...")
        
        try:
            # Verificar se os dados estão carregados
            data_available = driver.execute_script("return window.dashboardLoader.data !== null")
            print(f"✅ Dados carregados: {data_available}")
            
            if data_available:
                # Verificar estrutura dos dados
                data_keys = driver.execute_script("return Object.keys(window.dashboardLoader.data)")
                print(f"📋 Chaves dos dados: {data_keys}")
                
                # Verificar cada seção individualmente
                for key in ['metrics', 'contract', 'strategies', 'publishers', 'daily_data', 'per_data']:
                    try:
                        value = driver.execute_script(f"return window.dashboardLoader.data.{key}")
                        if value:
                            if key == 'publishers' and isinstance(value, list):
                                print(f"✅ {key}: {len(value)} itens")
                                for i, item in enumerate(value):
                                    print(f"   {i+1}. {item}")
                            elif key == 'strategies' and isinstance(value, dict):
                                print(f"✅ {key}: {list(value.keys())}")
                                for subkey, subvalue in value.items():
                                    print(f"   {subkey}: {subvalue}")
                            elif key == 'contract' and isinstance(value, dict):
                                print(f"✅ {key}: {list(value.keys())}")
                                for subkey, subvalue in value.items():
                                    print(f"   {subkey}: {subvalue}")
                            else:
                                print(f"✅ {key}: {type(value)}")
                        else:
                            print(f"❌ {key}: null ou undefined")
                    except Exception as e:
                        print(f"❌ Erro ao verificar {key}: {e}")
                
                # Verificar se renderPlanningData foi chamada
                print("\n🔧 Verificando se renderPlanningData foi chamada...")
                
                # Navegar para aba de planejamento
                planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
                driver.execute_script("arguments[0].click();", planning_tab)
                time.sleep(2)
                
                # Verificar publishers
                publishers_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(3) div[style*="grid-template-columns"] > div')
                print(f"📺 Publishers divs encontrados: {len(publishers_divs)}")
                
                if len(publishers_divs) >= 6:
                    print("✅ Lista de publishers carregada corretamente")
                    
                    # Verificar se são dados dinâmicos
                    for i, div in enumerate(publishers_divs[:3]):
                        try:
                            div_text = div.text
                            print(f"   {i+1}. {div_text}")
                            
                            # Verificar se é HTML dinâmico
                            div_html = driver.execute_script("return arguments[0].outerHTML", div)
                            if "border-left:4px solid #ff6b35" in div_html:
                                print(f"      ✅ Div {i+1} é dinâmico")
                            else:
                                print(f"      ⚠️ Div {i+1} é estático")
                                
                        except Exception as e:
                            print(f"   ❌ Erro ao verificar div {i+1}: {e}")
                else:
                    print("❌ Lista de publishers incompleta")
                    
            else:
                print("❌ Dados não estão carregados")
                
        except Exception as e:
            print(f"❌ Erro ao verificar dados JavaScript: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_debug_javascript_data.png")
        print("\n📸 Screenshot salvo: selenium_debug_javascript_data.png")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    debug_javascript_data()
