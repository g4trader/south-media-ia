#!/usr/bin/env python3
"""
Script final para corrigir de forma simples
"""

import os
import re

def final_simple_fix():
    """Corrigir de forma simples e definitiva"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo de forma simples e definitiva...")
    
    # ========================================
    # REMOVER TODAS AS INICIALIZAÇÕES DUPLICADAS
    # ========================================
    print("1. Removendo todas as inicializações duplicadas...")
    
    # Remover todas as inicializações duplicadas
    content = re.sub(r'// Inicialização.*?document\.addEventListener.*?\);', '', content, flags=re.DOTALL)
    
    # ========================================
    # ADICIONAR INICIALIZAÇÃO ÚNICA E SIMPLES
    # ========================================
    print("2. Adicionando inicialização única e simples...")
    
    init_script = '''
// Inicialização única e simples
let isInitialized = false;

document.addEventListener('DOMContentLoaded', function() {
    if (isInitialized) return;
    isInitialized = true;
    
    console.log('Dashboard carregado, inicializando...');
    
    setTimeout(() => {
        console.log('Inicializando métricas...');
        
        if (typeof updateFootfallMetrics === 'function') {
            updateFootfallMetrics();
        }
        
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
    print("3. Corrigindo erro de classList...")
    
    # Corrigir o erro de classList
    content = content.replace(
        "document.getElementById('tab-'+key).classList.toggle('hidden', key!==id);",
        "const tabElement = document.getElementById('tab-'+key); if (tabElement) { tabElement.classList.toggle('hidden', key!==id); }"
    )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo de forma simples e definitiva...")
    
    if final_simple_fix():
        print("\n🎉 Correção simples concluída!")
        print("📋 Resultado:")
        print("   ✅ Inicializações duplicadas removidas")
        print("   ✅ Inicialização única e simples adicionada")
        print("   ✅ Erro de classList corrigido")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir")

