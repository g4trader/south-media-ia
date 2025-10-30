#!/usr/bin/env python3
"""
Script para corrigir DEFINITIVAMENTE o problema
"""

import os
import re

def fix_definitively():
    """Corrigir definitivamente o problema"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo DEFINITIVAMENTE o problema...")
    
    # ========================================
    # RECRIAR COMPLETAMENTE AS FUNÇÕES
    # ========================================
    print("1. Recriando funções de métricas...")
    
    # Função updateFootfallMetrics (setembro)
    new_updateFootfallMetrics = """
function updateFootfallMetrics() {
    const metricsContainer = document.getElementById('footfall-metrics');
    if (!metricsContainer || typeof FOOTFALL_POINTS === 'undefined') {
        console.error('Elemento footfall-metrics não encontrado ou FOOTFALL_POINTS não definido');
        return;
    }
    
    const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);
    
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
    console.log('Métricas footfall SET atualizadas:', { totalLojas, totalUsuarios, taxaMedia: taxaMedia.toFixed(1) + '%', melhorLoja: melhorLoja.name });
}"""
    
    # Função updateFootfallOutMetrics (outubro)
    new_updateFootfallOutMetrics = """
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
}"""
    
    # Substituir as funções existentes
    content = re.sub(r'function updateFootfallMetrics\(\) \{[^}]*\}', new_updateFootfallMetrics, content, flags=re.DOTALL)
    content = re.sub(r'function updateFootfallOutMetrics\(\) \{[^}]*\}', new_updateFootfallOutMetrics, content, flags=re.DOTALL)
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO FORÇADA
    # ========================================
    print("2. Adicionando inicialização forçada...")
    
    force_init_script = """
// Forçar inicialização das métricas
function forceInitMetrics() {
    console.log('=== FORÇANDO INICIALIZAÇÃO DAS MÉTRICAS ===');
    
    // Aguardar um pouco para garantir que os elementos estejam prontos
    setTimeout(() => {
        console.log('Atualizando métricas Footfall Set...');
        updateFootfallMetrics();
        
        console.log('Atualizando métricas Footfall Out...');
        updateFootfallOutMetrics();
    }, 1000);
}

// Chamar quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página carregada, forçando inicialização...');
    forceInitMetrics();
});
"""
    
    # Adicionar o script de inicialização forçada
    content = content.replace('</script>', force_init_script + '\n</script>')
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo DEFINITIVAMENTE o problema...")
    
    if fix_definitively():
        print("\n🎉 Problema corrigido DEFINITIVAMENTE!")
        print("📋 Resultado:")
        print("   ✅ Funções de métricas recriadas completamente")
        print("   ✅ Inicialização forçada adicionada")
        print("   ✅ Logs de debug adicionados")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir o problema")

