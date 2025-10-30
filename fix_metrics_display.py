#!/usr/bin/env python3
"""
Script para corrigir a exibição das métricas
"""

import os
import re

def fix_metrics_display():
    """Corrigir a exibição das métricas"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo exibição das métricas...")
    
    # ========================================
    # CORRIGIR updateFootfallMetrics
    # ========================================
    print("1. Corrigindo updateFootfallMetrics...")
    
    # Encontrar a função updateFootfallMetrics e garantir que usa FOOTFALL_POINTS
    pattern = r'(function updateFootfallMetrics\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        # Garantir que usa FOOTFALL_POINTS
        new_function = old_function.replace('FOOTFALL_OUT_POINTS', 'FOOTFALL_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallMetrics corrigida")
    
    # ========================================
    # CORRIGIR updateFootfallOutMetrics
    # ========================================
    print("2. Corrigindo updateFootfallOutMetrics...")
    
    # Encontrar a função updateFootfallOutMetrics e garantir que usa FOOTFALL_OUT_POINTS
    pattern = r'(function updateFootfallOutMetrics\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        # Garantir que usa FOOTFALL_OUT_POINTS
        new_function = old_function.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallOutMetrics corrigida")
    
    # ========================================
    # GARANTIR QUE AS FUNÇÕES SÃO CHAMADAS CORRETAMENTE
    # ========================================
    print("3. Garantindo chamadas corretas das funções...")
    
    # Adicionar logs para debug
    debug_script = """
// Adicionar logs para debug
function debugFootfallData() {
    console.log('=== DEBUG FOOTFALL DATA ===');
    console.log('FOOTFALL_POINTS:', typeof FOOTFALL_POINTS !== 'undefined' ? FOOTFALL_POINTS.length : 'undefined');
    console.log('FOOTFALL_OUT_POINTS:', typeof FOOTFALL_OUT_POINTS !== 'undefined' ? FOOTFALL_OUT_POINTS.length : 'undefined');
    
    if (typeof FOOTFALL_POINTS !== 'undefined') {
        const setTotal = FOOTFALL_POINTS.reduce((sum, point) => sum + point.users, 0);
        console.log('Setembro total:', setTotal);
    }
    
    if (typeof FOOTFALL_OUT_POINTS !== 'undefined') {
        const outTotal = FOOTFALL_OUT_POINTS.reduce((sum, point) => sum + point.users, 0);
        console.log('Outubro total:', outTotal);
    }
    console.log('========================');
}

// Chamar debug quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(debugFootfallData, 1000);
});
"""
    
    # Adicionar o script de debug
    content = content.replace('</script>', debug_script + '\n</script>')
    
    # ========================================
    # FORÇAR ATUALIZAÇÃO DAS MÉTRICAS
    # ========================================
    print("4. Forçando atualização das métricas...")
    
    # Adicionar função para forçar atualização
    force_update_script = """
// Função para forçar atualização das métricas
function forceUpdateMetrics() {
    console.log('Forçando atualização das métricas...');
    
    // Atualizar Footfall Set
    if (typeof updateFootfallMetrics === 'function') {
        updateFootfallMetrics();
    }
    
    // Atualizar Footfall Out
    if (typeof updateFootfallOutMetrics === 'function') {
        updateFootfallOutMetrics();
    }
}

// Chamar quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(forceUpdateMetrics, 2000);
});
"""
    
    # Adicionar o script de força atualização
    content = content.replace('</script>', force_update_script + '\n</script>')
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo exibição das métricas...")
    
    if fix_metrics_display():
        print("\n🎉 Métricas corrigidas!")
        print("📋 Resultado:")
        print("   ✅ Funções de métricas corrigidas")
        print("   ✅ Logs de debug adicionados")
        print("   ✅ Força atualização adicionada")
        print("\n💡 Agora teste no navegador e verifique o console!")
    else:
        print("❌ Erro ao corrigir as métricas")

