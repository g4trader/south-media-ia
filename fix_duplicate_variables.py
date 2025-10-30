#!/usr/bin/env python3
"""
Script para corrigir declarações duplicadas de variáveis
"""

import os
import re

def fix_duplicate_variables():
    """Corrigir declarações duplicadas de variáveis"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigindo declarações duplicadas de variáveis...")
    
    # ========================================
    # REMOVER DECLARAÇÕES DUPLICADAS DE FOOTFALL_POINTS
    # ========================================
    print("1. Removendo declarações duplicadas de FOOTFALL_POINTS...")
    
    # Encontrar todas as declarações de FOOTFALL_POINTS
    footfall_points_matches = list(re.finditer(r'const FOOTFALL_POINTS = \[.*?\];', content, re.DOTALL))
    
    if len(footfall_points_matches) > 1:
        print(f"   Encontradas {len(footfall_points_matches)} declarações de FOOTFALL_POINTS")
        
        # Manter apenas a primeira declaração
        for i, match in enumerate(footfall_points_matches[1:], 1):
            content = content.replace(match.group(0), '')
            print(f"   Removida declaração duplicada {i+1}")
    
    # ========================================
    # REMOVER DECLARAÇÕES DUPLICADAS DE FOOTFALL_OUT_POINTS
    # ========================================
    print("2. Removendo declarações duplicadas de FOOTFALL_OUT_POINTS...")
    
    # Encontrar todas as declarações de FOOTFALL_OUT_POINTS
    footfall_out_points_matches = list(re.finditer(r'const FOOTFALL_OUT_POINTS = \[.*?\];', content, re.DOTALL))
    
    if len(footfall_out_points_matches) > 1:
        print(f"   Encontradas {len(footfall_out_points_matches)} declarações de FOOTFALL_OUT_POINTS")
        
        # Manter apenas a primeira declaração
        for i, match in enumerate(footfall_out_points_matches[1:], 1):
            content = content.replace(match.group(0), '')
            print(f"   Removida declaração duplicada {i+1}")
    
    # ========================================
    # VERIFICAR SE AINDA HÁ DECLARAÇÕES DUPLICADAS
    # ========================================
    print("3. Verificando se ainda há declarações duplicadas...")
    
    footfall_points_count = len(re.findall(r'const FOOTFALL_POINTS =', content))
    footfall_out_points_count = len(re.findall(r'const FOOTFALL_OUT_POINTS =', content))
    
    print(f"   FOOTFALL_POINTS: {footfall_points_count} declarações")
    print(f"   FOOTFALL_OUT_POINTS: {footfall_out_points_count} declarações")
    
    if footfall_points_count > 1 or footfall_out_points_count > 1:
        print("   ⚠️  Ainda há declarações duplicadas!")
        return False
    else:
        print("   ✅ Nenhuma declaração duplicada encontrada!")
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo declarações duplicadas de variáveis...")
    
    if fix_duplicate_variables():
        print("\n🎉 Declarações duplicadas corrigidas!")
        print("📋 Resultado:")
        print("   ✅ Declarações duplicadas removidas")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao corrigir declarações duplicadas")

