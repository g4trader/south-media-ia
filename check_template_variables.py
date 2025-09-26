#!/usr/bin/env python3
"""
Script simples para verificar variáveis reais do template
"""

import re

def check_template_variables():
    """
    Verifica as variáveis reais do template genérico
    """
    with open('static/dash_generic_template.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar apenas variáveis no formato {{VARIAVEL}}
    variables = re.findall(r'\{\{([A-Z_][A-Z0-9_]*)\}\}', content)
    
    print("🔍 Variáveis encontradas no template:")
    print("=" * 50)
    
    for i, var in enumerate(sorted(set(variables)), 1):
        print(f"{i:2d}. {var}")
    
    print(f"\n📊 Total: {len(set(variables))} variáveis únicas")
    
    # Verificar se todas estão sendo substituídas no servidor
    print("\n✅ Verificando implementação no servidor...")
    
    with open('real_server.py', 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    implemented = []
    not_implemented = []
    
    for var in set(variables):
        if var.lower() in server_content:
            implemented.append(var)
        else:
            not_implemented.append(var)
    
    print(f"✅ Implementadas: {len(implemented)}")
    print(f"❌ Não implementadas: {len(not_implemented)}")
    
    if not_implemented:
        print("\n⚠️ Variáveis não implementadas:")
        for var in not_implemented:
            print(f"  - {var}")
    
    # Mostrar exemplo de substituição
    print(f"\n📝 Exemplo de substituição:")
    print(f"campaign_data = {{")
    for var in sorted(set(variables))[:5]:  # Mostrar apenas as primeiras 5
        print(f'    "{var.lower()}": "valor_exemplo",')
    print(f"    # ... outras variáveis")
    print(f"}}")

if __name__ == "__main__":
    check_template_variables()

