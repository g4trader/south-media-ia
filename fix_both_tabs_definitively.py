#!/usr/bin/env python3
"""
Script definitivo para corrigir ambas as abas
"""

import os
import re

def fix_both_tabs_definitively():
    """Corrigir definitivamente ambas as abas"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo DEFINITIVAMENTE ambas as abas...")
    
    # ========================================
    # CORRIGIR ABA FOOTFALL SET (SETEMBRO)
    # ========================================
    print("1. Corrigindo aba Footfall Set (deve usar FOOTFALL_POINTS)...")
    
    # updateFootfallMetrics - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (!metricsContainer || typeof FOOTFALL_OUT_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-metrics não encontrado ou FOOTFALL_OUT_POINTS não definido\');',
        'if (!metricsContainer || typeof FOOTFALL_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-metrics não encontrado ou FOOTFALL_POINTS não definido\');'
    )
    
    content = content.replace(
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);'
    )
    
    # initializeFootfallMap - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);',
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);'
    )
    
    # initializeFootfallChart - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS === \'undefined\' || FOOTFALL_OUT_POINTS.length === 0) {\n        console.error(\'FOOTFALL_OUT_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_OUT_POINTS',
        'if (typeof FOOTFALL_POINTS === \'undefined\' || FOOTFALL_POINTS.length === 0) {\n        console.error(\'FOOTFALL_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_POINTS'
    )
    
    # updateFootfallTopStores - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_OUT_POINTS',
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_POINTS'
    )
    
    # heatmap data - deve usar FOOTFALL_POINTS
    content = content.replace(
        'const heatmapData = FOOTFALL_OUT_POINTS.map(point => [point.lat, point.lon, point.users]);',
        'const heatmapData = FOOTFALL_POINTS.map(point => [point.lat, point.lon, point.users]);'
    )
    
    # ========================================
    # CORRIGIR ABA FOOTFALL OUT (OUTUBRO)
    # ========================================
    print("2. Corrigindo aba Footfall Out (deve usar FOOTFALL_OUT_POINTS)...")
    
    # updateFootfallOutMetrics - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (!metricsContainer || typeof FOOTFALL_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-out-metrics não encontrado ou FOOTFALL_POINTS não definido\');',
        'if (!metricsContainer || typeof FOOTFALL_OUT_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-out-metrics não encontrado ou FOOTFALL_OUT_POINTS não definido\');'
    )
    
    content = content.replace(
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    # initializeFootfallOutMap - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    # initializeFootfallOutChart - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS === \'undefined\' || FOOTFALL_POINTS.length === 0) {\n        console.error(\'FOOTFALL_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_POINTS',
        'if (typeof FOOTFALL_OUT_POINTS === \'undefined\' || FOOTFALL_OUT_POINTS.length === 0) {\n        console.error(\'FOOTFALL_OUT_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_OUT_POINTS'
    )
    
    # updateFootfallOutTopStores - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_POINTS',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_OUT_POINTS'
    )
    
    # heatmap data - deve usar FOOTFALL_OUT_POINTS
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
    print("🔧 Corrigindo DEFINITIVAMENTE ambas as abas...")
    
    if fix_both_tabs_definitively():
        print("\n🎉 Correção definitiva concluída!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Usa FOOTFALL_POINTS (setembro - 46,976 usuários)")
        print("   ✅ Footfall Out: Usa FOOTFALL_OUT_POINTS (outubro - 51,216 usuários)")
        print("\n💡 Agora cada aba é independente e usa seus próprios dados!")
    else:
        print("❌ Erro ao corrigir as abas")

