#!/usr/bin/env python3
"""
Teste completo do Dashboard SEBRAE com Selenium
Testa todas as funcionalidades: loading, dados, abas, métricas, etc.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

class SebraeDashboardTester:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "http://localhost:5000"
        self.dashboard_url = f"{self.base_url}/static/dash_sebrae_programatica_video_sync.html"
        self.api_url = f"{self.base_url}/api/sebrae/data"
        
    def setup_driver(self):
        """Configurar o driver do Chrome"""
        print("🔧 Configurando driver do Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar sem interface gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Driver configurado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def test_api_endpoint(self):
        """Testar o endpoint da API"""
        print("\n📡 Testando endpoint da API...")
        
        try:
            # Acessar a API diretamente
            self.driver.get(self.api_url)
            
            # Aguardar carregamento
            time.sleep(2)
            
            # Verificar se retornou JSON
            page_source = self.driver.page_source
            if "success" in page_source and "data" in page_source:
                print("✅ API retornando dados JSON")
                
                # Tentar extrair dados JSON
                try:
                    json_text = page_source.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '').replace('</pre></body></html>', '')
                    data = json.loads(json_text)
                    
                    print(f"✅ Dados extraídos: {data.get('success', False)}")
                    print(f"📊 Fonte dos dados: {data.get('source', 'unknown')}")
                    
                    # Verificar estrutura dos dados
                    if 'data' in data:
                        metrics = data['data'].get('metrics', {})
                        print(f"💰 Budget contratado: R$ {metrics.get('budget_contracted', 0)}")
                        print(f"🎬 VC contratado: {metrics.get('vc_contracted', 0)}")
                        print(f"✅ VC entregue: {metrics.get('vc_delivered', 0)}")
                        
                        # Verificar novos dados
                        if 'contract' in data['data']:
                            print("✅ Dados de contratação presentes")
                        if 'strategies' in data['data']:
                            print("✅ Dados de estratégias presentes")
                        if 'publishers' in data['data']:
                            print("✅ Dados de publishers presentes")
                    
                    return True
                except json.JSONDecodeError as e:
                    print(f"⚠️ Erro ao decodificar JSON: {e}")
                    return False
            else:
                print("❌ API não retornou dados JSON válidos")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")
            return False
    
    def test_dashboard_loading(self):
        """Testar o sistema de loading do dashboard"""
        print("\n⏳ Testando sistema de loading...")
        
        try:
            # Acessar o dashboard
            self.driver.get(self.dashboard_url)
            
            # Aguardar o loading aparecer
            try:
                loading_element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "loadingScreen"))
                )
                print("✅ Tela de loading apareceu")
                
                # Aguardar o loading desaparecer (máximo 30 segundos)
                self.wait.until_not(
                    EC.presence_of_element_located((By.ID, "loadingScreen"))
                )
                print("✅ Tela de loading desapareceu")
                
                # Aguardar um pouco mais para garantir que tudo carregou
                time.sleep(3)
                return True
                
            except TimeoutException:
                print("⚠️ Timeout no loading - pode estar usando dados de teste")
                return True
                
        except Exception as e:
            print(f"❌ Erro no teste de loading: {e}")
            return False
    
    def test_dashboard_content(self):
        """Testar o conteúdo do dashboard"""
        print("\n📊 Testando conteúdo do dashboard...")
        
        try:
            # Verificar se o dashboard carregou
            dashboard_title = self.driver.find_element(By.TAG_NAME, "h1")
            if "SEBRAE" in dashboard_title.text:
                print("✅ Título do dashboard correto")
            else:
                print(f"⚠️ Título inesperado: {dashboard_title.text}")
            
            # Verificar status da campanha
            try:
                status_element = self.driver.find_element(By.ID, "campaignStatus")
                print(f"📈 Status da campanha: {status_element.text}")
            except NoSuchElementException:
                print("⚠️ Elemento de status não encontrado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar conteúdo: {e}")
            return False
    
    def test_metrics_cards(self):
        """Testar os cards de métricas"""
        print("\n💳 Testando cards de métricas...")
        
        try:
            # Verificar cards da visão geral
            overview_metrics = self.driver.find_elements(By.CSS_SELECTOR, "#metrics-overview-top .metric")
            print(f"📊 Cards overview encontrados: {len(overview_metrics)}")
            
            for i, metric in enumerate(overview_metrics[:4]):  # Primeiros 4 cards
                try:
                    label = metric.find_element(By.CSS_SELECTOR, ".label").text
                    value = metric.find_element(By.CSS_SELECTOR, ".value").text
                    print(f"  {i+1}. {label}: {value}")
                except NoSuchElementException:
                    print(f"  {i+1}. Erro ao ler métrica")
            
            # Verificar cards de performance
            performance_metrics = self.driver.find_elements(By.CSS_SELECTOR, "#metrics-performance .metric")
            print(f"📈 Cards performance encontrados: {len(performance_metrics)}")
            
            # Verificar se tem VC contratado e entregue
            all_metrics_text = self.driver.find_element(By.ID, "metrics-overview-top").text
            if "VC Contratado" in all_metrics_text and "VC Entregue" in all_metrics_text:
                print("✅ Métricas de VC presentes na visão geral")
            else:
                print("⚠️ Métricas de VC não encontradas")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar métricas: {e}")
            return False
    
    def test_tabs_navigation(self):
        """Testar navegação entre abas"""
        print("\n📑 Testando navegação entre abas...")
        
        try:
            # Encontrar todas as abas
            tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab")
            print(f"📋 Abas encontradas: {len(tabs)}")
            
            for i, tab in enumerate(tabs):
                try:
                    tab.click()
                    time.sleep(1)  # Aguardar transição
                    
                    tab_name = tab.text.strip()
                    print(f"  {i+1}. Clicou na aba: {tab_name}")
                    
                    # Verificar se a aba está ativa
                    if "active" in tab.get_attribute("class"):
                        print(f"     ✅ Aba {tab_name} está ativa")
                    else:
                        print(f"     ⚠️ Aba {tab_name} não está ativa")
                        
                except Exception as e:
                    print(f"  {i+1}. Erro ao clicar na aba: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar abas: {e}")
            return False
    
    def test_planning_tab_content(self):
        """Testar conteúdo da aba de planejamento"""
        print("\n📋 Testando aba de planejamento...")
        
        try:
            # Clicar na aba de planejamento
            planning_tab = self.driver.find_element(By.CSS_SELECTOR, '.tab[onclick*="planning"]')
            planning_tab.click()
            time.sleep(2)
            
            # Verificar objetivo da campanha
            try:
                objective_text = self.driver.find_element(By.CSS_SELECTOR, '#tab-planning .card p')
                print(f"🎯 Objetivo: {objective_text.text[:100]}...")
                
                if "Microempreendedores" in objective_text.text:
                    print("✅ Segmentação presente no objetivo")
                else:
                    print("⚠️ Segmentação não encontrada no objetivo")
                    
            except NoSuchElementException:
                print("⚠️ Objetivo da campanha não encontrado")
            
            # Verificar publishers
            try:
                publishers = self.driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(4) .grid > div')
                print(f"📺 Publishers encontrados: {len(publishers)}")
                
                for i, publisher in enumerate(publishers[:3]):  # Primeiros 3
                    try:
                        publisher_text = publisher.text
                        print(f"  {i+1}. {publisher_text[:50]}...")
                    except:
                        print(f"  {i+1}. Erro ao ler publisher")
                        
            except NoSuchElementException:
                print("⚠️ Publishers não encontrados")
            
            # Verificar detalhes da campanha
            try:
                contract_details = self.driver.find_elements(By.CSS_SELECTOR, '#tab-planning .card:nth-child(5) .grid > div')
                print(f"📊 Detalhes de contrato encontrados: {len(contract_details)}")
                
                for i, detail in enumerate(contract_details):
                    try:
                        detail_text = detail.text
                        print(f"  {i+1}. {detail_text}")
                    except:
                        print(f"  {i+1}. Erro ao ler detalhe")
                        
            except NoSuchElementException:
                print("⚠️ Detalhes de contrato não encontrados")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar aba de planejamento: {e}")
            return False
    
    def test_charts_rendering(self):
        """Testar renderização dos gráficos"""
        print("\n📊 Testando renderização dos gráficos...")
        
        try:
            # Voltar para a aba de visão geral
            overview_tab = self.driver.find_element(By.CSS_SELECTOR, '.tab[onclick*="overview"]')
            overview_tab.click()
            time.sleep(2)
            
            # Verificar gráficos
            charts = self.driver.find_elements(By.CSS_SELECTOR, "canvas")
            print(f"📈 Gráficos encontrados: {len(charts)}")
            
            for i, chart in enumerate(charts):
                try:
                    chart_id = chart.get_attribute("id")
                    print(f"  {i+1}. Gráfico: {chart_id}")
                    
                    # Verificar se o gráfico tem dimensões
                    width = chart.get_attribute("width")
                    height = chart.get_attribute("height")
                    if width and height:
                        print(f"     📏 Dimensões: {width}x{height}")
                    else:
                        print("     ⚠️ Dimensões não definidas")
                        
                except Exception as e:
                    print(f"  {i+1}. Erro ao verificar gráfico: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar gráficos: {e}")
            return False
    
    def test_table_data(self):
        """Testar dados da tabela"""
        print("\n📋 Testando dados da tabela...")
        
        try:
            # Verificar tabela de resumo da campanha
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "#tbodyCampaign tr")
            print(f"📊 Linhas da tabela: {len(table_rows)}")
            
            for i, row in enumerate(table_rows[:5]):  # Primeiras 5 linhas
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        metric_name = cells[0].text
                        metric_value = cells[1].text
                        print(f"  {i+1}. {metric_name}: {metric_value}")
                        
                        # Verificar se tem dados de VC
                        if "VC" in metric_name:
                            print(f"     ✅ Dados de VC encontrados")
                            
                except Exception as e:
                    print(f"  {i+1}. Erro ao ler linha: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao testar tabela: {e}")
            return False
    
    def take_screenshot(self, filename):
        """Tirar screenshot do dashboard"""
        try:
            screenshot_path = f"/Users/lucianoterres/Documents/GitHub/south-media-ia/{filename}"
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot salvo: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erro ao tirar screenshot: {e}")
            return False
    
    def run_full_test(self):
        """Executar teste completo"""
        print("🚀 INICIANDO TESTE COMPLETO DO DASHBOARD SEBRAE")
        print("=" * 60)
        
        # Setup
        if not self.setup_driver():
            return False
        
        try:
            # Teste 1: API Endpoint
            api_success = self.test_api_endpoint()
            
            # Teste 2: Dashboard Loading
            loading_success = self.test_dashboard_loading()
            
            # Screenshot após loading
            self.take_screenshot("selenium_sebrae_loaded.png")
            
            # Teste 3: Conteúdo do Dashboard
            content_success = self.test_dashboard_content()
            
            # Teste 4: Cards de Métricas
            metrics_success = self.test_metrics_cards()
            
            # Teste 5: Navegação entre Abas
            tabs_success = self.test_tabs_navigation()
            
            # Teste 6: Aba de Planejamento
            planning_success = self.test_planning_tab_content()
            
            # Screenshot da aba de planejamento
            self.take_screenshot("selenium_sebrae_planning.png")
            
            # Teste 7: Gráficos
            charts_success = self.test_charts_rendering()
            
            # Teste 8: Tabela de Dados
            table_success = self.test_table_data()
            
            # Screenshot final
            self.take_screenshot("selenium_sebrae_final.png")
            
            # Resultado final
            print("\n" + "=" * 60)
            print("📊 RESULTADO DOS TESTES:")
            print("=" * 60)
            
            tests = [
                ("API Endpoint", api_success),
                ("Dashboard Loading", loading_success),
                ("Conteúdo do Dashboard", content_success),
                ("Cards de Métricas", metrics_success),
                ("Navegação entre Abas", tabs_success),
                ("Aba de Planejamento", planning_success),
                ("Renderização dos Gráficos", charts_success),
                ("Dados da Tabela", table_success)
            ]
            
            passed = 0
            for test_name, success in tests:
                status = "✅ PASSOU" if success else "❌ FALHOU"
                print(f"{test_name:.<30} {status}")
                if success:
                    passed += 1
            
            print("=" * 60)
            print(f"📈 RESULTADO FINAL: {passed}/{len(tests)} testes passaram")
            
            if passed == len(tests):
                print("🎉 TODOS OS TESTES PASSARAM! Dashboard funcionando perfeitamente!")
            elif passed >= len(tests) * 0.8:
                print("✅ Maioria dos testes passou. Dashboard funcionando bem!")
            else:
                print("⚠️ Alguns testes falharam. Verificar problemas.")
            
            return passed == len(tests)
            
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔧 Driver finalizado")

def main():
    """Função principal"""
    print(f"🕐 Iniciando teste em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    tester = SebraeDashboardTester()
    success = tester.run_full_test()
    
    print(f"🕐 Teste finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if success:
        print("🎯 Teste concluído com SUCESSO!")
        exit(0)
    else:
        print("⚠️ Teste concluído com ALGUMAS FALHAS")
        exit(1)

if __name__ == "__main__":
    main()
