#!/usr/bin/env python3
"""
Debug específico para verificar acesso aos dados
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_data_access():
    """Debug específico do acesso aos dados"""
    print("🔍 DEBUG DO ACESSO AOS DADOS")
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
                        
        except Exception as e:
            print(f"❌ Erro ao verificar dados JavaScript: {e}")
        
        # Verificar se renderPlanningData foi chamada
        print("\n🔧 Verificando se renderPlanningData foi chamada...")
        
        try:
            # Verificar se a aba de planejamento foi atualizada
            planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
            driver.execute_script("arguments[0].click();", planning_tab)
            time.sleep(2)
            
            # Verificar objetivo
            objective = driver.find_element(By.CSS_SELECTOR, '#tab-planning .card p')
            objective_text = objective.text
            print(f"🎯 Objetivo atual: {objective_text[:100]}...")
            
            # Verificar se contém dados dinâmicos
            if "Microempreendedores" in objective_text and "Jovens Empreendedores" in objective_text:
                print("✅ Objetivo contém segmentação dinâmica")
            else:
                print("❌ Objetivo não contém segmentação dinâmica")
                
        except Exception as e:
            print(f"❌ Erro ao verificar objetivo: {e}")
        
        # Verificar publishers
        print("\n🔧 Verificando publishers...")
        
        try:
            publishers_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(3) div[style*="grid-template-columns"] > div')
            print(f"📺 Publishers divs encontrados: {len(publishers_divs)}")
            
            for i, div in enumerate(publishers_divs):
                try:
                    div_text = div.text
                    print(f"   {i+1}. {div_text}")
                except:
                    print(f"   {i+1}. Erro ao ler div")
                    
        except Exception as e:
            print(f"❌ Erro ao verificar publishers: {e}")
        
        # Verificar se há erro na função renderPlanningData
        print("\n🔧 Verificando se há erros na função renderPlanningData...")
        
        try:
            # Tentar executar renderPlanningData manualmente com dados
            result = driver.execute_script("""
                if (window.dashboardLoader && window.dashboardLoader.data) {
                    try {
                        console.log('Dados disponíveis:', window.dashboardLoader.data);
                        console.log('Publishers:', window.dashboardLoader.data.publishers);
                        console.log('Strategies:', window.dashboardLoader.data.strategies);
                        console.log('Contract:', window.dashboardLoader.data.contract);
                        
                        window.dashboardLoader.renderPlanningData(window.dashboardLoader.data);
                        return 'success';
                    } catch (e) {
                        console.error('Erro em renderPlanningData:', e);
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
        driver.save_screenshot("selenium_debug_data_access.png")
        print("\n📸 Screenshot salvo: selenium_debug_data_access.png")
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    debug_data_access()
