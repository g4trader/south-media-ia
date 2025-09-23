#!/usr/bin/env python3
"""
Teste específico para debugar o problema das datas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def setup_driver():
    """Configurar o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    return driver

def test_date_debug():
    """Testar especificamente o problema das datas"""
    print("🗓️ Testando problema das datas...")
    
    driver = setup_driver()
    
    try:
        # Login
        driver.get("https://dash.iasouth.tech/login.html")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        
        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()
        
        time.sleep(3)
        
        if "dashboard-protected.html" not in driver.current_url:
            print("❌ Login falhou")
            return False
        
        print("✅ Login realizado com sucesso")
        
        # Abrir dashboard builder
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        time.sleep(3)
        
        # Abrir modal
        create_button = driver.find_element(By.CLASS_NAME, "create-dashboard-btn")
        create_button.click()
        time.sleep(3)
        
        print("✅ Modal aberto")
        
        # Testar apenas os campos de data
        start_date_field = driver.find_element(By.ID, "startDate")
        end_date_field = driver.find_element(By.ID, "endDate")
        
        print(f"📅 Campo startDate encontrado: {start_date_field.get_attribute('type')}")
        print(f"📅 Campo endDate encontrado: {end_date_field.get_attribute('type')}")
        
        # Limpar e preencher data de início
        start_date_field.clear()
        time.sleep(0.5)
        start_date_field.send_keys("2024-01-01")
        time.sleep(0.5)
        
        # Verificar valor imediatamente após preenchimento
        start_value_after = start_date_field.get_attribute('value')
        print(f"📅 startDate após send_keys: '{start_value_after}'")
        
        # Limpar e preencher data de fim
        end_date_field.clear()
        time.sleep(0.5)
        end_date_field.send_keys("2024-12-31")
        time.sleep(0.5)
        
        # Verificar valor imediatamente após preenchimento
        end_value_after = end_date_field.get_attribute('value')
        print(f"📅 endDate após send_keys: '{end_value_after}'")
        
        # Aguardar um pouco e verificar novamente
        time.sleep(2)
        start_value_later = start_date_field.get_attribute('value')
        end_value_later = end_date_field.get_attribute('value')
        
        print(f"📅 startDate após 2 segundos: '{start_value_later}'")
        print(f"📅 endDate após 2 segundos: '{end_value_later}'")
        
        # Simular evento de blur
        driver.execute_script("document.getElementById('startDate').blur();")
        driver.execute_script("document.getElementById('endDate').blur();")
        time.sleep(1)
        
        start_value_blur = start_date_field.get_attribute('value')
        end_value_blur = end_date_field.get_attribute('value')
        
        print(f"📅 startDate após blur: '{start_value_blur}'")
        print(f"📅 endDate após blur: '{end_value_blur}'")
        
        # Verificar se os valores mudaram
        if start_value_after != start_value_blur or end_value_after != end_value_blur:
            print("⚠️ Os valores das datas mudaram após o blur!")
            return False
        else:
            print("✅ Os valores das datas permaneceram corretos")
            return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        driver.quit()

def main():
    """Executar teste de debug das datas"""
    print("🧪 TESTE DE DEBUG DAS DATAS\n")
    
    if test_date_debug():
        print("\n🎉 DATAS FUNCIONANDO CORRETAMENTE!")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO NAS DATAS")

if __name__ == "__main__":
    main()
