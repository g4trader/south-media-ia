#!/usr/bin/env python3
"""
Teste para verificar o timing do carregamento dos dados
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_data_timing():
    """Teste para verificar o timing do carregamento dos dados"""
    print("⏰ TESTE DE TIMING DO CARREGAMENTO DE DADOS")
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
        
        # Verificar dados em diferentes momentos
        for i in range(5):
            print(f"\n⏰ Verificação {i+1} - {i*2} segundos após carregamento...")
            time.sleep(2)
            
            try:
                # Verificar se os dados estão carregados
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados carregados: {data_available}")
                
                if data_available:
                    # Verificar publishers
                    publishers = driver.execute_script("return window.dashboardLoader.data.publishers")
                    if publishers:
                        print(f"📺 Publishers: {len(publishers)} itens")
                        for j, publisher in enumerate(publishers[:3]):
                            print(f"   {j+1}. {publisher}")
                    else:
                        print("❌ Publishers: null ou undefined")
                    
                    # Verificar estratégias
                    strategies = driver.execute_script("return window.dashboardLoader.data.strategies")
                    if strategies:
                        print(f"🎯 Estratégias: {list(strategies.keys())}")
                    else:
                        print("❌ Estratégias: null ou undefined")
                    
                    # Verificar contrato
                    contract = driver.execute_script("return window.dashboardLoader.data.contract")
                    if contract:
                        print(f"📋 Contrato: {list(contract.keys())}")
                    else:
                        print("❌ Contrato: null ou undefined")
                        
                else:
                    print("❌ Dados não carregados ainda")
                    
            except Exception as e:
                print(f"❌ Erro na verificação {i+1}: {e}")
        
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
        driver.save_screenshot("selenium_test_data_timing.png")
        print("\n📸 Screenshot salvo: selenium_test_data_timing.png")
        
        print("\n✅ Teste de timing concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_data_timing()
