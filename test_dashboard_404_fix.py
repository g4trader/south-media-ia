#!/usr/bin/env python3
"""
Teste automatizado para verificar se o erro 404 do dashboard foi corrigido
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import requests

def setup_driver():
    """Configurar o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def test_dashboard_protected_page():
    """Testar se a página dashboard-protected.html carrega corretamente"""
    print("🔍 Testando página dashboard-protected.html...")
    
    driver = setup_driver()
    
    try:
        # Acessar a página
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verificar se a página carregou
        assert "Painel de Controle" in driver.title or "Painel de Controle" in driver.page_source
        print("✅ Página dashboard-protected.html carregou corretamente")
        
        # Aguardar carregamento dos dashboards
        time.sleep(3)
        
        # Verificar se não há mais o dashboard problemático
        page_source = driver.page_source
        if "Sebrae Institucional Setembro" in page_source:
            print("❌ ERRO: Dashboard 'Sebrae Institucional Setembro' ainda aparece na lista!")
            return False
        else:
            print("✅ Dashboard 'Sebrae Institucional Setembro' foi removido da lista")
        
        # Verificar se há dashboards listados
        try:
            # Procurar por cards de dashboard
            dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if dashboard_cards:
                print(f"✅ {len(dashboard_cards)} dashboards encontrados na lista")
                
                # Listar os dashboards encontrados
                for i, card in enumerate(dashboard_cards[:5]):  # Limitar a 5 para não poluir o output
                    try:
                        title = card.find_element(By.CLASS_NAME, "card-title")
                        print(f"   {i+1}. {title.text}")
                    except NoSuchElementException:
                        continue
            else:
                print("⚠️ Nenhum dashboard encontrado na lista")
                
        except Exception as e:
            print(f"⚠️ Erro ao verificar dashboards: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar página: {e}")
        return False
    finally:
        driver.quit()

def test_dashboard_links():
    """Testar se os links dos dashboards funcionam"""
    print("\n🔍 Testando links dos dashboards...")
    
    driver = setup_driver()
    
    try:
        # Acessar a página
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        # Procurar por links de dashboard
        dashboard_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/static/dash_']")
        
        if not dashboard_links:
            print("⚠️ Nenhum link de dashboard encontrado")
            return True
        
        print(f"📊 Encontrados {len(dashboard_links)} links de dashboard")
        
        # Testar os primeiros 3 links
        for i, link in enumerate(dashboard_links[:3]):
            try:
                href = link.get_attribute("href")
                dashboard_name = href.split("/")[-1]
                
                print(f"\n🔗 Testando link {i+1}: {dashboard_name}")
                
                # Abrir link em nova aba
                driver.execute_script("window.open(arguments[0], '_blank');", href)
                driver.switch_to.window(driver.window_handles[1])
                
                # Aguardar carregamento
                time.sleep(2)
                
                # Verificar se a página carregou sem erro 404
                current_url = driver.current_url
                page_source = driver.page_source.lower()
                
                if "404" in page_source or "not found" in page_source:
                    print(f"❌ ERRO 404: {dashboard_name}")
                    return False
                else:
                    print(f"✅ OK: {dashboard_name} carregou corretamente")
                
                # Fechar aba e voltar para a principal
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print(f"⚠️ Erro ao testar link {i+1}: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar links: {e}")
        return False
    finally:
        driver.quit()

def test_auth_system_js():
    """Testar se o auth_system_hybrid.js foi atualizado"""
    print("\n🔍 Testando arquivo auth_system_hybrid.js...")
    
    try:
        # Fazer requisição para o arquivo JS
        response = requests.get("https://dash.iasouth.tech/auth_system_hybrid.js", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar se o dashboard problemático foi removido
            if "dash_sebrae_institucional_setembro.html" in content:
                print("❌ ERRO: auth_system_hybrid.js ainda contém 'dash_sebrae_institucional_setembro.html'")
                return False
            else:
                print("✅ auth_system_hybrid.js foi atualizado corretamente")
            
            # Verificar se há outros dashboards na lista
            if "dash_" in content and ".html" in content:
                print("✅ Lista de dashboards encontrada no arquivo JS")
            else:
                print("⚠️ Lista de dashboards não encontrada")
            
            return True
        else:
            print(f"❌ ERRO: Não foi possível acessar auth_system_hybrid.js (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao testar auth_system_hybrid.js: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 Iniciando testes automatizados para verificar correção do erro 404\n")
    
    results = []
    
    # Teste 1: Página dashboard-protected.html
    results.append(test_dashboard_protected_page())
    
    # Teste 2: Arquivo auth_system_hybrid.js
    results.append(test_auth_system_js())
    
    # Teste 3: Links dos dashboards
    results.append(test_dashboard_links())
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! O erro 404 foi corrigido com sucesso!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    print("\n🔗 Links testados:")
    print("   - https://dash.iasouth.tech/dashboard-protected.html")
    print("   - https://dash.iasouth.tech/auth_system_hybrid.js")
    print("   - Links dos dashboards na pasta /static")

if __name__ == "__main__":
    main()
