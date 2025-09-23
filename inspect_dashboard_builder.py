#!/usr/bin/env python3
"""
Script para inspecionar a estrutura da página dashboard-builder.html
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    """Configurar o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def inspect_page():
    """Inspecionar a página dashboard-builder.html"""
    print("🔍 Inspecionando página dashboard-builder.html...")
    
    driver = setup_driver()
    
    try:
        # Acessar a página
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        print("📄 Conteúdo da página:")
        print(f"Título: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Procurar por elementos de formulário
        print("\n🔍 Procurando elementos de formulário:")
        
        # Campos de input
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Inputs encontrados ({len(inputs)}):")
        for i, input_elem in enumerate(inputs):
            input_id = input_elem.get_attribute("id")
            input_name = input_elem.get_attribute("name")
            input_type = input_elem.get_attribute("type")
            input_class = input_elem.get_attribute("class")
            print(f"  {i+1}. ID: {input_id}, Name: {input_name}, Type: {input_type}, Class: {input_class}")
        
        # Textareas
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"\n📝 Textareas encontrados ({len(textareas)}):")
        for i, textarea in enumerate(textareas):
            textarea_id = textarea.get_attribute("id")
            textarea_name = textarea.get_attribute("name")
            textarea_class = textarea.get_attribute("class")
            print(f"  {i+1}. ID: {textarea_id}, Name: {textarea_name}, Class: {textarea_class}")
        
        # Botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Botões encontrados ({len(buttons)}):")
        for i, button in enumerate(buttons):
            button_id = button.get_attribute("id")
            button_class = button.get_attribute("class")
            button_text = button.text.strip()
            button_onclick = button.get_attribute("onclick")
            print(f"  {i+1}. ID: {button_id}, Class: {button_class}, Text: '{button_text}', OnClick: {button_onclick}")
        
        # Selects
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"\n📋 Selects encontrados ({len(selects)}):")
        for i, select in enumerate(selects):
            select_id = select.get_attribute("id")
            select_name = select.get_attribute("name")
            select_class = select.get_attribute("class")
            print(f"  {i+1}. ID: {select_id}, Name: {select_name}, Class: {select_class}")
        
        # Verificar se há modal ou elementos ocultos
        print(f"\n🔍 Verificando elementos ocultos:")
        hidden_elements = driver.find_elements(By.CSS_SELECTOR, "[style*='display: none'], [style*='display:none'], .hidden, .d-none")
        print(f"  Elementos ocultos encontrados: {len(hidden_elements)}")
        
        # Verificar se há modal
        modals = driver.find_elements(By.CSS_SELECTOR, ".modal, [role='dialog'], .popup")
        print(f"  Modais encontrados: {len(modals)}")
        
        # Salvar screenshot para análise
        driver.save_screenshot("dashboard_builder_inspection.png")
        print("📸 Screenshot salvo como 'dashboard_builder_inspection.png'")
        
        # Salvar HTML da página
        with open("dashboard_builder_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML da página salvo como 'dashboard_builder_page.html'")
        
    except Exception as e:
        print(f"❌ Erro na inspeção: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_page()
