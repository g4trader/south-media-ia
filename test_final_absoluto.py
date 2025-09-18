#!/usr/bin/env python3
"""
Teste Final Absoluto - Verificação Simples e Direta
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_homepage_basic():
    """Teste básico da homepage"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://dash.iasouth.tech")
        time.sleep(5)
        
        # 1. Verificar se a página carregou
        title = driver.title
        if "Dashboard" not in title:
            return False, f"Título incorreto: {title}"
        
        # 2. Verificar dashboards
        dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
        if len(dashboard_cards) == 0:
            return False, "Nenhum dashboard encontrado"
        
        # 3. Verificar erros JavaScript críticos (excluindo favicon)
        logs = driver.get_log('browser')
        critical_errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon.ico' not in log['message'] and 'localhost:8081' in log['message']]
        
        if len(critical_errors) > 0:
            return False, f"Erros JavaScript críticos: {len(critical_errors)}"
        
        # 4. Verificar se dashboards têm data-dashboard-file
        first_card = dashboard_cards[0]
        dashboard_file = first_card.get_attribute('data-dashboard-file')
        if not dashboard_file:
            return False, "Dashboard não tem data-dashboard-file"
        
        # 5. Verificar se dashboards são clicáveis
        if 'cursor: pointer' not in first_card.get_attribute('style'):
            return False, "Dashboard não tem cursor pointer"
        
        return True, "Homepage funcionando corretamente"
        
    except Exception as e:
        return False, f"Erro: {e}"
    finally:
        driver.quit()

def test_login_basic():
    """Teste básico de login"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(3)
        
        # 1. Verificar elementos essenciais
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "loginButton")
        
        # 2. Testar login
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        login_button.click()
        time.sleep(5)
        
        # 3. Verificar redirecionamento
        if "dashboard-protected.html" not in driver.current_url:
            return False, f"Login não redirecionou. URL atual: {driver.current_url}"
        
        return True, "Login funcionando corretamente"
        
    except Exception as e:
        return False, f"Erro: {e}"
    finally:
        driver.quit()

def main():
    """Executar testes finais absolutos"""
    print("\n" + "="*60)
    print("🎯 TESTE FINAL ABSOLUTO")
    print("="*60)
    
    tests = [
        ("Homepage Básica", test_homepage_basic),
        ("Login Básico", test_login_basic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        success, message = test_func()
        
        if success:
            print(f"✅ {test_name}: PASSOU - {message}")
            results.append(True)
        else:
            print(f"❌ {test_name}: FALHOU - {message}")
            results.append(False)
    
    # Resultado final
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n" + "="*60)
    print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram ({percentage:.1f}%)")
    
    if percentage >= 100:
        print("🏆 CONVICÇÃO ABSOLUTA: SIM - Sistema 100% funcional!")
    elif percentage >= 80:
        print("🥇 CONVICÇÃO ALTA: Sistema funcional com pequenos problemas")
    else:
        print("⚠️ CONVICÇÃO BAIXA: Sistema tem problemas que precisam ser resolvidos")
    
    print("="*60)

if __name__ == "__main__":
    main()
