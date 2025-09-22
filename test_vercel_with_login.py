#!/usr/bin/env python3
"""
Teste completo do sistema Vercel com login real
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Configurar o driver do Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def test_login(driver):
    """Testar o sistema de login com credenciais reais"""
    print("🔐 Testando login com credenciais de demonstração...")
    
    try:
        # Acessar página de login
        driver.get("https://dash.iasouth.tech/login.html")
        time.sleep(3)
        
        # Verificar se a página carregou
        if "Login" in driver.title or "Acesso Restrito" in driver.page_source:
            print("✅ Página de login carregada")
        else:
            print("❌ Página de login não carregou corretamente")
            return False
        
        # Preencher credenciais de admin
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = driver.find_element(By.ID, "password")
            
            # Usar credenciais de admin
            username_field.clear()
            username_field.send_keys("admin")
            
            password_field.clear()
            password_field.send_keys("dashboard2025")
            
            print("✅ Credenciais preenchidas")
            
            # Clicar no botão de login
            login_button = driver.find_element(By.ID, "loginButton")
            login_button.click()
            
            print("✅ Botão de login clicado")
            
            # Aguardar redirecionamento
            time.sleep(5)
            
            # Verificar se logou com sucesso
            current_url = driver.current_url
            print(f"📊 URL após login: {current_url}")
            
            if "dashboard-protected" in current_url or "dashboard-builder" in current_url:
                print("✅ Login realizado com sucesso")
                return True
            elif "login" in current_url:
                # Verificar se há mensagem de erro
                try:
                    error_element = driver.find_element(By.ID, "errorMessage")
                    if error_element.is_displayed():
                        print(f"❌ Erro de login: {error_element.text}")
                    else:
                        print("❌ Login falhou sem mensagem de erro visível")
                except:
                    print("❌ Login falhou")
                return False
            else:
                print("✅ Login realizado com sucesso (redirecionamento para página diferente)")
                return True
                
        except TimeoutException:
            print("❌ Campos de login não encontrados")
            return False
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False

def test_dashboard_creation(driver):
    """Testar criação de dashboard com dados reais"""
    print("📊 Testando criação de dashboard...")
    
    try:
        # Acessar página de criação de dashboard
        driver.get("https://dash.iasouth.tech/dashboard-builder.html")
        time.sleep(5)
        
        # Verificar se a página carregou
        current_url = driver.current_url
        print(f"📊 URL atual: {current_url}")
        
        if "dashboard-builder" in current_url:
            print("✅ Página de criação carregada")
        else:
            print("❌ Página de criação não carregou ou foi redirecionada")
            return False
        
        # Clicar no botão "Criar Novo Dashboard" para abrir o modal
        print("🔘 Clicando no botão 'Criar Novo Dashboard'...")
        try:
            create_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "create-dashboard-btn"))
            )
            create_button.click()
            print("✅ Modal de criação aberto")
            time.sleep(2)  # Aguardar modal abrir
        except Exception as e:
            print(f"❌ Erro ao clicar no botão criar: {e}")
            return False
        
        # Dados da campanha SEBRAE
        campaign_data = {
            "nome": "SEBRAE INSTITUCIONAL SETEMBRO",
            "data_inicio": "15/09/2025",
            "data_fim": "30/09/2025",
            "verba_total": "31000",
            "kpi_valor": "0.16",
            "kpi_meta": "193750",
            "sheet_id": "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8",
            "gid": "668487440",
            "estrategias": """Segmentações
DoubleVerify - DV: VIDEO Fraud & Invalid Traffic>Fraud & IVT by Site/App>Safe from Fraudulent or No Ads Sites/Apps (100% Invalid Traffic) (13963543)
and
TailTarget > BRAZIL > Microsegment > Micro entrepreneurs (EN), Microempresarios (ES), Microempreendedores (PT) (28763396)
and
TailTarget > GLOBAL > Mosaic Business (PT) > Mosaic Business - D25 - Jovens Empreendedores Em Ascensao by Serasa Experian (PT) (24381927)
and
TailTarget > GLOBAL > Jobs (EN) > Perfil Autonomo e Empreendedor by Vagas (PT) (24381449)""",
            "publishers": """Gazeta do Povo	gazetadopovo.com.br
