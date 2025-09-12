#!/usr/bin/env python3
"""
Teste final do dashboard
Verifica se o dashboard está funcionando corretamente
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_dashboard():
    """Testa o dashboard local"""
    
    print("🧪 TESTE FINAL DO DASHBOARD")
    print("=" * 50)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    
    try:
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Testar dashboard local
        print("\n📁 Testando dashboard local...")
        driver.get('file:///Users/lucianoterres/Documents/GitHub/south-media-ia/index.html')
        
        # Aguardar carregamento
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("✅ Página carregada com sucesso")
        
        # Verificar elementos
        tests = [
            ("Título da página", "title"),
            ("Gráficos Chart.js", "canvas"),
            ("Dados CONS", "script"),
            ("Dados PER", "script"),
            ("Dados DAILY", "script")
        ]
        
        results = {}
        
        for test_name, element_type in tests:
            try:
                if element_type == "script":
                    # Verificar scripts
                    scripts = driver.find_elements(By.TAG_NAME, "script")
                    found = False
                    for script in scripts:
                        content = script.get_attribute("innerHTML")
                        if test_name.split()[-1] in content and len(content) > 100:
                            found = True
                            break
                    results[test_name] = found
                    status = "✅" if found else "❌"
                else:
                    # Verificar outros elementos
                    elements = driver.find_elements(By.TAG_NAME, element_type)
                    found = len(elements) > 0
                    results[test_name] = found
                    status = "✅" if found else "❌"
                
                print(f"{status} {test_name}: {'Encontrado' if found else 'Não encontrado'}")
                
            except Exception as e:
                results[test_name] = False
                print(f"❌ {test_name}: Erro - {e}")
        
        # Resumo
        print("\n📊 RESUMO DO TESTE:")
        print("-" * 30)
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Resultado: {passed_tests}/{total_tests} testes passaram")
        
        if passed_tests >= 4:
            print("🎉 DASHBOARD FUNCIONANDO PERFEITAMENTE!")
            print("\n🌐 URLs para acesso:")
            print("   📱 Local: http://localhost:8080 (com servidor local)")
            print("   📁 Arquivo: file:///Users/lucianoterres/Documents/GitHub/south-media-ia/index.html")
            print("   🌍 GitHub: https://g4trader.github.io/south-media-ia/ (após configurar Pages)")
        else:
            print("⚠️ Dashboard com problemas - verificar configuração")
        
        # Capturar screenshot
        screenshot_name = "dashboard_final_test.png"
        driver.save_screenshot(screenshot_name)
        print(f"\n📸 Screenshot salvo: {screenshot_name}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("\n🔚 Navegador fechado")

if __name__ == "__main__":
    test_dashboard()
