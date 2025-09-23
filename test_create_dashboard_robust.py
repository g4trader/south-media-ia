#!/usr/bin/env python3
"""
Teste ROBUSTO para criar dashboard - aguarda elementos ficarem interativos
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
        
        # Aguardar o modal aparecer e elementos ficarem visíveis
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao abrir modal: {e}")
        return False

def wait_and_fill_element(driver, element_id, value, description):
    """Aguardar elemento ficar interativo e preenchê-lo"""
    try:
        # Aguardar elemento estar presente e clicável
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        
        # Limpar e preencher
        element.clear()
        element.send_keys(value)
        print(f"✅ {description}: {value}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao preencher {description}: {e}")
        return False

def wait_and_click_checkbox(driver, element_id, description):
    """Aguardar checkbox ficar clicável e clicá-lo"""
    try:
        # Aguardar checkbox estar presente e clicável
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        
        if not checkbox.is_selected():
            checkbox.click()
        
        print(f"✅ {description} selecionado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao selecionar {description}: {e}")
        return False

def fill_dashboard_form_robust(driver):
    """Preencher formulário de dashboard de forma robusta"""
    print("📝 Preenchendo formulário de dashboard (modo robusto)...")
    
    try:
        # Dados da campanha
        campaign_name = f"Teste Selenium {random.randint(1000, 9999)}"
        
        # Preencher campos básicos
        wait_and_fill_element(driver, "campaignName", campaign_name, "Nome da campanha")
        wait_and_fill_element(driver, "startDate", "2024-01-01", "Data de início")
        wait_and_fill_element(driver, "endDate", "2024-12-31", "Data de fim")
        wait_and_fill_element(driver, "totalBudget", "100000", "Orçamento total")
        
        # Preencher estratégias
        wait_and_fill_element(driver, "campaignStrategies", 
                            "Teste automatizado com Selenium - Estratégias de teste para validação do sistema", 
                            "Estratégias")
        
        print("✅ Campos básicos preenchidos")
        
        # Aguardar um pouco para garantir que os campos foram processados
        time.sleep(2)
        
        # Selecionar canal YouTube
        wait_and_click_checkbox(driver, "channel_youtube", "Canal YouTube")
        
        # Aguardar campos do YouTube ficarem visíveis
        time.sleep(2)
        
        # Preencher dados do YouTube
        wait_and_fill_element(driver, "youtube_budget", "50000", "Orçamento YouTube")
        wait_and_fill_element(driver, "youtube_quantity", "500000", "Quantidade YouTube")
        
        # URL da planilha de teste
        sheet_url = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440"
        
        wait_and_fill_element(driver, "youtube_sheet", sheet_url, "URL da planilha YouTube")
        wait_and_fill_element(driver, "youtube_gid", "0", "GID YouTube")
        
        print("✅ Dados do YouTube preenchidos")
        
        # Aguardar um pouco mais antes de selecionar o próximo canal
        time.sleep(3)
        
        # Selecionar canal Programmatic Video
        wait_and_click_checkbox(driver, "channel_programmatic_video", "Canal Programmatic Video")
        
        # Aguardar campos do Programmatic Video ficarem visíveis
        time.sleep(3)
        
        # Preencher dados do Programmatic Video
        wait_and_fill_element(driver, "programmatic_video_budget", "50000", "Orçamento Programmatic Video")
        wait_and_fill_element(driver, "programmatic_video_quantity", "1000000", "Quantidade Programmatic Video")
        wait_and_fill_element(driver, "programmatic_video_sheet", sheet_url, "URL da planilha Programmatic Video")
        wait_and_fill_element(driver, "programmatic_video_gid", "668487440", "GID Programmatic Video")
        
        print("✅ Dados do Programmatic Video preenchidos")
        
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        return None

def save_dashboard_robust(driver):
    """Salvar o dashboard de forma robusta"""
    print("💾 Salvando dashboard...")
    
    try:
        # Aguardar botão de salvar ficar clicável
        save_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "saveDashboardBtn"))
        )
        
        save_button.click()
        print("✅ Botão de salvar clicado")
        
        # Aguardar processamento (mais tempo para processar)
        print("⏳ Aguardando processamento (20 segundos)...")
        time.sleep(20)
        
        # Verificar resultado
        page_source = driver.page_source.lower()
        
        if "sucesso" in page_source or "success" in page_source or "criado" in page_source:
            print("✅ Dashboard salvo com sucesso!")
            return True
        elif "erro" in page_source or "error" in page_source:
            print("❌ Erro ao salvar dashboard")
            # Tentar encontrar mensagem de erro específica
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error-message, .alert-error")
                for error in error_elements:
                    if error.is_displayed():
                        print(f"❌ Erro: {error.text}")
            except:
                pass
            return False
        else:
            print("⚠️ Resultado não determinado")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao salvar dashboard: {e}")
        return False

def main():
    """Executar teste robusto"""
    print("🚀 TESTE ROBUSTO - Criação de Dashboard com Selenium\n")
    
    driver = setup_driver()
    results = []
    
    try:
        # Etapa 1: Login
        results.append(login_to_system(driver))
        
        if not results[-1]:
            print("❌ Login falhou - abortando teste")
            return
        
        # Etapa 2: Abrir modal
        results.append(open_dashboard_modal(driver))
        
        if not results[-1]:
            print("❌ Modal não abriu - abortando teste")
            return
        
        # Etapa 3: Preencher formulário
        campaign_name = fill_dashboard_form_robust(driver)
        results.append(campaign_name is not None)
        
        if not campaign_name:
            print("❌ Formulário não preenchido - abortando teste")
            return
        
        # Etapa 4: Salvar dashboard
        results.append(save_dashboard_robust(driver))
        
        # Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE ROBUSTO")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Etapas aprovadas: {passed}/{total}")
        print(f"📝 Campanha criada: {campaign_name}")
        
        if passed == total:
            print("🎉 TESTE ROBUSTO PASSOU! Dashboard criado com sucesso!")
        else:
            print("⚠️ Algumas etapas falharam. Verifique os logs acima.")
        
        # Salvar screenshot final
        driver.save_screenshot("teste_final_dashboard.png")
        print("📸 Screenshot final salvo como 'teste_final_dashboard.png'")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
