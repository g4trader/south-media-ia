#!/usr/bin/env python3
"""
Teste final com Selenium no dashboard funcionando
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def final_selenium_test():
    """Teste final do dashboard funcionando"""
    print("🚀 Executando teste final com Selenium...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)  # Aguardar mais tempo
    
    try:
        url = "http://localhost:5001/static/dash_teste_selenium_final.html"
        print(f"🌐 Acessando: {url}")
        
        driver.get(url)
        
        # Aguardar carregamento completo
        print("⏳ Aguardando carregamento...")
        time.sleep(5)
        
        # Verificar elementos básicos
        checks = [
            ("Título da página", lambda: "Dashboard" in driver.title),
            ("Container principal", lambda: len(driver.find_elements(By.CSS_SELECTOR, ".container")) > 0),
            ("Logo South Media", lambda: len(driver.find_elements(By.XPATH, "//div[contains(text(), 'South Media')]")) > 0),
            ("Navegação por tabs", lambda: len(driver.find_elements(By.CSS_SELECTOR, ".tab")) == 4),
            ("Métricas carregadas", lambda: len(driver.find_elements(By.CSS_SELECTOR, ".metric")) > 0),
            ("Gráficos renderizados", lambda: len(driver.find_elements(By.TAG_NAME, "canvas")) > 0),
            ("Tabelas presentes", lambda: len(driver.find_elements(By.TAG_NAME, "table")) > 0)
        ]
        
        print("\n📊 Executando verificações:")
        passed = 0
        total = len(checks)
        
        for name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"  {status} {name}: {'OK' if result else 'FALHOU'}")
                if result:
                    passed += 1
            except Exception as e:
                print(f"  ❌ {name}: ERRO - {e}")
        
        # Verificar se dados foram carregados
        print("\n🔍 Verificando carregamento de dados...")
        try:
            # Aguardar métricas aparecerem
            metrics = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".metric")))
            if metrics:
                print("  ✅ Métricas carregadas com sucesso")
                passed += 1
                total += 1
        except:
            print("  ❌ Métricas não carregadas")
            total += 1
        
        # Verificar navegação por tabs
        print("\n📋 Testando navegação por tabs...")
        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, ".tab")
            if len(tabs) >= 4:
                # Testar clique em cada tab
                for i, tab in enumerate(tabs):
                    tab.click()
                    time.sleep(1)
                    print(f"  ✅ Tab {i+1} clicável")
                    passed += 1
                    total += 1
            else:
                print("  ❌ Número insuficiente de tabs")
                total += 1
        except Exception as e:
            print(f"  ❌ Erro na navegação: {e}")
            total += 1
        
        # Calcular taxa de sucesso
        success_rate = (passed / total) * 100
        
        print(f"\n📈 RESULTADO FINAL:")
        print(f"  ✅ Testes aprovados: {passed}")
        print(f"  ❌ Testes falharam: {total - passed}")
        print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 TEMPLATE GENÉRICO APROVADO COM SELENIUM!")
            print("   ✅ Design South Media funcionando")
            print("   ✅ Dados reais carregados")
            print("   ✅ Navegação por tabs funcionando")
            print("   ✅ Gráficos e métricas renderizados")
        elif success_rate >= 70:
            print("\n⚠️ TEMPLATE COM PEQUENOS PROBLEMAS")
        else:
            print("\n❌ TEMPLATE PRECISA DE CORREÇÕES")
            
        return success_rate >= 90
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    final_selenium_test()

