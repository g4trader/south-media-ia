#!/usr/bin/env python3
"""
Debug específico para verificar a função loadDashboardData
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_load_function():
    """Debug específico da função loadDashboardData"""
    print("🔍 DEBUG DA FUNÇÃO LOADDASHBOARDDATA")
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
        
        # Verificar se a função loadDashboardData existe
        print("\n🔧 Verificando se a função loadDashboardData existe...")
        
        try:
            function_exists = driver.execute_script("return typeof window.dashboardLoader.loadDashboardData === 'function'")
            print(f"✅ Função loadDashboardData existe: {function_exists}")
            
            if function_exists:
                # Verificar se a função foi executada
                print("\n🔧 Verificando se a função foi executada...")
                
                # Verificar se os dados estão carregados
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados carregados: {data_available}")
                
                if data_available:
                    # Verificar o tipo dos dados
                    data_type = driver.execute_script("return typeof window.dashboardLoader.data")
                    print(f"📋 Tipo dos dados: {data_type}")
                    
                    # Verificar se é undefined
                    is_undefined = driver.execute_script("return window.dashboardLoader.data === undefined")
                    print(f"📋 É undefined: {is_undefined}")
                    
                    if is_undefined:
                        print("❌ Dados são undefined - problema na função loadDashboardData")
                    else:
                        print("✅ Dados são válidos")
                        
                else:
                    print("❌ Dados não estão carregados")
                    
            else:
                print("❌ Função loadDashboardData não existe")
                
        except Exception as e:
            print(f"❌ Erro ao verificar função: {e}")
        
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
        
        # Tentar executar loadDashboardData manualmente
        print("\n🔧 Tentando executar loadDashboardData manualmente...")
        
        try:
            result = driver.execute_script("""
                try {
                    if (window.dashboardLoader && window.dashboardLoader.loadDashboardData) {
                        console.log('Executando loadDashboardData...');
                        window.dashboardLoader.loadDashboardData();
                        return 'success';
                    } else {
                        return 'function not available';
                    }
                } catch (e) {
                    console.error('Erro:', e);
                    return 'error: ' + e.message;
                }
            """)
            print(f"📋 Resultado da execução manual: {result}")
            
            # Aguardar um pouco e verificar se os dados foram carregados
            time.sleep(3)
            
            data_available = driver.execute_script("return window.dashboardLoader.data !== null")
            print(f"✅ Dados carregados após execução manual: {data_available}")
            
            if data_available:
                data_type = driver.execute_script("return typeof window.dashboardLoader.data")
                print(f"📋 Tipo dos dados após execução manual: {data_type}")
                
        except Exception as e:
            print(f"❌ Erro ao executar loadDashboardData manualmente: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_debug_load_function.png")
        print("\n📸 Screenshot salvo: selenium_debug_load_function.png")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    debug_load_function()
