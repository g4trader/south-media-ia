#!/usr/bin/env python3
"""
Teste de Diagnóstico Detalhado
Investiga problemas específicos identificados na verificação crítica
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostico_detalhado.log'),
        logging.StreamHandler()
    ]
)

class DiagnosticoDetalhado:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self, headless=True):
        """Configurar o driver do Selenium"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            logging.info("✅ Driver do Selenium configurado com sucesso")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def diagnosticar_homepage(self):
        """Diagnosticar problemas na homepage"""
        logging.info("🔍 DIAGNÓSTICO: Homepage")
        
        try:
            self.driver.get("https://dash.iasouth.tech")
            time.sleep(5)
            
            # Verificar título
            title = self.driver.title
            logging.info(f"📄 Título da página: {title}")
            
            # Verificar se há erros JavaScript
            logs = self.driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            if js_errors:
                logging.error(f"🚨 Erros JavaScript encontrados: {len(js_errors)}")
                for error in js_errors:
                    logging.error(f"   - {error['message']}")
            
            # Verificar dashboards
            dashboard_cards = self.driver.find_elements(By.CLASS_NAME, "dashboard-card")
            logging.info(f"📊 Dashboards encontrados: {len(dashboard_cards)}")
            
            if len(dashboard_cards) > 0:
                # Testar clicabilidade do primeiro dashboard
                first_card = dashboard_cards[0]
                logging.info(f"🎯 Testando clicabilidade do dashboard: {first_card.text[:50]}...")
                
                try:
                    # Verificar se o card é clicável
                    if first_card.is_enabled() and first_card.is_displayed():
                        logging.info("✅ Dashboard está habilitado e visível")
                        
                        # Tentar clicar
                        original_url = self.driver.current_url
                        first_card.click()
                        time.sleep(3)
                        
                        new_url = self.driver.current_url
                        if new_url != original_url:
                            logging.info(f"✅ Dashboard clicável - redirecionou para: {new_url}")
                        else:
                            logging.warning("⚠️ Dashboard clicado mas não redirecionou")
                    else:
                        logging.error("❌ Dashboard não está habilitado ou visível")
                        
                except Exception as e:
                    logging.error(f"❌ Erro ao clicar no dashboard: {e}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no diagnóstico da homepage: {e}")
            return False
    
    def diagnosticar_login(self):
        """Diagnosticar problemas no login"""
        logging.info("🔍 DIAGNÓSTICO: Sistema de Login")
        
        try:
            self.driver.get("https://dash.iasouth.tech/login.html")
            time.sleep(5)
            
            # Verificar se a página carregou
            title = self.driver.title
            logging.info(f"📄 Título da página de login: {title}")
            
            # Verificar erros JavaScript
            logs = self.driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            if js_errors:
                logging.error(f"🚨 Erros JavaScript na página de login: {len(js_errors)}")
                for error in js_errors:
                    logging.error(f"   - {error['message']}")
            
            # Verificar elementos do formulário
            try:
                username_field = self.driver.find_element(By.ID, "username")
                logging.info("✅ Campo username encontrado")
            except NoSuchElementException:
                logging.error("❌ Campo username NÃO encontrado")
                return False
            
            try:
                password_field = self.driver.find_element(By.ID, "password")
                logging.info("✅ Campo password encontrado")
            except NoSuchElementException:
                logging.error("❌ Campo password NÃO encontrado")
                return False
            
            try:
                login_button = self.driver.find_element(By.ID, "loginButton")
                logging.info("✅ Botão de login encontrado")
            except NoSuchElementException:
                logging.error("❌ Botão de login NÃO encontrado")
                return False
            
            # Verificar se o sistema de autenticação está carregado
            auth_system_loaded = self.driver.execute_script("return typeof window.authSystem !== 'undefined';")
            logging.info(f"🔐 Sistema de autenticação carregado: {auth_system_loaded}")
            
            if auth_system_loaded:
                is_initialized = self.driver.execute_script("return window.authSystem.isInitialized;")
                logging.info(f"🔄 Sistema inicializado: {is_initialized}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no diagnóstico do login: {e}")
            return False
    
    def diagnosticar_paginas_protegidas(self):
        """Diagnosticar problemas nas páginas protegidas"""
        logging.info("🔍 DIAGNÓSTICO: Páginas Protegidas")
        
        try:
            # Limpar sessão
            self.driver.delete_all_cookies()
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            # Testar acesso sem login
            protected_pages = [
                "https://dash.iasouth.tech/dashboard-protected.html",
                "https://dash.iasouth.tech/users.html",
                "https://dash.iasouth.tech/companies.html"
            ]
            
            for page in protected_pages:
                logging.info(f"🔒 Testando acesso a: {page}")
                self.driver.get(page)
                time.sleep(3)
                
                current_url = self.driver.current_url
                logging.info(f"📍 URL atual: {current_url}")
                
                # Verificar se há alertas
                try:
                    alert = Alert(self.driver)
                    alert_text = alert.text
                    logging.info(f"🚨 Alerta encontrado: {alert_text}")
                    alert.accept()
                except:
                    logging.info("✅ Nenhum alerta encontrado")
                
                # Verificar se redirecionou para login
                if "login.html" in current_url:
                    logging.info("✅ Redirecionamento de segurança funcionando")
                else:
                    logging.warning(f"⚠️ Página {page} acessível sem login")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no diagnóstico das páginas protegidas: {e}")
            return False
    
    def diagnosticar_carregamento_completo(self):
        """Diagnosticar problemas de carregamento completo"""
        logging.info("🔍 DIAGNÓSTICO: Carregamento Completo")
        
        try:
            # Testar carregamento com timeout maior
            self.driver.set_page_load_timeout(30)
            
            pages_to_test = [
                "https://dash.iasouth.tech",
                "https://dash.iasouth.tech/login.html",
                "https://dash.iasouth.tech/dashboard-protected.html"
            ]
            
            for page in pages_to_test:
                logging.info(f"⏱️ Testando carregamento de: {page}")
                
                start_time = time.time()
                self.driver.get(page)
                load_time = time.time() - start_time
                
                logging.info(f"⏱️ Tempo de carregamento: {load_time:.2f}s")
                
                # Verificar se a página carregou completamente
                ready_state = self.driver.execute_script("return document.readyState;")
                logging.info(f"📄 Estado da página: {ready_state}")
                
                # Verificar erros JavaScript
                logs = self.driver.get_log('browser')
                js_errors = [log for log in logs if log['level'] == 'SEVERE']
                if js_errors:
                    logging.error(f"🚨 Erros JavaScript: {len(js_errors)}")
                    for error in js_errors[:3]:  # Mostrar apenas os primeiros 3
                        logging.error(f"   - {error['message']}")
                
                time.sleep(2)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro no diagnóstico de carregamento: {e}")
            return False
    
    def executar_diagnostico_completo(self):
        """Executar diagnóstico completo"""
        if not self.setup_driver(headless=False):  # Usar modo não-headless para melhor diagnóstico
            return False
        
        try:
            logging.info("🚀 INICIANDO DIAGNÓSTICO DETALHADO...")
            
            # Executar todos os diagnósticos
            self.diagnosticar_homepage()
            self.diagnosticar_login()
            self.diagnosticar_paginas_protegidas()
            self.diagnosticar_carregamento_completo()
            
            logging.info("✅ Diagnóstico completo finalizado")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro durante diagnóstico: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🧹 Driver encerrado")

def main():
    """Função principal"""
    diagnostico = DiagnosticoDetalhado()
    success = diagnostico.executar_diagnostico_completo()
    
    if success:
        logging.info("🎉 Diagnóstico detalhado concluído!")
    else:
        logging.error("❌ Diagnóstico detalhado falhou!")

if __name__ == "__main__":
    main()
