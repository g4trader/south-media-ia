#!/usr/bin/env python3
"""
Teste do dashboard com Selenium
Verifica se o dashboard está funcionando corretamente no Vercel
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_dashboard():
    """Testa o dashboard no Vercel"""
    
    print("🧪 Iniciando teste do dashboard com Selenium...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    
    try:
        # Inicializar driver
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # URLs para testar
        urls = [
            "https://south-media-ia.vercel.app/",
            "https://south-media-ia.vercel.app/dash_sonho.html"
        ]
        
        for url in urls:
            print(f"\n🌐 Testando URL: {url}")
            
            # Carregar página
            driver.get(url)
            
            # Aguardar carregamento
            wait = WebDriverWait(driver, 10)
            
            # Verificar se a página carregou
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                print("✅ Página carregada com sucesso")
            except TimeoutException:
                print("❌ Timeout ao carregar página")
                continue
            
            # Verificar elementos do dashboard
            tests = [
                {
                    "name": "Título da página",
                    "selector": "title",
                    "expected": "Dashboard"
                },
                {
                    "name": "Dados CONS",
                    "selector": "script",
                    "contains": "const CONS ="
                },
                {
                    "name": "Dados PER", 
                    "selector": "script",
                    "contains": "const PER ="
                },
                {
                    "name": "Dados DAILY",
                    "selector": "script", 
                    "contains": "const DAILY ="
                },
                {
                    "name": "Gráficos Chart.js",
                    "selector": "canvas"
                }
            ]
            
            for test in tests:
                try:
                    if "contains" in test:
                        # Verificar se contém texto específico
                        scripts = driver.find_elements(By.TAG_NAME, "script")
                        found = False
                        for script in scripts:
                            if test["contains"] in script.get_attribute("innerHTML"):
                                found = True
                                break
                        if found:
                            print(f"✅ {test['name']}: Encontrado")
                        else:
                            print(f"❌ {test['name']}: Não encontrado")
                    else:
                        # Verificar elemento
                        element = driver.find_element(By.CSS_SELECTOR, test["selector"])
                        if element:
                            print(f"✅ {test['name']}: Encontrado")
                        else:
                            print(f"❌ {test['name']}: Não encontrado")
                            
                except NoSuchElementException:
                    print(f"❌ {test['name']}: Não encontrado")
                except Exception as e:
                    print(f"⚠️ {test['name']}: Erro - {e}")
            
            # Verificar se há dados
            try:
                # Procurar por dados nos scripts
                scripts = driver.find_elements(By.TAG_NAME, "script")
                has_data = False
                
                for script in scripts:
                    content = script.get_attribute("innerHTML")
                    if "const CONS =" in content and len(content) > 100:
                        has_data = True
                        break
                
                if has_data:
                    print("✅ Dashboard contém dados")
                else:
                    print("⚠️ Dashboard pode estar sem dados")
                    
            except Exception as e:
                print(f"⚠️ Erro ao verificar dados: {e}")
            
            # Capturar screenshot
            screenshot_name = f"dashboard_test_{url.split('/')[-1] or 'home'}.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 Screenshot salvo: {screenshot_name}")
            
            time.sleep(2)  # Aguardar entre testes
        
        print("\n🎉 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Navegador fechado")

if __name__ == "__main__":
    test_dashboard()
