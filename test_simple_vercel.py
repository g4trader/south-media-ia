#!/usr/bin/env python3
"""
Teste simples do sistema Vercel
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Configurar o driver do Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def test_page_content():
    """Testar conteúdo das páginas"""
    print("🔍 Testando conteúdo das páginas...")
    
    # Testar login.html
    try:
        response = requests.get("https://dash.iasouth.tech/login.html", timeout=10)
        if response.status_code == 200:
            print("✅ login.html acessível")
            if "email" in response.text.lower() and "password" in response.text.lower():
                print("✅ Campos de login encontrados no HTML")
            else:
                print("❌ Campos de login não encontrados no HTML")
                print("📄 Primeiras 500 caracteres:")
                print(response.text[:500])
        else:
            print(f"❌ login.html retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar login.html: {e}")
    
    # Testar dashboard-builder.html
    try:
        response = requests.get("https://dash.iasouth.tech/dashboard-builder.html", timeout=10)
        if response.status_code == 200:
            print("✅ dashboard-builder.html acessível")
            if "campaignName" in response.text or "nome" in response.text.lower():
                print("✅ Campos de criação encontrados no HTML")
            else:
                print("❌ Campos de criação não encontrados no HTML")
                print("📄 Primeiras 500 caracteres:")
                print(response.text[:500])
        else:
            print(f"❌ dashboard-builder.html retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard-builder.html: {e}")

def test_selenium_simple():
    """Teste simples com Selenium"""
    print("\n🤖 Testando com Selenium...")
    
    driver = None
    try:
        driver = setup_driver()
        
        # Testar login.html
        print("📄 Acessando login.html...")
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(3)
        
        print(f"📊 Título da página: {driver.title}")
        print(f"📊 URL atual: {driver.current_url}")
        
        # Verificar se há elementos de login
        try:
            email_elements = driver.find_elements(By.XPATH, "//input[@type='email' or @name='email' or @id='email']")
            password_elements = driver.find_elements(By.XPATH, "//input[@type='password' or @name='password' or @id='password']")
            
            print(f"📊 Elementos email encontrados: {len(email_elements)}")
            print(f"📊 Elementos password encontrados: {len(password_elements)}")
            
            if email_elements and password_elements:
                print("✅ Campos de login encontrados com Selenium")
            else:
                print("❌ Campos de login não encontrados com Selenium")
                
        except Exception as e:
            print(f"❌ Erro ao buscar elementos: {e}")
        
        # Testar dashboard-builder.html
        print("\n📄 Acessando dashboard-builder.html...")
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        time.sleep(3)
        
        print(f"📊 Título da página: {driver.title}")
        print(f"📊 URL atual: {driver.current_url}")
        
        # Verificar se há elementos de criação
        try:
            campaign_elements = driver.find_elements(By.XPATH, "//input[@name='campaignName' or @id='campaignName']")
            print(f"📊 Elementos campaignName encontrados: {len(campaign_elements)}")
            
            if campaign_elements:
                print("✅ Campo campaignName encontrado com Selenium")
            else:
                print("❌ Campo campaignName não encontrado com Selenium")
                
        except Exception as e:
            print(f"❌ Erro ao buscar elementos: {e}")
        
    except Exception as e:
        print(f"❌ Erro no teste Selenium: {e}")
    
    finally:
        if driver:
            driver.quit()

def main():
    """Função principal"""
    print("🚀 Teste simples do sistema Vercel")
    print("=" * 50)
    
    # Teste de conteúdo
    test_page_content()
    
    # Teste com Selenium
    test_selenium_simple()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído")

if __name__ == "__main__":
    main()
