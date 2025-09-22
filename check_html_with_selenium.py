#!/usr/bin/env python3
"""
Verificar o HTML com Selenium para ver o que está sendo exibido
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def check_html_with_selenium():
    """Verificar o HTML com Selenium"""
    
    print("🔍 VERIFICANDO HTML COM SELENIUM")
    print("=" * 70)
    
    # Configurar Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Inicializar o driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Caminho para o arquivo HTML
        html_file = "static/dash_semana_do_pescado_FINAL_COMPLETE_20250916_115523.html"
        file_path = os.path.abspath(html_file)
        file_url = f"file://{file_path}"
        
        print(f"📁 Carregando arquivo: {file_url}")
        
        # Carregar a página
        driver.get(file_url)
        
        # Aguardar a página carregar
        time.sleep(3)
        
        print(f"\n📊 VERIFICANDO ELEMENTOS DOS QUARTIS:")
        print("=" * 50)
        
        # Verificar os elementos dos quartis
        quartis_selectors = [
            "//text[contains(@fill, 'white') and contains(@font-weight, 'bold')]"
        ]
        
        # Procurar por elementos de texto que contenham percentuais
        try:
            # Aguardar elementos carregarem
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "text"))
            )
            
            # Encontrar todos os elementos de texto
            text_elements = driver.find_elements(By.TAG_NAME, "text")
            
            print(f"📝 Encontrados {len(text_elements)} elementos de texto")
            
            # Procurar por percentuais nos quartis
            quartis_found = []
            for i, element in enumerate(text_elements):
                text_content = element.text.strip()
                if text_content and ('%' in text_content or text_content.replace('.', '').replace(',', '').isdigit()):
                    print(f"   Elemento {i+1}: '{text_content}'")
                    if '%' in text_content:
                        quartis_found.append(text_content)
            
            print(f"\n📊 PERCENTUAIS ENCONTRADOS NOS QUARTIS:")
            for i, percent in enumerate(quartis_found):
                print(f"   Quartil {i+1}: {percent}")
            
            # Verificar especificamente os quartis
            print(f"\n🔍 VERIFICANDO QUARTIS ESPECÍFICOS:")
            
            # Procurar por elementos que contenham os valores esperados
            expected_values = ["91,36%", "76,40%", "59,51%", "56,19%"]
            expected_numbers = ["641.925", "536.869", "418.194", "394.819"]
            
            for expected in expected_values + expected_numbers:
                try:
                    element = driver.find_element(By.XPATH, f"//text[contains(text(), '{expected}')]")
                    print(f"   ✅ Encontrado: {expected}")
                except:
                    print(f"   ❌ Não encontrado: {expected}")
            
            # Verificar se há elementos SVG (gráficos)
            svg_elements = driver.find_elements(By.TAG_NAME, "svg")
            print(f"\n📊 SVG Elements encontrados: {len(svg_elements)}")
            
            # Verificar se há elementos de círculo (donut charts)
            circle_elements = driver.find_elements(By.TAG_NAME, "circle")
            print(f"🔵 Circle Elements encontrados: {len(circle_elements)}")
            
            # Verificar se há elementos de path (gráficos)
            path_elements = driver.find_elements(By.TAG_NAME, "path")
            print(f"📈 Path Elements encontrados: {len(path_elements)}")
            
        except Exception as e:
            print(f"❌ Erro ao verificar elementos: {e}")
        
        # Verificar o título da página
        try:
            title = driver.title
            print(f"\n📄 Título da página: {title}")
        except:
            print(f"\n❌ Não foi possível obter o título")
        
        # Verificar se há erros no console
        try:
            logs = driver.get_log('browser')
            if logs:
                print(f"\n⚠️  Logs do navegador:")
                for log in logs:
                    print(f"   {log['level']}: {log['message']}")
            else:
                print(f"\n✅ Nenhum erro no console do navegador")
        except:
            print(f"\n❌ Não foi possível verificar logs do navegador")
        
        # Capturar screenshot para debug
        try:
            screenshot_path = "selenium_debug_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Screenshot salvo: {screenshot_path}")
        except:
            print(f"\n❌ Não foi possível capturar screenshot")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar Selenium: {e}")
        print("💡 Certifique-se de que o ChromeDriver está instalado")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    check_html_with_selenium()



