#!/usr/bin/env python3
"""
Script para corrigir os IDs da aba Footfall Out de forma precisa
"""

def fix_footfall_out_ids():
    """Corrigir IDs da aba Footfall Out"""
    
    file_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/static/dash_sonho_v2.html"
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção da aba Footfall Out
    start_marker = 'id="tab-footfall-out"'
    end_marker = '</div>'
    
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("Div tab-footfall-out não encontrada")
        return
    
    # Encontrar o final da seção
    section_end = content.find('</div>', start_pos)
    if section_end == -1:
        print("Fim da seção não encontrado")
        return
    
    # Extrair a seção
    section = content[start_pos:section_end + 6]
    
    # Contar quantas vezes cada ID aparece na seção
    map_count = section.count('id="footfall-map"')
    chart_count = section.count('id="footfall-performanceChart"')
    stores_count = section.count('id="footfall-topStores"')
    
    print(f"IDs encontrados na seção Footfall Out:")
    print(f"  footfall-map: {map_count}")
    print(f"  footfall-performanceChart: {chart_count}")
    print(f"  footfall-topStores: {stores_count}")
    
    # Corrigir os IDs apenas nesta seção
    section = section.replace('id="footfall-map"', 'id="footfall-out-map"')
    section = section.replace('id="footfall-performanceChart"', 'id="footfall-out-performanceChart"')
    section = section.replace('id="footfall-topStores"', 'id="footfall-out-topStores"')
    
    # Substituir a seção no conteúdo
    new_content = content[:start_pos] + section + content[section_end + 6:]
    
    # Salvar o arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("IDs da aba Footfall Out corrigidos com sucesso!")

if __name__ == "__main__":
    fix_footfall_out_ids()

