#!/usr/bin/env python3
"""
Script para debugar a extração da planilha Copacol
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from google_sheets_service import GoogleSheetsService

def debug_copacol_extraction():
    """Debugar extração da planilha Copacol"""
    print("🔍 Debugando extração da planilha Copacol...")
    
    sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"
    
    # Inicializar serviço
    sheets_service = GoogleSheetsService()
    if not sheets_service.is_configured():
        print("❌ Google Sheets não configurado")
        return
    
    print("✅ Google Sheets configurado")
    
    # 1. Verificar aba Report
    print("\n📊 Verificando aba 'Report':")
    try:
        df_report = sheets_service.read_sheet_data(sheet_id, sheet_name="Report")
        if df_report is not None and not df_report.empty:
            print(f"✅ Aba Report encontrada: {len(df_report)} linhas, {len(df_report.columns)} colunas")
            print(f"📋 Colunas: {list(df_report.columns)}")
            
            # Mostrar primeiras linhas
            print("\n📋 Primeiras 3 linhas:")
            for i in range(min(3, len(df_report))):
                row = df_report.iloc[i]
                print(f"  Linha {i+1}:")
                print(f"    Day: {row.get('Day', 'N/A')}")
                print(f"    Creative: {row.get('Creative', 'N/A')[:50]}...")
                print(f"    Valor investido: {row.get('Valor investido', 'N/A')}")
                print(f"    Imps: {row.get('Imps', 'N/A')}")
                print(f"    CPV: {row.get('CPV', 'N/A')}")
                print()
        else:
            print("❌ Aba Report vazia ou não encontrada")
    except Exception as e:
        print(f"❌ Erro ao ler aba Report: {e}")
    
    # 2. Verificar aba Informações de contrato
    print("\n📋 Verificando aba 'Informações de contrato':")
    try:
        df_contract = sheets_service.read_sheet_data(sheet_id, sheet_name="Informações de contrato")
        if df_contract is not None and not df_contract.empty:
            print(f"✅ Aba Informações de contrato encontrada: {len(df_contract)} linhas, {len(df_contract.columns)} colunas")
            print(f"📋 Colunas: {list(df_contract.columns)}")
            
            # Mostrar dados de contrato
            print("\n📋 Dados de contrato:")
            for i in range(len(df_contract)):
                row = df_contract.iloc[i]
                if len(row) >= 2:
                    key = str(row.iloc[0])
                    value = str(row.iloc[1])
                    if key and value and value.lower() != 'nan':
                        print(f"  {key}: {value}")
        else:
            print("❌ Aba Informações de contrato vazia ou não encontrada")
    except Exception as e:
        print(f"❌ Erro ao ler aba Informações de contrato: {e}")
    
    # 3. Listar todas as abas disponíveis
    print("\n📋 Listando todas as abas disponíveis:")
    try:
        spreadsheet_info = sheets_service.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = spreadsheet_info.get('sheets', [])
        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            print(f"  📄 {sheet_name}")
    except Exception as e:
        print(f"❌ Erro ao listar abas: {e}")

if __name__ == "__main__":
    debug_copacol_extraction()

