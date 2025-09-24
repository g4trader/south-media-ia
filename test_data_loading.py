#!/usr/bin/env python3
"""
Teste específico para verificar se os dados estão sendo carregados
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_data_loading():
    """Teste específico para verificar carregamento de dados"""
    print("📊 TESTE DE CARREGAMENTO DE DADOS")
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
        time.sleep(10)  # Aguardar carregamento completo
        
        print("🔧 Verificando dados carregados...")
        
        # Verificar se o DashboardLoader está disponível
        try:
            loader_available = driver.execute_script("return typeof window.dashboardLoader !== 'undefined'")
            print(f"✅ DashboardLoader disponível: {loader_available}")
            
            if loader_available:
                # Verificar se os dados foram carregados
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados carregados: {data_available}")
                
                if data_available:
                    # Verificar estrutura dos dados
                    try:
                        data_keys = driver.execute_script("return Object.keys(window.dashboardLoader.data)")
                        print(f"📋 Chaves dos dados: {data_keys}")
                        
                        # Verificar cada seção
                        for key in ['metrics', 'contract', 'strategies', 'publishers', 'daily_data', 'per_data']:
                            try:
                                value = driver.execute_script(f"return window.dashboardLoader.data.{key}")
                                if value:
                                    if key == 'publishers' and isinstance(value, list):
                                        print(f"✅ {key}: {len(value)} itens")
                                        for i, item in enumerate(value[:3]):  # Primeiros 3
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
                                        print(f"✅ {key}: {type(value)} - {str(value)[:100]}...")
                                else:
                                    print(f"⚠️ {key}: vazio ou null")
                            except Exception as e:
                                print(f"❌ Erro ao verificar {key}: {e}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao verificar estrutura dos dados: {e}")
                else:
                    print("❌ Dados não foram carregados")
            else:
                print("❌ DashboardLoader não está disponível")
                
        except Exception as e:
            print(f"❌ Erro ao verificar DashboardLoader: {e}")
        
        # Verificar se a função renderPlanningData foi chamada
        print("\n🔧 Verificando se renderPlanningData foi executada...")
        
        try:
            # Navegar para aba de planejamento
            planning_tab = driver.find_element(By.CSS_SELECTOR, '.tab[data-tab="planning"]')
            driver.execute_script("arguments[0].click();", planning_tab)
            time.sleep(3)
            
            # Verificar se os elementos foram atualizados
            try:
                # Verificar objetivo
                objective = driver.find_element(By.CSS_SELECTOR, '#tab-planning .card p')
                print(f"🎯 Objetivo atualizado: {objective.text[:100]}...")
                
                # Verificar se contém dados dinâmicos
                if "Microempreendedores" in objective.text and "Jovens Empreendedores" in objective.text:
                    print("✅ Objetivo contém segmentação dinâmica")
                else:
                    print("⚠️ Objetivo não contém segmentação dinâmica")
                    
            except Exception as e:
                print(f"⚠️ Erro ao verificar objetivo: {e}")
            
            # Verificar publishers
            try:
                publishers_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(3) div[style*="grid-template-columns"] > div')
                print(f"📺 Publishers encontrados: {len(publishers_divs)}")
                
                for i, publisher_div in enumerate(publishers_divs[:3]):
                    try:
                        publisher_text = publisher_div.text
                        print(f"   {i+1}. {publisher_text}")
                    except:
                        print(f"   {i+1}. Erro ao ler publisher")
                        
            except Exception as e:
                print(f"⚠️ Erro ao verificar publishers: {e}")
            
            # Verificar detalhes da campanha
            try:
                contract_divs = driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(4) div[style*="grid-template-columns"] > div')
                print(f"📊 Detalhes da campanha: {len(contract_divs)}")
                
                for i, detail_div in enumerate(contract_divs):
                    try:
                        detail_text = detail_div.text
                        print(f"   {i+1}. {detail_text}")
                    except:
                        print(f"   {i+1}. Erro ao ler detalhe")
                        
            except Exception as e:
                print(f"⚠️ Erro ao verificar detalhes da campanha: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar aba de planejamento: {e}")
        
        # Screenshot
        driver.save_screenshot("selenium_data_loading_test.png")
        print("\n📸 Screenshot salvo: selenium_data_loading_test.png")
        
        print("\n✅ Teste de carregamento de dados concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_data_loading()
