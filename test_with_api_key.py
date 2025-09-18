#!/usr/bin/env python3
"""
Testar acesso às planilhas usando API key (para planilhas públicas)
"""

import requests
import json

def test_with_api_key():
    """Testar acesso com API key"""
    
    print("🔑 TESTANDO COM API KEY")
    print("=" * 60)
    
    # Planilhas para testar
    sheets_config = {
        "YouTube": {
            "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
            "gid": "304137877"
        },
        "Programática Video": {
            "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
            "gid": "1489416055"
        }
    }
    
    # API key (você precisará criar uma no Google Cloud Console)
    api_key = "YOUR_API_KEY_HERE"  # Substitua pela sua API key
    
    for channel_name, config in sheets_config.items():
        print(f"\n📺 TESTANDO: {channel_name}")
        print(f"🆔 Sheet ID: {config['sheet_id']}")
        print("-" * 50)
        
        # URL da API do Google Sheets
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{config['sheet_id']}?key={api_key}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Planilha acessível: {data.get('properties', {}).get('title', 'Sem título')}")
                
                # Listar abas
                sheets = data.get('sheets', [])
                print(f"📊 Abas encontradas: {len(sheets)}")
                
                for sheet in sheets:
                    sheet_props = sheet.get('properties', {})
                    sheet_id = sheet_props.get('sheetId')
                    sheet_title = sheet_props.get('title')
                    print(f"  - {sheet_title} (ID: {sheet_id})")
                    
                    # Verificar se é a aba que queremos
                    if str(sheet_id) == str(config['gid']):
                        print(f"  ✅ Aba encontrada: {sheet_title}")
                        
                        # Tentar ler dados da aba
                        print(f"📊 Lendo dados da aba {sheet_title}...")
                        values_url = f"https://sheets.googleapis.com/v4/spreadsheets/{config['sheet_id']}/values/{sheet_title}!A:Z?key={api_key}"
                        
                        values_response = requests.get(values_url)
                        if values_response.status_code == 200:
                            values_data = values_response.json()
                            values = values_data.get('values', [])
                            print(f"✅ {len(values)} linhas encontradas")
                            
                            if values:
                                print(f"📋 Primeiras 3 linhas:")
                                for i, row in enumerate(values[:3]):
                                    print(f"  Linha {i+1}: {row}")
                        else:
                            print(f"❌ Erro ao ler dados: {values_response.status_code}")
                        
                        break
                else:
                    print(f"❌ Aba com GID {config['gid']} não encontrada")
                    
            elif response.status_code == 403:
                print("❌ Acesso negado - planilha não é pública ou não tem permissão")
            elif response.status_code == 404:
                print("❌ Planilha não encontrada")
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("⚠️  Para usar este teste, você precisa:")
    print("1. Criar uma API key no Google Cloud Console")
    print("2. Habilitar a Google Sheets API")
    print("3. Substituir 'YOUR_API_KEY_HERE' pela sua API key")
    print("4. Tornar as planilhas públicas ou dar permissão à API key")
    print()
    
    # test_with_api_key()  # Descomente quando tiver a API key

