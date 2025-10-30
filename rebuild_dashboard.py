#!/usr/bin/env python3
"""
Script para reconstruir o dashboard do zero
"""

import os
import re

def rebuild_dashboard():
    """Reconstruir o dashboard do zero"""
    
    # Ler o arquivo original
    with open("static/dash_sonho.html", 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print("🔧 Reconstruindo dashboard do zero...")
    
    # ========================================
    # CRIAR NOVA ESTRUTURA DE ABAS
    # ========================================
    print("1. Criando nova estrutura de abas...")
    
    # Substituir a aba Footfall por duas abas
    new_tabs = '''    <div class="tab" data-tab="footfall-set">👣 Footfall Set</div>
    <div class="tab" data-tab="footfall-out">👣 Footfall Out</div>'''
    
    content = re.sub(r'<div class="tab" data-tab="footfall">👣 Footfall</div>', new_tabs, original_content)
    
    # ========================================
    # CRIAR CONTEÚDO DAS ABAS
    # ========================================
    print("2. Criando conteúdo das abas...")
    
    # Encontrar o conteúdo da aba footfall original
    footfall_content_match = re.search(r'<div id="tab-footfall" class="hidden">(.*?)</div>', content, re.DOTALL)
    if not footfall_content_match:
        print("❌ Conteúdo da aba footfall não encontrado!")
        return False
    
    footfall_content = footfall_content_match.group(1)
    
    # Criar aba Footfall Set
    footfall_set_content = f'''<div id="tab-footfall-set" class="hidden">
{footfall_content}
</div>'''
    
    # Criar aba Footfall Out (com IDs únicos)
    footfall_out_content = footfall_content.replace('id="footfall-metrics"', 'id="footfall-out-metrics"')
    footfall_out_content = footfall_out_content.replace('id="footfall-map"', 'id="footfall-out-map"')
    footfall_out_content = footfall_out_content.replace('id="footfall-performanceChart"', 'id="footfall-out-performanceChart"')
    footfall_out_content = footfall_out_content.replace('id="footfall-topStores"', 'id="footfall-out-topStores"')
    
    footfall_out_content = f'''<div id="tab-footfall-out" class="hidden">
{footfall_out_content}
</div>'''
    
    # Substituir a aba original pelas duas novas
    content = re.sub(r'<div id="tab-footfall" class="hidden">.*?</div>', footfall_set_content + '\n' + footfall_out_content, content, flags=re.DOTALL)
    
    # ========================================
    # ATUALIZAR SISTEMA DE NAVEGAÇÃO
    # ========================================
    print("3. Atualizando sistema de navegação...")
    
    # Atualizar a lista de abas
    content = re.sub(r"const tabs = \['overview','channels','insights','planning','footfall'\]", 
                     "const tabs = ['overview','channels','insights','planning','footfall-set','footfall-out']", content)
    
    # Atualizar a lógica de navegação
    navigation_script = '''
  // Inicializar Footfall Set quando a aba for clicada
  if (id === 'footfall-set') {
    initializeFootfallContent();
  }
  
  // Inicializar Footfall Out quando a aba for clicada
  if (id === 'footfall-out') {
    initializeFootfallOutContent();
  }'''
    
    content = re.sub(r'// Inicializar Footfall quando a aba for clicada\n  if \(id === \'footfall\'\) \{\n    initializeFootfallContent\(\);\n  \}', 
                     navigation_script, content)
    
    # ========================================
    # ADICIONAR DADOS E FUNÇÕES
    # ========================================
    print("4. Adicionando dados e funções...")
    
    # Dados de setembro (Footfall Set)
    september_data = [
        {"lat": -8.09233930867147, "lon": -34.88847507746984, "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina", "users": 3784, "rate": 9.5},
        {"lat": -8.13196914950721, "lon": -34.89069687730163, "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300", "users": 4377, "rate": 7.9},
        {"lat": -8.04591568467357, "lon": -34.89092152269836, "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310", "users": 3189, "rate": 9.5},
        {"lat": -8.047434924792, "lon": -34.900162115344200, "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040", "users": 2776, "rate": 9.3},
        {"lat": -8.029882473548620, "lon": -34.906651673016300, "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380", "users": 1267, "rate": 12.5},
        {"lat": -8.119932249004490, "lon": -34.890091268465570, "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050", "users": 3673, "rate": 14.5},
        {"lat": -8.142543914194250, "lon": -34.908109113491800, "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300", "users": 4563, "rate": 6.5},
        {"lat": -8.028130780221500, "lon": -34.890250688465570, "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005", "users": 8355, "rate": 11.5},
        {"lat": -7.995667724325500, "lon": -34.884649217116390, "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260", "users": 8843, "rate": 13.5},
        {"lat": -8.183601155218950, "lon": -34.891945002883600, "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010", "users": 2021, "rate": 11.2},
        {"lat": -8.182334054796810, "lon": -34.918200238558100, "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400", "users": 4128, "rate": 14.51}
    ]
    
    # Dados de outubro (Footfall Out)
    october_data = [
        {"lat": -8.092339308671470, "lon": -34.888475077469840, "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina", "users": 5673, "rate": 12.1},
        {"lat": -8.131969149507210, "lon": -34.890696877301630, "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300", "users": 6731, "rate": 12.5},
        {"lat": -8.045915684673570, "lon": -34.890921522698360, "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310", "users": 5101, "rate": 11.9},
        {"lat": -8.047434924792, "lon": -34.900162115344200, "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040", "users": 4681, "rate": 9.9},
        {"lat": -8.029882473548620, "lon": -34.906651673016300, "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380", "users": 5693, "rate": 11.5},
        {"lat": -8.119932249004490, "lon": -34.890091268465570, "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050", "users": 6731, "rate": 12.9},
        {"lat": -8.142543914194250, "lon": -34.908109113491800, "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300", "users": 2389, "rate": 4.4},
        {"lat": -8.028130780221500, "lon": -34.890250688465570, "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005", "users": 3562, "rate": 6.7},
        {"lat": -7.995667724325500, "lon": -34.884649217116390, "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260", "users": 5631, "rate": 9.3},
        {"lat": -8.183601155218950, "lon": -34.891945002883600, "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010", "users": 3012, "rate": 10.2},
        {"lat": -8.182334054796810, "lon": -34.918200238558100, "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400", "users": 1121, "rate": 9.31},
        {"lat": -8.018367819706790, "lon": -34.996213513770500, "name": "Recibom - Timbi, Camaragibe - PE, 54765-290", "users": 891, "rate": 9.8}
    ]
    
    # Criar FOOTFALL_POINTS (setembro)
    footfall_points = "const FOOTFALL_POINTS = [\n"
    for store in september_data:
        footfall_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    footfall_points += "];"
    
    # Criar FOOTFALL_OUT_POINTS (outubro)
    footfall_out_points = "const FOOTFALL_OUT_POINTS = [\n"
    for store in october_data:
        footfall_out_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    footfall_out_points += "];"
    
    # Adicionar os dados antes do fechamento da tag script
    content = content.replace('</script>', '\n' + footfall_points + '\n\n' + footfall_out_points + '\n\n</script>')
    
    # ========================================
    # ADICIONAR FUNÇÕES PARA FOOTFALL OUT
    # ========================================
    print("5. Adicionando funções para Footfall Out...")
    
    # Função updateFootfallOutMetrics
    updateFootfallOutMetrics = '''
function updateFootfallOutMetrics() {
    const metricsContainer = document.getElementById('footfall-out-metrics');
    if (!metricsContainer || typeof FOOTFALL_OUT_POINTS === 'undefined') {
        console.error('Elemento footfall-out-metrics não encontrado ou FOOTFALL_OUT_POINTS não definido');
        return;
    }
    
    const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);
    
    if (footfallData.length === 0) {
        metricsContainer.innerHTML = '<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 2rem;">Carregando métricas...</div>';
        return;
    }
    
    // Calcular métricas
    const totalLojas = footfallData.length;
    const totalUsuarios = footfallData.reduce((sum, item) => sum + item.users, 0);
    const taxaMedia = footfallData.reduce((sum, item) => sum + item.rate, 0) / totalLojas;
    const melhorLoja = footfallData.reduce((max, item) => item.rate > max.rate ? item : max);
    
    const metricsHTML = `
        <div class="metric-card" style="background: rgba(255, 107, 53, 0.1); border: 1px solid rgba(255, 107, 53, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🏪</span>
                <h3 style="color: #ff6b35; font-size: 1.1rem; margin: 0;">Total de Lojas</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">${totalLojas}</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Lojas ativas</p>
        </div>
        
        <div class="metric-card" style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">👥</span>
                <h3 style="color: #8b5cf6; font-size: 1.1rem; margin: 0;">Total de Usuários</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">${totalUsuarios.toLocaleString()}</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Usuários detectados</p>
        </div>
        
        <div class="metric-card" style="background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">📊</span>
                <h3 style="color: #00ff88; font-size: 1.1rem; margin: 0;">Taxa Média</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">${taxaMedia.toFixed(1)}%</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Conversão média</p>
        </div>
        
        <div class="metric-card" style="background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🏆</span>
                <h3 style="color: #ffc107; font-size: 1.1rem; margin: 0;">Melhor Loja</h3>
            </div>
            <div class="metric-value" style="font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">${melhorLoja.name.split(' - ')[1] || melhorLoja.name}</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">${melhorLoja.rate}% conversão</p>
        </div>
    `;
    
    metricsContainer.innerHTML = metricsHTML;
    console.log('Métricas footfall OUT atualizadas:', { totalLojas, totalUsuarios, taxaMedia: taxaMedia.toFixed(1) + '%', melhorLoja: melhorLoja.name });
}'''
    
    # Função initializeFootfallOutContent
    initializeFootfallOutContent = '''
function initializeFootfallOutContent() {
    console.log('Inicializando conteúdo footfall-out...');
    
    // Aguardar um pouco para garantir que os elementos estejam prontos
    setTimeout(() => {
        updateFootfallOutMetrics();
        // Adicionar outras inicializações aqui se necessário
    }, 500);
}'''
    
    # Adicionar as funções antes do fechamento da tag script
    content = content.replace('</script>', '\n' + updateFootfallOutMetrics + '\n\n' + initializeFootfallOutContent + '\n\n</script>')
    
    # ========================================
    # SALVAR ARQUIVO
    # ========================================
    print("6. Salvando arquivo...")
    
    with open("static/dash_sonho_v2.html", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Dashboard reconstruído com sucesso!")
    return True

if __name__ == "__main__":
    print("🔧 Reconstruindo dashboard do zero...")
    
    if rebuild_dashboard():
        print("\n🎉 Dashboard reconstruído!")
        print("📋 Resultado:")
        print("   ✅ Duas abas independentes criadas")
        print("   ✅ Dados corretos: Setembro (46,976) e Outubro (51,216)")
        print("   ✅ Funções JavaScript corretas")
        print("   ✅ Sistema de navegação atualizado")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao reconstruir o dashboard")

