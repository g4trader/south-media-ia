#!/usr/bin/env python3
"""
Script para corrigir definitivamente as funções da aba Footfall Set
"""

import os
import re

def fix_footfall_set_functions_final():
    """Corrigir definitivamente as funções da aba Footfall Set"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo DEFINITIVAMENTE as funções da aba Footfall Set...")
    
    # ========================================
    # CORRIGIR updateFootfallMetrics
    # ========================================
    print("1. Corrigindo updateFootfallMetrics...")
    
    # Encontrar e corrigir a função updateFootfallMetrics
    pattern = r'(function updateFootfallMetrics\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_OUT_POINTS', 'FOOTFALL_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallMetrics corrigida")
    
    # ========================================
    # CORRIGIR initializeFootfallMap
    # ========================================
    print("2. Corrigindo initializeFootfallMap...")
    
    # Encontrar e corrigir a função initializeFootfallMap
    pattern = r'(function initializeFootfallMap\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_OUT_POINTS', 'FOOTFALL_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ initializeFootfallMap corrigida")
    
    # ========================================
    # CORRIGIR initializeFootfallChart
    # ========================================
    print("3. Corrigindo initializeFootfallChart...")
    
    # Encontrar e corrigir a função initializeFootfallChart
    pattern = r'(function initializeFootfallChart\(\) \{[^}]*const chartData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_OUT_POINTS', 'FOOTFALL_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ initializeFootfallChart corrigida")
    
    # ========================================
    # CORRIGIR updateFootfallTopStores
    # ========================================
    print("4. Corrigindo updateFootfallTopStores...")
    
    # Encontrar e corrigir a função updateFootfallTopStores
    pattern = r'(function updateFootfallTopStores\(\) \{[^}]*const sortedPoints = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_OUT_POINTS', 'FOOTFALL_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallTopStores corrigida")
    
    # ========================================
    # CORRIGIR TODAS AS OCORRÊNCIAS RESTANTES
    # ========================================
    print("5. Corrigindo todas as ocorrências restantes...")
    
    # Substituir todas as ocorrências de FOOTFALL_OUT_POINTS por FOOTFALL_POINTS
    # mas apenas nas funções da aba Footfall Set
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {',
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {'
    )
    
    content = content.replace(
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);'
    )
    
    content = content.replace(
        'const chartData = FOOTFALL_OUT_POINTS',
        'const chartData = FOOTFALL_POINTS'
    )
    
    content = content.replace(
        'const sortedPoints = FOOTFALL_OUT_POINTS',
        'const sortedPoints = FOOTFALL_POINTS'
    )
    
    content = content.replace(
        'const heatmapData = FOOTFALL_OUT_POINTS.map(point => [point.lat, point.lon, point.users]);',
        'const heatmapData = FOOTFALL_POINTS.map(point => [point.lat, point.lon, point.users]);'
    )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo DEFINITIVAMENTE as funções da aba Footfall Set...")
    
    if fix_footfall_set_functions_final():
        print("\n🎉 Funções da aba Footfall Set corrigidas!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Agora usa FOOTFALL_POINTS (setembro)")
        print("   ✅ Footfall Out: Usa FOOTFALL_OUT_POINTS (outubro)")
    else:
        print("❌ Erro ao corrigir as funções")

