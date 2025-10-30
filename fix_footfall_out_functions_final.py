#!/usr/bin/env python3
"""
Script para corrigir definitivamente as funções da aba Footfall Out
"""

import os
import re

def fix_footfall_out_functions_final():
    """Corrigir definitivamente as funções da aba Footfall Out"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo DEFINITIVAMENTE as funções da aba Footfall Out...")
    
    # ========================================
    # CORRIGIR updateFootfallOutMetrics
    # ========================================
    print("1. Corrigindo updateFootfallOutMetrics...")
    
    # Encontrar e corrigir a função updateFootfallOutMetrics
    pattern = r'(function updateFootfallOutMetrics\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallOutMetrics corrigida")
    
    # ========================================
    # CORRIGIR initializeFootfallOutMap
    # ========================================
    print("2. Corrigindo initializeFootfallOutMap...")
    
    # Encontrar e corrigir a função initializeFootfallOutMap
    pattern = r'(function initializeFootfallOutMap\(\) \{[^}]*const footfallData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ initializeFootfallOutMap corrigida")
    
    # ========================================
    # CORRIGIR initializeFootfallOutChart
    # ========================================
    print("3. Corrigindo initializeFootfallOutChart...")
    
    # Encontrar e corrigir a função initializeFootfallOutChart
    pattern = r'(function initializeFootfallOutChart\(\) \{[^}]*const chartData = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ initializeFootfallOutChart corrigida")
    
    # ========================================
    # CORRIGIR updateFootfallOutTopStores
    # ========================================
    print("4. Corrigindo updateFootfallOutTopStores...")
    
    # Encontrar e corrigir a função updateFootfallOutTopStores
    pattern = r'(function updateFootfallOutTopStores\(\) \{[^}]*const sortedPoints = [^;]+;)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_function = match.group(1)
        new_function = old_function.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
        content = content.replace(old_function, new_function)
        print("   ✅ updateFootfallOutTopStores corrigida")
    
    # ========================================
    # CORRIGIR TODAS AS OCORRÊNCIAS RESTANTES
    # ========================================
    print("5. Corrigindo todas as ocorrências restantes...")
    
    # Substituir todas as ocorrências de FOOTFALL_POINTS por FOOTFALL_OUT_POINTS
    # mas apenas nas funções da aba Footfall Out
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    content = content.replace(
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    content = content.replace(
        'const chartData = FOOTFALL_POINTS',
        'const chartData = FOOTFALL_OUT_POINTS'
    )
    
    content = content.replace(
        'const sortedPoints = FOOTFALL_POINTS',
        'const sortedPoints = FOOTFALL_OUT_POINTS'
    )
    
    content = content.replace(
        'const heatmapData = FOOTFALL_POINTS.map(point => [point.lat, point.lon, point.users]);',
        'const heatmapData = FOOTFALL_OUT_POINTS.map(point => [point.lat, point.lon, point.users]);'
    )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo DEFINITIVAMENTE as funções da aba Footfall Out...")
    
    if fix_footfall_out_functions_final():
        print("\n🎉 Funções da aba Footfall Out corrigidas!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Usa FOOTFALL_POINTS (setembro)")
        print("   ✅ Footfall Out: Agora usa FOOTFALL_OUT_POINTS (outubro)")
    else:
        print("❌ Erro ao corrigir as funções")

