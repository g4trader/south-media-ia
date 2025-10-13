#!/usr/bin/env python3
"""
Teste final de validação dos filtros na aba Por Canal
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_final_validation():
    """Teste final de validação"""
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🧪 Teste final de validação dos filtros...")
        
        url = "https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/dashboard/copacol_institucional_remarketing_programatica"
        print(f"📱 Acessando: {url}")
        
        driver.get(url)
        time.sleep(15)
        
        print("\n📊 Estado inicial...")
        
        # Verificar JavaScript
        initial_state = driver.execute_script("""
            return {
                filterBar: typeof window.filterBar !== 'undefined',
                dashboard: typeof window.dashboard !== 'undefined',
                originalLength: window.dashboard && window.dashboard.originalData ? window.dashboard.originalData.daily_data.length : 0,
                currentFilter: window.filterBar ? window.filterBar.activeFilter : 'undefined'
            };
        """)
        
        print(f"  - FilterBar: {'✅' if initial_state['filterBar'] else '❌'}")
        print(f"  - Dashboard: {'✅' if initial_state['dashboard'] else '❌'}")
        print(f"  - Total de registros: {initial_state['originalLength']}")
        print(f"  - Filtro atual: {initial_state['currentFilter']}")
        
        if not initial_state['filterBar'] or not initial_state['dashboard']:
            print("❌ Dashboard não carregou corretamente!")
            return
        
        # TESTE 1: Filtro "7 dias"
        print("\n🎯 TESTE 1: Filtro '7 dias'...")
        
        result_7dias = driver.execute_script("""
            try {
                // Aplicar filtro 7 dias
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(endDate.getDate() - 7);
                
                window.dashboard.applyDateFilter(
                    startDate.toISOString().split('T')[0], 
                    endDate.toISOString().split('T')[0]
                );
                
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        """)
        
        time.sleep(3)
        
        state_7dias = driver.execute_script("""
            const channelDailyBody = document.getElementById('channelDailyBody');
            const tbodyChannels = document.getElementById('tbodyChannels');
            
            return {
                originalLength: window.dashboard.originalData.daily_data.length,
                filteredLength: window.dashboard.filteredData.daily_data.length,
                channelDailyBodyRows: channelDailyBody ? channelDailyBody.querySelectorAll('tr').length : 0,
                channelDailyBodyContent: channelDailyBody ? channelDailyBody.textContent.substring(0, 100) : 'N/A',
                tbodyChannelsRows: tbodyChannels ? tbodyChannels.querySelectorAll('tr').length : 0,
                tbodyChannelsContent: tbodyChannels ? tbodyChannels.textContent.substring(0, 100) : 'N/A'
            };
        """)
        
        print(f"  - Dados: {state_7dias['originalLength']} → {state_7dias['filteredLength']}")
        print(f"  - Tabela entrega diária: {state_7dias['channelDailyBodyRows']} linhas")
        print(f"  - Tabela resumo: {state_7dias['tbodyChannelsRows']} linhas")
        
        if state_7dias['filteredLength'] < state_7dias['originalLength']:
            print("  ✅ FILTRO '7 DIAS' FUNCIONANDO!")
            else:
            print("  ❌ FILTRO '7 DIAS' NÃO FUNCIONANDO!")
        
        # TESTE 2: Filtro "Hoje"
        print("\n🎯 TESTE 2: Filtro 'Hoje'...")
        
        result_hoje = driver.execute_script("""
            try {
                // Aplicar filtro Hoje
                const today = new Date();
                const todayStr = today.toISOString().split('T')[0];
                
                window.dashboard.applyDateFilter(todayStr, todayStr);
                
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        """)
        
        time.sleep(3)
        
        state_hoje = driver.execute_script("""
            const channelDailyBody = document.getElementById('channelDailyBody');
            const tbodyChannels = document.getElementById('tbodyChannels');
            
            return {
                originalLength: window.dashboard.originalData.daily_data.length,
                filteredLength: window.dashboard.filteredData.daily_data.length,
                channelDailyBodyRows: channelDailyBody ? channelDailyBody.querySelectorAll('tr').length : 0,
                channelDailyBodyContent: channelDailyBody ? channelDailyBody.textContent.substring(0, 100) : 'N/A',
                tbodyChannelsRows: tbodyChannels ? tbodyChannels.querySelectorAll('tr').length : 0,
                tbodyChannelsContent: tbodyChannels ? tbodyChannels.textContent.substring(0, 100) : 'N/A'
            };
        """)
        
        print(f"  - Dados: {state_hoje['originalLength']} → {state_hoje['filteredLength']}")
        print(f"  - Tabela entrega diária: {state_hoje['channelDailyBodyRows']} linhas")
        print(f"  - Tabela entrega diária conteúdo: {state_hoje['channelDailyBodyContent']}")
        print(f"  - Tabela resumo: {state_hoje['tbodyChannelsRows']} linhas")
        print(f"  - Tabela resumo conteúdo: {state_hoje['tbodyChannelsContent']}")
        
        if state_hoje['filteredLength'] == 0:
            print("  ✅ FILTRO 'HOJE' FUNCIONANDO - 0 dados!")
            
            if "Nenhum dado disponível" in state_hoje['channelDailyBodyContent']:
                print("  ✅ MENSAGEM 'NENHUM DADO DISPONÍVEL' NA TABELA ENTREGA DIÁRIA!")
            else:
                print("  ❌ MENSAGEM 'NENHUM DADO DISPONÍVEL' NÃO APARECE NA TABELA ENTREGA DIÁRIA!")
                
            if "Nenhum dado disponível" in state_hoje['tbodyChannelsContent']:
                print("  ✅ MENSAGEM 'NENHUM DADO DISPONÍVEL' NA TABELA RESUMO!")
            else:
                print("  ❌ MENSAGEM 'NENHUM DADO DISPONÍVEL' NÃO APARECE NA TABELA RESUMO!")
        else:
            print("  ❌ FILTRO 'HOJE' NÃO FUNCIONANDO!")
        
        # RESUMO FINAL
        print("\n📊 RESUMO FINAL:")
        
        if (state_7dias['filteredLength'] < state_7dias['originalLength'] and 
            state_hoje['filteredLength'] == 0 and
            "Nenhum dado disponível" in state_hoje['channelDailyBodyContent']):
            print("🎉 ✅ TODOS OS FILTROS FUNCIONANDO PERFEITAMENTE NA ABA POR CANAL!")
            print("🚀 PRONTO PARA DEPLOY EM PRODUÇÃO!")
        else:
            print("❌ AINDA HÁ PROBLEMAS COM OS FILTROS")
        
        print("\n✅ Teste final concluído!")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
            driver.quit()

if __name__ == "__main__":
    test_final_validation()