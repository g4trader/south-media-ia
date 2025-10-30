#!/usr/bin/env python3
"""
Script para corrigir os problemas reais do dashboard
"""

import os
import re

def fix_real_problems():
    """Corrigir os problemas reais do dashboard"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo problemas reais do dashboard...")
    
    # ========================================
    # REMOVER MÚLTIPLAS INICIALIZAÇÕES
    # ========================================
    print("1. Removendo múltiplas inicializações...")
    
    # Remover todas as inicializações duplicadas
    init_pattern = r'// Inicialização simples e direta.*?document\.addEventListener\(\'DOMContentLoaded\'.*?\);'
    content = re.sub(init_pattern, '', content, flags=re.DOTALL)
    
    # ========================================
    # VERIFICAR SE EXISTE O ELEMENTO footfall-out-metrics
    # ========================================
    print("2. Verificando elemento footfall-out-metrics...")
    
    if 'id="footfall-out-metrics"' not in content:
        print("   ❌ Elemento footfall-out-metrics não encontrado!")
        print("   🔧 Adicionando elemento footfall-out-metrics...")
        
        # Adicionar o elemento footfall-out-metrics
        footfall_out_metrics = '''<div id="footfall-out-metrics" class="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
        <div class="metric-card" style="background: rgba(255, 107, 53, 0.1); border: 1px solid rgba(255, 107, 53, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🏪</span>
                <h3 style="color: #ff6b35; font-size: 1.1rem; margin: 0;">Total de Lojas</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">0</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Lojas ativas</p>
        </div>
        
        <div class="metric-card" style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">👥</span>
                <h3 style="color: #8b5cf6; font-size: 1.1rem; margin: 0;">Total de Usuários</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">0</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Usuários detectados</p>
        </div>
        
        <div class="metric-card" style="background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">📊</span>
                <h3 style="color: #00ff88; font-size: 1.1rem; margin: 0;">Taxa Média</h3>
            </div>
            <div class="metric-value" style="font-size: 2.5rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">0%</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">Conversão média</p>
        </div>
        
        <div class="metric-card" style="background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center; backdrop-filter: blur(10px);">
            <div class="metric-header" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🏆</span>
                <h3 style="color: #ffc107; font-size: 1.1rem; margin: 0;">Melhor Loja</h3>
            </div>
            <div class="metric-value" style="font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 0.5rem;">-</div>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">0% conversão</p>
        </div>
    </div>'''
        
        # Adicionar o elemento dentro da aba footfall-out
        content = content.replace('<div id="tab-footfall-out" class="hidden">', '<div id="tab-footfall-out" class="hidden">\n' + footfall_out_metrics)
    else:
        print("   ✅ Elemento footfall-out-metrics encontrado!")
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO ÚNICA E LIMPA
    # ========================================
    print("3. Adicionando inicialização única e limpa...")
    
    init_script = '''
// Inicialização única e limpa
let isInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    if (isInitialized) {
        console.log('Dashboard já inicializado, ignorando...');
        return;
    }
    
    isInitialized = true;
    console.log('Dashboard carregado, inicializando...');
    
    // Aguardar um pouco para garantir que tudo esteja pronto
    setTimeout(() => {
        console.log('Inicializando métricas...');
        
        // Atualizar métricas Footfall Set
        if (typeof updateFootfallMetrics === 'function') {
            updateFootfallMetrics();
        }
        
        // Atualizar métricas Footfall Out
        if (typeof updateFootfallOutMetrics === 'function') {
            updateFootfallOutMetrics();
        }
    }, 2000);
});
'''
    
    # Adicionar antes do fechamento da tag script
    content = content.replace('</script>', init_script + '\n</script>')
    
    # ========================================
    # CORRIGIR ERRO DE classList
    # ========================================
    print("4. Corrigindo erro de classList...")
    
    # Encontrar e corrigir o erro de classList
    classlist_error = 'document.getElementById(\'tab-\'+key).classList.toggle(\'hidden\', key!==id);'
    classlist_fix = 'const tabElement = document.getElementById(\'tab-\'+key); if (tabElement) { tabElement.classList.toggle(\'hidden\', key!==id); }'
    
    content = content.replace(classlist_error, classlist_fix)
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo problemas reais do dashboard...")
    
    if fix_real_problems():
        print("\n🎉 Problemas reais corrigidos!")
        print("📋 Resultado:")
        print("   ✅ Múltiplas inicializações removidas")
        print("   ✅ Elemento footfall-out-metrics adicionado")
        print("   ✅ Inicialização única e limpa")
        print("   ✅ Erro de classList corrigido")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir os problemas")
