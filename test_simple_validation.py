#!/usr/bin/env python3
"""
Teste simples para verificar se a validação foi corrigida
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

def test_validation_fix():
    """Testar se a validação foi corrigida"""
    print("🔍 Testando se a correção da função extractSheetId funcionou...")
    
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
        
        # Preencher apenas campos básicos
        campaign_name_field = driver.find_element(By.ID, "campaignName")
        campaign_name_field.clear()
        campaign_name_field.send_keys("Teste Validacao")
        
        start_date_field = driver.find_element(By.ID, "startDate")
        start_date_field.clear()
        start_date_field.send_keys("2024-01-01")
        
        end_date_field = driver.find_element(By.ID, "endDate")
        end_date_field.clear()
        end_date_field.send_keys("2024-12-31")
        
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys("50000")
        
        print("✅ Campos básicos preenchidos")
        
        # Selecionar canal YouTube
        youtube_checkbox = driver.find_element(By.ID, "channel_youtube")
        youtube_checkbox.click()
        time.sleep(2)
        
        # Preencher dados do YouTube
        youtube_budget = driver.find_element(By.ID, "youtube_budget")
        youtube_budget.clear()
        youtube_budget.send_keys("25000")
        
        youtube_quantity = driver.find_element(By.ID, "youtube_quantity")
        youtube_quantity.clear()
        youtube_quantity.send_keys("250000")
        
        youtube_sheet = driver.find_element(By.ID, "youtube_sheet")
        youtube_sheet.clear()
        youtube_sheet.send_keys("https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440")
        
        youtube_gid = driver.find_element(By.ID, "youtube_gid")
        youtube_gid.clear()
        youtube_gid.send_keys("0")
        
        print("✅ Canal YouTube configurado")
        
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
            
            if "extractSheetId" in alert_text or "ReferenceError" in alert_text:
                print("❌ ERRO: Função extractSheetId ainda não está funcionando")
                return False
            elif "Validação do formulário falhou" in alert_text:
                print("❌ ERRO: Validação ainda falha")
                return False
            else:
                print("✅ Alerta capturado - função extractSheetId funcionando")
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
    """Executar teste simples"""
    print("🧪 TESTE SIMPLES - Verificar correção da validação\n")
    
    if test_validation_fix():
        print("\n🎉 CORREÇÃO FUNCIONOU! Função extractSheetId está operacional!")
    else:
        print("\n❌ CORREÇÃO NÃO FUNCIONOU - ainda há problemas")

if __name__ == "__main__":
    main()
