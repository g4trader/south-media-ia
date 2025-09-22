#!/usr/bin/env python3
"""
Simular dados das planilhas baseado nas informações fornecidas
"""

import json
import os
from datetime import datetime, timedelta

def simulate_sheets_data():
    """Simular dados das planilhas baseado nas informações fornecidas"""
    
    print("📊 SIMULANDO DADOS DAS PLANILHAS")
    print("=" * 60)
    
    # Dados baseados nas informações fornecidas
    sheets_data = {
        "YouTube": {
            "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
            "gid": "304137877",
            "url": "https://docs.google.com/spreadsheets/d/1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg/edit?gid=304137877",
            "info": {
                "Data de início": "01/09/2025",
                "Data de conclusão": "30/09/2025", 
                "Impressões contratadas": "625.000",
                "Valor contratado": "50.000,00",
                "CPV": "R$ 0,08"
            },
            "columns": [
                "Day", "Creative", "Impressions", "Clicks", "Valor", "Visits", "Starts", "Q25", "Q50", "Q75", "Q100"
            ],
            "sample_data": [
                {
                    "Day": "01/09/2025",
                    "Creative": "Semana do Pescado - YouTube 1",
                    "Impressions": "25,000",
                    "Clicks": "500",
                    "Valor": "2,000.00",
                    "Visits": "450",
                    "Starts": "24,500",
                    "Q25": "22,000",
                    "Q50": "20,000",
                    "Q75": "18,000",
                    "Q100": "15,000"
                },
                {
                    "Day": "02/09/2025",
                    "Creative": "Semana do Pescado - YouTube 2",
                    "Impressions": "30,000",
                    "Clicks": "600",
                    "Valor": "2,400.00",
                    "Visits": "540",
                    "Starts": "29,400",
                    "Q25": "26,400",
                    "Q50": "24,000",
                    "Q75": "21,600",
                    "Q100": "18,000"
                },
                {
                    "Day": "03/09/2025",
                    "Creative": "Semana do Pescado - YouTube 3",
                    "Impressions": "28,000",
                    "Clicks": "560",
                    "Valor": "2,240.00",
                    "Visits": "504",
                    "Starts": "27,440",
                    "Q25": "24,640",
                    "Q50": "22,400",
                    "Q75": "20,160",
                    "Q100": "16,800"
                }
            ]
        },
        "Programática Video": {
            "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
            "gid": "1489416055",
            "url": "https://docs.google.com/spreadsheets/d/1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o/edit?gid=1489416055",
            "info": {
                "Data de início": "01/09/2025",
                "Data de conclusão": "30/09/2025",
                "Impressões contratadas": "173.914",
                "Valor contratado": "40.000,00",
                "CPV": "R$ 0,23"
            },
            "columns": [
                "Day", "Creative", "Impressions", "Clicks", "Valor", "Visits", "Publisher"
            ],
            "sample_data": [
                {
                    "Day": "01/09/2025",
                    "Creative": "Semana do Pescado - Programática 1",
                    "Impressions": "8,000",
                    "Clicks": "160",
                    "Valor": "1,840.00",
                    "Visits": "144",
                    "Publisher": "g1.globo.com"
                },
                {
                    "Day": "02/09/2025",
                    "Creative": "Semana do Pescado - Programática 2",
                    "Impressions": "9,500",
                    "Clicks": "190",
                    "Valor": "2,185.00",
                    "Visits": "171",
                    "Publisher": "oglobo.globo.com"
                },
                {
                    "Day": "03/09/2025",
                    "Creative": "Semana do Pescado - Programática 3",
                    "Impressions": "7,200",
                    "Clicks": "144",
                    "Valor": "1,656.00",
                    "Visits": "130",
                    "Publisher": "uol.com.br"
                }
            ]
        }
    }
    
    # Mostrar dados de cada planilha
    for channel_name, data in sheets_data.items():
        print(f"\n📺 PLANILHA: {channel_name}")
        print(f"🔗 URL: {data['url']}")
        print(f"🆔 Sheet ID: {data['sheet_id']}")
        print(f"🆔 GID: {data['gid']}")
        print("-" * 50)
        
        print(f"📋 INFORMAÇÕES CONTRATUAIS:")
        for key, value in data['info'].items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 COLUNAS DA PLANILHA:")
        for i, col in enumerate(data['columns'], 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n📈 DADOS DE EXEMPLO (3 primeiras linhas):")
        for i, row in enumerate(data['sample_data'], 1):
            print(f"  Linha {i}:")
            for key, value in row.items():
                print(f"    {key}: {value}")
            print()
    
    # Salvar dados simulados
    with open('simulated_sheets_data.json', 'w', encoding='utf-8') as f:
        json.dump(sheets_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Dados simulados salvos em: simulated_sheets_data.json")
    
    return sheets_data

def show_data_structure():
    """Mostrar estrutura dos dados"""
    print(f"\n📋 ESTRUTURA DOS DADOS:")
    print("=" * 60)
    
    if os.path.exists('simulated_sheets_data.json'):
        with open('simulated_sheets_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for channel, info in data.items():
            print(f"\n📺 {channel}:")
            print(f"  📊 Colunas: {len(info['columns'])}")
            print(f"  📋 Colunas: {', '.join(info['columns'])}")
            print(f"  📈 Dados de exemplo: {len(info['sample_data'])} linhas")
            
            # Calcular totais dos dados de exemplo
            total_impressions = sum(int(row['Impressions'].replace(',', '')) for row in info['sample_data'])
            total_clicks = sum(int(row['Clicks'].replace(',', '')) for row in info['sample_data'])
            total_valor = sum(float(row['Valor'].replace(',', '')) for row in info['sample_data'])
            
            print(f"  📊 Totais (exemplo):")
            print(f"    Impressões: {total_impressions:,}")
            print(f"    Cliques: {total_clicks:,}")
            print(f"    Valor: R$ {total_valor:,.2f}")

if __name__ == "__main__":
    data = simulate_sheets_data()
    show_data_structure()



