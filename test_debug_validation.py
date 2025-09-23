#!/usr/bin/env python3
"""
Teste para debugar qual validação está falhando no formulário
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

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

def login_to_system(driver):
    """Fazer login no sistema"""
    print("🔐 Fazendo login no sistema...")
    
    try:
        driver.get("https://dash.iasouth.tech/login.html")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        
        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()
        
        time.sleep(3)
        current_url = driver.current_url
        
        if "dashboard-protected.html" in current_url:
            print("✅ Login realizado com sucesso")
            return True
        else:
            print(f"❌ Login falhou - URL: {current_url}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def open_dashboard_modal(driver):
    """Abrir o modal de criação de dashboard"""
    print("🔧 Abrindo modal de criação de dashboard...")
    
    try:
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        time.sleep(3)
        
        # Clicar no botão "Criar Novo Dashboard"
        create_button = driver.find_element(By.CLASS_NAME, "create-dashboard-btn")
        create_button.click()
        
        print("✅ Modal aberto")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao abrir modal: {e}")
        return False

def fill_minimal_form(driver):
    """Preencher apenas os campos obrigatórios mínimos"""
    print("📝 Preenchendo campos obrigatórios mínimos...")
    
    try:
        # Dados mínimos da campanha
        campaign_name = f"Teste Minimo {random.randint(1000, 9999)}"
        
        # Apenas campos básicos obrigatórios
        campaign_name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "campaignName"))
        )
        campaign_name_field.clear()
        campaign_name_field.send_keys(campaign_name)
        print(f"✅ Nome da campanha: {campaign_name}")
        
        # Data de início
        start_date_field = driver.find_element(By.ID, "startDate")
        start_date_field.clear()
        start_date_field.send_keys("2024-01-01")
        print("✅ Data de início: 2024-01-01")
        
        # Data de fim
        end_date_field = driver.find_element(By.ID, "endDate")
        end_date_field.clear()
        end_date_field.send_keys("2024-12-31")
        print("✅ Data de fim: 2024-12-31")
        
        # Orçamento total
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys("50000")
        print("✅ Orçamento total: R$ 50.000")
        
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário mínimo: {e}")
        return None

def try_save_minimal(driver):
    """Tentar salvar com formulário mínimo"""
    print("💾 Tentando salvar com formulário mínimo...")
    
    try:
        # Clicar no botão salvar
        save_button = driver.find_element(By.ID, "saveDashboardBtn")
        save_button.click()
        print("✅ Botão de salvar clicado")
        
        # Aguardar e capturar qualquer alerta
        time.sleep(5)
        
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"🚨 ALERTA CAPTURADO: {alert_text}")
            alert.accept()  # Aceitar o alerta
            return False
        except:
            print("✅ Nenhum alerta encontrado")
            return True
        
    except Exception as e:
        print(f"❌ Erro ao tentar salvar: {e}")
        return False

def fill_with_one_channel(driver):
    """Preencher com apenas um canal"""
    print("📺 Adicionando apenas um canal...")
    
    try:
        # Selecionar apenas YouTube
        youtube_checkbox = driver.find_element(By.ID, "channel_youtube")
        if not youtube_checkbox.is_selected():
            youtube_checkbox.click()
        print("✅ Canal YouTube selecionado")
        
        # Aguardar campos aparecerem
        time.sleep(2)
        
        # Preencher dados básicos do YouTube
        youtube_budget = driver.find_element(By.ID, "youtube_budget")
        youtube_budget.clear()
        youtube_budget.send_keys("25000")
        
        youtube_quantity = driver.find_element(By.ID, "youtube_quantity")
        youtube_quantity.clear()
        youtube_quantity.send_keys("250000")
        
        # URL da planilha
        sheet_url = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440"
        
        youtube_sheet = driver.find_element(By.ID, "youtube_sheet")
        youtube_sheet.clear()
        youtube_sheet.send_keys(sheet_url)
        
        youtube_gid = driver.find_element(By.ID, "youtube_gid")
        youtube_gid.clear()
        youtube_gid.send_keys("0")
        
        print("✅ Dados do YouTube preenchidos")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao preencher canal: {e}")
        return False

def main():
    """Executar teste de debug"""
    print("🔍 TESTE DE DEBUG - Identificando validação que falha\n")
    
    driver = setup_driver()
    
    try:
        # Login
        if not login_to_system(driver):
            return
        
        # Abrir modal
        if not open_dashboard_modal(driver):
            return
        
        # Teste 1: Formulário mínimo
        print("\n🧪 TESTE 1: Formulário mínimo")
        campaign_name = fill_minimal_form(driver)
        if campaign_name:
            if try_save_minimal(driver):
                print("✅ Formulário mínimo funcionou!")
                return
            else:
                print("❌ Formulário mínimo falhou")
        
        # Teste 2: Com um canal
        print("\n🧪 TESTE 2: Com um canal")
        if fill_with_one_channel(driver):
            if try_save_minimal(driver):
                print("✅ Com um canal funcionou!")
                return
            else:
                print("❌ Com um canal falhou")
        
        print("\n❌ Todos os testes falharam - validação não identificada")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
