#!/usr/bin/env python3
"""
Script para validar variáveis do template genérico
Identifica todas as variáveis que precisam ser substituídas
"""

import re
import json
from typing import List, Dict, Set

def extract_template_variables(template_content: str) -> Dict[str, List[str]]:
    """
    Extrai todas as variáveis do template usando diferentes padrões
    """
    variables = {
        'double_braces': [],      # {{VARIAVEL}}
        'single_braces': [],      # {VARIAVEL}
        'html_placeholders': [],  # <!-- VARIAVEL -->
        'js_placeholders': [],    # 'PLACEHOLDER'
        'url_placeholders': []    # URL_PLACEHOLDER
    }
    
    # Padrão 1: {{VARIAVEL}}
    double_braces = re.findall(r'\{\{([^}]+)\}\}', template_content)
    variables['double_braces'] = double_braces
    
    # Padrão 2: {VARIAVEL} (sem duplo)
    single_braces = re.findall(r'(?<!\{)\{([^}]+)\}(?!\})', template_content)
    variables['single_braces'] = single_braces
    
    # Padrão 3: <!-- VARIAVEL -->
    html_placeholders = re.findall(r'<!--\s*([^-\s][^->]*?)\s*-->', template_content)
    variables['html_placeholders'] = html_placeholders
    
    # Padrão 4: 'PLACEHOLDER' ou "PLACEHOLDER"
    js_placeholders = re.findall(r'[\'"]([A-Z_][A-Z0-9_]*)[\'"]', template_content)
    variables['js_placeholders'] = js_placeholders
    
    # Padrão 5: URLs e endpoints
    url_placeholders = re.findall(r'[A-Z_]+_URL|[A-Z_]+_ENDPOINT', template_content)
    variables['url_placeholders'] = url_placeholders
    
    return variables

def analyze_template_structure(template_content: str) -> Dict[str, any]:
    """
    Analisa a estrutura do template para identificar seções
    """
    analysis = {
        'has_loading_screen': 'loadingScreen' in template_content,
        'has_api_calls': 'fetch(' in template_content or 'apiEndpoint' in template_content,
        'has_charts': 'Chart(' in template_content or 'chart.js' in template_content,
        'has_tables': '<table' in template_content,
        'has_tabs': 'data-tab=' in template_content,
        'has_responsive_design': '@media' in template_content,
        'has_south_media_branding': 'South Media' in template_content,
        'has_custom_styling': ':root' in template_content,
        'sections': []
    }
    
    # Identificar seções principais
    sections = re.findall(r'<!--\s*([^-\s][^->]*?)\s*-->', template_content)
    analysis['sections'] = sections
    
    return analysis

def create_variable_mapping() -> Dict[str, str]:
    """
    Cria mapeamento de variáveis para valores de exemplo
    """
    return {
        # Informações básicas
        'CLIENT_NAME': 'Nome do Cliente',
        'CAMPAIGN_NAME': 'Nome da Campanha',
        'CAMPAIGN_STATUS': 'ATIVA',
        'CAMPAIGN_PERIOD': '01/01/2024 a 31/01/2024',
        'CAMPAIGN_DESCRIPTION': 'Performance do Canal - Complete View',
        'CAMPAIGN_OBJECTIVES': 'Objetivos da campanha...',
        
        # Dados financeiros
        'TOTAL_BUDGET': '50.000,00',
        'BUDGET_USED': '25.000,00',
        'PACING_PERCENTAGE': '50',
        'TARGET_VC': '500.000',
        'CPV_CONTRACTED': '0,10',
        'CPV_CURRENT': '0,12',
        
        # Canais e formatos
        'PRIMARY_CHANNEL': 'YOUTUBE',
        'CHANNEL_BADGES': '<span style="background:rgba(255,107,53,0.2); padding:6px 12px; border-radius:20px; font-size:0.9rem">YOUTUBE</span>',
        
        # Estratégias
        'SEGMENTATION_STRATEGY': '''<li><strong>🎯 Segmentação:</strong> Estratégia focada em canais específicos</li>
            <li><strong>🚫 Exclusões:</strong> Canais negativados</li>''',
        
        'CREATIVE_STRATEGY': '''<li><strong>📱 Criativos:</strong> Testar variações focando nos primeiros segundos</li>
            <li><strong>🎬 Formato:</strong> Vídeo de 30s para máxima retenção</li>''',
        
        'FORMAT_SPECIFICATIONS': '''<li>Complete View (30s) para máxima atenção</li>
            <li>Vídeo institucional 30s</li>''',
        
        # URLs e endpoints
        'API_ENDPOINT': 'https://south-media-ia-609095880025.us-central1.run.app/api/CAMPAIGN_KEY/data',
        'CAMPAIGN_KEY': 'campaign_key_placeholder',
        
        # HTML original (placeholder)
        'ORIGINAL_HTML': '<!-- HTML original será inserido aqui -->'
    }

