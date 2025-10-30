#!/usr/bin/env python3
"""
Script para adicionar dados de forma limpa
"""

import os

def add_clean_data():
    """Adicionar dados de forma limpa"""
    
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Adicionando dados de forma limpa...")
    
    # ========================================
    # DADOS DE SETEMBRO (FOOTFALL_POINTS)
    # ========================================
    print("1. Adicionando dados de setembro...")
    
    footfall_points = '''const FOOTFALL_POINTS = [
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
    "users": 2776,
    "rate": 9.3
  },
  {
    "lat": -8.029882473548620,
    "lon": -34.906651673016300,
    "name": "Recibom - Parnamirim - Estr. do Arraial, 2668 - Tamarineira, Recife - PE, 52051-380",
    "users": 1267,
    "rate": 12.5
  },
  {
    "lat": -8.119932249004490,
    "lon": -34.890091268465570,
    "name": "Recibom - Boa Viagem - R. Prof. João Medeiros, 261 - Boa Viagem, Recife - PE, 51021-050",
    "users": 3673,
    "rate": 14.5
  },
  {
    "lat": -8.142543914194250,
    "lon": -34.908109113491800,
    "name": "Recibom - Setúbal - R. João Cardoso Aires, 407 - Boa Viagem, Recife - PE, 51130-300",
    "users": 4563,
    "rate": 6.5
  },
  {
    "lat": -8.028130780221500,
    "lon": -34.890250688465570,
    "name": "Recibom - Encruzilhada - Av. Norte Miguel Arraes de Alencar, S/N - Encruzilhada, Recife - PE, 52041-005",
    "users": 8355,
    "rate": 11.5
  },
  {
    "lat": -7.995667724325500,
    "lon": -34.884649217116390,
    "name": "Recibom - Olinda - Av. Carlos de Lima Cavalcante, 515 - Bultrins, Olinda - PE, 53030-260",
    "users": 8843,
    "rate": 13.5
  },
  {
    "lat": -8.183601155218950,
    "lon": -34.891945002883600,
    "name": "Recibom - Piedade - Av. Bernardo Vieira de Melo, 3454 - Piedade, Jaboatão dos Guararapes - PE, 54410-010",
    "users": 2021,
    "rate": 11.2
  },
  {
    "lat": -8.182334054796810,
    "lon": -34.918200238558100,
    "name": "Recibom - Piedade -Av. Ayrton Senna da Silva, 2851 - Piedade, Jaboatão dos Guararapes - PE, 54410-400",
    "users": 4128,
    "rate": 14.51
  }
];'''
    
    # ========================================
    # DADOS DE OUTUBRO (FOOTFALL_OUT_POINTS)
    # ========================================
    print("2. Adicionando dados de outubro...")
    
    footfall_out_points = '''const FOOTFALL_OUT_POINTS = [
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
];'''
    
    # ========================================
    # ADICIONAR DADOS ANTES DO FECHAMENTO DA TAG SCRIPT
    # ========================================
    print("3. Adicionando dados ao HTML...")
    
    # Adicionar os dados antes do fechamento da tag script
    content = content.replace('</script>', '\n' + footfall_points + '\n\n' + footfall_out_points + '\n\n</script>')
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado!")
    return True

if __name__ == "__main__":
    print("🔧 Adicionando dados de forma limpa...")
    
    if add_clean_data():
        print("\n🎉 Dados adicionados de forma limpa!")
        print("📋 Resultado:")
        print("   ✅ FOOTFALL_POINTS (setembro): 46,976 usuários, 11 lojas")
        print("   ✅ FOOTFALL_OUT_POINTS (outubro): 51,216 usuários, 12 lojas")
        print("\n💡 Agora teste no navegador!")
    else:
        print("❌ Erro ao adicionar dados")

