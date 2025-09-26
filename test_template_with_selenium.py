#!/usr/bin/env python3
"""
Teste automatizado com Selenium para validar o template genérico
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TemplateValidator:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
    
    def setup_driver(self):
        """Configurar o driver do Chrome"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Executar sem interface gráfica
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Driver do Chrome configurado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def test_dashboard_loading(self, url):
        """Testar carregamento do dashboard"""
        print(f"\n🔍 Testando carregamento: {url}")
        
        try:
            self.driver.get(url)
            
            # Aguardar carregamento da página
            time.sleep(3)
            
            # Verificar se a página carregou
            if "Dashboard" in self.driver.title:
                print("✅ Título da página correto")
                self.results["tests_passed"] += 1
            else:
                print(f"❌ Título incorreto: {self.driver.title}")
                self.results["tests_failed"] += 1
                self.results["errors"].append(f"Título incorreto: {self.driver.title}")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar página: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro ao carregar: {e}")
            return False
    
    def test_south_media_branding(self):
        """Testar se o branding South Media está presente"""
        print("\n🎨 Testando branding South Media...")
        
        try:
            # Verificar logo South Media
            logo = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'South Media')]")))
            if logo:
                print("✅ Logo South Media encontrado")
                self.results["tests_passed"] += 1
            else:
                print("❌ Logo South Media não encontrado")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Logo South Media não encontrado")
            
            # Verificar ícone SM
            icon = self.driver.find_element(By.XPATH, "//div[contains(@class, 'logo-icon')]")
            if icon and icon.text == "SM":
                print("✅ Ícone SM encontrado")
                self.results["tests_passed"] += 1
            else:
                print("❌ Ícone SM não encontrado")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Ícone SM não encontrado")
                
        except NoSuchElementException:
            print("❌ Elementos de branding não encontrados")
            self.results["tests_failed"] += 1
            self.results["errors"].append("Elementos de branding não encontrados")
        except Exception as e:
            print(f"❌ Erro ao testar branding: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro no branding: {e}")
    
    def test_navigation_tabs(self):
        """Testar navegação por tabs"""
        print("\n📋 Testando navegação por tabs...")
        
        try:
            # Verificar se as tabs existem
            tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab")
            if len(tabs) == 4:
                print("✅ 4 tabs encontradas")
                self.results["tests_passed"] += 1
            else:
                print(f"❌ Número incorreto de tabs: {len(tabs)}")
                self.results["tests_failed"] += 1
                self.results["errors"].append(f"Número incorreto de tabs: {len(tabs)}")
            
            # Testar clique nas tabs
            tab_names = ["Visão Geral", "Por Canal", "Análise & Insights", "Planejamento"]
            for i, tab_name in enumerate(tab_names):
                try:
                    tab = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{tab_name}')]")
                    tab.click()
                    time.sleep(1)
                    print(f"✅ Tab '{tab_name}' clicável")
                    self.results["tests_passed"] += 1
                except NoSuchElementException:
                    print(f"❌ Tab '{tab_name}' não encontrada")
                    self.results["tests_failed"] += 1
                    self.results["errors"].append(f"Tab '{tab_name}' não encontrada")
                    
        except Exception as e:
            print(f"❌ Erro ao testar tabs: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro nas tabs: {e}")
    
    def test_responsive_design(self):
        """Testar design responsivo"""
        print("\n📱 Testando design responsivo...")
        
        try:
            # Testar diferentes tamanhos de tela
            sizes = [
                (1920, 1080),  # Desktop
                (768, 1024),   # Tablet
                (375, 667)     # Mobile
            ]
            
            for width, height in sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Verificar se o container principal existe
                container = self.driver.find_element(By.CSS_SELECTOR, ".container")
                if container:
                    print(f"✅ Layout responsivo OK para {width}x{height}")
                    self.results["tests_passed"] += 1
                else:
                    print(f"❌ Layout quebrado para {width}x{height}")
                    self.results["tests_failed"] += 1
                    self.results["errors"].append(f"Layout quebrado para {width}x{height}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar responsividade: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro na responsividade: {e}")
    
    def test_css_styling(self):
        """Testar se o CSS está aplicado corretamente"""
        print("\n🎨 Testando CSS e estilização...")
        
        try:
            # Verificar se as variáveis CSS estão aplicadas
            bg_color = self.driver.execute_script("return getComputedStyle(document.documentElement).getPropertyValue('--bg')")
            if bg_color and "#0F1023" in bg_color:
                print("✅ Variáveis CSS aplicadas")
                self.results["tests_passed"] += 1
            else:
                print("❌ Variáveis CSS não aplicadas")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Variáveis CSS não aplicadas")
            
            # Verificar se o gradiente está aplicado
            body = self.driver.find_element(By.TAG_NAME, "body")
            bg_style = self.driver.execute_script("return getComputedStyle(arguments[0]).background", body)
            if "gradient" in bg_style.lower():
                print("✅ Gradiente de fundo aplicado")
                self.results["tests_passed"] += 1
            else:
                print("❌ Gradiente de fundo não aplicado")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Gradiente não aplicado")
                
        except Exception as e:
            print(f"❌ Erro ao testar CSS: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro no CSS: {e}")
    
    def test_api_data_loading(self):
        """Testar se os dados da API estão sendo carregados"""
        print("\n📊 Testando carregamento de dados da API...")
        
        try:
            # Aguardar carregamento dos dados (pode levar alguns segundos)
            time.sleep(5)
            
            # Verificar se há elementos de dados
            metrics = self.driver.find_elements(By.CSS_SELECTOR, ".metric")
            if len(metrics) > 0:
                print(f"✅ {len(metrics)} métricas encontradas")
                self.results["tests_passed"] += 1
            else:
                print("❌ Métricas não encontradas")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Métricas não encontradas")
            
            # Verificar se há tabelas
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if len(tables) > 0:
                print(f"✅ {len(tables)} tabelas encontradas")
                self.results["tests_passed"] += 1
            else:
                print("❌ Tabelas não encontradas")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Tabelas não encontradas")
                
        except Exception as e:
            print(f"❌ Erro ao testar dados da API: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro nos dados: {e}")
    
    def test_javascript_functionality(self):
        """Testar funcionalidades JavaScript"""
        print("\n⚡ Testando funcionalidades JavaScript...")
        
        try:
            # Verificar se Chart.js está carregado
            chart_loaded = self.driver.execute_script("return typeof Chart !== 'undefined'")
            if chart_loaded:
                print("✅ Chart.js carregado")
                self.results["tests_passed"] += 1
            else:
                print("❌ Chart.js não carregado")
                self.results["tests_failed"] += 1
                self.results["errors"].append("Chart.js não carregado")
            
            # Verificar se a classe DashboardLoader existe
            dashboard_loader = self.driver.execute_script("return typeof DashboardLoader !== 'undefined'")
            if dashboard_loader:
                print("✅ DashboardLoader carregado")
                self.results["tests_passed"] += 1
            else:
                print("❌ DashboardLoader não carregado")
                self.results["tests_failed"] += 1
                self.results["errors"].append("DashboardLoader não carregado")
                
        except Exception as e:
            print(f"❌ Erro ao testar JavaScript: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Erro no JavaScript: {e}")
    
    def run_all_tests(self, urls):
        """Executar todos os testes"""
        print("🚀 Iniciando testes automatizados do template genérico...")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            for url in urls:
                print(f"\n🌐 Testando: {url}")
                print("-" * 40)
                
                if self.test_dashboard_loading(url):
                    self.test_south_media_branding()
                    self.test_navigation_tabs()
                    self.test_responsive_design()
                    self.test_css_styling()
                    self.test_api_data_loading()
                    self.test_javascript_functionality()
                
                print("-" * 40)
        
        finally:
            self.driver.quit()
        
        # Mostrar resultados
        self.show_results()
        return True
    
    def show_results(self):
        """Mostrar resultados dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DOS TESTES")
        print("=" * 60)
        
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Testes aprovados: {self.results['tests_passed']}")
        print(f"❌ Testes falharam: {self.results['tests_failed']}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n⚠️ ERROS ENCONTRADOS:")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"  {i}. {error}")
        
        if success_rate >= 90:
            print(f"\n🎉 TEMPLATE GENÉRICO APROVADO! ({success_rate:.1f}%)")
        elif success_rate >= 70:
            print(f"\n⚠️ TEMPLATE COM PROBLEMAS MENORES ({success_rate:.1f}%)")
        else:
            print(f"\n❌ TEMPLATE PRECISA DE CORREÇÕES ({success_rate:.1f}%)")

def main():
    """Função principal"""
    # URLs para testar
    urls = [
        "http://localhost:5001/static/dash_template_final_test.html",
        "http://localhost:5001/static/dash_sebrae_pr_institucional_setembro.html",
        "http://localhost:5001/static/dash_teste_template_generico.html"
    ]
    
    validator = TemplateValidator()
    validator.run_all_tests(urls)

if __name__ == "__main__":
    main()

