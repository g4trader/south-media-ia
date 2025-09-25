#!/usr/bin/env python3
"""
Teste do Google Sheets Service
"""

from google_sheets_service import GoogleSheetsService

def test_google_sheets():
    """Testar conexão com Google Sheets"""
    print("🔍 Testando Google Sheets Service...")
    
    # Criar instância do serviço
    service = GoogleSheetsService()
    
    # Verificar se está configurado
    if not service.is_configured():
        print("❌ Google Sheets não está configurado")
        return False
    
    print("✅ Google Sheets configurado")
    
    # Testar conexão
    connection_status = service.test_connection()
    print(f"📡 Status da conexão: {connection_status}")
    
    if connection_status != "connected":
        print("❌ Falha na conexão com Google Sheets")
        return False
    
    print("✅ Conexão com Google Sheets funcionando")
    
    # Testar acesso à planilha específica
    sheet_id = "1scA5ykf49DLobPTAKSL5fNgGMiomcJn"  # Planilha do SEBRAE
    print(f"📊 Testando acesso à planilha: {sheet_id}")
    
    if service.validate_sheet_access(sheet_id):
        print("✅ Acesso à planilha confirmado")
        
        # Tentar ler dados da aba de dados diários
        try:
            df = service.read_sheet_data(sheet_id, "Report", "1791112204")
            if df is not None:
                print(f"✅ Dados lidos com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
                print(f"📋 Colunas: {list(df.columns)[:5]}...")  # Primeiras 5 colunas
                return True
            else:
                print("❌ Nenhum dado retornado")
                return False
        except Exception as e:
            print(f"❌ Erro ao ler dados: {e}")
            return False
    else:
        print("❌ Acesso negado à planilha")
        return False

if __name__ == "__main__":
    success = test_google_sheets()
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Google Sheets está funcionando corretamente")
    else:
        print("\n❌ TESTE FALHOU!")
        print("🔧 Verifique as credenciais e permissões")
