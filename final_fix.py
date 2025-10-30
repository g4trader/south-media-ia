#!/usr/bin/env python3
"""
Script final para corrigir o dashboard
"""

import os
import re

def final_fix():
    """Corrigir o dashboard de forma definitiva"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo dashboard de forma definitiva...")
    
    # ========================================
    # REMOVER TODAS AS DECLARAÇÕES DUPLICADAS
    # ========================================
    print("1. Removendo todas as declarações duplicadas...")
    
    # Encontrar todas as declarações de FOOTFALL_POINTS
    footfall_points_matches = list(re.finditer(r'const FOOTFALL_POINTS = \[.*?\];', content, re.DOTALL))
    
    if len(footfall_points_matches) > 1:
        print(f"   Encontradas {len(footfall_points_matches)} declarações de FOOTFALL_POINTS")
        
        # Manter apenas a primeira declaração
        for i, match in enumerate(footfall_points_matches[1:], 1):
            content = content.replace(match.group(0), '')
            print(f"   Removida declaração duplicada {i+1}")
    
    # Encontrar todas as declarações de FOOTFALL_OUT_POINTS
    footfall_out_points_matches = list(re.finditer(r'const FOOTFALL_OUT_POINTS = \[.*?\];', content, re.DOTALL))
    
    if len(footfall_out_points_matches) > 1:
        print(f"   Encontradas {len(footfall_out_points_matches)} declarações de FOOTFALL_OUT_POINTS")
        
        # Manter apenas a primeira declaração
        for i, match in enumerate(footfall_out_points_matches[1:], 1):
            content = content.replace(match.group(0), '')
            print(f"   Removida declaração duplicada {i+1}")
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO SIMPLES
    # ========================================
    print("2. Adicionando inicialização simples...")
    
    init_script = '''
// Inicialização simples e direta
document.addEventListener('DOMContentLoaded', function() {
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
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo dashboard de forma definitiva...")
    
    if final_fix():
        print("\n🎉 Dashboard corrigido definitivamente!")
        print("📋 Resultado:")
        print("   ✅ Declarações duplicadas removidas")
        print("   ✅ Inicialização simples adicionada")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir o dashboard")

