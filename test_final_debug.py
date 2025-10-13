#!/usr/bin/env python3
"""
Teste final para debugar renderTables
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_final_debug():
    """Teste final para debugar renderTables"""
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🧪 Teste final para debugar renderTables...")
        
        url = "https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/api/dashboard/copacol_institucional_remarketing_programatica"
        print(f"📱 Acessando: {url}")
        
        driver.get(url)
        time.sleep(15)
        
        # Ir para aba Por Canal
        driver.execute_script("""
            const channelsTab = document.querySelector('[data-tab=\"channels\"]');
            if (channelsTab) {
                channelsTab.click();
            }
        """)
        time.sleep(2)
        
        print("\n🎯 Testando renderTables com debug completo...")
        
        # Aplicar filtro com debug completo
        result = driver.execute_script("""
            try {
                // Adicionar debug ao renderTables
                const originalRenderTables = window.dashboard.renderTables;
                let renderTablesCalls = 0;
                let renderTablesData = [];
                
                window.dashboard.renderTables = function(data) {
                    renderTablesCalls++;
                    renderTablesData.push({
                        call: renderTablesCalls,
                        hasDailyData: data.daily_data ? data.daily_data.length : 0,
                        hasChannelMetrics: data.channel_metrics ? data.channel_metrics.length : 0,
                        hasCampaignSummary: !!data.campaign_summary,
                        hasContract: !!data.contract,
                        dailyDataSample: data.daily_data ? data.daily_data.slice(0, 2) : null
                    });
                    
                    console.log('🔧 renderTables chamado #' + renderTablesCalls + ':', {
                        dailyData: data.daily_data ? data.daily_data.length : 0,
                        channelMetrics: data.channel_metrics ? data.channel_metrics.length : 0
                    });
                    
                    return originalRenderTables.call(this, data);
                };
                
                // Aplicar filtro
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(endDate.getDate() - 7);
                
                console.log('🔄 Aplicando filtro...');
                await window.dashboard.applyDateFilter(
                    startDate.toISOString().split('T')[0], 
                    endDate.toISOString().split('T')[0]
                );
                
                console.log('✅ Filtro aplicado');
                
                return {
                    success: true,
                    renderTablesCalls: renderTablesCalls,
                    renderTablesData: renderTablesData,
                    originalLength: window.dashboard.originalData.daily_data.length,
                    filteredLength: window.dashboard.filteredData ? window.dashboard.filteredData.daily_data.length : 0,
                    channelMetricsLength: window.dashboard.filteredData && window.dashboard.filteredData.channel_metrics ? window.dashboard.filteredData.channel_metrics.length : 0
                };
            } catch (e) {
                console.error('❌ Erro:', e);
                return {
                    success: false,
                    error: e.message
                };
            }
        """)
        
        print(f"  - Resultado: {result}")
        
        # Aguardar e verificar estado final
        time.sleep(3)
        
        final_state = driver.execute_script("""
            const channelDailyBody = document.getElementById('channelDailyBody');
            const tbodyChannels = document.getElementById('tbodyChannels');
            
            return {
                channelDailyBodyRows: channelDailyBody ? channelDailyBody.querySelectorAll('tr').length : 0,
                tbodyChannelsRows: tbodyChannels ? tbodyChannels.querySelectorAll('tr').length : 0,
                channelDailyBodyContent: channelDailyBody ? channelDailyBody.textContent.substring(0, 100) : 'N/A',
                tbodyChannelsContent: tbodyChannels ? tbodyChannels.textContent.substring(0, 100) : 'N/A'
            };
        """)
        
        print(f"  - Tabela entrega diária: {final_state['channelDailyBodyRows']} linhas")
        print(f"  - Tabela resumo: {final_state['tbodyChannelsRows']} linhas")
        print(f"  - Conteúdo entrega diária: {final_state['channelDailyBodyContent']}")
        print(f"  - Conteúdo resumo: {final_state['tbodyChannelsContent']}")
        
        if result.get('success'):
            print(f"  - renderTables chamado {result['renderTablesCalls']} vezes")
            for call_data in result.get('renderTablesData', []):
                print(f"    Chamada {call_data['call']}: dailyData={call_data['hasDailyData']}, channelMetrics={call_data['hasChannelMetrics']}")
            
            print(f"  - Dados filtrados: {result['originalLength']} → {result['filteredLength']}")
            print(f"  - channel_metrics: {result['channelMetricsLength']}")
        else:
            print(f"  ❌ Erro: {result.get('error')}")
        
        print("\n✅ Teste concluído!")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_final_debug()