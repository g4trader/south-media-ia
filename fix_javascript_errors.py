#!/usr/bin/env python3
"""
Script para corrigir erros JavaScript
"""

import os
import re

def fix_javascript_errors():
    """Corrigir erros JavaScript"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo erros JavaScript...")
    
    # ========================================
    # CORRIGIR ERRO DE VARIÁVEL DUPLICADA
    # ========================================
    print("1. Corrigindo variável duplicada 'footfallData'...")
    
    # Encontrar e corrigir declarações duplicadas de footfallData
    content = re.sub(r'const footfallData = [^;]+;\s*const footfallData =', 'const footfallData =', content)
    
    # ========================================
    # GARANTIR QUE AS FUNÇÕES ESTÃO DEFINIDAS
    # ========================================
    print("2. Garantindo que as funções estão definidas...")
    
    # Verificar se as funções existem
    if 'function updateFootfallMetrics' not in content:
        print("   ❌ updateFootfallMetrics não encontrada!")
        return False
    
    if 'function updateFootfallOutMetrics' not in content:
        print("   ❌ updateFootfallOutMetrics não encontrada!")
        return False
    
    if 'function initializeFootfallContent' not in content:
        print("   ❌ initializeFootfallContent não encontrada!")
        return False
    
    # ========================================
    # CORRIGIR ORDEM DAS FUNÇÕES
    # ========================================
    print("3. Corrigindo ordem das funções...")
    
    # Mover as funções para o final do script para evitar problemas de hoisting
    script_end = content.rfind('</script>')
    if script_end != -1:
        # Extrair as funções
        functions = []
        
        # updateFootfallMetrics
        match = re.search(r'function updateFootfallMetrics\(\) \{[^}]*\}', content, re.DOTALL)
        if match:
            functions.append(match.group(0))
            content = content.replace(match.group(0), '')
        
        # updateFootfallOutMetrics
        match = re.search(r'function updateFootfallOutMetrics\(\) \{[^}]*\}', content, re.DOTALL)
        if match:
            functions.append(match.group(0))
            content = content.replace(match.group(0), '')
        
        # initializeFootfallContent
        match = re.search(r'function initializeFootfallContent\(\) \{[^}]*\}', content, re.DOTALL)
        if match:
            functions.append(match.group(0))
            content = content.replace(match.group(0), '')
        
        # initializeFootfallOutContent
        match = re.search(r'function initializeFootfallOutContent\(\) \{[^}]*\}', content, re.DOTALL)
        if match:
            functions.append(match.group(0))
            content = content.replace(match.group(0), '')
        
        # Adicionar as funções antes do fechamento da tag script
        functions_text = '\n\n'.join(functions)
        content = content[:script_end] + '\n\n' + functions_text + '\n\n' + content[script_end:]
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO SIMPLES
    # ========================================
    print("4. Adicionando inicialização simples...")
    
    simple_init = """
// Inicialização simples e direta
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página carregada, inicializando...');
    
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
"""
    
    # Adicionar antes do fechamento da tag script
    content = content.replace('</script>', simple_init + '\n</script>')
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo erros JavaScript...")
    
    if fix_javascript_errors():
        print("\n🎉 Erros JavaScript corrigidos!")
        print("📋 Resultado:")
        print("   ✅ Variável duplicada corrigida")
        print("   ✅ Funções reorganizadas")
        print("   ✅ Inicialização simples adicionada")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir os erros JavaScript")

