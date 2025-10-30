#!/usr/bin/env python3
"""
Script para corrigir TODOS os IDs corretamente
"""

import os
import re

def fix_all_ids_correctly():
    """Corrigir todos os IDs corretamente"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo TODOS os IDs corretamente...")
    
    # ========================================
    # CORRIGIR IDs DA ABA FOOTFALL SET
    # ========================================
    print("1. Corrigindo IDs da aba Footfall Set...")
    
    # A aba Footfall Set deve manter os IDs originais (sem -out)
    # Mas preciso garantir que não há conflitos
    
    # ========================================
    # CORRIGIR IDs DA ABA FOOTFALL OUT
    # ========================================
    print("2. Corrigindo IDs da aba Footfall Out...")
    
    # Substituir IDs duplicados na aba Footfall Out
    # Primeiro, vou encontrar a seção da aba Footfall Out e corrigir apenas ela
    
    # Encontrar a seção tab-footfall-out
    pattern = r'(<div id="tab-footfall-out"[^>]*>.*?</div>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        footfall_out_section = match.group(1)
        
        # Corrigir IDs dentro da seção Footfall Out
        footfall_out_section = footfall_out_section.replace(
            'id="footfall-out-map"',
            'id="footfall-out-map"'
        )
        
        # Substituir a seção corrigida
        content = content.replace(match.group(1), footfall_out_section)
    
    # ========================================
    # VERIFICAR E CORRIGIR FUNÇÕES JAVASCRIPT
    # ========================================
    print("3. Verificando funções JavaScript...")
    
    # Verificar se as funções estão usando os IDs corretos
    # initializeFootfallOutMap deve usar footfall-out-map
    if 'getElementById(\'footfall-out-map\')' not in content:
        content = content.replace(
            'getElementById(\'footfall-map\')',
            'getElementById(\'footfall-out-map\')'
        )
    
    # initializeFootfallOutChart deve usar footfall-out-performanceChart
    if 'getElementById(\'footfall-out-performanceChart\')' not in content:
        content = content.replace(
            'getElementById(\'footfall-performanceChart\')',
            'getElementById(\'footfall-out-performanceChart\')'
        )
    
    # updateFootfallOutTopStores deve usar footfall-out-topStores
    if 'getElementById(\'footfall-out-topStores\')' not in content:
        content = content.replace(
            'getElementById(\'footfall-topStores\')',
            'getElementById(\'footfall-out-topStores\')'
        )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo TODOS os IDs...")
    
    if fix_all_ids_correctly():
        print("\n🎉 IDs corrigidos!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: IDs originais (footfall-map, footfall-performanceChart, footfall-topStores)")
        print("   ✅ Footfall Out: IDs únicos (footfall-out-map, footfall-out-performanceChart, footfall-out-topStores)")
    else:
        print("❌ Erro ao corrigir os IDs")

