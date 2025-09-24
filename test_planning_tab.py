#!/usr/bin/env python3
"""
Teste específico para verificar a aba de planejamento
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_planning_tab():
    """Teste específico da aba de planejamento"""
    print("📋 TESTE ESPECÍFICO DA ABA PLANEJAMENTO")
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
        time.sleep(8)  # Aguardar carregamento
        
        # Verificar dados JavaScript primeiro
        print("\n🔧 Verificando dados JavaScript...")
        try:
            # Verificar se os dados estão carregados
            data_available = driver.execute_script("return window.dashboardLoader.data !== null")
            print(f"✅ Dados carregados: {data_available}")
            
            if data_available:
                # Verificar estratégias
                strategies = driver.execute_script("return window.dashboardLoader.data.strategies")
                print(f"📋 Estratégias: {strategies}")
                
                # Verificar publishers
                publishers = driver.execute_script("return window.dashboardLoader.data.publishers")
                print(f"📺 Publishers: {publishers}")
                
                if publishers:
                    publishers_count = driver.execute_script("return window.dashboardLoader.data.publishers.length")
                    print(f"📺 Quantidade de publishers: {publishers_count}")
                    
                    # Listar publishers
                    for i in range(publishers_count):
                        publisher = driver.execute_script(f"return window.dashboardLoader.data.publishers[{i}]")
                        print(f"   {i+1}. {publisher}")
                        
        except Exception as e:
            print(f"❌ Erro ao verificar dados: {e}")
        
        # Navegar para aba de planejamento
        print("\n📋 Navegando para aba de planejamento...")
        
        try:
            # Tentar encontrar e clicar na aba de planejamento
            planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
            print(f"✅ Aba de planejamento encontrada: {planning_tab.text}")
            
            # Clicar na aba
            driver.execute_script("arguments[0].click();", planning_tab)
            time.sleep(2)
            
            print("✅ Clicou na aba de planejamento")
            
        except Exception as e:
            print(f"❌ Erro ao navegar para aba de planejamento: {e}")
        
        # Verificar conteúdo da aba de planejamento
        print("\n🔍 Verificando conteúdo da aba de planejamento...")
        
        try:
            planning_content = driver.find_element(By.ID, "tab-planning")
            print("✅ Conteúdo da aba de planejamento encontrado")
            
            # Verificar objetivo da campanha
            try:
                objective_text = planning_content.find_element(By.CSS_SELECTOR, "p")
                print(f"🎯 Objetivo encontrado: {objective_text.text[:100]}...")
                
                # Verificar se contém informações de segmentação
                if "Microempreendedores" in objective_text.text or "Jovens Empreendedores" in objective_text.text:
                    print("✅ Segmentação presente no objetivo")
                else:
                    print("⚠️ Segmentação não encontrada no objetivo")
                    
            except Exception as e:
                print(f"⚠️ Objetivo não encontrado: {e}")
            
            # Verificar publishers
            try:
                publishers_container = planning_content.find_element(By.CSS_SELECTOR, ".card:nth-child(4) .grid")
                print("✅ Container de publishers encontrado")
                
                publishers_divs = publishers_container.find_elements(By.CSS_SELECTOR, "> div")
                print(f"📺 Publishers visíveis: {len(publishers_divs)}")
                
                for i, publisher_div in enumerate(publishers_divs):
                    try:
                        publisher_text = publisher_div.text
                        print(f"   {i+1}. {publisher_text}")
                    except:
                        print(f"   {i+1}. Erro ao ler publisher")
                        
            except Exception as e:
                print(f"⚠️ Publishers não encontrados: {e}")
            
            # Verificar detalhes da campanha
            try:
                contract_container = planning_content.find_element(By.CSS_SELECTOR, ".card:nth-child(5) .grid")
                print("✅ Container de detalhes da campanha encontrado")
                
                contract_divs = contract_container.find_elements(By.CSS_SELECTOR, "> div")
                print(f"📊 Detalhes da campanha: {len(contract_divs)}")
                
                for i, detail_div in enumerate(contract_divs):
                    try:
                        detail_text = detail_div.text
                        print(f"   {i+1}. {detail_text}")
                    except:
                        print(f"   {i+1}. Erro ao ler detalhe")
                        
            except Exception as e:
                print(f"⚠️ Detalhes da campanha não encontrados: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar conteúdo da aba: {e}")
        
        # Screenshot da aba de planejamento
        driver.save_screenshot("selenium_planning_tab_test.png")
        print("\n📸 Screenshot da aba de planejamento salvo")
        
        print("\n✅ Teste da aba de planejamento concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_planning_tab()
