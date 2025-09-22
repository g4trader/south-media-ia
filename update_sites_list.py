#!/usr/bin/env python3
"""
Atualizar lista de sites na aba Visão Geral do dashboard
"""

import json
import glob
from datetime import datetime

def update_sites_list():
    """Atualizar lista de sites no dashboard"""
    
    print("🔄 ATUALIZANDO LISTA DE SITES NO DASHBOARD")
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
    
    print(f"\n🔍 PROCURANDO SEÇÃO DE SITES NO TEMPLATE:")
    
    # Procurar pela seção de sites na aba Visão Geral
    # Vamos procurar por padrões como "Lista de Sites" ou similar
    import re
    
    # Procurar por seções que possam conter lista de sites
    sites_patterns = [
        r'<div[^>]*class="[^"]*sites[^"]*"[^>]*>.*?</div>',
        r'<div[^>]*class="[^"]*list[^"]*"[^>]*>.*?</div>',
        r'<ul[^>]*>.*?</ul>',
        r'<ol[^>]*>.*?</ol>'
    ]
    
    found_sections = []
    for pattern in sites_patterns:
        matches = re.findall(pattern, template_content, re.DOTALL | re.IGNORECASE)
        if matches:
            found_sections.extend(matches)
            print(f"   ✅ Encontradas {len(matches)} seções com padrão: {pattern[:30]}...")
    
    # Procurar por texto que indique lista de sites
    text_patterns = [
        r'Lista de Sites',
        r'Sites',
        r'Portais',
        r'Domínios'
    ]
    
    for pattern in text_patterns:
        if re.search(pattern, template_content, re.IGNORECASE):
            print(f"   ✅ Encontrado texto: {pattern}")
    
    # Procurar pela aba "Visão Geral" especificamente
    overview_section = re.search(r'<div[^>]*id="[^"]*overview[^"]*"[^>]*>.*?</div>', template_content, re.DOTALL | re.IGNORECASE)
    if overview_section:
        print(f"   ✅ Seção 'Visão Geral' encontrada")
        overview_content = overview_section.group(0)
        
        # Procurar por lista dentro da seção Visão Geral
        list_items = re.findall(r'<li[^>]*>.*?</li>', overview_content, re.DOTALL)
        if list_items:
            print(f"   ✅ Encontrados {len(list_items)} itens de lista na Visão Geral")
            
            # Mostrar alguns itens para identificar a lista de sites
            print(f"\n📋 ITENS ENCONTRADOS NA VISÃO GERAL:")
            for i, item in enumerate(list_items[:5], 1):
                # Extrair texto do item
                text_match = re.search(r'>([^<]+)<', item)
                if text_match:
                    text = text_match.group(1).strip()
                    print(f"   {i}. {text}")
    
    # Procurar por uma seção específica que contenha sites
    # Vamos procurar por uma div que contenha múltiplos links ou domínios
    potential_sites_section = re.search(r'<div[^>]*>.*?(?:\.com|\.br|\.org).*?</div>', template_content, re.DOTALL | re.IGNORECASE)
    if potential_sites_section:
        print(f"   ✅ Seção potencial com sites encontrada")
        section_content = potential_sites_section.group(0)
        
        # Extrair domínios da seção
        domains = re.findall(r'([a-zA-Z0-9.-]+\.(?:com|br|org|net))', section_content, re.IGNORECASE)
        if domains:
            print(f"   📋 Domínios encontrados: {domains[:5]}...")
    
    # Vamos procurar por uma abordagem mais específica
    # Procurar por uma div que contenha uma lista de sites
    sites_div_pattern = r'<div[^>]*class="[^"]*sites[^"]*"[^>]*>(.*?)</div>'
    sites_div_match = re.search(sites_div_pattern, template_content, re.DOTALL | re.IGNORECASE)
    
    if sites_div_match:
        print(f"   ✅ Div de sites encontrada")
        sites_div_content = sites_div_match.group(1)
        print(f"   📄 Conteúdo: {sites_div_content[:200]}...")
        
        # Substituir o conteúdo da div de sites
        new_sites_html = generate_sites_html(sites_list)
        template_content = template_content.replace(sites_div_content, new_sites_html)
        print(f"   ✅ Conteúdo da div de sites substituído")
    
    else:
        # Se não encontrarmos uma div específica, vamos procurar por uma lista
        # e substituir os itens
        print(f"   🔍 Procurando por lista para substituir...")
        
        # Procurar por uma lista (ul ou ol) que contenha sites
        list_pattern = r'<ul[^>]*>(.*?)</ul>'
        list_match = re.search(list_pattern, template_content, re.DOTALL)
        
        if list_match:
            print(f"   ✅ Lista encontrada")
            list_content = list_match.group(1)
            
            # Verificar se a lista contém sites
            if re.search(r'\.(com|br|org)', list_content, re.IGNORECASE):
                print(f"   ✅ Lista contém sites")
                
                # Substituir o conteúdo da lista
                new_sites_html = generate_sites_list_html(sites_list)
                template_content = template_content.replace(list_content, new_sites_html)
                print(f"   ✅ Conteúdo da lista substituído")
    
    # Salvar template atualizado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_template = f"templates/template_simple_sites_updated_{timestamp}.html"
    
    with open(updated_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ Template atualizado salvo: {updated_template}")
    
    return updated_template

def generate_sites_html(sites_list):
    """Gerar HTML para lista de sites"""
    html = ""
    for site in sites_list:
        html += f'<div class="site-item">{site}</div>\n'
    return html

def generate_sites_list_html(sites_list):
    """Gerar HTML para lista de sites (ul/li)"""
    html = ""
    for site in sites_list:
        html += f'<li class="site-item">{site}</li>\n'
    return html

if __name__ == "__main__":
    update_sites_list()



