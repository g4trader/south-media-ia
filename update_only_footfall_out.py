#!/usr/bin/env python3
"""
Script para atualizar APENAS a aba Footfall Out com dados de outubro
Mantém os dados originais da aba Footfall Set (setembro)
"""

import json
import os
import re

def update_only_footfall_out():
    """Atualizar apenas a aba Footfall Out com dados de outubro"""
    
    # Dados de outubro (apenas para Footfall Out)
    october_footfall_data = [
        {
            "lat": -8.092339308671470,
            "lon": -34.888475077469840,
            "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina",
            "users": 5673,
            "rate": 12.1
        },
        {
            "lat": -8.131969149507210,
            "lon": -34.890696877301630,
            "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300",
            "users": 6731,
            "rate": 12.5
        },
        {
            "lat": -8.045915684673570,
            "lon": -34.890921522698360,
            "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310",
            "users": 5101,
            "rate": 11.9
        },
        {
            "lat": -8.047434924792,
            "lon": -34.900162115344200,
            "name": "Recibom - Graças - Av. Rui Barbosa, 551 - Graças, Recife - PE, 52011-040",
            "users": 4681,
            "rate": 9.9
        },
        {
            "lat": -8.029882473548620,
            "lon": -34.906651673016300,
            "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380",
            "users": 5693,
            "rate": 11.5
        },
        {
            "lat": -8.119932249004490,
            "lon": -34.890091268465570,
            "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050",
            "users": 6731,
            "rate": 12.9
        },
        {
            "lat": -8.142543914194250,
            "lon": -34.908109113491800,
            "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300",
            "users": 2389,
            "rate": 4.4
        },
        {
            "lat": -8.028130780221500,
            "lon": -34.890250688465570,
            "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005",
            "users": 3562,
            "rate": 6.7
        },
        {
            "lat": -7.995667724325500,
            "lon": -34.884649217116390,
            "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260",
            "users": 5631,
            "rate": 9.3
        },
        {
            "lat": -8.183601155218950,
            "lon": -34.891945002883600,
            "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010",
            "users": 3012,
            "rate": 10.2
        },
        {
            "lat": -8.182334054796810,
            "lon": -34.918200238558100,
            "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400",
            "users": 1121,
            "rate": 9.31
        },
        {
            "lat": -8.018367819706790,
            "lon": -34.996213513770500,
            "name": "Recibom - Timbi, Camaragibe - PE, 54765-290",
            "users": 891,
            "rate": 9.8
        }
    ]
    
    # Calcular métricas de outubro
    total_users = sum(store['users'] for store in october_footfall_data)
    active_stores = len(october_footfall_data)
    avg_conversion = sum(store['rate'] for store in october_footfall_data) / len(october_footfall_data)
    best_store = max(october_footfall_data, key=lambda x: x['users'])
    
    print("📊 Atualizando APENAS a aba Footfall Out (Outubro):")
    print(f"   Total de usuários: {total_users:,}")
    print(f"   Lojas ativas: {active_stores}")
    print(f"   Taxa de conversão média: {avg_conversion:.1f}%")
    print(f"   Melhor loja: {best_store['name']} ({best_store['users']:,} usuários)")
    
    # Salvar dados de outubro em arquivo separado
    october_data_file = "footfall_out_october_data.json"
    with open(october_data_file, 'w', encoding='utf-8') as f:
        json.dump({
            "month": "October 2024",
            "last_updated": "2024-10-27",
            "source": "https://docs.google.com/spreadsheets/d/1etGnblqr5YZIqXIweKj5qTMGqmWlxL9OLbN_Ss5tzlQ/edit?gid=120680471#gid=120680471",
            "data": october_footfall_data,
            "metrics": {
                "total_users": total_users,
                "active_stores": active_stores,
                "avg_conversion": round(avg_conversion, 1),
                "best_store": best_store['name'],
                "best_store_users": best_store['users']
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Dados de outubro salvos em: {october_data_file}")
    
    return october_footfall_data

def update_html_footfall_out_only(footfall_data):
    """Atualizar apenas as funções da aba Footfall Out"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar FOOTFALL_OUT_POINTS para outubro
    footfall_out_points = "const FOOTFALL_OUT_POINTS = [\n"
    for store in footfall_data:
        footfall_out_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    footfall_out_points += "];"
    
    # Adicionar FOOTFALL_OUT_POINTS após FOOTFALL_POINTS
    pattern = r'(const FOOTFALL_POINTS = \[.*?\]);'
    replacement = r'\1;\n\n' + footfall_out_points
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Atualizar funções da aba Footfall Out para usar FOOTFALL_OUT_POINTS
    # Substituir apenas nas funções específicas da aba Footfall Out
    content = content.replace(
        'function updateFootfallOutMetrics() {\n    const metricsContainer = document.getElementById(\'footfall-out-metrics\');\n    if (!metricsContainer || typeof FOOTFALL_POINTS === \'undefined\') {',
        'function updateFootfallOutMetrics() {\n    const metricsContainer = document.getElementById(\'footfall-out-metrics\');\n    if (!metricsContainer || typeof FOOTFALL_OUT_POINTS === \'undefined\') {'
    )
    
    content = content.replace(
        '    const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        '    const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    content = content.replace(
        '    if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        '    if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    content = content.replace(
        '        const footfallData = FOOTFALL_POINTS.filter(point => point.users > 0);',
        '        const footfallData = FOOTFALL_OUT_POINTS.filter(point => point.users > 0);'
    )
    
    content = content.replace(
        '    if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        '    if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    content = content.replace(
        '        const chartData = FOOTFALL_POINTS',
        '        const chartData = FOOTFALL_OUT_POINTS'
    )
    
    content = content.replace(
        '    if (typeof FOOTFALL_POINTS !== \'undefined\' && FOOTFALL_POINTS.length > 0) {',
        '    if (typeof FOOTFALL_OUT_POINTS !== \'undefined\' && FOOTFALL_OUT_POINTS.length > 0) {'
    )
    
    content = content.replace(
        '        const sortedPoints = FOOTFALL_POINTS',
        '        const sortedPoints = FOOTFALL_OUT_POINTS'
    )
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado - APENAS aba Footfall Out!")
    return True

if __name__ == "__main__":
    print("🔄 Atualizando APENAS a aba Footfall Out (Outubro)...")
    print("📊 Mantendo dados originais da aba Footfall Set (Setembro)")
    
    # Preparar dados de outubro
    october_data = update_only_footfall_out()
    
    # Atualizar HTML apenas para Footfall Out
    if update_html_footfall_out_only(october_data):
        print("\n🎉 Atualização concluída!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Dados de setembro (originais mantidos)")
        print("   ✅ Footfall Out: Dados de outubro (atualizados)")
        print("\n💡 Para verificar:")
        print("   1. Abra dash_sonho_v2.html no navegador")
        print("   2. Compare as duas abas Footfall")
        print("   3. Footfall Set deve ter dados de setembro")
        print("   4. Footfall Out deve ter dados de outubro")
    else:
        print("❌ Erro ao atualizar o arquivo HTML")

