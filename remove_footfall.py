#!/usr/bin/env python3
"""
Script para remover todas as referências ao footfall do dashboard
"""

import re

def remove_footfall_content():
    # Ler o arquivo HTML
    with open('static/dash_multicanal_spotify_programatica.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Remover FOOTFALL_POINTS array
    html_content = re.sub(r'const FOOTFALL_POINTS = \[.*?\];', '', html_content, flags=re.DOTALL)
    
    # Remover footfallData array
    html_content = re.sub(r'const footfallData = \[.*?\];', '', html_content, flags=re.DOTALL)
    
    # Remover todas as funções footfall
    footfall_functions = [
        r'function initializeFootfall\(\) \{.*?\}',
        r'function initializeFootfallMetrics\(\) \{.*?\}',
        r'function updateFootfallTopStores\(\) \{.*?\}',
        r'function initializeFootfallContent\(\) \{.*?\}',
        r'function updateFootfallMetrics\(\) \{.*?\}',
        r'function initializeFootfallMap\(\) \{.*?\}',
        r'function initializeFootfallChart\(\) \{.*?\}',
        r'function initializeFootfallTopStores\(\) \{.*?\}'
    ]
    
    for pattern in footfall_functions:
        html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)
    
    # Remover comentários footfall
    html_content = re.sub(r'// FOOTFALL FUNCTIONS REMOVED.*?\n', '', html_content)
    html_content = re.sub(r'// Dados de footfall.*?\n', '', html_content)
    
    # Remover referências footfall no JavaScript
    html_content = re.sub(r'const showFF = false;.*?\n', '', html_content)
    html_content = re.sub(r'const footfallWrap = document\.getElementById.*?\n', '', html_content)
    html_content = re.sub(r'if\(footfallWrap\).*?\n', '', html_content)
    
    # Remover seção footfallExtras
    html_content = re.sub(r'<div id="footfallExtras".*?</div>', '', html_content, flags=re.DOTALL)
    
    # Limpar linhas vazias extras
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    
    # Salvar o arquivo atualizado
    with open('static/dash_multicanal_spotify_programatica.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Conteúdo footfall removido com sucesso!")

if __name__ == "__main__":
    remove_footfall_content()
