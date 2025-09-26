#!/usr/bin/env python3
"""
Teste End-to-End com Selenium para o Gerador de Dashboards
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_dashboard_generator():
    """Teste completo do gerador de dashboards"""
    
    print("🚀 Iniciando teste End-to-End com Selenium...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Inicializar driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 1. Acessar a interface do gerador
        print("📱 Acessando interface do gerador...")
        driver.get("http://localhost:5002/test-generator")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("✅ Interface carregada com sucesso")
        
        # 2. Preencher formulário
        print("📝 Preenchendo formulário...")
        
        # Cliente
        client_field = driver.find_element(By.NAME, "client")
        client_field.clear()
        client_field.send_keys("Copacol")
        
        # Nome da Campanha
        campaign_field = driver.find_element(By.NAME, "campaign_name")
        campaign_field.clear()
        campaign_field.send_keys("Institucional 30s")
        
        # ID da Planilha
        sheet_field = driver.find_element(By.NAME, "sheet_id")
        sheet_field.clear()
        sheet_field.send_keys("1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8")
        
        # Canal (selecionar Video Programática)
        canal_select = driver.find_element(By.NAME, "channel")
        canal_select.send_keys("Video Programática")
        
        print("✅ Formulário preenchido")
        
        # 3. Clicar em Gerar Dashboard
        print("🚀 Clicando em 'Gerar Dashboard'...")
        generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Gerar Dashboard')]")
        generate_button.click()
        
        # 4. Aguardar resultado
        print("⏳ Aguardando resultado...")
        time.sleep(5)
        
        # 5. Verificar se houve erro
        try:
            error_element = driver.find_element(By.CLASS_NAME, "error")
            error_text = error_element.text
            print(f"❌ ERRO ENCONTRADO: {error_text}")
            return False
        except:
            print("✅ Nenhum erro visível na interface")
        
        # 6. Verificar se dashboard foi gerado
        try:
            success_element = driver.find_element(By.CLASS_NAME, "success")
            success_text = success_element.text
            print(f"✅ SUCESSO: {success_text}")
        except:
            print("⚠️ Nenhuma mensagem de sucesso encontrada")
        
        # 7. Verificar logs do console
        print("🔍 Verificando logs do console...")
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"❌ ERRO NO CONSOLE: {log['message']}")
        
        # 8. Testar API diretamente
        print("🔧 Testando API diretamente...")
        driver.get("http://localhost:5002/api/copacol_institucional_30s/data")
        
        # Aguardar resposta
        time.sleep(2)
        
        # Verificar se a resposta é JSON válido
        try:
            page_source = driver.page_source
            if "success" in page_source:
                print("✅ API retornou resposta válida")
                # Tentar extrair dados JSON
                json_start = page_source.find('{')
                json_end = page_source.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = page_source[json_start:json_end]
                    data = json.loads(json_str)
                    if data.get('success'):
                        print("✅ API funcionando corretamente")
                        print(f"📊 Dados: {len(data.get('data', {}).get('daily_data', []))} registros")
                    else:
                        print(f"❌ API retornou erro: {data.get('message', 'Erro desconhecido')}")
            else:
                print("❌ API não retornou resposta válida")
        except Exception as e:
            print(f"❌ Erro ao processar resposta da API: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        return False
        
    finally:
        driver.quit()
        print("🔚 Teste finalizado")

if __name__ == "__main__":
    success = test_dashboard_generator()
    if success:
        print("🎉 Teste concluído com sucesso!")
    else:
        print("💥 Teste falhou!")
