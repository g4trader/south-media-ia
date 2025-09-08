#!/usr/bin/env python3
"""
Teste de mapeamento específico por canal
Valida se a estrutura de dados está sendo processada corretamente
"""

import sys
import os
sys.path.append('backend/src')

import pandas as pd
from services.sheets_service import SheetsService
import json

def test_channel_mapping():
    """Testa o mapeamento de dados por canal"""
    print("🧪 TESTE DE MAPEAMENTO POR CANAL")
    print("=" * 50)
    
    # Inicializar serviço
    sheets_service = SheetsService()
    
    # Canais para testar
    channels = ["CTV", "Disney", "Netflix", "TikTok", "YouTube", "Footfall Display"]
    
    for channel in channels:
        print(f"\n📊 Testando canal: {channel}")
        print("-" * 30)
        
        try:
            # Simular dados baseados na estrutura real dos TSV
            mock_data = get_mock_data_for_channel(channel)
            
            if mock_data:
                # Testar mapeamento
                mapped_data = sheets_service._map_channel_specific_data(channel, mock_data)
                
                print(f"   ✅ Dados mapeados com sucesso")
                print(f"   📅 Data: {mapped_data.get('date', 'N/A')}")
                print(f"   🎨 Creative: {mapped_data.get('creative', 'N/A')}")
                print(f"   💰 Spend: R$ {mapped_data.get('spend', 0):.2f}")
                
                # Mostrar métricas específicas
                if mapped_data.get('starts'):
                    print(f"   🎬 Starts: {mapped_data.get('starts', 0):,}")
                if mapped_data.get('q25'):
                    print(f"   📊 Q25: {mapped_data.get('q25', 0):,}")
                if mapped_data.get('impressions'):
                    print(f"   👁️ Impressions: {mapped_data.get('impressions', 0):,}")
                if mapped_data.get('clicks'):
                    print(f"   👆 Clicks: {mapped_data.get('clicks', 0):,}")
                
            else:
                print(f"   ⚠️ Dados mock não disponíveis para {channel}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar {channel}: {e}")

def get_mock_data_for_channel(channel):
    """Retorna dados mock baseados na estrutura real de cada canal"""
    
    if channel == "CTV":
        return {
            "Data": "01/09/2025",
            "Creative": "Sonho 15s",
            "Starts (Video)": 891,
            "Skips (Video)": 0,
            "First-Quartile Views (Video)": 889,
            "Midpoint Views (Video)": 871,
            "Third-Quartile Views (Video)": 864,
            "Complete Views (Video)": 859,
            "Active View: % Audible and Visible at Start": "98,389%",
            "Active View: % Play Time Visible": "99,861%",
            "Active View: % Play Time Audible and Visible": "99,012%",
            "Valor investido": 171.8
        }
    
    elif channel in ["Disney", "Netflix"]:
        return {
            "Day": "01/09/2025",
            "Video Completion Rate %": 0.97811,
            "25% Video Complete": 861,
            "50% Video Complete": 859,
            "75% Video Complete": 855,
            "100% Complete": 845,
            "Video Starts": 893,
            "Valor investido": 388.7,
            "Criativo": "Sonho 30s"
        }
    
    elif channel == "TikTok":
        return {
            "Ad name": "Sonho 15 segundos",
            "By Day": "2025-09-02",
            "Valor Investido": "R$ 176,52",
            "CPC": 0.062,
            "CPM": "R$ 15,20",
            "Impressions": 11613,
            "Clicks": 11,
            "CTR": 0.095
        }
    
    elif channel == "YouTube":
        return {
            "Date": "2025/09/01",
            "Starts (Video)": 2093,
            "First-Quartile Views (Video)": 1831,
            "Midpoint Views (Video)": 1734,
            "Third-Quartile Views (Video)": 1637,
            "Complete Views (Video)": 1563,
            "Active View: % Audible and Visible at Start": "95,762%",
            "Active View: % Play Time Visible": "99,863%",
            "Active View: % Play Time Audible and Visible": "99,808%",
            "criativo": "shorts",
            "Valor investido": 46.89
        }
    
    elif channel == "Footfall Display":
        return {
            "Date": "2025/08/30",
            "Creative": "180x150 -cta 2",
            "Impressions": 783,
            "Clicks": 12,
            "Click Rate (CTR)": "1,533%",
            "VALOR DO INVESTIMENTO": "R$ 14,88",
            "CPM": "R$ 19,00"
        }
    
    return None

