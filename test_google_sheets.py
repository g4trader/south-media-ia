#!/usr/bin/env python3
"""
Teste de integração com Google Sheets
"""

import sys
import os
sys.path.append('backend/src')

from services.sheets_service import SheetsService
import json

def test_sheets_service():
    """Testa o serviço do Google Sheets"""
    print("🧪 TESTE DE INTEGRAÇÃO COM GOOGLE SHEETS")
    print("=" * 50)
    
    # Inicializar serviço
    sheets_service = SheetsService()
    
    # Verificar se está disponível
    if not sheets_service.is_available():
        print("❌ Google Sheets não disponível")
        print("   Verifique se:")
        print("   1. O arquivo credentials.json existe")
        print("   2. As credenciais estão corretas")
        print("   3. As variáveis de ambiente estão configuradas")
        return False
    
    print("✅ Cliente Google Sheets inicializado")
    
    # Testar conexão
    print("\n🔗 Testando conexão com planilhas...")
    connection_result = sheets_service.test_connection()
    
    print(f"Status geral: {connection_result['status']}")
    
    for channel, result in connection_result['results'].items():
        status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⚠️"
        print(f"   {status_icon} {channel}: {result['message']}")
        
        if result['status'] == 'success':
            print(f"      📊 Linhas encontradas: {result.get('rows_found', 0)}")
            print(f"      📋 Título: {result.get('spreadsheet_title', 'N/A')}")
    
    # Testar obtenção de dados
    print("\n📊 Testando obtenção de dados...")
    
    for channel in ["CTV", "Footfall Display", "TikTok"]:
        print(f"\n   📈 Testando canal: {channel}")
        try:
            data = sheets_service.get_sheet_data(channel)
            if data:
                print(f"      ✅ {len(data)} registros obtidos")
                if data:
                    print(f"      📋 Primeiro registro: {list(data[0].keys())}")
            else:
                print(f"      ⚠️ Nenhum dado obtido")
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    # Testar processamento de dados
    print("\n🔄 Testando processamento de dados...")
    try:
        all_data = sheets_service.get_all_channels_data()
        print(f"   ✅ Total de registros processados: {len(all_data)}")
        
        if all_data:
            # Mostrar estatísticas
            channels = {}
            for record in all_data:
                channel = record['channel']
                if channel not in channels:
                    channels[channel] = 0
                channels[channel] += 1
            
            print("   📊 Registros por canal:")
            for channel, count in channels.items():
                print(f"      {channel}: {count} registros")
    except Exception as e:
        print(f"   ❌ Erro no processamento: {e}")
    
    # Testar dados contratados
    print("\n📋 Testando dados contratados...")
    try:
        contract_data = sheets_service.get_contract_data()
        print(f"   ✅ {len(contract_data)} canais configurados")
        
        for channel, data in contract_data.items():
            budget = data.get('Budget Contratado (R$)', 0)
            used = data.get('Budget Utilizado (R$)', 0)
            print(f"      {channel}: R$ {used:,.2f} / R$ {budget:,.2f}")
    except Exception as e:
        print(f"   ❌ Erro nos dados contratados: {e}")
    
    print("\n🎯 TESTE CONCLUÍDO!")
    return True

def show_setup_instructions():
    """Mostra instruções de configuração"""
    print("""
📋 INSTRUÇÕES DE CONFIGURAÇÃO:

1. 🔑 Criar credenciais do Google Sheets:
   - Acesse: https://console.cloud.google.com/
   - Crie um projeto ou selecione um existente
   - Ative a Google Sheets API
   - Crie uma Service Account
   - Baixe o arquivo JSON de credenciais
   - Renomeie para 'credentials.json' e coloque em backend/

2. 📊 Configurar planilhas:
   - Compartilhe suas planilhas com o email da Service Account
   - Cada canal deve ter uma planilha com aba "Entrega Diária"
   - Configure as variáveis de ambiente com os IDs das planilhas

3. 🔧 Configurar variáveis de ambiente:
   - Copie backend/sheets_config.example para backend/.env
   - Preencha os IDs das planilhas
   - Configure o caminho para credentials.json

4. 🧪 Testar:
   - python3 test_google_sheets.py
   - Verifique se todas as conexões estão funcionando

📝 ESTRUTURA ESPERADA DAS PLANILHAS:
   - Coluna A: Data
   - Coluna B: Creative
   - Coluna C: Spend/Investimento
   - Colunas D-G: Métricas específicas por canal
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        show_setup_instructions()
    else:
        success = test_sheets_service()
        
        if not success:
            print("\n❌ TESTE FALHOU!")
            print("   Execute: python3 test_google_sheets.py setup")
            print("   Para ver instruções de configuração")
        else:
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("   O sistema está pronto para usar Google Sheets")