def validate_template_completeness(template_content: str, variables: Dict[str, List[str]]) -> Dict[str, any]:
    """
    Valida se o template está completo e funcional
    """
    validation = {
        'is_complete': True,
        'missing_elements': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Verificar elementos essenciais
    essential_elements = [
        'CLIENT_NAME', 'CAMPAIGN_NAME', 'CAMPAIGN_STATUS',
        'API_ENDPOINT', 'CAMPAIGN_KEY'
    ]
    
    all_variables = []
    for var_list in variables.values():
        all_variables.extend(var_list)
    
    for element in essential_elements:
        if element not in all_variables:
            validation['missing_elements'].append(element)
            validation['is_complete'] = False
    
    # Verificar estrutura HTML
    if not re.search(r'<html[^>]*>', template_content):
        validation['warnings'].append('Estrutura HTML básica não encontrada')
    
    if not re.search(r'<head[^>]*>', template_content):
        validation['warnings'].append('Seção HEAD não encontrada')
    
    if not re.search(r'<body[^>]*>', template_content):
        validation['warnings'].append('Seção BODY não encontrada')
    
    # Verificar JavaScript
    if 'DashboardLoader' not in template_content:
        validation['warnings'].append('Classe DashboardLoader não encontrada')
    
    if 'fetch(' not in template_content:
        validation['warnings'].append('Função fetch() não encontrada para carregar dados')
    
    # Recomendações
    if 'loadingScreen' not in template_content:
        validation['recommendations'].append('Adicionar tela de loading para melhor UX')
    
    if 'error' not in template_content.lower():
        validation['recommendations'].append('Adicionar tratamento de erros')
    
    return validation

def generate_replacement_script(variables: Dict[str, List[str]], mapping: Dict[str, str]) -> str:
    """
    Gera script Python para fazer as substituições no template
    """
    script = '''#!/usr/bin/env python3
"""
Script gerado automaticamente para substituir variáveis no template
"""

def replace_template_variables(template_content: str, campaign_data: dict) -> str:
    """
    Substitui todas as variáveis do template com dados reais
    """
    replacements = {
'''
    
    # Adicionar todas as variáveis encontradas
    all_variables = set()
    for var_list in variables.values():
        all_variables.update(var_list)
    
    for var in sorted(all_variables):
        if var in mapping:
            script += f'        "{var}": campaign_data.get("{var.lower()}", "{mapping[var]}"),\n'
        else:
            script += f'        "{var}": campaign_data.get("{var.lower()}", "VALOR_NAO_DEFINIDO"),\n'
    
    script += '''    }
    
    # Fazer substituições
    result = template_content
    for placeholder, value in replacements.items():
        result = result.replace(f"{{{{{placeholder}}}}}", str(value))
    
    return result

# Exemplo de uso:
if __name__ == "__main__":
    # Carregar template
    with open('static/dash_generic_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Dados de exemplo
    campaign_data = {
        "client_name": "SEBRAE PR",
        "campaign_name": "Institucional Setembro",
        "campaign_status": "ATIVA",
        "campaign_period": "01/09/2024 a 30/09/2024",
        "campaign_description": "Performance do YouTube - Complete View",
        "campaign_objectives": "Fortalecer a marca e comunicar valores institucionais",
        "total_budget": "30.000,00",
        "budget_used": "15.000,00",
        "pacing_percentage": "50",
        "target_vc": "300.000",
        "cpv_contracted": "0,10",
        "cpv_current": "0,12",
        "primary_channel": "YOUTUBE",
        "api_endpoint": "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_institucional_setembro/data",
        "campaign_key": "sebrae_pr_institucional_setembro"
    }
    
    # Substituir variáveis
    result = replace_template_variables(template, campaign_data)
    
    # Salvar resultado
    with open('static/dash_test_output.html', 'w', encoding='utf-8') as f:
        f.write(result)
    
    print("✅ Template processado e salvo em static/dash_test_output.html")
'''
    
    return script

def main():
    """
    Função principal para validar o template
    """
    print("🔍 Validando template genérico...")
    
    # Carregar template
    try:
        with open('static/dash_generic_template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        print("✅ Template carregado com sucesso")
    except FileNotFoundError:
        print("❌ Arquivo template não encontrado: static/dash_generic_template.html")
        return
    except Exception as e:
        print(f"❌ Erro ao carregar template: {e}")
        return
    
    # Extrair variáveis
    print("\n📊 Extraindo variáveis...")
    variables = extract_template_variables(template_content)
    
    # Mostrar variáveis encontradas
    total_variables = 0
    for pattern, var_list in variables.items():
        if var_list:
            print(f"  {pattern}: {len(var_list)} variáveis")
            for var in var_list[:5]:  # Mostrar apenas as primeiras 5
                print(f"    - {var}")
            if len(var_list) > 5:
                print(f"    ... e mais {len(var_list) - 5}")
            total_variables += len(var_list)
    
    print(f"\n📈 Total de variáveis encontradas: {total_variables}")
    
    # Analisar estrutura
    print("\n🏗️ Analisando estrutura...")
    structure = analyze_template_structure(template_content)
    for key, value in structure.items():
        if isinstance(value, bool):
            status = "✅" if value else "❌"
            print(f"  {status} {key.replace('_', ' ').title()}")
        elif isinstance(value, list) and value:
            print(f"  📋 {key.replace('_', ' ').title()}: {', '.join(value)}")
    
    # Validar completude
    print("\n✅ Validando completude...")
    validation = validate_template_completeness(template_content, variables)
    
    if validation['is_complete']:
        print("  ✅ Template está completo")
    else:
        print("  ❌ Template incompleto")
        for missing in validation['missing_elements']:
            print(f"    - Faltando: {missing}")
    
    if validation['warnings']:
        print("\n⚠️ Avisos:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['recommendations']:
        print("\n💡 Recomendações:")
        for rec in validation['recommendations']:
            print(f"  - {rec}")
    
    # Criar mapeamento de variáveis
    print("\n🗺️ Criando mapeamento de variáveis...")
    mapping = create_variable_mapping()
    print(f"  📊 {len(mapping)} variáveis mapeadas")
    
    # Gerar script de substituição
    print("\n🔧 Gerando script de substituição...")
    replacement_script = generate_replacement_script(variables, mapping)
    
    with open('replace_template_variables.py', 'w', encoding='utf-8') as f:
        f.write(replacement_script)
    
    print("  ✅ Script salvo em: replace_template_variables.py")
    
    # Resumo final
    print("\n" + "="*60)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("="*60)
    print(f"📊 Total de variáveis: {total_variables}")
    print(f"🏗️ Estrutura HTML: {'✅' if structure.get('has_loading_screen') else '❌'}")
    print(f"📱 Responsivo: {'✅' if structure.get('has_responsive_design') else '❌'}")
    print(f"🎨 South Media: {'✅' if structure.get('has_south_media_branding') else '❌'}")
    print(f"📈 Gráficos: {'✅' if structure.get('has_charts') else '❌'}")
    print(f"📋 Tabelas: {'✅' if structure.get('has_tables') else '❌'}")
    print(f"🔄 API Calls: {'✅' if structure.get('has_api_calls') else '❌'}")
    print(f"✅ Completude: {'✅' if validation['is_complete'] else '❌'}")
    
    if validation['warnings'] or validation['recommendations']:
        print(f"\n⚠️ {len(validation['warnings'])} avisos, 💡 {len(validation['recommendations'])} recomendações")
    
    print("\n🚀 Próximos passos:")
    print("  1. Execute: python3 replace_template_variables.py")
    print("  2. Verifique: static/dash_test_output.html")
    print("  3. Integre no gerador de dashboards")

if __name__ == "__main__":
    main()

