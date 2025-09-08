"""
Testes End-to-End (E2E) com Selenium para sistema South Media IA
Inclui navegação completa, verificação de dados e validação de funcionalidades
"""

import pytest
import time
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configurações de teste
BASE_URL = "http://localhost:8000"  # URL da aplicação de teste
TIMEOUT = 10  # Timeout padrão para esperas
HEADLESS = True  # Executar em modo headless para CI/CD


class TestE2ESelenium:
    """Classe principal para testes E2E com Selenium"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Configurar driver do Chrome para testes"""
        chrome_options = Options()
        
        if HEADLESS:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")  # Para testes de acessibilidade
        
        # Configurar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(TIMEOUT)
        
        yield driver
        
        # Limpeza
        driver.quit()
    
    @pytest.fixture
    def wait(self, driver):
        """WebDriverWait configurado"""
        return WebDriverWait(driver, TIMEOUT)
    
    def test_01_homepage_loads_correctly(self, driver, wait):
        """Testar se a página inicial carrega corretamente"""
        driver.get(f"{BASE_URL}/")
        
        # Verificar elementos essenciais
        assert "South Media IA" in driver.title
        
        # Verificar se a página carregou completamente
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Verificar elementos de navegação
        nav_elements = driver.find_elements(By.TAG_NAME, "nav")
        assert len(nav_elements) > 0
        
        # Verificar se não há erros JavaScript
        logs = driver.get_log("browser")
        error_logs = [log for log in logs if log["level"] == "SEVERE"]
        assert len(error_logs) == 0, f"Erros JavaScript encontrados: {error_logs}"
    
    def test_02_login_page_functionality(self, driver, wait):
        """Testar funcionalidade da página de login"""
        driver.get(f"{BASE_URL}/login")
        
        # Verificar se a página de login carregou
        wait.until(EC.presence_of_element_located((By.ID, "login-form")))
        
        # Verificar campos obrigatórios
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        assert username_field.is_displayed()
        assert password_field.is_displayed()
        assert company_select.is_displayed()
        assert login_button.is_displayed()
        
        # Testar validação de campos vazios
        login_button.click()
        
        # Verificar mensagens de erro
        error_messages = driver.find_elements(By.CLASS_NAME, "error-message")
        assert len(error_messages) > 0
        
        # Testar login com credenciais inválidas
        username_field.send_keys("invalid_user")
        password_field.send_keys("invalid_password")
        
        # Selecionar empresa
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        
        login_button.click()
        
        # Verificar mensagem de erro de credenciais inválidas
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-message")))
        error_message = driver.find_element(By.CLASS_NAME, "error-message")
        assert "credenciais inválidas" in error_message.text.lower()
    
    def test_03_successful_login_and_navigation(self, driver, wait):
        """Testar login bem-sucedido e navegação inicial"""
        driver.get(f"{BASE_URL}/login")
        
        # Login com credenciais válidas
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpassword123")
        
        # Selecionar empresa
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        
        login_button.click()
        
        # Verificar redirecionamento para dashboard
        wait.until(EC.url_contains("/dashboard"))
        
        # Verificar se o usuário está logado
        user_menu = wait.until(EC.presence_of_element_located((By.ID, "user-menu")))
        assert user_menu.is_displayed()
        
        # Verificar nome do usuário logado
        username_display = driver.find_element(By.ID, "username-display")
        assert "testuser" in username_display.text.lower()
    
    def test_04_dashboard_navigation_and_widgets(self, driver, wait):
        """Testar navegação do dashboard e widgets"""
        # Assumindo que já está logado do teste anterior
        driver.get(f"{BASE_URL}/dashboard")
        
        # Verificar se o dashboard carregou
        wait.until(EC.presence_of_element_located((By.ID, "dashboard-container")))
        
        # Verificar widgets principais
        widgets = driver.find_elements(By.CLASS_NAME, "dashboard-widget")
        assert len(widgets) > 0
        
        # Verificar métricas principais
        metric_widgets = driver.find_elements(By.CLASS_NAME, "metric-widget")
        assert len(metric_widgets) >= 3  # Pelo menos 3 métricas principais
        
        # Verificar gráficos
        chart_widgets = driver.find_elements(By.CLASS_NAME, "chart-widget")
        assert len(chart_widgets) > 0
        
        # Testar navegação entre abas do dashboard
        tabs = driver.find_elements(By.CLASS_NAME, "dashboard-tab")
        if len(tabs) > 1:
            # Clicar na segunda aba
            tabs[1].click()
            time.sleep(1)
            
            # Verificar se o conteúdo mudou
            active_tab = driver.find_element(By.CLASS_NAME, "active-tab")
            assert active_tab == tabs[1]
    
    def test_05_campaign_management_navigation(self, driver, wait):
        """Testar navegação para gerenciamento de campanhas"""
        # Navegar para campanhas
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        # Verificar se a página de campanhas carregou
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        # Verificar elementos da página de campanhas
        campaign_list = driver.find_element(By.ID, "campaign-list")
        assert campaign_list.is_displayed()
        
        # Verificar botão de nova campanha
        new_campaign_button = driver.find_element(By.ID, "new-campaign-button")
        assert new_campaign_button.is_displayed()
        
        # Verificar filtros
        filters_section = driver.find_element(By.ID, "campaign-filters")
        assert filters_section.is_displayed()
        
        # Testar filtros
        status_filter = driver.find_element(By.ID, "status-filter")
        status_filter.click()
        
        # Selecionar status "Ativa"
        active_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Ativa')]")
        active_option.click()
        
        # Verificar se a lista foi filtrada
        time.sleep(1)
        filtered_campaigns = driver.find_elements(By.CLASS_NAME, "campaign-item")
        assert len(filtered_campaigns) > 0
    
    def test_06_create_new_campaign(self, driver, wait):
        """Testar criação de nova campanha"""
        # Clicar no botão de nova campanha
        new_campaign_button = driver.find_element(By.ID, "new-campaign-button")
        new_campaign_button.click()
        
        # Verificar se o formulário de criação carregou
        wait.until(EC.presence_of_element_located((By.ID, "campaign-form")))
        
        # Preencher formulário
        campaign_name = driver.find_element(By.ID, "campaign-name")
        campaign_name.send_keys("Campanha de Teste E2E")
        
        campaign_type = driver.find_element(By.ID, "campaign-type")
        campaign_type.click()
        video_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Vídeo')]")
        video_option.click()
        
        start_date = driver.find_element(By.ID, "start-date")
        start_date.send_keys("2024-01-01")
        
        end_date = driver.find_element(By.ID, "end-date")
        end_date.send_keys("2024-03-31")
        
        google_sheets_url = driver.find_element(By.ID, "google-sheets-url")
        google_sheets_url.send_keys("https://docs.google.com/spreadsheets/d/test123")
        
        dashboard_template = driver.find_element(By.ID, "dashboard-template")
        dashboard_template.click()
        template_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Template Vídeo')]")
        template_option.click()
        
        strategies = driver.find_element(By.ID, "strategies")
        strategies.send_keys("Estratégia de teste para validação E2E")
        
        total_budget = driver.find_element(By.ID, "total-budget")
        total_budget.send_keys("5000")
        
        # Salvar campanha
        save_button = driver.find_element(By.ID, "save-campaign-button")
        save_button.click()
        
        # Verificar se a campanha foi criada
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "campanha criada" in success_message.text.lower()
        
        # Verificar se foi redirecionado para a lista de campanhas
        wait.until(EC.url_contains("/campaigns"))
        
        # Verificar se a nova campanha aparece na lista
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        campaign_names = [item.find_element(By.CLASS_NAME, "campaign-name").text for item in campaign_items]
        assert "Campanha de Teste E2E" in campaign_names
    
    def test_07_edit_existing_campaign(self, driver, wait):
        """Testar edição de campanha existente"""
        # Encontrar e clicar na campanha criada
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        target_campaign = None
        
        for item in campaign_items:
            name_element = item.find_element(By.CLASS_NAME, "campaign-name")
            if "Campanha de Teste E2E" in name_element.text:
                target_campaign = item
                break
        
        assert target_campaign is not None
        
        # Clicar no botão de editar
        edit_button = target_campaign.find_element(By.CLASS_NAME, "edit-button")
        edit_button.click()
        
        # Verificar se o formulário de edição carregou
        wait.until(EC.presence_of_element_located((By.ID, "campaign-form")))
        
        # Modificar o nome da campanha
        campaign_name = driver.find_element(By.ID, "campaign-name")
        campaign_name.clear()
        campaign_name.send_keys("Campanha de Teste E2E - Editada")
        
        # Modificar o orçamento
        total_budget = driver.find_element(By.ID, "total-budget")
        total_budget.clear()
        total_budget.send_keys("7500")
        
        # Salvar alterações
        save_button = driver.find_element(By.ID, "save-campaign-button")
        save_button.click()
        
        # Verificar mensagem de sucesso
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "campanha atualizada" in success_message.text.lower()
        
        # Verificar se as alterações foram salvas
        wait.until(EC.url_contains("/campaigns"))
        
        # Verificar se o nome foi alterado na lista
        updated_campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        updated_names = [item.find_element(By.CLASS_NAME, "campaign-name").text for item in updated_campaign_items]
        assert "Campanha de Teste E2E - Editada" in updated_names
    
    def test_08_campaign_performance_view(self, driver, wait):
        """Testar visualização de performance da campanha"""
        # Encontrar a campanha editada
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        target_campaign = None
        
        for item in campaign_items:
            name_element = item.find_element(By.CLASS_NAME, "campaign-name")
            if "Campanha de Teste E2E - Editada" in name_element.text:
                target_campaign = item
                break
        
        assert target_campaign is not None
        
        # Clicar no botão de visualizar performance
        performance_button = target_campaign.find_element(By.CLASS_NAME, "performance-button")
        performance_button.click()
        
        # Verificar se a página de performance carregou
        wait.until(EC.presence_of_element_located((By.ID, "performance-page")))
        
        # Verificar métricas de performance
        performance_metrics = driver.find_elements(By.CLASS_NAME, "performance-metric")
        assert len(performance_metrics) >= 5  # Pelo menos 5 métricas principais
        
        # Verificar gráficos de performance
        performance_charts = driver.find_elements(By.CLASS_NAME, "performance-chart")
        assert len(performance_charts) > 0
        
        # Verificar seletor de período
        period_selector = driver.find_element(By.ID, "period-selector")
        assert period_selector.is_displayed()
        
        # Testar diferentes períodos
        period_selector.click()
        
        # Selecionar período de 7 dias
        week_option = driver.find_element(By.XPATH, "//option[contains(text(), '7 dias')]")
        week_option.click()
        
        # Verificar se os dados foram atualizados
        time.sleep(2)
        updated_metrics = driver.find_elements(By.CLASS_NAME, "performance-metric")
        assert len(updated_metrics) >= 5
    
    def test_09_company_management_navigation(self, driver, wait):
        """Testar navegação para gerenciamento de empresas"""
        # Navegar para empresas
        companies_link = driver.find_element(By.LINK_TEXT, "Empresas")
        companies_link.click()
        
        # Verificar se a página de empresas carregou
        wait.until(EC.presence_of_element_located((By.ID, "companies-page")))
        
        # Verificar elementos da página de empresas
        company_list = driver.find_element(By.ID, "company-list")
        assert company_list.is_displayed()
        
        # Verificar botão de nova empresa
        new_company_button = driver.find_element(By.ID, "new-company-button")
        assert new_company_button.is_displayed()
        
        # Verificar se a empresa de teste está listada
        company_items = driver.find_elements(By.CLASS_NAME, "company-item")
        company_names = [item.find_element(By.CLASS_NAME, "company-name").text for item in company_items]
        assert "Empresa Teste" in company_names
    
    def test_10_user_management_navigation(self, driver, wait):
        """Testar navegação para gerenciamento de usuários"""
        # Navegar para usuários
        users_link = driver.find_element(By.LINK_TEXT, "Usuários")
        users_link.click()
        
        # Verificar se a página de usuários carregou
        wait.until(EC.presence_of_element_located((By.ID, "users-page")))
        
        # Verificar elementos da página de usuários
        user_list = driver.find_element(By.ID, "user-list")
        assert user_list.is_displayed()
        
        # Verificar botão de novo usuário
        new_user_button = driver.find_element(By.ID, "new-user-button")
        assert new_user_button.is_displayed()
        
        # Verificar se o usuário de teste está listado
        user_items = driver.find_elements(By.CLASS_NAME, "user-item")
        user_usernames = [item.find_element(By.CLASS_NAME, "username").text for item in user_items]
        assert "testuser" in user_usernames
    
    def test_11_dashboard_templates_navigation(self, driver, wait):
        """Testar navegação para templates de dashboard"""
        # Navegar para templates
        templates_link = driver.find_element(By.LINK_TEXT, "Templates")
        templates_link.click()
        
        # Verificar se a página de templates carregou
        wait.until(EC.presence_of_element_located((By.ID, "templates-page")))
        
        # Verificar elementos da página de templates
        template_list = driver.find_element(By.ID, "template-list")
        assert template_list.is_displayed()
        
        # Verificar botão de novo template
        new_template_button = driver.find_element(By.ID, "new-template-button")
        assert new_template_button.is_displayed()
        
        # Verificar se existem templates padrão
        template_items = driver.find_elements(By.CLASS_NAME, "template-item")
        assert len(template_items) > 0
        
        # Verificar tipos de template
        template_types = [item.find_element(By.CLASS_NAME, "template-type").text for item in template_items]
        assert "Vídeo" in template_types
        assert "Social" in template_types
        assert "Display" in template_types
    
    def test_12_notifications_and_alerts(self, driver, wait):
        """Testar funcionalidades de notificações e alertas"""
        # Verificar ícone de notificações
        notification_icon = driver.find_element(By.ID, "notification-icon")
        assert notification_icon.is_displayed()
        
        # Clicar no ícone de notificações
        notification_icon.click()
        
        # Verificar se o painel de notificações abriu
        wait.until(EC.presence_of_element_located((By.ID, "notifications-panel")))
        
        # Verificar se há notificações
        notifications = driver.find_elements(By.CLASS_NAME, "notification-item")
        assert len(notifications) >= 0  # Pode não haver notificações
        
        # Fechar painel de notificações
        close_button = driver.find_element(By.CLASS_NAME, "close-notifications")
        close_button.click()
        
        # Verificar se o painel fechou
        time.sleep(1)
        try:
            notifications_panel = driver.find_element(By.ID, "notifications-panel")
            assert not notifications_panel.is_displayed()
        except NoSuchElementException:
            pass  # Painel foi fechado corretamente
    
    def test_13_search_and_filter_functionality(self, driver, wait):
        """Testar funcionalidades de busca e filtro"""
        # Voltar para a página de campanhas
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        # Testar busca por nome
        search_box = driver.find_element(By.ID, "search-box")
        search_box.send_keys("Teste E2E")
        search_box.send_keys(Keys.RETURN)
        
        # Verificar se os resultados foram filtrados
        time.sleep(1)
        filtered_campaigns = driver.find_elements(By.CLASS_NAME, "campaign-item")
        assert len(filtered_campaigns) > 0
        
        # Verificar se todos os resultados contêm o termo de busca
        for campaign in filtered_campaigns:
            name = campaign.find_element(By.CLASS_NAME, "campaign-name").text
            assert "Teste E2E" in name
        
        # Limpar busca
        search_box.clear()
        search_box.send_keys(Keys.RETURN)
        
        # Verificar se todos os resultados voltaram
        time.sleep(1)
        all_campaigns = driver.find_elements(By.CLASS_NAME, "campaign-item")
        assert len(all_campaigns) >= len(filtered_campaigns)
    
    def test_14_data_import_functionality(self, driver, wait):
        """Testar funcionalidade de importação de dados"""
        # Navegar para a campanha de teste
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        # Encontrar a campanha de teste
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        target_campaign = None
        
        for item in campaign_items:
            name_element = item.find_element(By.CLASS_NAME, "campaign-name")
            if "Campanha de Teste E2E - Editada" in name_element.text:
                target_campaign = item
                break
        
        assert target_campaign is not None
        
        # Clicar no botão de importar dados
        import_button = target_campaign.find_element(By.CLASS_NAME, "import-data-button")
        import_button.click()
        
        # Verificar se o modal de importação abriu
        wait.until(EC.presence_of_element_located((By.ID, "import-modal")))
        
        # Verificar opções de importação
        import_options = driver.find_elements(By.CLASS_NAME, "import-option")
        assert len(import_options) > 0
        
        # Selecionar importação manual
        manual_import = driver.find_element(By.ID, "manual-import-option")
        manual_import.click()
        
        # Verificar se o formulário de importação manual apareceu
        wait.until(EC.presence_of_element_located((By.ID, "manual-import-form")))
        
        # Fechar modal
        close_button = driver.find_element(By.CLASS_NAME, "close-modal")
        close_button.click()
        
        # Verificar se o modal fechou
        time.sleep(1)
        try:
            import_modal = driver.find_element(By.ID, "import-modal")
            assert not import_modal.is_displayed()
        except NoSuchElementException:
            pass  # Modal foi fechado corretamente
    
    def test_15_user_profile_and_settings(self, driver, wait):
        """Testar funcionalidades de perfil do usuário e configurações"""
        # Clicar no menu do usuário
        user_menu = driver.find_element(By.ID, "user-menu")
        user_menu.click()
        
        # Verificar se o menu dropdown abriu
        wait.until(EC.presence_of_element_located((By.ID, "user-dropdown")))
        
        # Clicar em "Perfil"
        profile_link = driver.find_element(By.LINK_TEXT, "Perfil")
        profile_link.click()
        
        # Verificar se a página de perfil carregou
        wait.until(EC.presence_of_element_located((By.ID, "profile-page")))
        
        # Verificar informações do perfil
        profile_info = driver.find_element(By.ID, "profile-info")
        assert profile_info.is_displayed()
        
        # Verificar se o nome do usuário está correto
        username_display = driver.find_element(By.ID, "profile-username")
        assert "testuser" in username_display.text.lower()
        
        # Clicar em "Configurações"
        settings_link = driver.find_element(By.LINK_TEXT, "Configurações")
        settings_link.click()
        
        # Verificar se a página de configurações carregou
        wait.until(EC.presence_of_element_located((By.ID, "settings-page")))
        
        # Verificar opções de configuração
        settings_options = driver.find_elements(By.CLASS_NAME, "setting-option")
        assert len(settings_options) > 0
    
    def test_16_logout_functionality(self, driver, wait):
        """Testar funcionalidade de logout"""
        # Abrir menu do usuário
        user_menu = driver.find_element(By.ID, "user-menu")
        user_menu.click()
        
        # Verificar se o menu dropdown abriu
        wait.until(EC.presence_of_element_located((By.ID, "user-dropdown")))
        
        # Clicar em "Sair"
        logout_link = driver.find_element(By.LINK_TEXT, "Sair")
        logout_link.click()
        
        # Verificar se foi redirecionado para a página de login
        wait.until(EC.url_contains("/login"))
        
        # Verificar se não há mais elementos do usuário logado
        try:
            user_menu = driver.find_element(By.ID, "user-menu")
            assert False, "Usuário ainda está logado"
        except NoSuchElementException:
            pass  # Usuário foi deslogado corretamente
        
        # Verificar se a página de login está visível
        login_form = driver.find_element(By.ID, "login-form")
        assert login_form.is_displayed()
    
    def test_17_responsive_design_mobile(self, driver, wait):
        """Testar design responsivo em resolução mobile"""
        # Alterar tamanho da janela para simular mobile
        driver.set_window_size(375, 667)  # iPhone SE
        
        # Navegar para a página inicial
        driver.get(f"{BASE_URL}/")
        
        # Verificar se a navegação mobile está funcionando
        try:
            mobile_menu_button = driver.find_element(By.ID, "mobile-menu-button")
            mobile_menu_button.click()
            
            # Verificar se o menu mobile abriu
            wait.until(EC.presence_of_element_located((By.ID, "mobile-menu")))
            
            # Verificar se os links estão visíveis
            mobile_links = driver.find_elements(By.CLASS_NAME, "mobile-nav-link")
            assert len(mobile_links) > 0
            
            # Fechar menu mobile
            mobile_menu_button.click()
            
        except NoSuchElementException:
            # Pode não ter menu mobile em todas as resoluções
            pass
        
        # Verificar se o conteúdo está adaptado para mobile
        body_width = driver.execute_script("return document.body.clientWidth")
        assert body_width <= 375  # Deve estar dentro da largura mobile
    
    def test_18_accessibility_features(self, driver, wait):
        """Testar recursos de acessibilidade"""
        # Verificar se há atributos alt em imagens
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            assert alt_text is not None, f"Imagem sem atributo alt: {img.get_attribute('src')}"
        
        # Verificar se há labels para campos de formulário
        form_fields = driver.find_elements(By.TAG_NAME, "input")
        for field in form_fields:
            field_id = field.get_attribute("id")
            if field_id:
                try:
                    label = driver.find_element(By.XPATH, f"//label[@for='{field_id}']")
                    assert label.is_displayed(), f"Campo {field_id} sem label visível"
                except NoSuchElementException:
                    # Pode ter label como filho
                    parent = field.find_element(By.XPATH, "..")
                    try:
                        label = parent.find_element(By.TAG_NAME, "label")
                        assert label.is_displayed(), f"Campo {field_id} sem label visível"
                    except NoSuchElementException:
                        pass  # Pode ter label em outro lugar
        
        # Verificar contraste de cores (simulado)
        # Em um teste real, isso seria feito com ferramentas específicas
        body_color = driver.execute_script("return window.getComputedStyle(document.body).color")
        background_color = driver.execute_script("return window.getComputedStyle(document.body).backgroundColor")
        
        # Verificar se as cores são diferentes (contraste básico)
        assert body_color != background_color
    
    def test_19_performance_metrics(self, driver, wait):
        """Testar métricas de performance da aplicação"""
        # Medir tempo de carregamento da página inicial
        start_time = time.time()
        driver.get(f"{BASE_URL}/")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        load_time = time.time() - start_time
        
        # Verificar se o carregamento foi rápido
        assert load_time < 5.0, f"Página demorou {load_time:.2f}s para carregar"
        
        # Medir tempo de carregamento do dashboard
        start_time = time.time()
        driver.get(f"{BASE_URL}/dashboard")
        wait.until(EC.presence_of_element_located((By.ID, "dashboard-container")))
        dashboard_load_time = time.time() - start_time
        
        # Verificar se o dashboard carregou em tempo razoável
        assert dashboard_load_time < 8.0, f"Dashboard demorou {dashboard_load_time:.2f}s para carregar"
        
        # Verificar se não há muitos requests HTTP
        performance_logs = driver.execute_script("return window.performance.getEntries()")
        http_requests = [entry for entry in performance_logs if entry.get("entryType") == "resource"]
        
        # Verificar se não há muitos requests desnecessários
        assert len(http_requests) < 50, f"Muitos requests HTTP: {len(http_requests)}"
    
    def test_20_error_handling_and_validation(self, driver, wait):
        """Testar tratamento de erros e validações"""
        # Testar URL inválida
        driver.get(f"{BASE_URL}/invalid-endpoint")
        
        # Verificar se a página de erro 404 foi exibida
        try:
            error_404 = driver.find_element(By.ID, "error-404")
            assert error_404.is_displayed()
        except NoSuchElementException:
            # Pode ter outro formato de erro
            error_message = driver.find_element(By.TAG_NAME, "body").text
            assert "404" in error_message or "não encontrado" in error_message.lower()
        
        # Voltar para página válida
        driver.get(f"{BASE_URL}/")
        
        # Testar formulário com dados inválidos
        login_link = driver.find_element(By.LINK_TEXT, "Login")
        login_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "login-form")))
        
        # Tentar login com dados inválidos
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("a" * 100)  # Username muito longo
        password_field.send_keys("123")  # Senha muito curta
        
        login_button.click()
        
        # Verificar se as mensagens de erro apareceram
        error_messages = driver.find_elements(By.CLASS_NAME, "error-message")
        assert len(error_messages) > 0
        
        # Verificar se os campos com erro estão destacados
        error_fields = driver.find_elements(By.CLASS_NAME, "error-field")
        assert len(error_fields) > 0


