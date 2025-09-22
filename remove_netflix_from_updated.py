#!/usr/bin/env python3
"""
Remover Netflix do template que já tem os canais corretos
"""

import json
import glob
from datetime import datetime

def remove_netflix_from_updated():
    """Remover Netflix do template atualizado"""
    
    print("🔄 REMOVENDO NETFLIX DO TEMPLATE ATUALIZADO")
    print("=" * 70)
    
    # Carregar template que já tem os canais corretos
    template_files = glob.glob("templates/template_simple_planning_updated_*.html")
    if not template_files:
        print("❌ Nenhum template atualizado encontrado")
        return
    
    latest_template = max(template_files)
    print(f"📁 Carregando template: {latest_template}")
    
    with open(latest_template, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print(f"📄 Template carregado: {len(template_content)} caracteres")
    
    # Procurar por referências ao Netflix
    import re
    
    print(f"\n🔍 PROCURANDO REFERÊNCIAS AO NETFLIX:")
    
    # Remover comentário "Quartis Netflix"
    template_content = re.sub(r'<!-- Quartis Netflix -->\s*', '', template_content)
    print(f"   ✅ Comentário 'Quartis Netflix' removido")
    
    # Remover seção de insights sobre Netflix
    netflix_insight_pattern = r'<div style="background: rgba\(16, 185, 129, 0\.1\); border: 1px solid #10B981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">\s*<div style="display: flex; align-items: center; margin-bottom: 0\.5rem;">\s*<span style="color: #10B981; font-size: 1rem; margin-right: 0\.5rem;">✅</span>\s*<span style="color: #10B981; font-weight: bold; font-size: 0\.875rem;">Netflix: Excelente Retenção</span>\s*</div>\s*<p style="color: white; font-size: 0\.75rem; line-height: 1\.4;">99,7%</p>\s*</div>\s*'
    template_content = re.sub(netflix_insight_pattern, '', template_content, flags=re.DOTALL)
    print(f"   ✅ Insight sobre Netflix removido")
    
    # Substituir texto sobre combinação
    template_content = template_content.replace(
        'Combinação Netflix + Programático mostrou-se ideal para awareness de marca da Copacol, com alta retenção e engajamento.',
        'Combinação YouTube + Programática Video mostrou-se ideal para awareness de marca da Semana do Pescado, com alta retenção e engajamento.'
    )
    print(f"   ✅ Texto sobre combinação atualizado")
    
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
    updated_template = f"templates/template_simple_final_no_netflix_{timestamp}.html"
    
    with open(updated_template, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"\n✅ Template final sem Netflix salvo: {updated_template}")
    
    return updated_template

if __name__ == "__main__":
    remove_netflix_from_updated()



