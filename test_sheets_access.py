#!/usr/bin/env python3
"""
Testar acesso às planilhas fornecidas
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Definir variável de ambiente para usar service account
os.environ['GOOGLE_CREDENTIALS_FILE'] = 'service-account-key.json'

def test_sheets_access():
    """Testar acesso às planilhas"""
    
    print("🔐 TESTANDO ACESSO ÀS PLANILHAS")
    print("=" * 60)
    
    # Configuração das planilhas
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
    
    try:
        # Carregar credenciais
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Criar serviço
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Autenticação realizada com sucesso")
        
        for channel_name, config in sheets_config.items():
            print(f"\n📺 TESTANDO: {channel_name}")
            print(f"🆔 Sheet ID: {config['sheet_id']}")
            print(f"🆔 GID: {config['gid']}")
            print("-" * 50)
            
            try:
                # Tentar obter metadados da planilha
                print("📋 Obtendo metadados da planilha...")
                metadata = service.spreadsheets().get(spreadsheetId=config['sheet_id']).execute()
                
                print(f"✅ Planilha acessível: {metadata.get('properties', {}).get('title', 'Sem título')}")
                
                # Listar abas
                sheets = metadata.get('sheets', [])
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
                        range_name = f"{sheet_title}!A:Z"
                        result = service.spreadsheets().values().get(
                            spreadsheetId=config['sheet_id'],
                            range=range_name
                        ).execute()
                        
                        values = result.get('values', [])
                        print(f"✅ {len(values)} linhas encontradas")
                        
                        if values:
                            print(f"📋 Primeiras 3 linhas:")
                            for i, row in enumerate(values[:3]):
                                print(f"  Linha {i+1}: {row}")
                        
                        break
                else:
                    print(f"❌ Aba com GID {config['gid']} não encontrada")
                
            except Exception as e:
                print(f"❌ Erro ao acessar {channel_name}: {e}")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_sheets_access()



