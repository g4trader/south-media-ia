#!/usr/bin/env python3
"""
Script para configurar credenciais do Google Sheets
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_credentials():
    """Configurar credenciais do Google Sheets"""
    
    print("🔐 Configuração de Credenciais do Google Sheets")
    print("=" * 50)
    
    print("\n📋 Você precisa de:")
    print("1. Service Account do Google Cloud Console")
    print("2. Arquivo JSON com as credenciais")
    print("3. Planilha compartilhada com o email da service account")
    
    print("\n🔧 Opções de configuração:")
    print("1. Arquivo local (credentials.json)")
    print("2. Variável de ambiente (GOOGLE_APPLICATION_CREDENTIALS_JSON)")
    
    choice = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    if choice == "1":
        setup_local_file()
    elif choice == "2":
        setup_env_variable()
    else:
        print("❌ Opção inválida")
        return False
    
    return True

def setup_local_file():
    """Configurar arquivo local"""
    print("\n📁 Configuração de arquivo local")
    
    # Verificar se já existe
    if os.path.exists("credentials.json"):
        print("✅ Arquivo credentials.json já existe")
        use_existing = input("Usar arquivo existente? (s/n): ").strip().lower()
        if use_existing == 's':
            test_credentials("credentials.json")
            return
    
    print("\n📝 Cole o conteúdo JSON das credenciais da service account:")
    print("(Cole todo o JSON e pressione Enter duas vezes para finalizar)")
    
    lines = []
    empty_lines = 0
    
    while True:
        line = input()
        if line.strip() == "":
            empty_lines += 1
            if empty_lines >= 2:
                break
        else:
            empty_lines = 0
            lines.append(line)
    
    json_content = "\n".join(lines)
    
    try:
        # Validar JSON
        credentials_data = json.loads(json_content)
        
        # Salvar arquivo
        with open("credentials.json", "w") as f:
            f.write(json_content)
        
        print("✅ Arquivo credentials.json criado com sucesso")
        
        # Testar credenciais
        test_credentials("credentials.json")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False
    
    return True

def setup_env_variable():
    """Configurar variável de ambiente"""
    print("\n🌍 Configuração de variável de ambiente")
    
    print("\n📝 Cole o conteúdo JSON das credenciais:")
    json_content = input()
    
    try:
        # Validar JSON
        credentials_data = json.loads(json_content)
        
        # Configurar variável de ambiente
        os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'] = json_content
        
        print("✅ Variável de ambiente configurada")
        print("⚠️  Lembre-se de configurar no seu sistema:")
        print("export GOOGLE_APPLICATION_CREDENTIALS_JSON='<seu_json_aqui>'")
        
        # Testar credenciais
        test_credentials_from_env()
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

def test_credentials(credentials_path):
    """Testar credenciais"""
    try:
        print(f"\n🧪 Testando credenciais em {credentials_path}...")
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Testar com uma planilha pública conhecida
        test_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        result = service.spreadsheets().values().get(
            spreadsheetId=test_sheet_id,
            range='Class Data!A2:E'
        ).execute()
        
        print("✅ Credenciais funcionando!")
        print("🔗 Agora você pode acessar planilhas do Google Sheets")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar credenciais: {e}")
        print("\n🔧 Verifique:")
        print("1. Se o arquivo JSON está correto")
        print("2. Se a service account tem permissão para acessar planilhas")
        print("3. Se a planilha está compartilhada com o email da service account")
        return False

def test_credentials_from_env():
    """Testar credenciais da variável de ambiente"""
    try:
        print("\n🧪 Testando credenciais da variável de ambiente...")
        
        json_content = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not json_content:
            print("❌ Variável de ambiente não encontrada")
            return False
        
        credentials_data = json.loads(json_content)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_data,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        # Testar com uma planilha pública conhecida
        test_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        result = service.spreadsheets().values().get(
            spreadsheetId=test_sheet_id,
            range='Class Data!A2:E'
        ).execute()
        
        print("✅ Credenciais funcionando!")
        print("🔗 Agora você pode acessar planilhas do Google Sheets")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar credenciais: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configuração de Credenciais do Google Sheets")
    print("Este script irá ajudar você a configurar as credenciais necessárias")
    print("para acessar planilhas do Google Sheets.\n")
    
    setup_credentials()

