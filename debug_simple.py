#!/usr/bin/env python3
"""
Script simples para debugar valores da planilha
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

def debug_simple():
    """Debugar valores da planilha de forma simples"""
    print("🔍 Debugando valores da planilha...")
    
    if not GOOGLE_AVAILABLE:
        print("❌ Google API não disponível")
        return
    
    sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"
    
    try:
        # Inicializar serviço
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json",
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Ler dados da aba Report
        range_name = "Report!A:O"  # A até O para pegar todas as colunas
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("❌ Dados vazios")
            return
        
        print(f"✅ {len(values)} linhas encontradas")
        
        # Mostrar cabeçalho
        if values:
            headers = values[0]
            print(f"📋 Cabeçalhos: {headers}")
            
            # Encontrar índice da coluna de investimento
            invest_index = None
            for i, header in enumerate(headers):
                if 'investido' in header.lower():
                    invest_index = i
                    print(f"💰 Coluna de investimento encontrada: '{header}' (índice {i})")
                    break
            
            if invest_index is not None:
                print(f"\n📊 Primeiros 10 valores de investimento:")
                for i in range(1, min(11, len(values))):
                    if invest_index < len(values[i]):
                        value = values[i][invest_index]
                        print(f"  Linha {i}: '{value}'")
                    else:
                        print(f"  Linha {i}: (vazio)")
                
                # Calcular total
                total = 0
                count = 0
                for i in range(1, len(values)):
                    if invest_index < len(values[i]):
                        value_str = values[i][invest_index]
                        if value_str:
                            try:
                                # Remover R$ e converter
                                clean_value = value_str.replace('R$', '').replace(' ', '').replace(',', '.')
                                numeric_value = float(clean_value)
                                total += numeric_value
                                count += 1
                            except:
                                pass
                
                print(f"\n💰 Total calculado: R$ {total:,.2f} ({count} registros)")
            else:
                print("❌ Coluna de investimento não encontrada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_simple()