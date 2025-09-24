#!/usr/bin/env python3
"""
Teste direto no navegador - sem headless para ver o que está acontecendo
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_browser_visible():
    """Teste com navegador visível para debug"""
    print("🚀 TESTE DIRETO NO NAVEGADOR")
    print("=" * 50)
    
    # Setup - SEM headless para ver o que está acontecendo
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # COMENTADO para ver o navegador
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        print("📊 Acessando dashboard...")
        driver.get("http://localhost:5000/static/dash_sebrae_programatica_video_sync.html")
        
        print("⏳ Aguardando 10 segundos para carregamento...")
        time.sleep(10)
        
        print("🔍 Verificando elementos...")
        
        # Verificar se há loading screen
        try:
            loading = driver.find_element(By.ID, "loadingScreen")
            print(f"⏳ Loading screen visível: {loading.is_displayed()}")
        except:
            print("ℹ️ Loading screen não encontrado")
        
        # Verificar H1
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1")
            print(f"📄 H1 encontrado: '{h1.text}'")
        except:
            print("❌ H1 não encontrado")
        
        # Verificar cards de métricas
        try:
            metrics = driver.find_elements(By.CSS_SELECTOR, ".metric")
            print(f"💳 Cards de métricas: {len(metrics)}")
            
            # Verificar se os cards têm conteúdo
            for i, metric in enumerate(metrics[:4]):
                try:
                    label = metric.find_element(By.CSS_SELECTOR, ".label")
                    value = metric.find_element(By.CSS_SELECTOR, ".value")
                    print(f"   {i+1}. {label.text}: {value.text}")
                except:
                    print(f"   {i+1}. Erro ao ler métrica")
        except Exception as e:
            print(f"❌ Erro ao verificar métricas: {e}")
        
        # Verificar JavaScript
        try:
            loader_available = driver.execute_script("return typeof window.dashboardLoader !== 'undefined'")
            print(f"🔧 DashboardLoader disponível: {loader_available}")
            
            if loader_available:
                data_available = driver.execute_script("return window.dashboardLoader.data !== null")
                print(f"📊 Dados disponíveis: {data_available}")
        except Exception as e:
            print(f"❌ Erro no JavaScript: {e}")
        
        print("\n⏳ Aguardando mais 5 segundos...")
        time.sleep(5)
        
        # Screenshot
        driver.save_screenshot("selenium_visible_test.png")
        print("📸 Screenshot salvo: selenium_visible_test.png")
        
        print("\n✅ Teste concluído! Verifique o screenshot.")
        print("🔍 O navegador deve estar visível para inspeção manual.")
        
        # Aguardar input do usuário para fechar
        input("Pressione Enter para fechar o navegador...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔧 Navegador fechado")

if __name__ == "__main__":
    test_browser_visible()
