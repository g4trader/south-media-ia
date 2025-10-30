#!/usr/bin/env python3
"""
Script para corrigir IDs duplicados entre as abas
"""

import os
import re

def fix_duplicate_ids():
    """Corrigir IDs duplicados entre as abas"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo IDs duplicados entre as abas...")
    
    # ========================================
    # CORRIGIR IDs DA ABA FOOTFALL OUT
    # ========================================
    print("1. Corrigindo IDs da aba Footfall Out...")
    
    # Substituir IDs duplicados na aba Footfall Out
    # footfall-map -> footfall-out-map
    content = content.replace(
        'id="footfall-map" style="height: 400px; width: 100%; border-radius: 8px; filter: hue-rotate(15deg) saturate(1.2);"></div>',
        'id="footfall-out-map" style="height: 400px; width: 100%; border-radius: 8px; filter: hue-rotate(15deg) saturate(1.2);"></div>'
    )
    
    # footfall-performanceChart -> footfall-out-performanceChart
    content = content.replace(
        'id="footfall-performanceChart"></canvas>',
        'id="footfall-out-performanceChart"></canvas>'
    )
    
    # footfall-topStores -> footfall-out-topStores
    content = content.replace(
        'id="footfall-topStores">',
        'id="footfall-out-topStores">'
    )
    
    # ========================================
    # CORRIGIR FUNÇÕES JAVASCRIPT
    # ========================================
    print("2. Corrigindo funções JavaScript...")
    
    # initializeFootfallOutMap - deve usar footfall-out-map
    content = content.replace(
        'const mapElement = document.getElementById(\'footfall-map\');',
        'const mapElement = document.getElementById(\'footfall-out-map\');'
    )
    
    # initializeFootfallOutChart - deve usar footfall-out-performanceChart
    content = content.replace(
        'const ctx = document.getElementById(\'footfall-performanceChart\').getContext(\'2d\');',
        'const ctx = document.getElementById(\'footfall-out-performanceChart\').getContext(\'2d\');'
    )
    
    # updateFootfallOutTopStores - deve usar footfall-out-topStores
    content = content.replace(
        'const topStoresContainer = document.getElementById(\'footfall-topStores\');',
        'const topStoresContainer = document.getElementById(\'footfall-out-topStores\');'
    )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo IDs duplicados...")
    
    if fix_duplicate_ids():
        print("\n🎉 IDs duplicados corrigidos!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: IDs únicos (footfall-map, footfall-performanceChart, footfall-topStores)")
        print("   ✅ Footfall Out: IDs únicos (footfall-out-map, footfall-out-performanceChart, footfall-out-topStores)")
        print("\n💡 Agora as abas são completamente independentes!")
    else:
        print("❌ Erro ao corrigir os IDs")

