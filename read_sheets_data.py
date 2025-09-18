#!/usr/bin/env python3
"""
Ler e mostrar dados das planilhas fornecidas
"""

import os
import json
from google_sheets_processor import GoogleSheetsProcessor

# Definir variável de ambiente para usar service account
os.environ['GOOGLE_CREDENTIALS_FILE'] = 'service-account-key.json'

def read_sheets_data():
    """Ler dados das planilhas fornecidas"""
    
    print("📊 LENDO DADOS DAS PLANILHAS")
    print("=" * 60)
    
    # Configuração das planilhas fornecidas
    sheets_config = {
        "YouTube": {
            "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
            "gid": "304137877",
            "url": "https://docs.google.com/spreadsheets/d/1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg/edit?gid=304137877"
        },
        "Programática Video": {
            "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
            "gid": "1489416055",
            "url": "https://docs.google.com/spreadsheets/d/1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o/edit?gid=1489416055"
        }
    }
    
    try:
        # Inicializar processador com service account
        processor = GoogleSheetsProcessor()
        # Forçar uso de service account
        processor.credentials_file = "service-account-key.json"
        processor.authenticate()
        print("✅ Processador inicializado com service account")
        
        all_data = {}
        
        for channel_name, config in sheets_config.items():
            print(f"\n📺 PROCESSANDO: {channel_name}")
            print(f"🔗 URL: {config['url']}")
            print(f"🆔 Sheet ID: {config['sheet_id']}")
            print(f"🆔 GID: {config['gid']}")
            print("-" * 50)
            
            try:
                # Ler dados brutos da planilha
                df = processor.read_sheet_data(
                    config['sheet_id'],
                    gid=config['gid']
                )
                
                if not df.empty:
                    print(f"✅ {len(df)} linhas encontradas")
                    print(f"📋 Colunas: {list(df.columns)}")
                    
                    # Mostrar primeiras linhas
                    print(f"\n📊 PRIMEIRAS 5 LINHAS:")
                    for i, (_, row) in enumerate(df.head().iterrows()):
                        print(f"  Linha {i+1}: {dict(row)}")
                    
                    # Mostrar tipos de dados
                    print(f"\n🔍 TIPOS DE DADOS:")
                    for col in df.columns:
                        sample_values = df[col].dropna().head(3).tolist()
                        print(f"  {col}: {sample_values}")
                    
                    # Salvar dados
                    all_data[channel_name] = {
                        "columns": list(df.columns),
                        "rows": len(df),
                        "data": df.to_dict('records')
                    }
                    
                else:
                    print("❌ Nenhum dado encontrado")
                    all_data[channel_name] = {"error": "Nenhum dado encontrado"}
                    
            except Exception as e:
                print(f"❌ Erro ao ler {channel_name}: {e}")
                all_data[channel_name] = {"error": str(e)}
        
        # Salvar todos os dados
        with open('sheets_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Dados salvos em: sheets_data.json")
        
        return all_data
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return {}

def show_sheets_summary():
    """Mostrar resumo das planilhas"""
    print(f"\n📋 RESUMO DAS PLANILHAS:")
    print("=" * 60)
    
    if os.path.exists('sheets_data.json'):
        with open('sheets_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for channel, info in data.items():
            print(f"\n📺 {channel}:")
            if 'error' in info:
                print(f"  ❌ Erro: {info['error']}")
            else:
                print(f"  📊 Linhas: {info['rows']}")
                print(f"  📋 Colunas: {len(info['columns'])}")
                print(f"  🔍 Colunas: {', '.join(info['columns'])}")
    else:
        print("❌ Arquivo sheets_data.json não encontrado")

if __name__ == "__main__":
    data = read_sheets_data()
    show_sheets_summary()
