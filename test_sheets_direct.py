#!/usr/bin/env python3
"""
Teste direto do Google Sheets Service
"""

import requests
import json

def test_sheets_direct():
    """Testar Google Sheets diretamente no Cloud Run"""
    print("🔍 Testando Google Sheets diretamente...")
    
    # Dados da planilha
    sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJmgSJqXolV679M"
    gids = {
        "daily_data": "1791112204",
        "contract": "1738408005", 
        "publishers": "409983185",
        "strategies": "587646711"
    }
    
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"📋 GIDs: {gids}")
    
    # Testar se o Google Sheets Service está funcionando
    try:
        from google_sheets_service import GoogleSheetsService
        
        service = GoogleSheetsService()
        print(f"🔑 Service configurado: {service.is_configured()}")
        
        if service.is_configured():
            print("✅ Google Sheets Service configurado")
            
            # Testar acesso à planilha
            if service.validate_sheet_access(sheet_id):
                print("✅ Acesso à planilha confirmado")
                
                # Tentar ler dados da aba Report
                try:
                    df = service.read_sheet_data(sheet_id, "Report", "1791112204")
                    if df is not None:
                        print(f"✅ Dados lidos: {len(df)} linhas, {len(df.columns)} colunas")
                        print(f"📋 Colunas: {list(df.columns)}")
                        return True
                    else:
                        print("❌ DataFrame vazio")
                        return False
                except Exception as e:
                    print(f"❌ Erro ao ler dados: {e}")
                    return False
            else:
                print("❌ Acesso negado à planilha")
                return False
        else:
            print("❌ Google Sheets Service não configurado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao inicializar Google Sheets Service: {e}")
        return False

if __name__ == "__main__":
    success = test_sheets_direct()
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Google Sheets está funcionando corretamente")
    else:
        print("\n❌ TESTE FALHOU!")
        print("🔧 Verifique as credenciais e permissões")
