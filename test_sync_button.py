#!/usr/bin/env python3
"""
Script para testar o botão de sync no painel de controle usando Selenium
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """Configurar o driver do Chrome com opções otimizadas"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Executar sem interface gráfica
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("✅ Driver do Chrome configurado com sucesso")
        return driver
    except Exception as e:
        logger.error(f"❌ Erro ao configurar driver: {e}")
        return None

def navigate_to_control_panel(driver):
    """Navegar para o painel de controle"""
    try:
        url = "https://dash.iasouth.tech/"
        logger.info(f"🌐 Navegando para: {url}")
        
        driver.get(url)
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        logger.info("✅ Página carregada com sucesso")
        return True
        
    except TimeoutException:
        logger.error("❌ Timeout ao carregar a página")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao navegar: {e}")
        return False

def wait_for_dashboards_load(driver):
    """Aguardar carregamento dos dashboards"""
    try:
        logger.info("⏳ Aguardando carregamento dos dashboards...")
        
        # Aguardar desaparecer o loading state (se existir)
        try:
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.ID, "loadingState"))
            )
            logger.info("✅ Loading state desapareceu")
        except TimeoutException:
            logger.warning("⚠️ Loading state não encontrado ou já desapareceu")
        
        # Aguardar aparecer os cards dos dashboards com timeout maior
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard-card"))
            )
            logger.info("✅ Cards de dashboard carregados")
        except TimeoutException:
            # Tentar encontrar elementos alternativos
            logger.warning("⚠️ Tentando encontrar elementos alternativos...")
            cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
            if not cards:
                cards = driver.find_elements(By.CSS_SELECTOR, "[class*='dashboard']")
            if not cards:
                cards = driver.find_elements(By.CSS_SELECTOR, "[class*='card']")
            
            if cards:
                logger.info(f"✅ Encontrados {len(cards)} cards alternativos")
            else:
                logger.error("❌ Nenhum card encontrado")
                return False
        
        logger.info("✅ Dashboards carregados com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao aguardar dashboards: {e}")
        return False

def find_sonho_dashboard_card(driver):
    """Encontrar o card do Dashboard Sonho"""
    try:
        logger.info("🔍 Procurando card do Dashboard Sonho...")
        
        # Procurar por cards de dashboard
        dashboard_cards = driver.find_elements(By.CLASS_NAME, "dashboard-card")
        logger.info(f"📊 Encontrados {len(dashboard_cards)} cards de dashboard")
        
        # Procurar o card que contém "Dashboard Sonho"
        for card in dashboard_cards:
            try:
                title_element = card.find_element(By.CLASS_NAME, "card-title")
                title_text = title_element.text
                logger.info(f"📋 Card encontrado: {title_text}")
                
                if "Dashboard Sonho" in title_text:
                    logger.info("✅ Card do Dashboard Sonho encontrado!")
                    return card
                    
            except NoSuchElementException:
                continue
                
        logger.error("❌ Card do Dashboard Sonho não encontrado")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao procurar card: {e}")
        return None

def click_sync_button(driver, card):
    """Clicar no botão de sync"""
    try:
        logger.info("🔄 Procurando botão de sync...")
        
        # Procurar botão de sync dentro do card
        sync_button = card.find_element(By.CLASS_NAME, "sync-button")
        logger.info("✅ Botão de sync encontrado!")
        
        # Verificar se o botão está habilitado
        if not sync_button.is_enabled():
            logger.warning("⚠️ Botão de sync está desabilitado")
            return False
            
        # Fazer scroll para o botão
        driver.execute_script("arguments[0].scrollIntoView(true);", sync_button)
        time.sleep(1)
        
        # Clicar no botão
        logger.info("🖱️ Clicando no botão de sync...")
        sync_button.click()
        
        logger.info("✅ Botão de sync clicado com sucesso!")
        return True
        
    except NoSuchElementException:
        logger.error("❌ Botão de sync não encontrado no card")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao clicar no botão: {e}")
        return False

