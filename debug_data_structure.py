#!/usr/bin/env python3
"""
Debug específico para verificar a estrutura dos dados
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_data_structure():
    """Debug específico da estrutura dos dados"""
    print("🔍 DEBUG DA ESTRUTURA DOS DADOS")
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
        print("\n🔧 Verificando estrutura dos dados JavaScript...")
        
        try:
            # Verificar se os dados estão carregados
            data_available = driver.execute_script("return window.dashboardLoader.data !== null")
            print(f"✅ Dados carregados: {data_available}")
            
            if data_available:
                # Verificar o tipo dos dados
                data_type = driver.execute_script("return typeof window.dashboardLoader.data")
                print(f"📋 Tipo dos dados: {data_type}")
                
                # Verificar se é um objeto
                is_object = driver.execute_script("return typeof window.dashboardLoader.data === 'object'")
                print(f"📋 É um objeto: {is_object}")
                
                # Verificar se é null
                is_null = driver.execute_script("return window.dashboardLoader.data === null")
                print(f"📋 É null: {is_null}")
                
                # Verificar se é undefined
                is_undefined = driver.execute_script("return window.dashboardLoader.data === undefined")
                print(f"📋 É undefined: {is_undefined}")
                
                # Verificar se é um array
                is_array = driver.execute_script("return Array.isArray(window.dashboardLoader.data)")
                print(f"📋 É um array: {is_array}")
                
                # Verificar se tem propriedades
                has_properties = driver.execute_script("return window.dashboardLoader.data && typeof window.dashboardLoader.data === 'object' && !Array.isArray(window.dashboardLoader.data)")
                print(f"📋 Tem propriedades: {has_properties}")
                
                if has_properties:
                    # Verificar propriedades específicas
                    for key in ['metrics', 'contract', 'strategies', 'publishers', 'daily_data', 'per_data']:
                        try:
                            value = driver.execute_script(f"return window.dashboardLoader.data.{key}")
                            if value is not None:
                                print(f"✅ {key}: {type(value).__name__}")
                                if key == 'publishers' and isinstance(value, list):
                                    print(f"   📺 Publishers: {len(value)} itens")
                                elif key == 'strategies' and isinstance(value, dict):
                                    print(f"   🎯 Estratégias: {list(value.keys())}")
                                elif key == 'contract' and isinstance(value, dict):
                                    print(f"   📋 Contrato: {list(value.keys())}")
                            else:
                                print(f"❌ {key}: null ou undefined")
                        except Exception as e:
                            print(f"❌ Erro ao verificar {key}: {e}")
                else:
                    print("❌ Dados não têm propriedades válidas")
                    
            else:
                print("❌ Dados não estão carregados")
                
        except Exception as e:
            print(f"❌ Erro ao verificar estrutura dos dados: {e}")
        
        # Verificar se a aba de planejamento foi atualizada
        print("\n🔧 Verificando aba de planejamento...")
        
        try:
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
                
        except Exception as e:
            print(f"❌ Erro ao verificar aba de planejamento: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_debug_data_structure.png")
        print("\n📸 Screenshot salvo: selenium_debug_data_structure.png")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    debug_data_structure()
