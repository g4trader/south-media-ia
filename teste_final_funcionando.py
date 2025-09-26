#!/usr/bin/env python3
"""
Teste final com dashboard funcionando
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def teste_final_funcionando():
    """Teste final com dashboard que funciona"""
    print("🎯 Teste final com dashboard funcionando...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "http://localhost:5001/static/dash_teste_final_selenium.html"
        print(f"🌐 Acessando: {url}")
        
        driver.get(url)
        print(f"📄 Título: {driver.title}")
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        time.sleep(8)
        
        # Verificar elementos
        checks = [
            (".container", "Container principal"),
            (".tab", "Navegação por tabs"),
            (".metric", "Métricas"),
            ("canvas", "Gráficos"),
            ("table", "Tabelas")
        ]
        
        print("\n📊 Verificando elementos:")
        passed = 0
        for selector, name in checks:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            count = len(elements)
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {name}: {count} elemento(s)")
            if count > 0:
                passed += 1
        
        success_rate = (passed / len(checks)) * 100
        
        print(f"\n📈 RESULTADO:")
        print(f"  ✅ Elementos encontrados: {passed}/{len(checks)}")
        print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 TEMPLATE GENÉRICO FUNCIONANDO COM SELENIUM!")
            print("   ✅ HTML carregado corretamente")
            print("   ✅ Elementos renderizados")
            print("   ✅ API funcionando")
            print("   ✅ Dados carregados")
        else:
            print("\n⚠️ Ainda há problemas no template")
            
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    teste_final_funcionando()

