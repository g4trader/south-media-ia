#!/usr/bin/env python3
"""
Substituir tabela de publishers com nova lista de sites
"""

import json
import glob
from datetime import datetime

def replace_publishers_table():
    """Substituir tabela de publishers"""
    
    print("🔄 SUBSTITUINDO TABELA DE PUBLISHERS")
    print("=" * 70)
    
    # Carregar lista de sites
    sites_files = glob.glob("sites_list_direct_*.json")
    if not sites_files:
        print("❌ Nenhum arquivo de sites encontrado")
        return
    
    latest_sites_file = max(sites_files)
    print(f"📁 Carregando lista de sites: {latest_sites_file}")
    
    with open(latest_sites_file, 'r', encoding='utf-8') as f:
        sites_data = json.load(f)
    
    sites_list = sites_data["sites_list"]
    print(f"🌐 Sites carregados: {len(sites_list)}")
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"\n🔍 PROCURANDO TABELA DE PUBLISHERS:")
    
    # Procurar pela tabela de publishers
    import re
    
    # Padrão para encontrar a tabela completa de publishers
    table_pattern = r'(<div class="card" style="padding: 1\.25rem; margin-top: 1rem;">\s*<h3 style="font-size: 1rem; font-weight: bold; color: white; margin-bottom: 1rem;">TOP PUBLISHERS PROGRAMÁTICO</h3>\s*<div class="table-responsive">\s*<table style="width: 100%; border-collapse: collapse;">\s*<thead>\s*<tr style="border-bottom: 1px solid #374151;">\s*<th style="text-align: left; padding: 0\.75rem 0\.5rem; color: #9CA3AF; font-size: 0\.75rem;">PUBLISHER</th>\s*</tr>\s*</thead>\s*<tbody>)(.*?)(</tbody>\s*</table>\s*</div>\s*</div>)'
    
    table_match = re.search(table_pattern, template_content, re.DOTALL)
    
    if table_match:
        print(f"   ✅ Tabela de publishers encontrada")
        
        # Extrair as partes da tabela
        table_start = table_match.group(1)
        table_body = table_match.group(2)
        table_end = table_match.group(3)
        
        print(f"   📄 Conteúdo atual da tabela: {len(table_body)} caracteres")
        
        # Gerar novo conteúdo da tabela
        new_table_body = generate_publishers_table_body(sites_list)
        
        # Substituir o conteúdo da tabela
        new_table = table_start + new_table_body + table_end
        template_content = template_content.replace(table_match.group(0), new_table)
        
        print(f"   ✅ Tabela substituída com {len(sites_list)} sites")
        
    else:
        print(f"   ❌ Tabela de publishers não encontrada")
        return None
    
    # Salvar template atualizado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_template = f"templates/template_simple_publishers_updated_{timestamp}.html"
    
    with open(updated_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ Template atualizado salvo: {updated_template}")
    
    return updated_template

def generate_publishers_table_body(sites_list):
    """Gerar corpo da tabela de publishers"""
    table_body = ""
    
    for i, site in enumerate(sites_list):
        # Última linha não deve ter border-bottom
        if i == len(sites_list) - 1:
            table_body += f'                <tr>\n'
            table_body += f'                    <td style="padding: 0.75rem 0.5rem; color: white; font-size: 0.75rem;">{site}</td>\n'
            table_body += f'                </tr>\n'
        else:
            table_body += f'                <tr style="border-bottom: 1px solid #374151;">\n'
            table_body += f'                    <td style="padding: 0.75rem 0.5rem; color: white; font-size: 0.75rem;">{site}</td>\n'
            table_body += f'                </tr>\n'
    
    return table_body

if __name__ == "__main__":
    replace_publishers_table()



