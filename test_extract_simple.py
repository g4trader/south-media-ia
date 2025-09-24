#!/usr/bin/env python3
"""
Teste simples para extrair dados das abas específicas
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_sheets_service import GoogleSheetsService

def test_extract_simple():
    """Teste simples de extração"""
    print("🔍 TESTE SIMPLES DE EXTRAÇÃO")
    print("=" * 50)
    
    # Configurar credenciais
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    
    # Inicializar serviço
    sheets_service = GoogleSheetsService()
    
    if not sheets_service.is_configured():
        print("❌ Google Sheets não configurado")
        return
    
    sheet_id = "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8"
    
    # Testar cada aba
    abas = [
        ("daily_data", "Report"),
        ("contract", "Informações de Contrato"),
        ("strategies", "Estratégias"),
        ("publishers", "Lista de Publishers")
    ]
    
    for aba_name, sheet_name in abas:
        print(f"\n📊 Testando aba: {aba_name} ({sheet_name})")
        try:
            df = sheets_service.read_sheet_data(sheet_id, sheet_name=sheet_name)
            if df is not None:
                print(f"✅ Sucesso: {len(df)} linhas, {len(df.columns)} colunas")
                print(f"Colunas: {list(df.columns)}")
                if len(df) > 0:
                    print(f"Primeira linha: {df.iloc[0].to_dict()}")
            else:
                print("❌ Falha: DataFrame é None")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_extract_simple()
