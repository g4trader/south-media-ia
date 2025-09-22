#!/usr/bin/env python3
"""
Debug template replacement para verificar se os placeholders estão sendo substituídos
"""

import json
import glob
from datetime import datetime

def debug_template_replacement():
    """Debug template replacement"""
    
    print("🔍 DEBUGGING TEMPLATE REPLACEMENT")
    print("=" * 70)
    
    # Carregar dados dos quartis corrigidos
    quartis_files = glob.glob("quartis_corrected_video_starts_*.json")
    if not quartis_files:
        print("❌ Nenhum arquivo de dados dos quartis encontrado")
        return
    
    latest_quartis_file = max(quartis_files)
    print(f"📁 Carregando dados dos quartis: {latest_quartis_file}")
    
    with open(latest_quartis_file, 'r', encoding='utf-8') as f:
        quartis_data = json.load(f)
    
    print("📊 DADOS DOS QUARTIS:")
    for key, value in quartis_data.items():
        print(f"   {key}: {value}")
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"\n🔍 VERIFICANDO PLACEHOLDERS NO TEMPLATE:")
    
    # Verificar se os placeholders existem
    placeholders = [
        "{{QUARTIL_25_PERCENTAGE}}",
        "{{QUARTIL_50_PERCENTAGE}}",
        "{{QUARTIL_75_PERCENTAGE}}",
        "{{QUARTIL_100_PERCENTAGE}}",
        "{{QUARTIL_25_VALUE}}",
        "{{QUARTIL_50_VALUE}}",
        "{{QUARTIL_75_VALUE}}",
        "{{QUARTIL_100_VALUE}}"
    ]
    
    for placeholder in placeholders:
        count = template_content.count(placeholder)
        print(f"   {placeholder}: {count} ocorrências")
    
    # Fazer a substituição
    print(f"\n🔄 FAZENDO SUBSTITUIÇÃO:")
    for key, value in quartis_data.items():
        placeholder = f"{{{{{key}}}}}"
        old_count = template_content.count(placeholder)
        template_content = template_content.replace(placeholder, value)
        new_count = template_content.count(placeholder)
        print(f"   {placeholder} -> {value} ({old_count} -> {new_count})")
    
    # Verificar se ainda há placeholders não substituídos
    print(f"\n🔍 VERIFICANDO PLACEHOLDERS RESTANTES:")
    remaining_placeholders = []
    for placeholder in placeholders:
        count = template_content.count(placeholder)
        if count > 0:
            remaining_placeholders.append(placeholder)
            print(f"   ❌ {placeholder}: {count} ocorrências restantes")
        else:
            print(f"   ✅ {placeholder}: substituído")
    
    if remaining_placeholders:
        print(f"\n❌ PROBLEMA: {len(remaining_placeholders)} placeholders não foram substituídos")
        return False
    else:
        print(f"\n✅ SUCESSO: Todos os placeholders foram substituídos")
        
        # Salvar template corrigido
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"static/dash_semana_do_pescado_DEBUG_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"📁 Template corrigido salvo: {filename}")
        return True

if __name__ == "__main__":
    debug_template_replacement()



