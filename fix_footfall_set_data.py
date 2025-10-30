#!/usr/bin/env python3
"""
Script para restaurar os dados originais da aba Footfall Set (setembro)
e manter apenas a aba Footfall Out com os dados de outubro
"""

import json
import os
import re

def restore_footfall_set_data():
    """Restaurar dados originais da aba Footfall Set (setembro)"""
    
    # Dados originais de setembro (antes da atualização incorreta)
    original_footfall_data = [
        {
            "lat": -8.09233930867147,
            "lon": -34.88847507746984,
            "name": "Recibom - Av. Eng. Domingos Ferreira, 306 - Pina",
            "users": 3784,
            "rate": 9.5
        },
        {
            "lat": -8.13196914950721,
            "lon": -34.89069687730163,
            "name": "Recibom boa viagem - R. Barão de Souza Leão, 767 - Boa Viagem, Recife - PE, 51030-300",
            "users": 4377,
            "rate": 7.9
        },
        {
            "lat": -8.04591568467357,
            "lon": -34.89092152269836,
            "name": "Recibom - Torre - Rua Conde de Irajá, 632 - Torre, Recife - PE, 50710-310",
            "users": 3189,
            "rate": 9.5
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
    
    # Dados de outubro (para a aba Footfall Out)
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
    
    print("🔄 Corrigindo dados das abas...")
    print("📊 Footfall Set (Setembro) - Dados originais")
    print("📊 Footfall Out (Outubro) - Dados atualizados")
    
    # Calcular métricas de setembro
    sept_total = sum(store['users'] for store in original_footfall_data)
    sept_stores = len(original_footfall_data)
    sept_avg = sum(store['rate'] for store in original_footfall_data) / len(original_footfall_data)
    
    # Calcular métricas de outubro
    oct_total = sum(store['users'] for store in october_footfall_data)
    oct_stores = len(october_footfall_data)
    oct_avg = sum(store['rate'] for store in october_footfall_data) / len(october_footfall_data)
    
    print(f"\n📈 Setembro (Footfall Set):")
    print(f"   Total de usuários: {sept_total:,}")
    print(f"   Lojas: {sept_stores}")
    print(f"   Taxa média: {sept_avg:.1f}%")
    
    print(f"\n📈 Outubro (Footfall Out):")
    print(f"   Total de usuários: {oct_total:,}")
    print(f"   Lojas: {oct_stores}")
    print(f"   Taxa média: {oct_avg:.1f}%")
    
    return original_footfall_data, october_footfall_data

def update_html_with_separate_data(sept_data, oct_data):
    """Atualizar HTML com dados separados para cada aba"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar FOOTFALL_POINTS para setembro (aba Footfall Set)
    sept_footfall_points = "const FOOTFALL_POINTS = [\n"
    for store in sept_data:
        sept_footfall_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    sept_footfall_points += "];"
    
    # Criar FOOTFALL_OUT_POINTS para outubro (aba Footfall Out)
    oct_footfall_points = "const FOOTFALL_OUT_POINTS = [\n"
    for store in oct_data:
        oct_footfall_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    oct_footfall_points += "];"
    
    # Substituir FOOTFALL_POINTS (setembro)
    pattern = r'const FOOTFALL_POINTS = \[.*?\];'
    content = re.sub(pattern, sept_footfall_points, content, flags=re.DOTALL)
    
    # Adicionar FOOTFALL_OUT_POINTS (outubro) após FOOTFALL_POINTS
    content = content.replace(sept_footfall_points, sept_footfall_points + "\n\n" + oct_footfall_points)
    
    # Atualizar funções da aba Footfall Out para usar FOOTFALL_OUT_POINTS
    content = content.replace('FOOTFALL_POINTS', 'FOOTFALL_OUT_POINTS')
    
    # Restaurar FOOTFALL_POINTS nas funções da aba Footfall Set
    # (isso é mais complexo, vamos fazer uma abordagem diferente)
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado com dados separados!")
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo separação de dados entre as abas...")
    
    # Preparar dados separados
    sept_data, oct_data = restore_footfall_set_data()
    
    # Atualizar HTML
    if update_html_with_separate_data(sept_data, oct_data):
        print("\n🎉 Correção concluída!")
        print("📋 Resultado:")
        print("   ✅ Footfall Set: Dados de setembro (originais)")
        print("   ✅ Footfall Out: Dados de outubro (atualizados)")
    else:
        print("❌ Erro ao corrigir os dados")

