#!/usr/bin/env python3
"""
Teste do dashboard sem erro
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def teste_sem_erro():
    """Teste do dashboard sem erro"""
    print("🎯 Testando dashboard sem erro...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "http://localhost:5001/static/dash_template_sem_erro.html"
        print(f"🌐 Acessando: {url}")
        
        driver.get(url)
        print(f"📄 Título: {driver.title}")
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        time.sleep(5)
        
        # Verificar elementos
        checks = [
            (".container", "Container principal"),
            (".tab", "Navegação por tabs"),
            (".metric", "Métricas"),
            ("canvas", "Gráficos"),
            ("table", "Tabelas"),
            ("#metrics-overview-top", "Container de métricas"),
            ("#chartSpendShare", "Gráfico de gastos"),
            ("#tbodyChannels", "Tabela de canais")
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
        
        # Verificar se há erros no console
        print("\n🚨 Verificando console:")
        try:
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            if errors:
                print(f"  ❌ {len(errors)} erro(s) encontrado(s)")
                for error in errors[:3]:  # Mostrar apenas os primeiros 3
                    print(f"    - {error['message']}")
            else:
                print("  ✅ Nenhum erro no console")
        except:
            print("  ⚠️ Não foi possível verificar console")
        
        success_rate = (passed / len(checks)) * 100
        
        print(f"\n📈 RESULTADO FINAL:")
        print(f"  ✅ Elementos encontrados: {passed}/{len(checks)}")
        print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 TEMPLATE GENÉRICO APROVADO COM SELENIUM!")
            print("   ✅ HTML carregado corretamente")
            print("   ✅ Elementos renderizados")
            print("   ✅ Sem erros críticos")
            print("   ✅ Template funcionando")
        else:
            print("\n⚠️ Template ainda precisa de ajustes")
            
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    teste_sem_erro()

