#!/usr/bin/env python3
"""
Remover todas as referências ao Netflix do dashboard
"""

import json
import glob
from datetime import datetime

def remove_netflix_references():
    """Remover referências ao Netflix"""
    
    print("🔄 REMOVENDO REFERÊNCIAS AO NETFLIX")
    print("=" * 70)
    
    # Carregar template
    with open('templates/template_simple.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"📄 Template carregado: {len(template_content)} caracteres")
    
    # Procurar por referências ao Netflix
    import re
    
    netflix_references = [
        # Comentário "Quartis Netflix"
        r'<!-- Quartis Netflix -->\s*',
        
        # Seção de insights sobre Netflix
        r'<div style="background: rgba\(16, 185, 129, 0\.1\); border: 1px solid #10B981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">\s*<div style="display: flex; align-items: center; margin-bottom: 0\.5rem;">\s*<span style="color: #10B981; font-size: 1rem; margin-right: 0\.5rem;">✅</span>\s*<span style="color: #10B981; font-weight: bold; font-size: 0\.875rem;">Netflix: Excelente Retenção</span>\s*</div>\s*<p style="color: white; font-size: 0\.75rem; line-height: 1\.4;">99,7%</p>\s*</div>\s*',
        
        # Texto sobre combinação Netflix + Programático
        r'Combinação Netflix \+ Programático mostrou-se ideal para awareness de marca da Copacol, com alta retenção e engajamento\.',
        
        # Card do Netflix na seção de canais
        r'<div style="background: rgba\(251, 146, 60, 0\.2\); padding: 1rem; border-radius: 8px; border: 1px solid #FB923C;">\s*<div style="font-weight: bold; color: #FB923C; font-size: 0\.875rem; margin-bottom: 0\.25rem;">Netflix</div>\s*<div style="color: white; font-size: 0\.75rem;">Plataforma premium com audiência qualificada</div>\s*</div>\s*'
    ]
    
    print(f"\n🔍 PROCURANDO REFERÊNCIAS AO NETFLIX:")
    
    removed_count = 0
    for i, pattern in enumerate(netflix_references, 1):
        matches = re.findall(pattern, template_content, re.DOTALL)
        if matches:
            print(f"   ✅ Referência {i} encontrada: {len(matches)} ocorrência(s)")
            template_content = re.sub(pattern, '', template_content, flags=re.DOTALL)
            removed_count += len(matches)
        else:
            print(f"   ❌ Referência {i} não encontrada")
    
    # Substituir texto sobre combinação
    template_content = template_content.replace(
        'Combinação Netflix + Programático mostrou-se ideal para awareness de marca da Copacol, com alta retenção e engajamento.',
        'Combinação YouTube + Programática Video mostrou-se ideal para awareness de marca da Semana do Pescado, com alta retenção e engajamento.'
    )
    
    print(f"\n✅ Total de referências removidas: {removed_count}")
    
    # Verificar se ainda há referências ao Netflix
    remaining_netflix = re.findall(r'[Nn]etflix', template_content)
    if remaining_netflix:
        print(f"⚠️ Ainda há {len(remaining_netflix)} referência(s) ao Netflix:")
        for ref in remaining_netflix:
            print(f"   - {ref}")
    else:
        print(f"✅ Todas as referências ao Netflix foram removidas")
    
    # Salvar template atualizado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updated_template = f"templates/template_simple_no_netflix_{timestamp}.html"
    
    with open(updated_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ Template sem Netflix salvo: {updated_template}")
    
    return updated_template

if __name__ == "__main__":
    remove_netflix_references()



