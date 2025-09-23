#!/usr/bin/env python3
"""
Teste específico para debugar qual validação está falhando
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

def test_validation_specific():
    """Testar validação específica"""
    print("🔍 Testando validação específica...")
    
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
        
        # Preencher campos básicos
        campaign_name_field = driver.find_element(By.ID, "campaignName")
        campaign_name_field.clear()
        campaign_name_field.send_keys("Teste Debug")
        
        start_date_field = driver.find_element(By.ID, "startDate")
        start_date_field.clear()
        start_date_field.send_keys("2024-01-01")
        
        end_date_field = driver.find_element(By.ID, "endDate")
        end_date_field.clear()
        end_date_field.send_keys("2024-12-31")
        
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys("50000")
        
        strategies_field = driver.find_element(By.ID, "campaignStrategies")
        strategies_field.clear()
        strategies_field.send_keys("Teste de debug")
        
        print("✅ Campos básicos preenchidos")
        
        # Verificar se o checkbox YouTube está presente
        youtube_checkbox = driver.find_element(By.ID, "channel_youtube")
        print(f"✅ Checkbox YouTube encontrado: {youtube_checkbox.is_selected()}")
        
        # Selecionar canal YouTube
        youtube_checkbox.click()
        time.sleep(2)
        
        print(f"✅ Checkbox YouTube clicado: {youtube_checkbox.is_selected()}")
        
        # Verificar se os campos do YouTube estão habilitados
        youtube_sheet = driver.find_element(By.ID, "youtube_sheet")
        youtube_budget = driver.find_element(By.ID, "youtube_budget")
        youtube_quantity = driver.find_element(By.ID, "youtube_quantity")
        
        print(f"📊 Campos do YouTube:")
        print(f"  - youtube_sheet enabled: {youtube_sheet.is_enabled()}")
        print(f"  - youtube_budget enabled: {youtube_budget.is_enabled()}")
        print(f"  - youtube_quantity enabled: {youtube_quantity.is_enabled()}")
        
        # Preencher dados do YouTube
        if youtube_sheet.is_enabled():
            youtube_sheet.clear()
            youtube_sheet.send_keys("https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440")
            print("✅ Planilha YouTube preenchida")
        else:
            print("❌ Campo de planilha YouTube não habilitado")
        
        if youtube_budget.is_enabled():
            youtube_budget.clear()
            youtube_budget.send_keys("25000")
            print("✅ Orçamento YouTube preenchido")
        else:
            print("❌ Campo de orçamento YouTube não habilitado")
        
        if youtube_quantity.is_enabled():
            youtube_quantity.clear()
            youtube_quantity.send_keys("250000")
            print("✅ Quantidade YouTube preenchida")
        else:
            print("❌ Campo de quantidade YouTube não habilitado")
        
        # Tentar salvar
        save_button = driver.find_element(By.ID, "saveDashboardBtn")
        save_button.click()
        
        print("✅ Botão salvar clicado")
        
        # Aguardar e capturar alertas
        time.sleep(5)
        
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"🚨 Alerta capturado: {alert_text}")
            
            if "Validação do formulário falhou" in alert_text:
                print("❌ Validação ainda falha")
                return False
            else:
                print("✅ Validação passou!")
                alert.accept()
                return True
                
        except:
            print("✅ Nenhum alerta de erro - validação pode ter passado")
            return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        driver.quit()

def main():
    """Executar teste de debug específico"""
    print("🧪 TESTE DE DEBUG ESPECÍFICO - Identificar validação que falha\n")
    
    if test_validation_specific():
        print("\n🎉 VALIDAÇÃO FUNCIONANDO!")
    else:
        print("\n❌ VALIDAÇÃO AINDA FALHA")

if __name__ == "__main__":
    main()
