#!/usr/bin/env python3
"""
Script final para corrigir TODOS os problemas
"""

import os
import re

def final_clean_fix():
    """Corrigir TODOS os problemas de forma definitiva"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo TODOS os problemas de forma definitiva...")
    
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
    # VERIFICAR SE AINDA HÁ DECLARAÇÕES DUPLICADAS
    # ========================================
    print("2. Verificando se ainda há declarações duplicadas...")
    
    footfall_points_count = len(re.findall(r'const FOOTFALL_POINTS =', content))
    footfall_out_points_count = len(re.findall(r'const FOOTFALL_OUT_POINTS =', content))
    
    print(f"   FOOTFALL_POINTS: {footfall_points_count} declarações")
    print(f"   FOOTFALL_OUT_POINTS: {footfall_out_points_count} declarações")
    
    if footfall_points_count > 1 or footfall_out_points_count > 1:
        print("   ⚠️  Ainda há declarações duplicadas!")
        return False
    else:
        print("   ✅ Nenhuma declaração duplicada encontrada!")
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO SIMPLES
    # ========================================
    print("3. Adicionando inicialização simples...")
    
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
    print("🔧 Corrigindo TODOS os problemas de forma definitiva...")
    
    if final_clean_fix():
        print("\n🎉 Todos os problemas corrigidos!")
        print("📋 Resultado:")
        print("   ✅ Declarações duplicadas removidas")
        print("   ✅ Inicialização simples adicionada")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir os problemas")

