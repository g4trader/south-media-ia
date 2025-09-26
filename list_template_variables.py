#!/usr/bin/env python3
"""
Script para listar todas as variáveis do template genérico
e mostrar quais ainda precisam ser implementadas
"""

import re
from typing import Set, Dict, List

def extract_all_variables(template_path: str) -> Dict[str, Set[str]]:
    """
    Extrai todas as variáveis do template
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    variables = {
        'double_braces': set(),
        'single_braces': set(),
        'html_comments': set(),
        'js_placeholders': set(),
        'url_patterns': set()
    }
    
    # Padrão 1: {{VARIAVEL}}
    double_braces = re.findall(r'\{\{([^}]+)\}\}', content)
    variables['double_braces'] = set(double_braces)
    
    # Padrão 2: {VARIAVEL} (sem duplo)
    single_braces = re.findall(r'(?<!\{)\{([^}]+)\}(?!\})', content)
    variables['single_braces'] = set(single_braces)
    
    # Padrão 3: <!-- VARIAVEL -->
    html_comments = re.findall(r'<!--\s*([^-\s][^->]*?)\s*-->', content)
    variables['html_comments'] = set(html_comments)
    
    # Padrão 4: 'PLACEHOLDER' ou "PLACEHOLDER"
    js_placeholders = re.findall(r'[\'"]([A-Z_][A-Z0-9_]*)[\'"]', content)
    variables['js_placeholders'] = set(js_placeholders)
    
    # Padrão 5: URLs e endpoints
    url_patterns = re.findall(r'[A-Z_]+_URL|[A-Z_]+_ENDPOINT|[A-Z_]+_PATH', content)
    variables['url_patterns'] = set(url_patterns)
    
    return variables

def analyze_variable_usage(variables: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """
    Analisa o uso das variáveis e categoriza por tipo
    """
    analysis = {
        'campaign_info': [],
        'financial_data': [],
        'performance_metrics': [],
        'creative_info': [],
        'technical_settings': [],
        'ui_elements': [],
        'unimplemented': []
    }
    
    # Todas as variáveis encontradas
    all_vars = set()
    for var_set in variables.values():
        all_vars.update(var_set)
    
    # Categorizar variáveis
    for var in sorted(all_vars):
        var_lower = var.lower()
        
        if any(keyword in var_lower for keyword in ['client', 'campaign', 'name', 'status', 'period', 'description', 'objectives']):
            analysis['campaign_info'].append(var)
        elif any(keyword in var_lower for keyword in ['budget', 'investment', 'spend', 'cost', 'price']):
            analysis['financial_data'].append(var)
        elif any(keyword in var_lower for keyword in ['metric', 'performance', 'impression', 'click', 'view', 'completion', 'rate']):
            analysis['performance_metrics'].append(var)
        elif any(keyword in var_lower for keyword in ['creative', 'strategy', 'segment', 'channel', 'format', 'specification']):
            analysis['creative_info'].append(var)
        elif any(keyword in var_lower for keyword in ['api', 'endpoint', 'url', 'key', 'path', 'original']):
            analysis['technical_settings'].append(var)
        elif any(keyword in var_lower for keyword in ['badge', 'tab', 'section', 'header', 'footer']):
            analysis['ui_elements'].append(var)
        else:
            analysis['unimplemented'].append(var)
    
    return analysis

def generate_implementation_guide(analysis: Dict[str, List[str]]) -> str:
    """
    Gera um guia de implementação para as variáveis
    """
    guide = "# 📋 Guia de Implementação - Variáveis do Template\n\n"
    
    for category, vars_list in analysis.items():
        if not vars_list:
            continue
            
        category_name = category.replace('_', ' ').title()
        guide += f"## 🏷️ {category_name}\n\n"
        
        for var in vars_list:
            guide += f"- **{var}**: \n"
            
            # Adicionar descrição baseada no nome da variável
            var_lower = var.lower()
            if 'client' in var_lower:
                guide += "  - Descrição: Nome do cliente\n"
                guide += "  - Exemplo: `'SEBRAE PR'`\n"
            elif 'campaign' in var_lower and 'name' in var_lower:
                guide += "  - Descrição: Nome da campanha\n"
                guide += "  - Exemplo: `'Institucional Setembro'`\n"
            elif 'status' in var_lower:
                guide += "  - Descrição: Status da campanha\n"
                guide += "  - Exemplo: `'ATIVA'`, `'FINALIZADA'`, `'PAUSADA'`\n"
            elif 'budget' in var_lower:
                guide += "  - Descrição: Valores financeiros\n"
                guide += "  - Exemplo: `'50.000,00'`\n"
            elif 'api' in var_lower or 'endpoint' in var_lower:
                guide += "  - Descrição: URL da API\n"
                guide += "  - Exemplo: `'http://localhost:5001/api/campaign_key/data'`\n"
            
            guide += "\n"
        
        guide += "\n"
    
    return guide

def main():
    """
    Função principal
    """
    print("🔍 Analisando variáveis do template genérico...")
    
    # Extrair variáveis
    variables = extract_all_variables('static/dash_generic_template.html')
    
    # Analisar uso
    analysis = analyze_variable_usage(variables)
    
    # Mostrar estatísticas
    total_vars = sum(len(var_list) for var_list in variables.values())
    implemented_vars = sum(len(var_list) for category, var_list in analysis.items() 
                          if category != 'unimplemented')
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"  Total de variáveis: {total_vars}")
    print(f"  Variáveis implementadas: {implemented_vars}")
    print(f"  Variáveis não implementadas: {len(analysis['unimplemented'])}")
    
    # Mostrar categorias
    print(f"\n🏷️ CATEGORIAS:")
    for category, vars_list in analysis.items():
        if vars_list:
            category_name = category.replace('_', ' ').title()
            print(f"  📋 {category_name}: {len(vars_list)} variáveis")
    
    # Mostrar variáveis não implementadas
    if analysis['unimplemented']:
        print(f"\n⚠️ VARIÁVEIS NÃO IMPLEMENTADAS:")
        for var in analysis['unimplemented']:
            print(f"  - {var}")
    
    # Gerar guia de implementação
    guide = generate_implementation_guide(analysis)
    
    with open('template_implementation_guide.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n📝 Guia de implementação salvo em: template_implementation_guide.md")
    
    # Mostrar resumo por categoria
    print(f"\n📋 RESUMO POR CATEGORIA:")
    for category, vars_list in analysis.items():
        if vars_list:
            category_name = category.replace('_', ' ').title()
            print(f"\n🔹 {category_name}:")
            for var in vars_list[:3]:  # Mostrar apenas as primeiras 3
                print(f"  - {var}")
            if len(vars_list) > 3:
                print(f"  ... e mais {len(vars_list) - 3}")
    
    print(f"\n✅ Análise concluída!")

if __name__ == "__main__":
    main()

