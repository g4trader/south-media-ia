#!/usr/bin/env python3
"""
Script para corrigir as funções da aba Footfall Set para usar FOOTFALL_POINTS
"""

import os
import re

def fix_footfall_set_functions():
    """Corrigir funções da aba Footfall Set"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo funções da aba Footfall Set...")
    
    # 1. Corrigir updateFootfallMetrics - deve usar FOOTFALL_POINTS
    content = content.replace(
        'const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);',
        'const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);'
    )
    
    # 2. Corrigir initializeFootfallMap - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);',
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);'
    )
    
    # 3. Corrigir initializeFootfallChart - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS === \'undefined\' || FOOTFALL_OUT_POINTS.length === 0) {\n        console.error(\'FOOTFALL_OUT_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_OUT_POINTS',
        'if (typeof FOOTFALL_POINTS === \'undefined\' || FOOTFALL_POINTS.length === 0) {\n        console.error(\'FOOTFALL_POINTS não definido ou vazio\');\n        return;\n    }\n    \n    const chartData = FOOTFALL_POINTS'
    )
    
    # 4. Corrigir updateFootfallTopStores - deve usar FOOTFALL_POINTS
    content = content.replace(
        'if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_OUT_POINTS',
        'if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {\n        // Ordenar por usuários (descendente) e pegar top 5\n        const sortedPoints = FOOTFALL_POINTS'
    )
    
    # 5. Corrigir heatmap data - deve usar FOOTFALL_POINTS
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
    print("🔧 Corrigindo funções da aba Footfall Set...")
    
    if fix_footfall_set_functions():
        print("\n🎉 Funções corrigidas!")
        print("💡 Agora a aba Footfall Set deve mostrar os dados corretos de setembro!")
    else:
        print("❌ Erro ao corrigir as funções")
