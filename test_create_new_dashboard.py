#!/usr/bin/env python3
"""
Teste automatizado para criar um novo dashboard via interface web
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import string

def setup_driver():
    """Configurar o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login_to_system(driver):
    """Fazer login no sistema"""
    print("🔐 Fazendo login no sistema...")
    
    try:
        # Acessar página de login
        driver.get("https://dash.iasouth.tech/login.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Preencher dados de login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        # Clicar no botão de login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard-protected.html")
        )
        
        print("✅ Login realizado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def navigate_to_dashboard_builder(driver):
    """Navegar para o dashboard builder"""
    print("🔧 Navegando para o dashboard builder...")
    
    try:
        # Acessar dashboard builder
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("✅ Dashboard builder carregado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao navegar para dashboard builder: {e}")
        return False

def fill_campaign_form(driver):
    """Preencher formulário de criação de campanha"""
    print("📝 Preenchendo formulário de campanha...")
    
    try:
        # Dados da campanha de teste
        campaign_name = f"Teste Automatizado {random.randint(1000, 9999)}"
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        total_budget = "100000"
        strategies = "Teste automatizado com Selenium - Estratégias de teste para validação do sistema"
        
        # Preencher nome da campanha
        campaign_name_field = driver.find_element(By.ID, "campaignName")
        campaign_name_field.clear()
        campaign_name_field.send_keys(campaign_name)
        
        # Preencher data de início
        start_date_field = driver.find_element(By.ID, "startDate")
        start_date_field.clear()
        start_date_field.send_keys(start_date)
        
        # Preencher data de fim
        end_date_field = driver.find_element(By.ID, "endDate")
        end_date_field.clear()
        end_date_field.send_keys(end_date)
        
        # Preencher orçamento total
        budget_field = driver.find_element(By.ID, "totalBudget")
        budget_field.clear()
        budget_field.send_keys(total_budget)
        
        # Preencher estratégias
        strategies_field = driver.find_element(By.ID, "strategies")
        strategies_field.clear()
        strategies_field.send_keys(strategies)
        
        print(f"✅ Formulário preenchido - Campanha: {campaign_name}")
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        return None

def configure_channels(driver):
    """Configurar canais de mídia"""
    print("📺 Configurando canais de mídia...")
    
    try:
        # Selecionar canal Programmatic Video
        programmatic_video_checkbox = driver.find_element(By.CSS_SELECTOR, "input[value='programmatic_video']")
        if not programmatic_video_checkbox.is_selected():
            programmatic_video_checkbox.click()
        
        # Aguardar aparecer campos do canal
        time.sleep(2)
        
        # Preencher dados do Programmatic Video
        prog_budget_field = driver.find_element(By.ID, "programmatic_video-budget")
        prog_budget_field.clear()
        prog_budget_field.send_keys("50000")
        
        prog_quantity_field = driver.find_element(By.ID, "programmatic_video-quantity")
        prog_quantity_field.clear()
        prog_quantity_field.send_keys("1000000")
        
        # URL da planilha de teste (usando a planilha fornecida pelo usuário)
        sheet_url = "https://docs.google.com/spreadsheets/d/1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8/edit?gid=668487440#gid=668487440"
        
        prog_sheet_field = driver.find_element(By.ID, "programmatic_video-sheetId")
        prog_sheet_field.clear()
        prog_sheet_field.send_keys(sheet_url)
        
        prog_gid_field = driver.find_element(By.ID, "programmatic_video-gid")
        prog_gid_field.clear()
        prog_gid_field.send_keys("668487440")
        
        print("✅ Canal Programmatic Video configurado")
        
        # Selecionar canal YouTube
        youtube_checkbox = driver.find_element(By.CSS_SELECTOR, "input[value='youtube']")
        if not youtube_checkbox.is_selected():
            youtube_checkbox.click()
        
        # Aguardar aparecer campos do canal
        time.sleep(2)
        
        # Preencher dados do YouTube
        yt_budget_field = driver.find_element(By.ID, "youtube-budget")
        yt_budget_field.clear()
        yt_budget_field.send_keys("50000")
        
        yt_quantity_field = driver.find_element(By.ID, "youtube-quantity")
        yt_quantity_field.clear()
        yt_quantity_field.send_keys("500000")
        
        yt_sheet_field = driver.find_element(By.ID, "youtube-sheetId")
        yt_sheet_field.clear()
        yt_sheet_field.send_keys(sheet_url)
        
        yt_gid_field = driver.find_element(By.ID, "youtube-gid")
        yt_gid_field.clear()
        yt_gid_field.send_keys("0")
        
        print("✅ Canal YouTube configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar canais: {e}")
        return False

def create_dashboard(driver):
    """Criar o dashboard"""
    print("🚀 Criando dashboard...")
    
    try:
        # Clicar no botão "Criar Dashboard"
        create_button = driver.find_element(By.ID, "createDashboardBtn")
        create_button.click()
        
        print("✅ Botão 'Criar Dashboard' clicado")
        
        # Aguardar processamento (pode demorar alguns segundos)
        print("⏳ Aguardando processamento...")
        time.sleep(10)
        
        # Verificar se apareceu mensagem de sucesso
        try:
            success_message = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .success-message"))
            )
            print(f"✅ Dashboard criado com sucesso: {success_message.text}")
            return True
        except TimeoutException:
            # Verificar se há mensagem de erro
            try:
                error_message = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error-message")
                print(f"❌ Erro ao criar dashboard: {error_message.text}")
                return False
            except NoSuchElementException:
                print("⚠️ Não foi possível determinar o resultado da criação")
                return False
        
    except Exception as e:
        print(f"❌ Erro ao criar dashboard: {e}")
        return False

