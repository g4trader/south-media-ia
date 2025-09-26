#!/usr/bin/env python3
"""
Teste rápido do template corrigido
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_corrected_template():
    """Teste rápido do template corrigido"""
    print("🔍 Testando template corrigido...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "http://localhost:5001/static/dash_template_corrigido_test.html"
        driver.get(url)
        time.sleep(3)
        
        # Verificar elementos básicos
        checks = [
            ("Título", "Dashboard" in driver.title),
            ("Container", len(driver.find_elements(By.CSS_SELECTOR, ".container")) > 0),
            ("Logo South Media", len(driver.find_elements(By.XPATH, "//div[contains(text(), 'South Media')]")) > 0),
            ("Tabs", len(driver.find_elements(By.CSS_SELECTOR, ".tab")) == 4),
            ("Métricas", len(driver.find_elements(By.CSS_SELECTOR, ".metric")) > 0),
            ("Gráficos", len(driver.find_elements(By.TAG_NAME, "canvas")) > 0)
        ]
        
        print("\n📊 Resultados:")
        passed = 0
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {name}: {'OK' if result else 'FALHOU'}")
            if result:
                passed += 1
        
        success_rate = (passed / len(checks)) * 100
        print(f"\n📈 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 TEMPLATE CORRIGIDO COM SUCESSO!")
        else:
            print("⚠️ Ainda há problemas no template")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_corrected_template()

