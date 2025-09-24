#!/usr/bin/env python3
"""
Teste específico para verificar a aba Lista de Publishers da planilha
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_publishers_sheet():
    """Teste específico da aba Lista de Publishers"""
    print("🔍 TESTE DA ABA LISTA DE PUBLISHERS")
    print("=" * 50)
    
    try:
        from google_sheets_service import GoogleSheetsService
        
        # Inicializar serviço
        sheets_service = GoogleSheetsService()
        
        if not sheets_service.is_configured():
            print("❌ Google Sheets não configurado - credenciais não encontradas")
            print("📋 Para configurar as credenciais:")
            print("   1. Baixe o arquivo JSON de credenciais do Google Cloud Console")
            print("   2. Renomeie para 'google_credentials.json'")
            print("   3. Coloque na pasta raiz do projeto")
            print("   4. Ou configure a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS")
            return None
        
        # Configuração da planilha
        sheet_id = "1IUUSXaN0Drrdt-7B0IUiMRQK2gT-JtzhCFZvV7e5-V8"
        publishers_gid = "531141406"  # GID da aba Lista de Publishers
        
        print(f"📊 Tentando acessar aba Lista de Publishers...")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   GID: {publishers_gid}")
        
        # Ler dados da aba Lista de Publishers
        df = sheets_service.read_sheet_data(sheet_id, gid=publishers_gid)
        
        if df is not None:
            print(f"✅ Aba Lista de Publishers acessada com sucesso!")
            print(f"📋 Linhas encontradas: {len(df)}")
            print(f"📋 Colunas encontradas: {list(df.columns)}")
            
            print("\n📺 Dados da aba Lista de Publishers:")
            print("-" * 50)
            
            for i, row in df.iterrows():
                print(f"Linha {i+1}:")
                for col in df.columns:
                    value = str(row[col]).strip()
                    if value and value != 'nan':
                        print(f"  {col}: {value}")
                print()
            
            return df
        else:
            print("❌ Não foi possível acessar a aba Lista de Publishers")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao acessar planilha: {e}")
        return None

if __name__ == "__main__":
    test_publishers_sheet()
