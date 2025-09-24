#!/usr/bin/env python3
"""
Script para limpar restos do código footfall que ficaram soltos
"""

import re

def clean_footfall_remnants():
    # Ler o arquivo HTML
    with open('static/dash_multicanal_spotify_programatica.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Encontrar onde termina o JavaScript correto
    end_js_pattern = r'}\)\);'
    match = re.search(end_js_pattern, html_content)
    
    if match:
        # Pegar tudo até o final do JavaScript correto
        clean_content = html_content[:match.end()]
        
        # Adicionar o fechamento correto
        clean_content += '\n\n</script>\n</body>\n</html>'
        
        # Salvar o arquivo limpo
        with open('static/dash_multicanal_spotify_programatica.html', 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print("✅ Código footfall limpo com sucesso!")
    else:
        print("❌ Não foi possível encontrar o final do JavaScript")

if __name__ == "__main__":
    clean_footfall_remnants()