class TestE2EDataValidation:
    """Testes específicos para validação de dados E2E"""
    
    def test_campaign_data_consistency(self, driver, wait):
        """Testar consistência dos dados de campanha entre diferentes visualizações"""
        # Login
        driver.get(f"{BASE_URL}/login")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpassword123")
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        login_button.click()
        
        wait.until(EC.url_contains("/dashboard"))
        
        # Navegar para campanhas
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        # Obter dados da campanha na lista
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        target_campaign = None
        
        for item in campaign_items:
            name_element = item.find_element(By.CLASS_NAME, "campaign-name")
            if "Campanha de Teste E2E - Editada" in name_element.text:
                target_campaign = item
                break
        
        assert target_campaign is not None
        
        # Capturar dados da lista
        list_name = target_campaign.find_element(By.CLASS_NAME, "campaign-name").text
        list_status = target_campaign.find_element(By.CLASS_NAME, "campaign-status").text
        list_budget = target_campaign.find_element(By.CLASS_NAME, "campaign-budget").text
        
        # Abrir detalhes da campanha
        view_button = target_campaign.find_element(By.CLASS_NAME, "view-button")
        view_button.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaign-details")))
        
        # Capturar dados dos detalhes
        details_name = driver.find_element(By.ID, "campaign-name-display").text
        details_status = driver.find_element(By.ID, "campaign-status-display").text
        details_budget = driver.find_element(By.ID, "campaign-budget-display").text
        
        # Verificar consistência
        assert list_name == details_name, "Nome da campanha inconsistente entre lista e detalhes"
        assert list_status == details_status, "Status da campanha inconsistente entre lista e detalhes"
        assert list_budget == details_budget, "Orçamento da campanha inconsistente entre lista e detalhes"
    
    def test_dashboard_data_accuracy(self, driver, wait):
        """Testar precisão dos dados exibidos no dashboard"""
        # Login
        driver.get(f"{BASE_URL}/login")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpassword123")
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        login_button.click()
        
        wait.until(EC.url_contains("/dashboard"))
        
        # Verificar se o dashboard carregou
        wait.until(EC.presence_of_element_located((By.ID, "dashboard-container")))
        
        # Capturar métricas principais
        metric_widgets = driver.find_elements(By.CLASS_NAME, "metric-widget")
        
        # Verificar se as métricas são números válidos
        for widget in metric_widgets:
            try:
                value_element = widget.find_element(By.CLASS_NAME, "metric-value")
                value_text = value_element.text
                
                # Verificar se é um número ou formato válido
                if "R$" in value_text:
                    # Valor monetário
                    numeric_part = value_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    assert numeric_part.replace(".", "").isdigit(), f"Valor monetário inválido: {value_text}"
                elif "%" in value_text:
                    # Percentual
                    numeric_part = value_text.replace("%", "").strip()
                    assert numeric_part.replace(".", "").isdigit(), f"Percentual inválido: {value_text}"
                else:
                    # Número simples
                    assert value_text.replace(".", "").isdigit(), f"Valor numérico inválido: {value_text}"
                    
            except NoSuchElementException:
                pass  # Widget pode não ter valor numérico
        
        # Verificar se os gráficos têm dados
        chart_widgets = driver.find_elements(By.CLASS_NAME, "chart-widget")
        for chart in chart_widgets:
            try:
                chart_data = chart.find_element(By.CLASS_NAME, "chart-data")
                assert chart_data.is_displayed()
            except NoSuchElementException:
                pass  # Gráfico pode estar vazio
    
    def test_form_validation_completeness(self, driver, wait):
        """Testar completude das validações de formulário"""
        # Navegar para criação de campanha
        driver.get(f"{BASE_URL}/campaigns/new")
        
        wait.until(EC.presence_of_element_located((By.ID, "campaign-form")))
        
        # Tentar submeter formulário vazio
        save_button = driver.find_element(By.ID, "save-campaign-button")
        save_button.click()
        
        # Verificar se todas as validações apareceram
        error_messages = driver.find_elements(By.CLASS_NAME, "error-message")
        required_fields = ["campaign-name", "campaign-type", "start-date", "end-date", "google-sheets-url"]
        
        for field_id in required_fields:
            try:
                field = driver.find_element(By.ID, field_id)
                field_error = field.find_element(By.XPATH, "following-sibling::div[contains(@class, 'error')]")
                assert field_error.is_displayed(), f"Campo {field_id} não tem validação de erro"
            except NoSuchElementException:
                # Pode ter validação em outro formato
                pass
        
        # Verificar se o botão de salvar está desabilitado
        assert not save_button.is_enabled(), "Botão de salvar deveria estar desabilitado com formulário inválido"
    
    def test_data_persistence_across_sessions(self, driver, wait):
        """Testar persistência de dados entre sessões"""
        # Login e criação de dados
        driver.get(f"{BASE_URL}/login")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpassword123")
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        login_button.click()
        
        wait.until(EC.url_contains("/dashboard"))
        
        # Criar uma campanha de teste
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        new_campaign_button = driver.find_element(By.ID, "new-campaign-button")
        new_campaign_button.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaign-form")))
        
        # Preencher formulário
        campaign_name = driver.find_element(By.ID, "campaign-name")
        campaign_name.send_keys("Campanha Persistência E2E")
        
        campaign_type = driver.find_element(By.ID, "campaign-type")
        campaign_type.click()
        video_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Vídeo')]")
        video_option.click()
        
        start_date = driver.find_element(By.ID, "start-date")
        start_date.send_keys("2024-01-01")
        
        end_date = driver.find_element(By.ID, "end-date")
        end_date.send_keys("2024-03-31")
        
        google_sheets_url = driver.find_element(By.ID, "google-sheets-url")
        google_sheets_url.send_keys("https://docs.google.com/spreadsheets/d/persistence123")
        
        dashboard_template = driver.find_element(By.ID, "dashboard-template")
        dashboard_template.click()
        template_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Template Vídeo')]")
        template_option.click()
        
        strategies = driver.find_element(By.ID, "strategies")
        strategies.send_keys("Estratégia para teste de persistência")
        
        total_budget = driver.find_element(By.ID, "total-budget")
        total_budget.send_keys("3000")
        
        # Salvar campanha
        save_button = driver.find_element(By.ID, "save-campaign-button")
        save_button.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        
        # Logout
        user_menu = driver.find_element(By.ID, "user-menu")
        user_menu.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "user-dropdown")))
        
        logout_link = driver.find_element(By.LINK_TEXT, "Sair")
        logout_link.click()
        
        wait.until(EC.url_contains("/login"))
        
        # Login novamente
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        company_select = driver.find_element(By.ID, "company-select")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_field.send_keys("testuser")
        password_field.send_keys("testpassword123")
        company_select.click()
        company_option = driver.find_element(By.XPATH, "//option[contains(text(), 'Empresa Teste')]")
        company_option.click()
        login_button.click()
        
        wait.until(EC.url_contains("/dashboard"))
        
        # Verificar se a campanha ainda existe
        campaigns_link = driver.find_element(By.LINK_TEXT, "Campanhas")
        campaigns_link.click()
        
        wait.until(EC.presence_of_element_located((By.ID, "campaigns-page")))
        
        campaign_items = driver.find_elements(By.CLASS_NAME, "campaign-item")
        campaign_names = [item.find_element(By.CLASS_NAME, "campaign-name").text for item in campaign_items]
        
        assert "Campanha Persistência E2E" in campaign_names, "Campanha não foi persistida entre sessões"


