#!/usr/bin/env python3
"""
Teste específico para verificar a função renderPlanningData
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_planning_function():
    """Teste específico da função renderPlanningData"""
    print("🔧 TESTE DA FUNÇÃO RENDERPLANNINGDATA")
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
        
        # Verificar se a função renderPlanningData existe
        print("\n🔧 Verificando se a função renderPlanningData existe...")
        
        try:
            function_exists = driver.execute_script("return typeof window.dashboardLoader.renderPlanningData === 'function'")
            print(f"✅ Função renderPlanningData existe: {function_exists}")
            
            if function_exists:
                # Verificar se os dados estão disponíveis
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados disponíveis: {data_available}")
                
                if data_available:
                    # Verificar se renderPlanningData foi chamada
                    print("\n🔧 Verificando se renderPlanningData foi chamada...")
                    
                    # Navegar para aba de planejamento
                    planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
                    driver.execute_script("arguments[0].click();", planning_tab)
                    time.sleep(2)
                    
                    # Verificar se os elementos foram atualizados
                    try:
                        # Verificar objetivo
                        objective = driver.find_element(By.CSS_SELECTOR, '#tab-planning .card p')
                        objective_text = objective.text
                        print(f"🎯 Objetivo: {objective_text[:100]}...")
                        
                        # Verificar se contém dados dinâmicos
                        if "Microempreendedores" in objective_text and "Jovens Empreendedores" in objective_text:
                            print("✅ Objetivo contém segmentação dinâmica")
                        else:
                            print("❌ Objetivo não contém segmentação dinâmica")
                            
                    except Exception as e:
                        print(f"❌ Erro ao verificar objetivo: {e}")
                    
                    # Verificar publishers
                    try:
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
                        print(f"❌ Erro ao verificar publishers: {e}")
                    
                    # Verificar detalhes da campanha
                    try:
                        contract_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(4) div[style*="grid-template-columns"] > div')
                        print(f"📊 Detalhes da campanha: {len(contract_divs)}")
                        
                        if len(contract_divs) >= 4:
                            print("✅ Detalhes da campanha carregados corretamente")
                        else:
                            print("❌ Detalhes da campanha incompletos")
                            
                    except Exception as e:
                        print(f"❌ Erro ao verificar detalhes da campanha: {e}")
                    
                    # Tentar executar renderPlanningData manualmente
                    print("\n🔧 Tentando executar renderPlanningData manualmente...")
                    
                    try:
                        result = driver.execute_script("""
                            try {
                                if (window.dashboardLoader && window.dashboardLoader.data) {
                                    console.log('Executando renderPlanningData...');
                                    window.dashboardLoader.renderPlanningData(window.dashboardLoader.data);
                                    return 'success';
                                } else {
                                    return 'no data available';
                                }
                            } catch (e) {
                                console.error('Erro:', e);
                                return 'error: ' + e.message;
                            }
                        """)
                        print(f"📋 Resultado da execução manual: {result}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao executar renderPlanningData manualmente: {e}")
                        
                else:
                    print("❌ Dados não estão disponíveis")
            else:
                print("❌ Função renderPlanningData não existe")
                
        except Exception as e:
            print(f"❌ Erro ao verificar função: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_test_planning_function.png")
        print("\n📸 Screenshot salvo: selenium_test_planning_function.png")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_planning_function()
