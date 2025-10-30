#!/usr/bin/env python3
"""
Script para corrigir as funções da aba Footfall Out para usar FOOTFALL_OUT_POINTS
"""

import os
import re

def fix_footfall_out_functions():
    """Corrigir funções da aba Footfall Out"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo funções da aba Footfall Out...")
    
    # 1. Corrigir updateFootfallOutMetrics
    content = content.replace(
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    # 2. Corrigir initializeFootfallOutMap
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    # 3. Corrigir initializeFootfallOutChart
    content = content.replace(
        'if (typeof FOOTFALL_POINTS === \'undefined\' || FOOTFALL_POINTS.length === 0) {',
        'if (typeof FOOTFALL_OUT_POINTS === \'undefined\' || FOOTFALL_OUT_POINTS.length === 0) {'
    )
    
    content = content.replace(
        'const chartData = FOOTFALL_POINTS',
        'const chartData = FOOTFALL_OUT_POINTS'
    )
    
    # 4. Corrigir updateFootfallOutTopStores
    content = content.replace(
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    content = content.replace(
        'const sortedPoints = FOOTFALL_POINTS',
        'const sortedPoints = FOOTFALL_OUT_POINTS'
    )
    
    # 5. Corrigir heatmap data
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
    print("🔧 Corrigindo funções da aba Footfall Out...")
    
    if fix_footfall_out_functions():
        print("\n🎉 Funções corrigidas!")
        print("💡 Agora a aba Footfall Out deve mostrar os dados corretos de outubro!")
    else:
        print("❌ Erro ao corrigir as funções")
