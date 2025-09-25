#!/usr/bin/env python3
"""
Script para debug específico do Google Sheets no Cloud Run
"""

import os
import sys
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def debug_google_sheets_cloud_run():
    """Debug detalhado do Google Sheets no Cloud Run"""
    print("🔍 Debug detalhado do Google Sheets no Cloud Run...")
    
    # Dados da planilha
    sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M"
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"🔑 Escopos: {scopes}")
    
    # Verificar variáveis de ambiente
    print("\n🔧 Variáveis de ambiente:")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NÃO DEFINIDA')}")
    print(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'NÃO DEFINIDA')}")
    print(f"K_SERVICE: {os.environ.get('K_SERVICE', 'NÃO DEFINIDA')}")
    print(f"K_REVISION: {os.environ.get('K_REVISION', 'NÃO DEFINIDA')}")
    
    # Tentar obter credenciais
    print("\n🔑 Tentando obter credenciais...")
    try:
        credentials, project = default(scopes=scopes)
        print(f"✅ Credenciais obtidas: {type(credentials)}")
        print(f"✅ Projeto: {project}")
        
        # Verificar se as credenciais têm os escopos corretos
        if hasattr(credentials, 'scopes'):
            print(f"✅ Escopos das credenciais: {credentials.scopes}")
        
        # Tentar fazer refresh
        print("\n🔄 Fazendo refresh das credenciais...")
        credentials.refresh(Request())
        print("✅ Refresh concluído")
        
        # Tentar construir o serviço
        print("\n🔧 Construindo serviço Google Sheets...")
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Serviço construído com sucesso")
        
        # Tentar acessar a planilha
        print("\n📊 Tentando acessar metadados da planilha...")
        try:
            result = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            print("✅ Metadados da planilha acessados com sucesso!")
            print(f"📋 Título: {result.get('properties', {}).get('title', 'N/A')}")
            
            # Tentar ler uma aba específica
            print("\n📋 Tentando ler aba 'Report'...")
            range_name = 'Report!A1:Z100'
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            print(f"✅ Dados lidos com sucesso! {len(values)} linhas encontradas")
            
            if values:
                print(f"📊 Primeira linha: {values[0]}")
            
            return True
            
        except HttpError as e:
            print(f"❌ Erro ao acessar planilha: {e}")
            print(f"❌ Status Code: {e.resp.status}")
            print(f"❌ Detalhes: {e.error_details}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter credenciais: {e}")
        return False

if __name__ == "__main__":
    success = debug_google_sheets_cloud_run()
    if success:
        print("\n🎉 DEBUG CONCLUÍDO - ACESSO OK")
    else:
        print("\n❌ DEBUG CONCLUÍDO - PROBLEMA IDENTIFICADO")
