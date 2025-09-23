#!/usr/bin/env python3
"""
Teste CORRIGIDO para criar dashboard - seleciona canal ANTES de salvar
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
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao abrir modal: {e}")
        return False

def fill_complete_form(driver):
    """Preencher formulário completo com canal obrigatório"""
    print("📝 Preenchendo formulário completo...")
    
    try:
        # Dados da campanha
        campaign_name = f"Teste Completo {random.randint(1000, 9999)}"
        
        # Campos básicos
        campaign_name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "campaignName"))
        )
        campaign_name_field.clear()
        campaign_name_field.send_keys(campaign_name)
        print(f"✅ Nome da campanha: {campaign_name}")
        
        # Data de início - usando JavaScript para evitar problema do Selenium
        start_date_field = driver.find_element(By.ID, "startDate")
        driver.execute_script("document.getElementById('startDate').value = '2024-01-01';")
        print("✅ Data de início: 2024-01-01")
        
        # Data de fim - usando JavaScript para evitar problema do Selenium
        end_date_field = driver.find_element(By.ID, "endDate")
        driver.execute_script("document.getElementById('endDate').value = '2024-12-31';")
        print("✅ Data de fim: 2024-12-31")
        
        # Orçamento total
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys("100000")
        print("✅ Orçamento total: R$ 100.000")
        
        # Estratégias
        strategies_field = driver.find_element(By.ID, "campaignStrategies")
        strategies_field.clear()
        strategies_field.send_keys("Teste automatizado com Selenium - Estratégias de teste")
        print("✅ Estratégias preenchidas")
        
        # Modelo de Relatório
        report_model_field = driver.find_element(By.ID, "reportModel")
        report_model_field.send_keys("Simples")
        print("✅ Modelo de relatório: Simples")
        
        # KPI Type
        kpi_type_field = driver.find_element(By.ID, "kpiType")
        kpi_type_field.send_keys("CPV")
        print("✅ KPI Type: CPV")
        
        # KPI Value
        kpi_value_field = driver.find_element(By.ID, "kpiValue")
        kpi_value_field.clear()
        kpi_value_field.send_keys("2.50")
        print("✅ KPI Value: R$ 2.50")
        
        # KPI Target
        kpi_target_field = driver.find_element(By.ID, "kpiTarget")
        kpi_target_field.clear()
        kpi_target_field.send_keys("10000")
        print("✅ KPI Target: 10000")
        
        # *** OBRIGATÓRIO: Selecionar pelo menos um canal ***
        print("📺 Selecionando canal obrigatório...")
        
        # Selecionar canal YouTube
        youtube_checkbox = driver.find_element(By.ID, "channel_youtube")
        if not youtube_checkbox.is_selected():
            youtube_checkbox.click()
        print("✅ Canal YouTube selecionado")
        
        # Aguardar campos do YouTube aparecerem
        time.sleep(2)
        
        # Preencher dados do YouTube
        youtube_budget = driver.find_element(By.ID, "youtube_budget")
        youtube_budget.clear()
        youtube_budget.send_keys("50000")
        
        youtube_quantity = driver.find_element(By.ID, "youtube_quantity")
        youtube_quantity.clear()
        youtube_quantity.send_keys("500000")
        
        # URL da planilha
        sheet_url = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440"
        
        youtube_sheet = driver.find_element(By.ID, "youtube_sheet")
        youtube_sheet.clear()
        youtube_sheet.send_keys(sheet_url)
        
        youtube_gid = driver.find_element(By.ID, "youtube_gid")
        youtube_gid.clear()
        youtube_gid.send_keys("0")
        
        print("✅ Dados do YouTube preenchidos")
        
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        return None

def save_dashboard_and_handle_alerts(driver):
    """Salvar dashboard e lidar com alertas"""
    print("💾 Salvando dashboard...")
    
    try:
        # Clicar no botão salvar
        save_button = driver.find_element(By.ID, "saveDashboardBtn")
        save_button.click()
        print("✅ Botão de salvar clicado")
        
        # Aguardar e lidar com alertas sequenciais
        time.sleep(3)
        
        alerts_handled = []
        
        # Lidar com múltiplos alertas se necessário
        for i in range(5):  # Máximo 5 alertas
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                alerts_handled.append(alert_text)
                print(f"🚨 Alerta {i+1}: {alert_text}")
                alert.accept()
                time.sleep(1)
            except:
                break
        
        print(f"📋 Total de alertas tratados: {len(alerts_handled)}")
        
        # Verificar se houve sucesso
        time.sleep(5)
        
        page_source = driver.page_source.lower()
        
        if "sucesso" in page_source or "success" in page_source or "criado" in page_source:
            print("✅ Dashboard criado com sucesso!")
            return True
        elif "erro" in page_source or "error" in page_source:
            print("❌ Erro ao criar dashboard")
            return False
        else:
            print("⚠️ Resultado não determinado")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao salvar dashboard: {e}")
        return False

def verify_dashboard_in_list(driver, campaign_name):
    """Verificar se o dashboard aparece na lista"""
    print("🔍 Verificando se o dashboard foi criado e aparece na lista...")
    
    try:
        # Navegar para a página de dashboards
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        time.sleep(5)
        
        # Verificar se o dashboard aparece na página
        page_source = driver.page_source
        dashboard_filename = f"dash_{campaign_name.lower().replace(' ', '_')}.html"
        
        print(f"🔍 Procurando por: {dashboard_filename}")
        
        if dashboard_filename in page_source:
            print(f"✅ Dashboard encontrado na lista: {dashboard_filename}")
            
            # Testar acesso ao dashboard
            dashboard_url = f"https://dash.iasouth.tech/static/{dashboard_filename}"
            print(f"🔗 Testando acesso: {dashboard_url}")
            
            driver.get(dashboard_url)
            time.sleep(5)
            
            if "404" not in driver.page_source and "not found" not in driver.page_source.lower():
                print(f"✅ Dashboard acessível e funcionando!")
                return True
            else:
                print(f"❌ Dashboard não acessível (404)")
                return False
        else:
            print(f"❌ Dashboard não encontrado na lista")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar dashboard: {e}")
        return False

def main():
    """Executar teste completo e correto"""
    print("🚀 TESTE CORRIGIDO - Criação completa de dashboard\n")
    
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
        
        # Etapa 3: Preencher formulário COMPLETO (com canal obrigatório)
        campaign_name = fill_complete_form(driver)
        results.append(campaign_name is not None)
        
        if not campaign_name:
            print("❌ Formulário não preenchido - abortando teste")
            return
        
        # Etapa 4: Salvar dashboard
        results.append(save_dashboard_and_handle_alerts(driver))
        
        # Etapa 5: Verificar se aparece na lista
        results.append(verify_dashboard_in_list(driver, campaign_name))
        
        # Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE CORRIGIDO")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Etapas aprovadas: {passed}/{total}")
        print(f"📝 Campanha criada: {campaign_name}")
        
        if passed == total:
            print("🎉 TESTE COMPLETO PASSOU!")
            print("✅ Dashboard criado com sucesso!")
            print("✅ Dashboard aparece na lista!")
            print("✅ Dashboard é acessível!")
        else:
            print("⚠️ Algumas etapas falharam. Verifique os logs acima.")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
