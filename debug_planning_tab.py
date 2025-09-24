#!/usr/bin/env python3
"""
Debug específico para verificar o que está acontecendo na aba de planejamento
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_planning_tab():
    """Debug específico da aba de planejamento"""
    print("🔍 DEBUG DA ABA DE PLANEJAMENTO")
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
                # Verificar publishers especificamente
                publishers = driver.execute_script("return window.dashboardLoader.data.publishers")
                print(f"📺 Publishers no JavaScript: {publishers}")
                
                if publishers:
                    print(f"📺 Quantidade de publishers: {len(publishers)}")
                    for i, publisher in enumerate(publishers):
                        print(f"   {i+1}. {publisher}")
                else:
                    print("❌ Publishers é null ou undefined")
                    
                # Verificar se renderPlanningData foi chamada
                data_loaded = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados disponíveis para renderPlanningData: {data_loaded}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar dados JavaScript: {e}")
        
        # Verificar HTML estático vs dinâmico
        print("\n🔍 Verificando HTML da aba de planejamento...")
        
        # Navegar para aba de planejamento
        planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
        driver.execute_script("arguments[0].click();", planning_tab)
        time.sleep(3)
        
        # Verificar se o HTML foi atualizado
        try:
            # Verificar o container de publishers
            publishers_container = driver.find_element(By.CSS_SELECTOR, '#tab-planning .card:nth-child(3) div[style*="grid-template-columns"]')
            print("✅ Container de publishers encontrado")
            
            # Verificar o HTML interno
            inner_html = driver.execute_script("return arguments[0].innerHTML", publishers_container)
            print(f"📋 HTML interno do container de publishers:")
            print(inner_html[:500] + "..." if len(inner_html) > 500 else inner_html)
            
            # Verificar se contém dados dinâmicos
            if "YouTube" in inner_html and "Google Display Network" in inner_html:
                print("✅ HTML contém publishers dinâmicos")
            else:
                print("⚠️ HTML não contém publishers dinâmicos")
                
        except Exception as e:
            print(f"❌ Erro ao verificar container de publishers: {e}")
        
        # Verificar se a função renderPlanningData foi executada
        print("\n🔧 Verificando se renderPlanningData foi executada...")
        
        try:
            # Verificar se os elementos foram atualizados
            publishers_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(3) div[style*="grid-template-columns"] > div')
            print(f"📺 Publishers divs encontrados: {len(publishers_divs)}")
            
            for i, div in enumerate(publishers_divs):
                try:
                    div_text = div.text
                    print(f"   {i+1}. {div_text}")
                    
                    # Verificar se é HTML estático ou dinâmico
                    div_html = driver.execute_script("return arguments[0].outerHTML", div)
                    if "border-left:4px solid #ff6b35" in div_html:
                        print(f"      ✅ Div {i+1} parece ser dinâmico")
                    else:
                        print(f"      ⚠️ Div {i+1} parece ser estático")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao verificar div {i+1}: {e}")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar publishers divs: {e}")
        
        # Verificar se há erro na função renderPlanningData
        print("\n🔧 Verificando se há erros na função renderPlanningData...")
        
        try:
            # Tentar executar renderPlanningData manualmente
            result = driver.execute_script("""
                if (window.dashboardLoader && window.dashboardLoader.data) {
                    try {
                        window.dashboardLoader.renderPlanningData(window.dashboardLoader.data);
                        return 'success';
                    } catch (e) {
                        return 'error: ' + e.message;
                    }
                } else {
                    return 'no data available';
                }
            """)
            print(f"📋 Resultado da execução manual de renderPlanningData: {result}")
            
        except Exception as e:
            print(f"❌ Erro ao executar renderPlanningData manualmente: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_debug_planning.png")
        print("\n📸 Screenshot salvo: selenium_debug_planning.png")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    debug_planning_tab()
