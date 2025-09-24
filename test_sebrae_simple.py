#!/usr/bin/env python3
"""
Teste simples do Dashboard SEBRAE - foco em identificar problemas
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_dashboard():
    """Teste simples do dashboard"""
    print("🚀 Teste Simples do Dashboard SEBRAE")
    print("=" * 50)
    
    # Setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Teste 1: Acessar dashboard
        print("📊 Acessando dashboard...")
        driver.get("http://localhost:5000/static/dash_sebrae_programatica_video_sync.html")
        time.sleep(5)  # Aguardar carregamento
        
        # Screenshot inicial
        driver.save_screenshot("selenium_simple_1_loaded.png")
        print("📸 Screenshot 1 salvo")
        
        # Teste 2: Verificar se a página carregou
        print("🔍 Verificando elementos da página...")
        
        # Verificar título
        try:
            title = driver.find_element(By.TAG_NAME, "title")
            print(f"📄 Título da página: {title.get_attribute('text')}")
        except:
            print("⚠️ Título não encontrado")
        
        # Verificar se há elementos h1
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            print(f"📋 Elementos H1 encontrados: {len(h1_elements)}")
            for i, h1 in enumerate(h1_elements):
                print(f"  {i+1}. {h1.text}")
        except:
            print("⚠️ Elementos H1 não encontrados")
        
        # Verificar loading screen
        try:
            loading = driver.find_element(By.ID, "loadingScreen")
            print(f"⏳ Loading screen encontrado: {loading.is_displayed()}")
        except:
            print("ℹ️ Loading screen não encontrado (pode ter desaparecido)")
        
        # Teste 3: Verificar conteúdo principal
        print("📊 Verificando conteúdo principal...")
        
        # Verificar se há divs com métricas
        metric_divs = driver.find_elements(By.CSS_SELECTOR, ".metric")
        print(f"💳 Cards de métricas encontrados: {len(metric_divs)}")
        
        # Verificar tabs
        tabs = driver.find_elements(By.CSS_SELECTOR, ".tab")
        print(f"📑 Abas encontradas: {len(tabs)}")
        for i, tab in enumerate(tabs):
            try:
                print(f"  {i+1}. {tab.text} - onclick: {tab.get_attribute('onclick')}")
            except:
                print(f"  {i+1}. Erro ao ler aba")
        
        # Teste 4: Verificar JavaScript
        print("🔧 Verificando JavaScript...")
        
        # Executar JavaScript para verificar se os dados carregaram
        try:
            result = driver.execute_script("return typeof window.dashboardLoader !== 'undefined'")
            print(f"📊 DashboardLoader disponível: {result}")
            
            if result:
                data_loaded = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"📊 Dados carregados: {data_loaded}")
                
                if data_loaded:
                    metrics = driver.execute_script("return window.dashboardLoader.data.metrics")
                    print(f"📊 Métricas disponíveis: {metrics is not None}")
                    if metrics:
                        print(f"  💰 Budget: {metrics.get('budget_contracted', 'N/A')}")
                        print(f"  🎬 VC Contratado: {metrics.get('vc_contracted', 'N/A')}")
                        print(f"  ✅ VC Entregue: {metrics.get('vc_delivered', 'N/A')}")
        except Exception as e:
            print(f"⚠️ Erro ao verificar JavaScript: {e}")
        
        # Teste 5: Verificar API
        print("📡 Verificando API...")
        try:
            driver.get("http://localhost:5000/api/sebrae/data")
            time.sleep(2)
            
            page_source = driver.page_source
            if "success" in page_source:
                print("✅ API respondendo")
                
                # Tentar extrair JSON
                if page_source.startswith('<html>'):
                    # Remover tags HTML
                    json_start = page_source.find('{')
                    json_end = page_source.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_text = page_source[json_start:json_end]
                        try:
                            data = json.loads(json_text)
                            print(f"✅ JSON válido - Success: {data.get('success', False)}")
                            print(f"📊 Source: {data.get('source', 'unknown')}")
                        except:
                            print("⚠️ JSON inválido")
                else:
                    print("✅ Resposta direta da API")
            else:
                print("❌ API não está respondendo corretamente")
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")
        
        # Screenshot final
        driver.save_screenshot("selenium_simple_2_final.png")
        print("📸 Screenshot 2 salvo")
        
        print("\n✅ Teste simples concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_dashboard()
