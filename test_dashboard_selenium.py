#!/usr/bin/env python3
"""
Script para testar o dashboard com Selenium e verificar se os dados estão aparecendo
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_dashboard():
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        print("🚀 Iniciando teste do dashboard com Selenium...")
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # Abrir o dashboard
        dashboard_path = "file:///Users/lucianoterres/Documents/GitHub/south-media-ia/static/dash_multicanal_spotify_programatica.html"
        print(f"📂 Abrindo dashboard: {dashboard_path}")
        driver.get(dashboard_path)
        
        # Aguardar carregamento
        time.sleep(3)
        
        print("🔍 Verificando elementos do dashboard...")
        
        # Verificar título
        try:
            title = driver.find_element(By.TAG_NAME, "title")
            print(f"✅ Título: {title.get_attribute('textContent')}")
        except NoSuchElementException:
            print("❌ Título não encontrado")
        
        # Verificar nome da campanha
        try:
            campaign_name = driver.find_element(By.XPATH, "//div[contains(text(), 'Feira do Empreendedor')]")
            print(f"✅ Nome da campanha: {campaign_name.text}")
        except NoSuchElementException:
            print("❌ Nome da campanha 'Feira do Empreendedor' não encontrado")
        
        # Verificar abas
        try:
            tabs = driver.find_elements(By.CLASS_NAME, "tab")
            print(f"✅ Abas encontradas: {len(tabs)}")
            for tab in tabs:
                print(f"   - {tab.text}")
        except NoSuchElementException:
            print("❌ Abas não encontradas")
        
        # Verificar dados na aba Overview
        print("\n📊 Verificando dados na aba Overview...")
        try:
            # Verificar métricas principais
            metrics = driver.find_elements(By.CLASS_NAME, "metric")
            print(f"✅ Métricas encontradas: {len(metrics)}")
            
            if len(metrics) > 0:
                for i, metric in enumerate(metrics[:5]):  # Primeiras 5 métricas
                    try:
                        label = metric.find_element(By.CLASS_NAME, "label").text
                        value = metric.find_element(By.CLASS_NAME, "value").text
                        print(f"   {i+1}. {label}: {value}")
                    except NoSuchElementException:
                        print(f"   {i+1}. Métrica sem label/value")
            else:
                print("❌ Nenhuma métrica encontrada")
                
        except NoSuchElementException:
            print("❌ Seção de métricas não encontrada")
        
        # Verificar tabela de canais
        try:
            table_rows = driver.find_elements(By.CSS_SELECTOR, "#tbodyChannels tr")
            print(f"✅ Linhas na tabela de canais: {len(table_rows)}")
            
            if len(table_rows) > 0:
                for i, row in enumerate(table_rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        channel = cells[0].text if len(cells) > 0 else "N/A"
                        print(f"   {i+1}. Canal: {channel}")
            else:
                print("❌ Nenhuma linha na tabela de canais")
                
        except NoSuchElementException:
            print("❌ Tabela de canais não encontrada")
        
        # Testar aba "Por Canal"
        print("\n🧭 Testando aba 'Por Canal'...")
        try:
            channels_tab = driver.find_element(By.XPATH, "//div[contains(text(), 'Por Canal')]")
            channels_tab.click()
            time.sleep(2)
            
            # Verificar se há dropdown de seleção
            try:
                channel_select = driver.find_element(By.ID, "channelSelect")
                options = channel_select.find_elements(By.TAG_NAME, "option")
                print(f"✅ Opções de canal: {len(options)}")
                for option in options:
                    print(f"   - {option.text}")
            except NoSuchElementException:
                print("❌ Dropdown de seleção de canal não encontrado")
                
        except NoSuchElementException:
            print("❌ Aba 'Por Canal' não encontrada")
        
        # Testar aba "Análise & Insights"
        print("\n📊 Testando aba 'Análise & Insights'...")
        try:
            insights_tab = driver.find_element(By.XPATH, "//div[contains(text(), 'Análise & Insights')]")
            insights_tab.click()
            time.sleep(2)
            
            # Verificar se há insights
            try:
                insights_cards = driver.find_element(By.ID, "insightsCards")
                insights_items = insights_cards.find_elements(By.TAG_NAME, "li")
                print(f"✅ Insights encontrados: {len(insights_items)}")
                for i, item in enumerate(insights_items):
                    print(f"   {i+1}. {item.text[:100]}...")
            except NoSuchElementException:
                print("❌ Lista de insights não encontrada")
                
        except NoSuchElementException:
            print("❌ Aba 'Análise & Insights' não encontrada")
        
        # Testar aba "Planejamento"
        print("\n📋 Testando aba 'Planejamento'...")
        try:
            planning_tab = driver.find_element(By.XPATH, "//div[contains(text(), 'Planejamento')]")
            planning_tab.click()
            time.sleep(2)
            
            # Verificar se há dados do DoubleVerify
            try:
                doubleverify = driver.find_element(By.XPATH, "//h3[contains(text(), 'DoubleVerify')]")
                print("✅ Seção DoubleVerify encontrada")
            except NoSuchElementException:
                print("❌ Seção DoubleVerify não encontrada")
                
            # Verificar se há lista de sites premium
            try:
                sites_premium = driver.find_element(By.XPATH, "//h3[contains(text(), 'Lista de Sites Premium')]")
                print("✅ Lista de Sites Premium encontrada")
            except NoSuchElementException:
                print("❌ Lista de Sites Premium não encontrada")
                
        except NoSuchElementException:
            print("❌ Aba 'Planejamento' não encontrada")
        
        # Verificar se há erros no console
        print("\n🔍 Verificando erros no console...")
        logs = driver.get_log('browser')
        if logs:
            print(f"⚠️ {len(logs)} mensagens no console:")
            for log in logs[-5:]:  # Últimas 5 mensagens
                print(f"   {log['level']}: {log['message']}")
        else:
            print("✅ Nenhuma mensagem de erro no console")
        
        # Tirar screenshot
        screenshot_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/dashboard_test_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot salvo em: {screenshot_path}")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_dashboard()
