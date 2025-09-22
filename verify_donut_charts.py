#!/usr/bin/env python3
"""
Verificar se os gráficos de donut estão corretos
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def verify_donut_charts():
    """Verificar gráficos de donut"""
    
    print("🔍 VERIFICANDO GRÁFICOS DE DONUT COM SELENIUM")
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
        html_file = "static/dash_semana_do_pescado_DONUTS_FIXED_20250916_121759.html"
        file_path = os.path.abspath(html_file)
        file_url = f"file://{file_path}"
        
        print(f"📁 Carregando arquivo: {file_url}")
        
        # Carregar a página
        driver.get(file_url)
        
        # Aguardar a página carregar
        time.sleep(3)
        
        print(f"\n📊 VERIFICANDO ELEMENTOS DOS DONUTS:")
        print("=" * 50)
        
        # Verificar os elementos de círculo (donut charts)
        circle_elements = driver.find_elements(By.TAG_NAME, "circle")
        print(f"🔵 Circle Elements encontrados: {len(circle_elements)}")
        
        # Verificar stroke-dashoffset dos círculos
        expected_offsets = ["24.4", "66.7", "114.5", "123.9"]
        print(f"\n🔍 Verificando stroke-dashoffset:")
        
        for i, circle in enumerate(circle_elements):
            try:
                # Verificar se é um círculo com stroke-dashoffset
                dashoffset = circle.get_attribute("stroke-dashoffset")
                if dashoffset:
                    print(f"   Círculo {i+1}: stroke-dashoffset = {dashoffset}")
            except:
                pass
        
        # Verificar se os percentuais corretos estão sendo exibidos
        expected_percentages = ["91,36%", "76,40%", "59,51%", "56,19%"]
        print(f"\n🔍 Verificando percentuais exibidos:")
        
        text_elements = driver.find_elements(By.TAG_NAME, "text")
        for i, element in enumerate(text_elements):
            text_content = element.text.strip()
            if text_content and '%' in text_content:
                print(f"   Texto {i+1}: '{text_content}'")
        
        # Verificar se há elementos SVG
        svg_elements = driver.find_elements(By.TAG_NAME, "svg")
        print(f"\n📊 SVG Elements encontrados: {len(svg_elements)}")
        
        # Capturar screenshot
        try:
            screenshot_path = "selenium_donuts_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Screenshot salvo: {screenshot_path}")
        except:
            print(f"\n❌ Não foi possível capturar screenshot")
        
        # Verificar o HTML source para confirmar os valores
        print(f"\n🔍 Verificando HTML source:")
        page_source = driver.page_source
        
        # Procurar por stroke-dashoffset no HTML
        import re
        dashoffsets_found = re.findall(r'stroke-dashoffset="([^"]+)"', page_source)
        print(f"   stroke-dashoffset encontrados: {dashoffsets_found}")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar Selenium: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    verify_donut_charts()
