#!/usr/bin/env python3
"""
Teste para verificar se o erro JavaScript foi corrigido
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_error_fix():
    """Teste para verificar se o erro foi corrigido"""
    print("🔧 TESTE DE CORREÇÃO DE ERRO JAVASCRIPT")
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
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        time.sleep(10)
        
        # Verificar se há erros JavaScript
        print("🔍 Verificando erros JavaScript...")
        
        # Verificar se o DashboardLoader está funcionando
        try:
            loader_available = driver.execute_script("return typeof window.dashboardLoader !== 'undefined'")
            print(f"✅ DashboardLoader disponível: {loader_available}")
            
            if loader_available:
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"✅ Dados carregados: {data_available}")
                
                if data_available:
                    # Tentar acessar métricas sem erro
                    try:
                        metrics = driver.execute_script("return window.dashboardLoader.data.metrics")
                        print(f"✅ Métricas acessíveis: {metrics is not None}")
                        
                        if metrics:
                            print(f"💰 Budget: {metrics.get('budget_contracted', 'N/A')}")
                            print(f"🎬 VC Contratado: {metrics.get('vc_contracted', 'N/A')}")
                            print(f"✅ VC Entregue: {metrics.get('vc_delivered', 'N/A')}")
                    except Exception as e:
                        print(f"❌ Erro ao acessar métricas: {e}")
                    
                    # Verificar dados de contrato
                    try:
                        contract = driver.execute_script("return window.dashboardLoader.data.contract")
                        print(f"📋 Dados de contrato: {'✅' if contract else '❌'}")
                    except Exception as e:
                        print(f"❌ Erro ao acessar contrato: {e}")
        except Exception as e:
            print(f"❌ Erro no DashboardLoader: {e}")
        
        # Verificar se há elementos visíveis
        print("\n🔍 Verificando elementos visíveis...")
        
        # Verificar métricas
        try:
            metrics_elements = driver.find_elements(By.CSS_SELECTOR, ".metric")
            print(f"💳 Cards de métricas visíveis: {len(metrics_elements)}")
            
            # Verificar se os cards têm conteúdo
            overview_metrics = driver.find_elements(By.CSS_SELECTOR, "#metrics-overview-top .metric")
            print(f"📊 Cards overview: {len(overview_metrics)}")
            
            for i, metric in enumerate(overview_metrics[:4]):
                try:
                    label = metric.find_element(By.CSS_SELECTOR, ".label").text
                    value = metric.find_element(By.CSS_SELECTOR, ".value").text
                    if label and value:
                        print(f"   ✅ {label}: {value}")
                    else:
                        print(f"   ⚠️ Card {i+1}: Vazio")
                except:
                    print(f"   ❌ Erro ao ler card {i+1}")
        except Exception as e:
            print(f"❌ Erro ao verificar métricas: {e}")
        
        # Verificar se há loading screen
        try:
            loading = driver.find_element(By.ID, "loadingScreen")
            print(f"⏳ Loading screen visível: {loading.is_displayed()}")
        except:
            print("ℹ️ Loading screen não encontrado (pode ter desaparecido)")
        
        # Verificar se há dashboard content
        try:
            dashboard_content = driver.find_element(By.ID, "dashboardContent")
            print(f"📊 Dashboard content visível: {dashboard_content.is_displayed()}")
        except:
            print("❌ Dashboard content não encontrado")
        
        # Screenshot
        driver.save_screenshot("selenium_error_fix_test.png")
        print("\n📸 Screenshot salvo: selenium_error_fix_test.png")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Driver finalizado")

if __name__ == "__main__":
    test_error_fix()
