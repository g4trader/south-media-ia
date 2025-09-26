#!/usr/bin/env python3
"""
Teste de debug com Selenium - mais tempo de espera
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_selenium_test():
    """Teste de debug com mais tempo"""
    print("🔍 Teste de debug com Selenium...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "http://localhost:5001/static/dash_teste_selenium_final.html"
        print(f"🌐 Acessando: {url}")
        
        driver.get(url)
        print(f"📄 Título da página: {driver.title}")
        
        # Aguardar muito mais tempo
        print("⏳ Aguardando 10 segundos...")
        time.sleep(10)
        
        # Verificar HTML completo
        html_content = driver.page_source
        print(f"📊 Tamanho do HTML: {len(html_content)} caracteres")
        
        # Verificar elementos específicos
        elements = [
            (".container", "Container"),
            (".tab", "Tabs"),
            (".metric", "Métricas"),
            ("canvas", "Gráficos"),
            ("table", "Tabelas"),
            ("#metrics-overview-top", "Container de métricas"),
            ("#chartSpendShare", "Gráfico de gastos"),
            ("#tbodyChannels", "Tabela de canais")
        ]
        
        print("\n🔍 Verificando elementos:")
        for selector, name in elements:
            try:
                elements_found = driver.find_elements(By.CSS_SELECTOR, selector)
                count = len(elements_found)
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {name}: {count} elemento(s)")
            except Exception as e:
                print(f"  ❌ {name}: ERRO - {e}")
        
        # Verificar se há JavaScript carregado
        print("\n⚡ Verificando JavaScript:")
        try:
            # Verificar se Chart.js está disponível
            chart_available = driver.execute_script("return typeof Chart !== 'undefined'")
            print(f"  {'✅' if chart_available else '❌'} Chart.js: {'Disponível' if chart_available else 'Não disponível'}")
            
            # Verificar se DashboardLoader está disponível
            loader_available = driver.execute_script("return typeof DashboardLoader !== 'undefined'")
            print(f"  {'✅' if loader_available else '❌'} DashboardLoader: {'Disponível' if loader_available else 'Não disponível'}")
            
        except Exception as e:
            print(f"  ❌ Erro no JavaScript: {e}")
        
        # Verificar console por erros
        print("\n🚨 Verificando console:")
        try:
            logs = driver.get_log('browser')
            if logs:
                for log in logs:
                    if log['level'] == 'SEVERE':
                        print(f"  ❌ Erro: {log['message']}")
            else:
                print("  ✅ Nenhum erro no console")
        except:
            print("  ⚠️ Não foi possível verificar console")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_selenium_test()

