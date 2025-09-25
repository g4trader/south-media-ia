#!/usr/bin/env python3
"""
Teste direto da planilha do SEBRAE
"""

import requests
import json

def test_sebrae_sheet():
    """Testar acesso à planilha do SEBRAE"""
    print("🔍 Testando acesso à planilha do SEBRAE...")
    
    # Dados da planilha
    sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJn"
    gids = {
        "daily_data": "1791112204",
        "contract": "1738408005", 
        "publishers": "409983185",
        "strategies": "587646711"
    }
    
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"📋 GIDs: {gids}")
    
    # Tentar acessar via API pública (se a planilha for pública)
    try:
        # URL da planilha
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
        print(f"🔗 URL da planilha: {sheet_url}")
        
        # Verificar se a planilha existe
        import urllib.request
        response = urllib.request.urlopen(sheet_url)
        if response.getcode() == 200:
            print("✅ Planilha acessível via URL")
        else:
            print(f"❌ Erro ao acessar planilha: {response.getcode()}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar planilha: {e}")
    
    # Testar via API do Google Sheets (se tivermos credenciais)
    try:
        from google.auth import default
        from googleapiclient.discovery import build
        
        credentials, project = default()
        service = build('sheets', 'v4', credentials=credentials)
        
        print(f"🔑 Usando credenciais do projeto: {project}")
        
        # Tentar acessar a planilha
        result = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        print(f"✅ Planilha acessível via API: {result.get('properties', {}).get('title', 'N/A')}")
        
        # Tentar ler dados da aba Report
        range_name = "Report!A1:Z10"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if values:
            print(f"✅ Dados lidos com sucesso: {len(values)} linhas")
            print(f"📋 Primeira linha: {values[0] if values else 'Vazia'}")
        else:
            print("❌ Nenhum dado retornado")
            
    except Exception as e:
        print(f"❌ Erro ao acessar via API: {e}")
        print("💡 Isso é esperado se as credenciais não tiverem permissão para acessar esta planilha")

if __name__ == "__main__":
    test_sebrae_sheet()