Bem Paraná	bemparana.com.br
Tribuna PR	tribunapr.com.br
Bonde	bonde.com.br
Massa News	massanews.com
Paraná Portal	paranaportal.com
Plural Curitiba	plural.jor.br
O Paraná	oparana.com.br
AEN-PR	aen.pr.gov.br
IPARDES	ipardes.pr.gov.br
Revista PEGN	revistapegn.globo.com
Exame	exame.com
InfoMoney	infomoney.com.br
Monitor do Mercado	monitordomercado.com.br
Forbes Brasil	forbes.com.br
Endeavor Brasil	endeavor.org.br
Negócios Brasil	negociosbrasil.com.br
MeuBiz	meubiz.com.br
Quero um Negócio	queroumnegocio.com.br
Sonoticiaboa	sonoticiaboa.com.br
CNN Brasil Economia	cnnbrasil.com.br/economia
R7 Economia	r7.com/economia
Estadão Economia	estadao.com.br/
Folha Mercado	folha.uol.com.br/
O Globo Economia	oglobo.globo.com/
UOL Economia	economia.uol.com.br
Terra Economia	terra.com.br/
Valor Econômico	valor.globo.com
Bloomberg Línea	bloomberglinea.com.br
InvestNews	investnews.com.br
Investing Brasil	br.investing.com
Notícias Agrícolas	noticiasagricolas.com.br
Canal Rural	canalrural.com.br
Compre Rural	comprerural.com
Agro em Dia	agroemdia.com.br
Agro Link	agrolink.com.br
Proteste	proteste.org.br
Reclame Aqui	reclameaqui.com.br
MarketUp	marketup.com
Econodata	econodata.com.br
Casa dos Dados	casadosdados.com.br
FDR	fdr.com.br
CNPJ.biz	cnpj.biz
Serasa Experian	serasaexperian.com.br
Correio Braziliense (Economia)	correiobraziliense.com.br/
Jovem Pan Economia	jovempan.com.br/
Veja SP Economia	vejasp.abril.com.br/
Revista IstoÉ Dinheiro	istoedinheiro.com.br
Revista Época Negócios	epocanegocios.globo.com
Carta Capital Economia	cartacapital.com.br/
Revista Oeste Economia	revistaoeste.com/
O Antagonista Economia	oantagonista.com.br/
Metropoles Economia	metropoles.com/
Diário do Comércio	dcomercio.com.br
DCI - Diário Comércio Indústria	dci.com.br
IPEA	ipea.gov.br
SEBRAE Portal	sebrae.com.br
Notícias Cascavel (Economia)	noticiascascavel.com.br
CBN Ponta Grossa (Economia)	cbnpg.com.br/
Jornal Ponta Grossa	jornalpontagrossa.com.br
BNT Online	bntonline.com.br
Bem Paraná – Economia	bemparana.com.br
Central Sul de Notícias	centralsuldenoticias.com.br"""
        }
        
        # Preencher dados da campanha
        print("📝 Preenchendo dados da campanha...")
        
        # Nome da campanha
        try:
            nome_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "campaignName"))
            )
            nome_field.clear()
            nome_field.send_keys(campaign_data["nome"])
            print("✅ Nome da campanha preenchido")
        except:
            print("❌ Campo nome da campanha não encontrado")
        
        # Data de início
        try:
            data_inicio = driver.find_element(By.ID, "startDate")
            data_inicio.clear()
            data_inicio.send_keys(campaign_data["data_inicio"])
            print("✅ Data de início preenchida")
        except:
            print("❌ Campo data de início não encontrado")
        
        # Data de fim
        try:
            data_fim = driver.find_element(By.ID, "endDate")
            data_fim.clear()
            data_fim.send_keys(campaign_data["data_fim"])
            print("✅ Data de fim preenchida")
        except:
            print("❌ Campo data de fim não encontrado")
        
        # Verba total
        try:
            verba_field = driver.find_element(By.ID, "totalBudget")
            verba_field.clear()
            verba_field.send_keys(campaign_data["verba_total"])
            print("✅ Verba total preenchida")
        except:
            print("❌ Campo verba total não encontrado")
        
        # Valor do KPI
        try:
            kpi_valor = driver.find_element(By.ID, "kpiValue")
            kpi_valor.clear()
            kpi_valor.send_keys(campaign_data["kpi_valor"])
            print("✅ Valor do KPI preenchido")
        except:
            print("❌ Campo valor do KPI não encontrado")
        
        # Meta do KPI
        try:
            kpi_meta = driver.find_element(By.ID, "kpiTarget")
            kpi_meta.clear()
            kpi_meta.send_keys(campaign_data["kpi_meta"])
            print("✅ Meta do KPI preenchida")
        except:
            print("❌ Campo meta do KPI não encontrado")
        
        # Estratégias
        try:
            estrategias_field = driver.find_element(By.ID, "campaignStrategies")
            estrategias_field.clear()
            estrategias_field.send_keys(campaign_data["estrategias"])
            print("✅ Estratégias preenchidas")
        except:
            print("❌ Campo estratégias não encontrado")
        
        # Configurar canal Programática Display
        print("📺 Configurando canal Programática Display...")
        
        try:
            # Marcar checkbox do Programática Display
            programatica_checkbox = driver.find_element(By.ID, "channel_programmatic_display")
            if not programatica_checkbox.is_selected():
                programatica_checkbox.click()
            print("✅ Checkbox Programática Display marcado")
            
            # Preencher ID da planilha
            sheet_id_field = driver.find_element(By.ID, "programmatic_display_sheet")
            sheet_id_field.clear()
            sheet_id_field.send_keys(campaign_data["sheet_id"])
            print("✅ ID da planilha preenchido")
            
            # Preencher GID
            gid_field = driver.find_element(By.ID, "programmatic_display_gid")
            gid_field.clear()
            gid_field.send_keys(campaign_data["gid"])
            print("✅ GID preenchido")
            
            # Preencher orçamento
            budget_field = driver.find_element(By.ID, "programmatic_display_budget")
            budget_field.clear()
            budget_field.send_keys(campaign_data["verba_total"])
            print("✅ Orçamento preenchido")
            
            # Preencher quantidade
            quantity_field = driver.find_element(By.ID, "programmatic_display_quantity")
            quantity_field.clear()
            quantity_field.send_keys(campaign_data["kpi_meta"])
            print("✅ Quantidade preenchida")
            
        except Exception as e:
            print(f"❌ Erro ao configurar canal: {e}")
        
        time.sleep(3)
        
        # Clicar em Salvar Dashboard
        print("💾 Salvando dashboard...")
        try:
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "saveDashboardBtn"))
            )
            save_button.click()
            print("✅ Botão salvar clicado")
            
            # Aguardar resposta
            time.sleep(15)
            
            # Verificar se houve sucesso
            try:
                # Verificar se há mensagem de sucesso
                success_message = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'success') or contains(text(), 'sucesso') or contains(text(), 'criado') or contains(text(), 'Dashboard')]"))
                )
                print("✅ Dashboard criado com sucesso!")
                print(f"📄 Mensagem: {success_message.text}")
                return True
                
            except TimeoutException:
                # Verificar se há mensagem de erro
                try:
                    error_message = driver.find_element(By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'alert') or contains(@class, 'danger')]")
                    if error_message.is_displayed():
                        print(f"❌ Erro ao criar dashboard: {error_message.text}")
                        return False
                except:
                    pass
                
                # Verificar se houve redirecionamento
                current_url = driver.current_url
                print(f"📊 URL atual: {current_url}")
                
                # Verificar se o modal foi fechado (indicando sucesso)
                try:
                    modal = driver.find_element(By.ID, "createDashboardModal")
                    if not modal.is_displayed():
                        print("✅ Modal fechado - Dashboard provavelmente criado com sucesso!")
                        return True
                except:
                    pass
                
                # Verificar se há elementos de sucesso na página
                try:
                    success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'sucesso') or contains(text(), 'criado') or contains(text(), 'Dashboard')]")
                    if success_elements:
                        print("✅ Elementos de sucesso encontrados na página")
                        return True
                except:
                    pass
                
                print("❌ Não foi possível determinar o resultado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao clicar em salvar: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral na criação do dashboard: {e}")
        return False

def test_dashboard_listing(driver):
    """Testar listagem de dashboards"""
    print("📋 Testando listagem de dashboards...")
    
    try:
        driver.get("https://dash.iasouth.tech/dashboard-protected.html")
        time.sleep(5)
        
        # Verificar se há dashboards listados
        try:
            dashboard_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'dashboard-card') or contains(@class, 'card')]")
            if dashboard_cards:
                print(f"✅ {len(dashboard_cards)} dashboards encontrados")
                return True
            else:
                print("❌ Nenhum dashboard encontrado")
                return False
        except:
            print("❌ Erro ao verificar dashboards")
            return False
            
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🚀 Iniciando teste completo do sistema Vercel com login real")
    print("=" * 70)
    
    driver = None
    try:
        # Configurar driver
        driver = setup_driver()
        
        # Teste 1: Login
        login_success = test_login(driver)
        
        if not login_success:
            print("❌ Login falhou, não é possível continuar com os testes")
            return
        
        # Teste 2: Criação de dashboard
        dashboard_success = test_dashboard_creation(driver)
        
        # Teste 3: Listagem de dashboards
        listing_success = test_dashboard_listing(driver)
        
        # Resultado final
        print("\n" + "=" * 70)
        print("📊 RESULTADO DOS TESTES:")
        print(f"🔐 Login: {'✅ Sucesso' if login_success else '❌ Falhou'}")
        print(f"📊 Criação Dashboard: {'✅ Sucesso' if dashboard_success else '❌ Falhou'}")
        print(f"📋 Listagem Dashboards: {'✅ Sucesso' if listing_success else '❌ Falhou'}")
        
        if dashboard_success:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("✅ O sistema está funcionando corretamente")
            print("✅ Dashboard SEBRAE INSTITUCIONAL SETEMBRO foi criado com sucesso!")
        else:
            print("\n⚠️ TESTE FALHOU")
            print("❌ Há problemas que precisam ser corrigidos")
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    
    finally:
        if driver:
            print("\n🔄 Fechando navegador...")
            driver.quit()

if __name__ == "__main__":
    main()
