#!/usr/bin/env python3
"""
Debug detalhado do acesso ao Google Sheets
"""

import requests
import json
from google_sheets_service import GoogleSheetsService
from googleapiclient.errors import HttpError

def debug_sheets_access():
    """Debug detalhado do acesso ao Google Sheets"""
    print("🔍 Debug detalhado do acesso ao Google Sheets...")
    
    # Dados da planilha
    sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M"
    
    print(f"📊 Sheet ID: {sheet_id}")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsService()
        print(f"🔑 Service configurado: {service.is_configured()}")
        
        if not service.is_configured():
            print("❌ Serviço não configurado")
            return
        
        print("✅ Serviço configurado, testando acesso...")
        
        # Testar acesso detalhado
        try:
            print("🔍 Tentando acessar metadados da planilha...")
            result = service.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            print(f"✅ Metadados acessados: {result.get('properties', {}).get('title', 'N/A')}")
            
            # Testar acesso aos valores
            print("🔍 Tentando acessar valores da planilha...")
            values_result = service.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="A1:Z1"
            ).execute()
            
            values = values_result.get('values', [])
            print(f"✅ Valores acessados: {len(values)} linhas")
            if values:
                print(f"📋 Primeira linha: {values[0]}")
            
            # Testar aba específica
            print("🔍 Testando aba Report...")
            report_result = service.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="Report!A1:Z1"
            ).execute()
            
            report_values = report_result.get('values', [])
            print(f"✅ Aba Report acessada: {len(report_values)} linhas")
            if report_values:
                print(f"📋 Primeira linha Report: {report_values[0]}")
            
            print("\n🎉 ACESSO TOTALMENTE FUNCIONAL!")
            return True
            
        except HttpError as e:
            print(f"❌ HttpError: {e}")
            print(f"❌ Status Code: {e.resp.status}")
            print(f"❌ Error Details: {e.error_details}")
            print(f"❌ Reason: {e.reason}")
            return False
            
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            print(f"❌ Tipo do erro: {type(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço: {e}")
        return False

if __name__ == "__main__":
    success = debug_sheets_access()
    if not success:
        print("\n❌ DEBUG CONCLUÍDO - PROBLEMA IDENTIFICADO")
    else:
        print("\n✅ DEBUG CONCLUÍDO - TUDO FUNCIONANDO")
