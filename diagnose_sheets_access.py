#!/usr/bin/env python3
"""
Diagnosticar problemas de acesso às planilhas do Google Sheets
"""

import os
import json
from datetime import datetime

def diagnose_sheets_access():
    """Diagnosticar problemas de acesso"""
    
    print("🔍 DIAGNÓSTICO DE ACESSO ÀS PLANILHAS")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now()}")
    print()
    
    # Verificar arquivos de credenciais
    print("📁 VERIFICANDO ARQUIVOS DE CREDENCIAIS:")
    print("-" * 40)
    
    cred_files = [
        'service-account-key.json',
        'service-account-key-fixed.json',
        'credentials.json'
    ]
    
    for file in cred_files:
        if os.path.exists(file):
            print(f"✅ {file} - Existe")
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if 'type' in data and data['type'] == 'service_account':
                        print(f"   📧 Email: {data.get('client_email', 'N/A')}")
                        print(f"   🆔 Project: {data.get('project_id', 'N/A')}")
                    elif 'installed' in data:
                        print(f"   🆔 Project: {data.get('project_id', 'N/A')}")
                        print(f"   📧 Client ID: {data.get('installed', {}).get('client_id', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Erro ao ler: {e}")
        else:
            print(f"❌ {file} - Não existe")
    
    print()
    
    # Verificar variáveis de ambiente
    print("🌍 VERIFICANDO VARIÁVEIS DE AMBIENTE:")
    print("-" * 40)
    
    env_vars = [
        'GOOGLE_CREDENTIALS_FILE',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_CLOUD_PROJECT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} - Não definida")
    
    print()
    
    # Verificar dependências Python
    print("🐍 VERIFICANDO DEPENDÊNCIAS PYTHON:")
    print("-" * 40)
    
    try:
        import google.oauth2.service_account
        print("✅ google.oauth2.service_account - OK")
    except ImportError as e:
        print(f"❌ google.oauth2.service_account - {e}")
    
    try:
        import googleapiclient.discovery
        print("✅ googleapiclient.discovery - OK")
    except ImportError as e:
        print(f"❌ googleapiclient.discovery - {e}")
    
    try:
        import google.auth.transport.requests
        print("✅ google.auth.transport.requests - OK")
    except ImportError as e:
        print(f"❌ google.auth.transport.requests - {e}")
    
    print()
    
    # Verificar conectividade
    print("🌐 VERIFICANDO CONECTIVIDADE:")
    print("-" * 40)
    
    try:
        import requests
        response = requests.get('https://sheets.googleapis.com', timeout=10)
        print(f"✅ Google Sheets API - Acessível (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Google Sheets API - {e}")
    
    try:
        response = requests.get('https://oauth2.googleapis.com', timeout=10)
        print(f"✅ Google OAuth2 - Acessível (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Google OAuth2 - {e}")
    
    print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES PARA RESOLVER O PROBLEMA:")
    print("-" * 40)
    print("1. 🔐 Verificar se a service account está ativa no Google Cloud Console")
    print("2. 📧 Compartilhar as planilhas com: southmedia@automatizar-452311.iam.gserviceaccount.com")
    print("3. 🔑 Verificar se a chave privada está correta e não expirou")
    print("4. ⏰ Verificar se o relógio do sistema está sincronizado")
    print("5. 🌐 Verificar se não há proxy/firewall bloqueando o acesso")
    print("6. 🔄 Tentar regenerar a chave da service account")
    print()
    
    # URLs das planilhas
    print("📊 PLANILHAS PARA COMPARTILHAR:")
    print("-" * 40)
    print("YouTube:")
    print("  https://docs.google.com/spreadsheets/d/1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg/edit?gid=304137877")
    print()
    print("Programática Video:")
    print("  https://docs.google.com/spreadsheets/d/1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o/edit?gid=1489416055")
    print()
    
    # Email da service account
    print("📧 EMAIL DA SERVICE ACCOUNT:")
    print("-" * 40)
    print("southmedia@automatizar-452311.iam.gserviceaccount.com")
    print()

if __name__ == "__main__":
    diagnose_sheets_access()