def monitor_sync_progress(driver, card):
    """Monitorar o progresso da sincronização"""
    try:
        logger.info("👀 Monitorando progresso da sincronização...")
        
        sync_button = card.find_element(By.CLASS_NAME, "sync-button")
        
        # Monitorar mudanças no botão por até 120 segundos
        start_time = time.time()
        timeout = 120
        
        while time.time() - start_time < timeout:
            try:
                button_text = sync_button.text
                button_enabled = sync_button.is_enabled()
                
                logger.info(f"🔄 Status do botão: '{button_text}' (habilitado: {button_enabled})")
                
                # Verificar se a sincronização foi concluída
                if "Concluído" in button_text or "Erro" in button_text:
                    if "Concluído" in button_text:
                        logger.info("🎉 Sincronização concluída com sucesso!")
                        return True
                    else:
                        logger.error("❌ Sincronização falhou!")
                        return False
                        
                # Aguardar antes da próxima verificação
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar status: {e}")
                time.sleep(3)
                
        logger.error("❌ Timeout ao aguardar conclusão da sincronização")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao monitorar progresso: {e}")
        return False

def take_screenshot(driver, filename):
    """Tirar screenshot da página"""
    try:
        driver.save_screenshot(filename)
        logger.info(f"📸 Screenshot salvo: {filename}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar screenshot: {e}")
        return False

def debug_page_content(driver):
    """Fazer debug do conteúdo da página"""
    try:
        logger.info("🔍 Fazendo debug do conteúdo da página...")
        
        # Verificar título da página
        title = driver.title
        logger.info(f"📄 Título da página: {title}")
        
        # Verificar elementos presentes
        body = driver.find_element(By.TAG_NAME, "body")
        logger.info(f"📝 Texto da página: {body.text[:200]}...")
        
        # Verificar classes CSS presentes
        elements_with_classes = driver.find_elements(By.CSS_SELECTOR, "[class]")
        classes_found = set()
        for element in elements_with_classes:
            class_attr = element.get_attribute("class")
            if class_attr:
                classes_found.update(class_attr.split())
        
        logger.info(f"🎨 Classes CSS encontradas: {list(classes_found)[:10]}...")
        
        # Salvar HTML da página
        with open("page_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("💾 HTML da página salvo em: page_debug.html")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no debug: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando teste do botão de sync no painel de controle...")
    
    driver = None
    try:
        # Configurar driver
        driver = setup_driver()
        if not driver:
            return False
            
        # Navegar para o painel de controle
        if not navigate_to_control_panel(driver):
            return False
            
        # Tirar screenshot inicial
        take_screenshot(driver, "control_panel_initial.png")
        
        # Fazer debug do conteúdo da página
        debug_page_content(driver)
        
        # Aguardar carregamento dos dashboards
        if not wait_for_dashboards_load(driver):
            return False
            
        # Tirar screenshot após carregamento
        take_screenshot(driver, "control_panel_loaded.png")
        
        # Encontrar card do Dashboard Sonho
        sonho_card = find_sonho_dashboard_card(driver)
        if not sonho_card:
            return False
            
        # Tirar screenshot do card encontrado
        take_screenshot(driver, "sonho_card_found.png")
        
        # Clicar no botão de sync
        if not click_sync_button(driver, sonho_card):
            return False
            
        # Tirar screenshot após clicar
        take_screenshot(driver, "sync_button_clicked.png")
        
        # Monitorar progresso da sincronização
        success = monitor_sync_progress(driver, sonho_card)
        
        # Tirar screenshot final
        take_screenshot(driver, "sync_completed.png")
        
        if success:
            logger.info("🎉 Teste do botão de sync concluído com SUCESSO!")
        else:
            logger.error("❌ Teste do botão de sync FALHOU!")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        return False
        
    finally:
        if driver:
            logger.info("🔚 Fechando driver...")
            driver.quit()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
