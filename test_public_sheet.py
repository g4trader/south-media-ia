#!/usr/bin/env python3
"""
Testar acesso a uma planilha pública para verificar se o problema é de permissão
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Definir variável de ambiente para usar service account
os.environ['GOOGLE_CREDENTIALS_FILE'] = 'service-account-key.json'

def test_public_sheet():
    """Testar acesso a uma planilha pública"""
    
    print("🔐 TESTANDO ACESSO A PLANILHA PÚBLICA")
    print("=" * 60)
    
    # Planilha pública de exemplo (Google Sheets Sample)
    public_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    try:
        # Carregar credenciais
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Criar serviço
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Autenticação realizada com sucesso")
        
        print(f"📊 Testando planilha pública: {public_sheet_id}")
        
        # Tentar obter metadados da planilha
        print("📋 Obtendo metadados da planilha...")
        metadata = service.spreadsheets().get(spreadsheetId=public_sheet_id).execute()
        
        print(f"✅ Planilha acessível: {metadata.get('properties', {}).get('title', 'Sem título')}")
        
        # Listar abas
        sheets = metadata.get('sheets', [])
        print(f"📊 Abas encontradas: {len(sheets)}")
        
        for sheet in sheets:
            sheet_props = sheet.get('properties', {})
            sheet_title = sheet_props.get('title')
            print(f"  - {sheet_title}")
        
        # Tentar ler dados da primeira aba
        if sheets:
            first_sheet = sheets[0]['properties']['title']
            print(f"\n📊 Lendo dados da aba: {first_sheet}")
            
            range_name = f"{first_sheet}!A1:E5"
            result = service.spreadsheets().values().get(
                spreadsheetId=public_sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            print(f"✅ {len(values)} linhas encontradas")
            
            if values:
                print(f"📋 Dados:")
                for i, row in enumerate(values):
                    print(f"  Linha {i+1}: {row}")
        
        print("\n✅ Teste com planilha pública bem-sucedido!")
        print("🔍 O problema pode ser de permissão nas planilhas específicas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔍 O problema é com a autenticação em si")

if __name__ == "__main__":
    test_public_sheet()

