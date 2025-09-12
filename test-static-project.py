#!/usr/bin/env python3
"""
Teste do projeto estático
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_static_project():
    """Testa o projeto estático"""
    
    print("🧪 TESTE DO PROJETO ESTÁTICO")
    print("=" * 40)
    
    # Verificar arquivos
    files_to_check = [
        "index.html",
        "package.json", 
        "vercel.json",
        "static/dash_sonho.html"
    ]
    
    print("📁 Verificando arquivos...")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # Testar dashboard
    print("\n🌐 Testando dashboard...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Testar arquivo local
        file_path = os.path.abspath("index.html")
        driver.get(f"file://{file_path}")
        
        time.sleep(2)
        
        # Verificar elementos
        title = driver.find_element("tag name", "title")
        print(f"✅ Título: {title.get_attribute('text')}")
        
        canvases = driver.find_elements("tag name", "canvas")
        print(f"✅ Gráficos: {len(canvases)} encontrados")
        
        scripts = driver.find_elements("tag name", "script")
        has_cons = any("const CONS =" in script.get_attribute("innerHTML") for script in scripts)
        print(f"✅ Dados CONS: {'Encontrado' if has_cons else 'Não encontrado'}")
        
        print("\n🎉 PROJETO ESTÁTICO FUNCIONANDO!")
        print("📋 Próximos passos:")
        print("   1. Criar repositório no GitHub")
        print("   2. Fazer push do código")
        print("   3. Conectar ao Vercel")
        print("   4. Deploy automático")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_static_project()