def test_tsv_processing():
    """Testa o processamento dos arquivos TSV reais"""
    print("\n📁 TESTE DE PROCESSAMENTO DE ARQUIVOS TSV")
    print("=" * 50)
    
    tsv_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv"
    
    if not os.path.exists(tsv_path):
        print("❌ Pasta TSV não encontrada")
        return
    
    # Mapear arquivos para canais
    file_mapping = {
        "Report Sonho -  Sonho - CTV  Househoud Sync - Video - Setembro (2).tsv": "CTV",
        "_Report Sonho -  Sonho - Disney - Setembro (1).tsv": "Disney",
        "Report Sonho - Netflix - Setembro (1).tsv": "Netflix",
        "Report Sonho _ TikTok.xlsx - Report (2).tsv": "TikTok",
        "Report Sonho Youtube - Entrega (1).tsv": "YouTube",
        "_Report Sonho -  Sonho -  Footfall - display - Setembro (2).tsv": "Footfall Display"
    }
    
    for filename, channel in file_mapping.items():
        filepath = os.path.join(tsv_path, filename)
        
        if os.path.exists(filepath):
            print(f"\n📊 Processando: {channel}")
            print(f"   📁 Arquivo: {filename}")
            
            try:
                # Ler arquivo TSV
                df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
                
                print(f"   📋 Linhas: {len(df)}")
                print(f"   📊 Colunas: {len(df.columns)}")
                print(f"   🏷️ Headers: {list(df.columns)}")
                
                if not df.empty:
                    # Mostrar primeira linha de dados
                    first_row = df.iloc[0]
                    print(f"   📝 Primeira linha:")
                    for col, value in first_row.items():
                        if pd.notna(value) and str(value).strip():
                            print(f"      {col}: {value}")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
        else:
            print(f"   ⚠️ Arquivo não encontrado: {filename}")

def show_structure_summary():
    """Mostra resumo da estrutura de cada canal"""
    print("\n📋 RESUMO DA ESTRUTURA POR CANAL")
    print("=" * 50)
    
    structures = {
        "CTV": {
            "tipo": "Vídeo",
            "colunas": ["Data", "Creative", "Starts", "Skips", "Q25", "Q50", "Q75", "Q100", "Active Views", "Valor investido"],
            "métricas": ["starts", "q25", "q50", "q75", "q100"]
        },
        "Disney": {
            "tipo": "Vídeo",
            "colunas": ["Day", "Completion Rate", "Q25", "Q50", "Q75", "Q100", "Starts", "Valor investido", "Criativo"],
            "métricas": ["starts", "q25", "q50", "q75", "q100"]
        },
        "Netflix": {
            "tipo": "Vídeo",
            "colunas": ["Day", "Completion Rate", "Q25", "Q50", "Q75", "Q100", "Starts", "Valor investido", "Criativo"],
            "métricas": ["starts", "q25", "q50", "q75", "q100"]
        },
        "TikTok": {
            "tipo": "Social",
            "colunas": ["Ad name", "By Day", "Valor Investido", "CPC", "CPM", "Impressions", "Clicks", "CTR"],
            "métricas": ["impressions", "clicks"]
        },
        "YouTube": {
            "tipo": "Vídeo",
            "colunas": ["Date", "Starts", "Q25", "Q50", "Q75", "Q100", "Active Views", "criativo", "Valor investido"],
            "métricas": ["starts", "q25", "q50", "q75", "q100"]
        },
        "Footfall Display": {
            "tipo": "Display",
            "colunas": ["Date", "Creative", "Impressions", "Clicks", "CTR", "VALOR DO INVESTIMENTO", "CPM"],
            "métricas": ["impressions", "clicks"]
        }
    }
    
    for channel, info in structures.items():
        print(f"\n📺 {channel} ({info['tipo']})")
        print(f"   📊 Métricas: {', '.join(info['métricas'])}")
        print(f"   📋 Colunas: {len(info['colunas'])}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "structure":
        show_structure_summary()
    elif len(sys.argv) > 1 and sys.argv[1] == "tsv":
        test_tsv_processing()
    else:
        test_channel_mapping()
        test_tsv_processing()
        show_structure_summary()
        
        print("\n🎯 TESTE CONCLUÍDO!")
        print("   Use 'python3 test_channel_mapping.py structure' para ver resumo")
        print("   Use 'python3 test_channel_mapping.py tsv' para testar arquivos TSV")
