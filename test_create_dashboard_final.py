#!/usr/bin/env python3
"""
Teste automatizado FINAL para criar um novo dashboard via interface web
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
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
    driver.implicitly_wait(10)
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
        
        # Aguardar o modal aparecer
        time.sleep(2)
        
        # Verificar se o modal está visível
        try:
            modal = driver.find_element(By.CSS_SELECTOR, ".modal, [role='dialog']")
            if modal.is_displayed():
                print("✅ Modal visível")
                return True
            else:
                print("❌ Modal não está visível")
                return False
        except NoSuchElementException:
            print("❌ Modal não encontrado")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao abrir modal: {e}")
        return False

def fill_dashboard_form(driver):
    """Preencher formulário de dashboard no modal"""
    print("📝 Preenchendo formulário de dashboard...")
    
    try:
        # Dados da campanha
        campaign_name = f"Teste Selenium {random.randint(1000, 9999)}"
        
        # Preencher nome da campanha
        campaign_name_field = driver.find_element(By.ID, "campaignName")
        campaign_name_field.clear()
        campaign_name_field.send_keys(campaign_name)
        print(f"✅ Nome da campanha: {campaign_name}")
        
        # Preencher data de início
        start_date_field = driver.find_element(By.ID, "startDate")
        start_date_field.clear()
        start_date_field.send_keys("2024-01-01")
        print("✅ Data de início: 2024-01-01")
        
        # Preencher data de fim
        end_date_field = driver.find_element(By.ID, "endDate")
        end_date_field.clear()
        end_date_field.send_keys("2024-12-31")
        print("✅ Data de fim: 2024-12-31")
        
        # Preencher orçamento total
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys("100000")
        print("✅ Orçamento total: R$ 100.000")
        
        # Preencher estratégias
        strategies_field = driver.find_element(By.ID, "campaignStrategies")
        strategies_field.clear()
        strategies_field.send_keys("Teste automatizado com Selenium - Estratégias de teste para validação do sistema de criação de dashboards")
        print("✅ Estratégias preenchidas")
        
        # Selecionar canal YouTube
        youtube_checkbox = driver.find_element(By.ID, "channel_youtube")
        if not youtube_checkbox.is_selected():
            youtube_checkbox.click()
        print("✅ Canal YouTube selecionado")
        
        # Preencher dados do YouTube
        youtube_budget = driver.find_element(By.ID, "youtube_budget")
        youtube_budget.clear()
        youtube_budget.send_keys("50000")
        
        youtube_quantity = driver.find_element(By.ID, "youtube_quantity")
        youtube_quantity.clear()
        youtube_quantity.send_keys("500000")
        
        # URL da planilha de teste
        sheet_url = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440"
        
        youtube_sheet = driver.find_element(By.ID, "youtube_sheet")
        youtube_sheet.clear()
        youtube_sheet.send_keys(sheet_url)
        
        youtube_gid = driver.find_element(By.ID, "youtube_gid")
        youtube_gid.clear()
        youtube_gid.send_keys("0")
        
        print("✅ Dados do YouTube preenchidos")
        
        # Selecionar canal Programmatic Video
        prog_video_checkbox = driver.find_element(By.ID, "channel_programmatic_video")
        if not prog_video_checkbox.is_selected():
            prog_video_checkbox.click()
        print("✅ Canal Programmatic Video selecionado")
        
        # Preencher dados do Programmatic Video
        prog_video_budget = driver.find_element(By.ID, "programmatic_video_budget")
        prog_video_budget.clear()
        prog_video_budget.send_keys("50000")
        
        prog_video_quantity = driver.find_element(By.ID, "programmatic_video_quantity")
        prog_video_quantity.clear()
        prog_video_quantity.send_keys("1000000")
        
        prog_video_sheet = driver.find_element(By.ID, "programmatic_video_sheet")
        prog_video_sheet.clear()
        prog_video_sheet.send_keys(sheet_url)
        
        prog_video_gid = driver.find_element(By.ID, "programmatic_video_gid")
        prog_video_gid.clear()
        prog_video_gid.send_keys("668487440")
        
        print("✅ Dados do Programmatic Video preenchidos")
        
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        return None

def save_dashboard(driver):
    """Salvar o dashboard"""
    print("💾 Salvando dashboard...")
    
    try:
        # Clicar no botão "Salvar Dashboard"
        save_button = driver.find_element(By.ID, "saveDashboardBtn")
        save_button.click()
        
        print("✅ Botão de salvar clicado")
        
        # Aguardar processamento
        print("⏳ Aguardando processamento...")
        time.sleep(15)
        
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

def verify_dashboard_created(driver, campaign_name):
    """Verificar se o dashboard foi criado e aparece na lista"""
    print("🔍 Verificando se o dashboard foi criado...")
    
    try:
        # Navegar para a página de dashboards
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        time.sleep(3)
        
        # Verificar se o dashboard aparece na página
        page_source = driver.page_source
        dashboard_filename = f"dash_{campaign_name.lower().replace(' ', '_')}.html"
        
        if dashboard_filename in page_source:
            print(f"✅ Dashboard encontrado na lista: {dashboard_filename}")
            
            # Testar acesso ao dashboard
            dashboard_url = f"https://dash.iasouth.tech/static/{dashboard_filename}"
            driver.get(dashboard_url)
            time.sleep(3)
            
            if "404" not in driver.page_source and "not found" not in driver.page_source.lower():
                print(f"✅ Dashboard acessível: {dashboard_url}")
                return True
            else:
                print(f"❌ Dashboard não acessível: {dashboard_url}")
                return False
        else:
            print(f"❌ Dashboard não encontrado na lista: {dashboard_filename}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar dashboard: {e}")
        return False

def main():
    """Executar teste completo"""
    print("🚀 TESTE FINAL - Criação de Dashboard com Selenium\n")
    
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
        campaign_name = fill_dashboard_form(driver)
        results.append(campaign_name is not None)
        
        if not campaign_name:
            print("❌ Formulário não preenchido - abortando teste")
            return
        
        # Etapa 4: Salvar dashboard
        results.append(save_dashboard(driver))
        
        # Etapa 5: Verificar criação
        results.append(verify_dashboard_created(driver, campaign_name))
        
        # Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE FINAL")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Etapas aprovadas: {passed}/{total}")
        print(f"📝 Campanha criada: {campaign_name}")
        
        if passed == total:
            print("🎉 TESTE COMPLETO PASSOU! Dashboard criado e funcionando!")
        else:
            print("⚠️ Algumas etapas falharam. Verifique os logs acima.")
        
        print("\n🔗 URLs testadas:")
        print("   - https://dash.iasouth.tech/login.html")
        print("   - https://dash.iasouth.tech/dashboard-builder.html")
        print("   - https://dash.iasouth.tech/dashboard-protected.html")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