def verify_dashboard_in_list(driver, campaign_name):
    """Verificar se o dashboard aparece na lista"""
    print("🔍 Verificando se o dashboard aparece na lista...")
    
    try:
        # Navegar para a página de dashboards
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        # Verificar se o dashboard aparece na página
        page_source = driver.page_source
        
        # Procurar por elementos relacionados ao dashboard criado
        dashboard_elements = driver.find_elements(By.CSS_SELECTOR, ".dashboard-card, .card")
        
        print(f"📊 Encontrados {len(dashboard_elements)} elementos de dashboard na página")
        
        # Verificar se há algum link para o dashboard criado
        dashboard_filename = f"dash_{campaign_name.lower().replace(' ', '_')}.html"
        
        if dashboard_filename in page_source:
            print(f"✅ Dashboard encontrado na lista: {dashboard_filename}")
            return True
        else:
            print(f"⚠️ Dashboard não encontrado na lista: {dashboard_filename}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar lista: {e}")
        return False

def test_dashboard_access(driver, campaign_name):
    """Testar acesso ao dashboard criado"""
    print("🔗 Testando acesso ao dashboard...")
    
    try:
        dashboard_filename = f"dash_{campaign_name.lower().replace(' ', '_')}.html"
        dashboard_url = f"https://dash.iasouth.tech/static/{dashboard_filename}"
        
        # Acessar o dashboard
        driver.get(dashboard_url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        # Verificar se carregou sem erro 404
        if "404" in driver.page_source or "not found" in driver.page_source.lower():
            print(f"❌ Dashboard não acessível: {dashboard_url}")
            return False
        else:
            print(f"✅ Dashboard acessível: {dashboard_url}")
            
            # Verificar se contém dados da campanha
            if campaign_name.lower() in driver.page_source.lower():
                print("✅ Dashboard contém dados da campanha criada")
                return True
            else:
                print("⚠️ Dashboard não contém dados da campanha")
                return False
        
    except Exception as e:
        print(f"❌ Erro ao testar acesso: {e}")
        return False

def main():
    """Executar teste completo de criação de dashboard"""
    print("🚀 Iniciando teste automatizado de criação de dashboard\n")
    
    driver = setup_driver()
    results = []
    
    try:
        # Etapa 1: Login
        results.append(login_to_system(driver))
        
        # Etapa 2: Navegar para dashboard builder
        results.append(navigate_to_dashboard_builder(driver))
        
        # Etapa 3: Preencher formulário
        campaign_name = fill_campaign_form(driver)
        results.append(campaign_name is not None)
        
        # Etapa 4: Configurar canais
        results.append(configure_channels(driver))
        
        # Etapa 5: Criar dashboard
        results.append(create_dashboard(driver))
        
        # Etapa 6: Verificar na lista
        if campaign_name:
            results.append(verify_dashboard_in_list(driver, campaign_name))
            results.append(test_dashboard_access(driver, campaign_name))
        
        # Resumo dos resultados
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE DE CRIAÇÃO DE DASHBOARD")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Etapas aprovadas: {passed}/{total}")
        
        if campaign_name:
            print(f"📝 Campanha criada: {campaign_name}")
            print(f"📁 Arquivo esperado: dash_{campaign_name.lower().replace(' ', '_')}.html")
        
        if passed == total:
            print("🎉 TESTE COMPLETO PASSOU! Dashboard criado com sucesso!")
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
