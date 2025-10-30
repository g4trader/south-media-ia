#!/usr/bin/env python3
"""
Script para corrigir APENAS as funções da aba Footfall Out
"""

import os
import re

def fix_footfall_out_only():
    """Corrigir APENAS as funções da aba Footfall Out"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo APENAS as funções da aba Footfall Out...")
    
    # 1. Corrigir updateFootfallOutMetrics - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (!metricsContainer || typeof FOOTFALL_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-out-metrics não encontrado ou FOOTFALL_POINTS não definido\');',
        'if (!metricsContainer || typeof FOOTFALL_OUT_POINTS === \'undefined\') {\n        console.error(\'Elemento footfall-out-metrics não encontrado ou FOOTFALL_OUT_POINTS não definido\');'
    )
    
    content = content.replace(
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    # 2. Corrigir initializeFootfallOutMap - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    # 3. Corrigir initializeFootfallOutChart - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS === \'undefined\' || FOOTFALL_POINTS.length === 0) {\n        console.error(\'FOOTFALL_POINTS não definido ou vazio\');',
        'if (typeof FOOTFALL_OUT_POINTS === \'undefined\' || FOOTFALL_OUT_POINTS.length === 0) {\n        console.error(\'FOOTFALL_OUT_POINTS não definido ou vazio\');'
    )
    
    content = content.replace(
        'const chartData = FOOTFALL_POINTS',
        'const chartData = FOOTFALL_OUT_POINTS'
    )
    
    # 4. Corrigir updateFootfallOutTopStores - deve usar FOOTFALL_OUT_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_POINTS',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_OUT_POINTS'
    )
    
    # 5. Corrigir heatmap data - deve usar FOOTFALL_OUT_POINTS
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
    print("🔧 Corrigindo APENAS as funções da aba Footfall Out...")
    
    if fix_footfall_out_only():
        print("\n🎉 Funções da aba Footfall Out corrigidas!")
        print("💡 Agora a aba Footfall Out deve mostrar os dados corretos de outubro!")
    else:
        print("❌ Erro ao corrigir as funções")

