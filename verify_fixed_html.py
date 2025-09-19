#!/usr/bin/env python3
"""
Verificar se o HTML corrigido está exibindo os dados corretos
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def verify_fixed_html():
    """Verificar HTML corrigido"""
    
    print("🔍 VERIFICANDO HTML CORRIGIDO COM SELENIUM")
    print("=" * 70)
    
    # Configurar Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Inicializar o driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Caminho para o arquivo HTML corrigido
        html_file = "static/dash_semana_do_pescado_FIXED_20250916_115815.html"
        file_path = os.path.abspath(html_file)
        file_url = f"file://{file_path}"
        
        print(f"📁 Carregando arquivo: {file_url}")
        
        # Carregar a página
        driver.get(file_url)
        
        # Aguardar a página carregar
        time.sleep(3)
        
        print(f"\n📊 VERIFICANDO QUARTIS CORRIGIDOS:")
        print("=" * 50)
        
        # Verificar os percentuais corretos
        expected_percentages = ["91,36%", "76,40%", "59,51%", "56,19%"]
        expected_values = ["641.925", "536.869", "418.194", "394.819"]
        
        print(f"🔍 Procurando percentuais corretos:")
        for expected in expected_percentages:
            try:
                element = driver.find_element(By.XPATH, f"//text[contains(text(), '{expected}')]")
                print(f"   ✅ Encontrado: {expected}")
            except:
                print(f"   ❌ Não encontrado: {expected}")
        
        print(f"\n🔍 Procurando valores corretos:")
        for expected in expected_values:
            try:
                element = driver.find_element(By.XPATH, f"//text[contains(text(), '{expected}')]")
                print(f"   ✅ Encontrado: {expected}")
            except:
                print(f"   ❌ Não encontrado: {expected}")
        
        # Verificar se os percentuais antigos ainda estão lá
        old_percentages = ["162,59%", "135,98%", "105,92%", "100,00%"]
        print(f"\n🔍 Verificando se percentuais antigos foram removidos:")
        for old in old_percentages:
            try:
                element = driver.find_element(By.XPATH, f"//text[contains(text(), '{old}')]")
                print(f"   ❌ AINDA ENCONTRADO (antigo): {old}")
            except:
                print(f"   ✅ Removido (antigo): {old}")
        
        # Encontrar todos os elementos de texto para ver o que está sendo exibido
        try:
            text_elements = driver.find_elements(By.TAG_NAME, "text")
            print(f"\n📝 Todos os elementos de texto encontrados:")
            for i, element in enumerate(text_elements):
                text_content = element.text.strip()
                if text_content and ('%' in text_content or text_content.replace('.', '').replace(',', '').isdigit()):
                    print(f"   Elemento {i+1}: '{text_content}'")
        except Exception as e:
            print(f"❌ Erro ao verificar elementos de texto: {e}")
        
        # Capturar screenshot
        try:
            screenshot_path = "selenium_verified_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Screenshot salvo: {screenshot_path}")
        except:
            print(f"\n❌ Não foi possível capturar screenshot")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar Selenium: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    verify_fixed_html()


