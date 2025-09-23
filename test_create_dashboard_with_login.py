#!/usr/bin/env python3
"""
Teste automatizado para criar um novo dashboard via interface web com login
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
        
        print("📄 Página de login carregada")
        
        # Preencher dados de login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("dashboard2025")
        
        print("📝 Dados de login preenchidos")
        
        # Clicar no botão de login
        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()
        
        print("🔘 Botão de login clicado")
        
        # Aguardar redirecionamento ou verificar se há erro
        time.sleep(3)
        
        # Verificar se houve erro de login
        try:
            error_message = driver.find_element(By.CSS_SELECTOR, ".error-message")
            if error_message.is_displayed():
                print(f"❌ Erro de login: {error_message.text}")
                return False
        except NoSuchElementException:
            pass
        
        # Verificar se foi redirecionado para dashboard-protected.html
        current_url = driver.current_url
        print(f"📍 URL atual após login: {current_url}")
        
        if "dashboard-protected.html" in current_url:
            print("✅ Login realizado com sucesso - redirecionado para dashboard-protected.html")
            return True
        else:
            print(f"⚠️ Não foi redirecionado para dashboard-protected.html. URL atual: {current_url}")
            return False
        
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
        
        time.sleep(3)
        
        # Verificar se não foi redirecionado para login
        current_url = driver.current_url
        print(f"📍 URL atual: {current_url}")
        
        if "login.html" in current_url:
            print("❌ Foi redirecionado para login - sessão expirada")
            return False
        
        # Verificar se a página carregou corretamente
        page_title = driver.title
        print(f"📄 Título da página: {page_title}")
        
        # Procurar por elementos do formulário
        form_elements = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Elementos de input encontrados: {len(form_elements)}")
        
        if len(form_elements) > 0:
            print("✅ Dashboard builder carregado com sucesso")
            return True
        else:
            print("❌ Nenhum elemento de formulário encontrado")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao navegar para dashboard builder: {e}")
        return False

def inspect_form_elements(driver):
    """Inspecionar elementos do formulário para entender a estrutura"""
    print("🔍 Inspecionando elementos do formulário...")
    
    try:
        # Procurar por todos os inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Inputs encontrados ({len(inputs)}):")
        for i, input_elem in enumerate(inputs):
            input_id = input_elem.get_attribute("id")
            input_name = input_elem.get_attribute("name")
            input_type = input_elem.get_attribute("type")
            input_class = input_elem.get_attribute("class")
            input_placeholder = input_elem.get_attribute("placeholder")
            print(f"  {i+1}. ID: {input_id}, Name: {input_name}, Type: {input_type}, Placeholder: {input_placeholder}")
        
        # Procurar por textareas
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"\n📝 Textareas encontrados ({len(textareas)}):")
        for i, textarea in enumerate(textareas):
            textarea_id = textarea.get_attribute("id")
            textarea_name = textarea.get_attribute("name")
            textarea_placeholder = textarea.get_attribute("placeholder")
            print(f"  {i+1}. ID: {textarea_id}, Name: {textarea_name}, Placeholder: {textarea_placeholder}")
        
        # Procurar por botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Botões encontrados ({len(buttons)}):")
        for i, button in enumerate(buttons):
            button_id = button.get_attribute("id")
            button_class = button.get_attribute("class")
            button_text = button.text.strip()
            print(f"  {i+1}. ID: {button_id}, Class: {button_class}, Text: '{button_text}'")
        
        # Salvar screenshot para análise
        driver.save_screenshot("dashboard_builder_form.png")
        print("📸 Screenshot salvo como 'dashboard_builder_form.png'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inspeção: {e}")
        return False

def fill_campaign_form(driver):
    """Preencher formulário de criação de campanha"""
    print("📝 Preenchendo formulário de campanha...")
    
    try:
        # Dados da campanha de teste
        campaign_name = f"Teste Selenium {random.randint(1000, 9999)}"
        
        # Procurar por campos específicos
        campaign_name_field = None
        start_date_field = None
        end_date_field = None
        budget_field = None
        strategies_field = None
        
        # Procurar por inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_elem in inputs:
            input_id = input_elem.get_attribute("id")
            input_placeholder = input_elem.get_attribute("placeholder") or ""
            
            if "campaign" in input_id.lower() or "nome" in input_placeholder.lower():
                campaign_name_field = input_elem
            elif "start" in input_id.lower() or "inicio" in input_placeholder.lower():
                start_date_field = input_elem
            elif "end" in input_id.lower() or "fim" in input_placeholder.lower():
                end_date_field = input_elem
            elif "budget" in input_id.lower() or "orcamento" in input_placeholder.lower():
                budget_field = input_elem
        
        # Procurar por textarea
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for textarea in textareas:
            textarea_placeholder = textarea.get_attribute("placeholder") or ""
            if "estrategia" in textarea_placeholder.lower() or "strategy" in textarea_placeholder.lower():
                strategies_field = textarea
        
        # Preencher campos encontrados
        if campaign_name_field:
            campaign_name_field.clear()
            campaign_name_field.send_keys(campaign_name)
            print(f"✅ Nome da campanha preenchido: {campaign_name}")
        else:
            print("⚠️ Campo de nome da campanha não encontrado")
        
        if start_date_field:
            start_date_field.clear()
            start_date_field.send_keys("2024-01-01")
            print("✅ Data de início preenchida")
        else:
            print("⚠️ Campo de data de início não encontrado")
        
        if end_date_field:
            end_date_field.clear()
            end_date_field.send_keys("2024-12-31")
            print("✅ Data de fim preenchida")
        else:
            print("⚠️ Campo de data de fim não encontrado")
        
        if budget_field:
            budget_field.clear()
            budget_field.send_keys("100000")
            print("✅ Orçamento preenchido")
        else:
            print("⚠️ Campo de orçamento não encontrado")
        
        if strategies_field:
            strategies_field.clear()
            strategies_field.send_keys("Teste automatizado com Selenium")
            print("✅ Estratégias preenchidas")
        else:
            print("⚠️ Campo de estratégias não encontrado")
        
        return campaign_name
        
    except Exception as e:
        print(f"❌ Erro ao preencher formulário: {e}")
        return None

def create_dashboard(driver):
    """Criar o dashboard"""
    print("🚀 Tentando criar dashboard...")
    
    try:
        # Procurar por botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        create_button = None
        for button in buttons:
            button_text = button.text.strip().lower()
            if "criar" in button_text or "create" in button_text or "gerar" in button_text:
                create_button = button
                break
        
        if create_button:
            print(f"🔘 Botão encontrado: '{create_button.text.strip()}'")
            create_button.click()
            print("✅ Botão clicado")
            
            # Aguardar processamento
            print("⏳ Aguardando processamento...")
            time.sleep(10)
            
            # Verificar resultado
            page_source = driver.page_source.lower()
            if "sucesso" in page_source or "success" in page_source:
                print("✅ Dashboard criado com sucesso!")
                return True
            elif "erro" in page_source or "error" in page_source:
                print("❌ Erro ao criar dashboard")
                return False
            else:
                print("⚠️ Resultado não determinado")
                return False
        else:
            print("❌ Botão de criação não encontrado")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao criar dashboard: {e}")
        return False

def main():
    """Executar teste completo de criação de dashboard"""
    print("🚀 Iniciando teste automatizado de criação de dashboard com login\n")
    
    driver = setup_driver()
    results = []
    
    try:
        # Etapa 1: Login
        results.append(login_to_system(driver))
        
        if not results[-1]:
            print("❌ Login falhou - abortando teste")
            return
        
        # Etapa 2: Navegar para dashboard builder
        results.append(navigate_to_dashboard_builder(driver))
        
        if not results[-1]:
            print("❌ Navegação falhou - abortando teste")
            return
        
        # Etapa 3: Inspecionar elementos
        results.append(inspect_form_elements(driver))
        
        # Etapa 4: Preencher formulário
        campaign_name = fill_campaign_form(driver)
        results.append(campaign_name is not None)
        
        # Etapa 5: Criar dashboard
        results.append(create_dashboard(driver))
        
        # Resumo dos resultados
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE DE CRIAÇÃO DE DASHBOARD")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Etapas aprovadas: {passed}/{total}")
        
        if campaign_name:
            print(f"📝 Campanha criada: {campaign_name}")
        
        if passed == total:
            print("🎉 TESTE COMPLETO PASSOU! Dashboard criado com sucesso!")
        else:
            print("⚠️ Algumas etapas falharam. Verifique os logs acima.")
        
        print("\n🔗 URLs testadas:")
        print("   - https://dash.iasouth.tech/login.html")
        print("   - https://dash.iasouth.tech/dashboard-builder.html")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
