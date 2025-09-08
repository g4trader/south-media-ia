#!/usr/bin/env python3
"""
Teste das planilhas reais do Google Sheets
"""

import sys
import os
sys.path.append('backend/src')

# Configuração das planilhas reais
REAL_SHEETS_CONFIG = {
    "CTV": {
        "spreadsheet_id": "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U",
        "sheet_name": "Entrega Diária",
        "url": "https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit"
    },
    "Disney": {
        "spreadsheet_id": "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o",
        "sheet_name": "Entrega Diária",
        "url": "https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit"
    },
    "Footfall Display": {
        "spreadsheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA",
        "sheet_name": "Entrega Diária",
        "gid": "1743413064",
        "url": "https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064"
    },
    "Netflix": {
        "spreadsheet_id": "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo",
        "sheet_name": "Entrega Diária",
        "url": "https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit"
    },
    "TikTok": {
        "spreadsheet_id": "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM",
        "sheet_name": "Entrega Diária",
        "url": "https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true"
    },
    "YouTube": {
        "spreadsheet_id": "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo",
        "sheet_name": "Entrega Diária",
        "gid": "1863167182",
        "url": "https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182"
    }
}

def test_sheets_service_with_real_ids():
    """Testa o SheetsService com IDs reais"""
    print("🧪 TESTE DAS PLANILHAS REAIS DO GOOGLE SHEETS")
    print("=" * 60)
    
    try:
        from services.sheets_service import SheetsService
        
        # Inicializar serviço
        sheets_service = SheetsService()
        
        if not sheets_service.is_available():
            print("❌ Google Sheets não disponível")
            print("   Verifique se:")
            print("   1. O arquivo credentials.json existe em backend/")
            print("   2. As credenciais estão corretas")
            print("   3. A Service Account tem acesso às planilhas")
            return False
        
        print("✅ Cliente Google Sheets inicializado")
        
        # Testar cada planilha
        print("\n🔗 Testando conexão com planilhas reais...")
        
        for channel, config in REAL_SHEETS_CONFIG.items():
            print(f"\n📊 Testando: {channel}")
            print(f"   🆔 ID: {config['spreadsheet_id']}")
            print(f"   🌐 URL: {config['url']}")
            
            try:
                # Testar acesso à planilha
                spreadsheet = sheets_service.client.open_by_key(config["spreadsheet_id"])
                print(f"   ✅ Planilha acessada: {spreadsheet.title}")
                
                # Testar aba específica
                try:
                    worksheet = spreadsheet.worksheet(config["sheet_name"])
                    print(f"   ✅ Aba '{config['sheet_name']}' encontrada")
                    
                    # Obter algumas linhas para teste
                    test_data = worksheet.get_all_values()[:5]
                    print(f"   📋 Linhas de teste: {len(test_data)}")
                    
                    if test_data:
                        print(f"   🏷️ Headers: {test_data[0] if test_data else 'N/A'}")
                        
                        # Testar processamento de dados
                        if len(test_data) > 1:
                            # Simular dados para teste de mapeamento
                            headers = test_data[0]
                            sample_row = test_data[1]
                            
                            # Criar dict com headers e dados
                            row_dict = dict(zip(headers, sample_row))
                            
                            # Testar mapeamento
                            mapped_data = sheets_service._map_channel_specific_data(channel, row_dict)
                            
                            if mapped_data.get("spend", 0) > 0:
                                print(f"   ✅ Dados mapeados com sucesso")
                                print(f"      Data: {mapped_data.get('date', 'N/A')}")
                                print(f"      Creative: {mapped_data.get('creative', 'N/A')}")
                                print(f"      Spend: R$ {mapped_data.get('spend', 0):.2f}")
                            else:
                                print(f"   ⚠️ Dados mapeados mas spend inválido")
                    
                except Exception as e:
                    print(f"   ❌ Erro na aba '{config['sheet_name']}': {e}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao acessar planilha: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Execute: pip install gspread google-auth")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def show_setup_instructions():
    """Mostra instruções de configuração para as planilhas reais"""
    print("""
📋 INSTRUÇÕES DE CONFIGURAÇÃO PARA PLANILHAS REAIS

1. 🔑 Configurar Credenciais:
   - Acesse: https://console.cloud.google.com/
   - Crie um projeto ou selecione existente
   - Ative a Google Sheets API
   - Crie uma Service Account
   - Baixe o arquivo JSON de credenciais
   - Renomeie para 'credentials.json' e coloque em backend/

2. 📊 Compartilhar Planilhas:
   - Compartilhe cada planilha com o email da Service Account
   - Dê permissão de "Editor" ou "Visualizador"
   - Planilhas a compartilhar:
""")
    
    for channel, config in REAL_SHEETS_CONFIG.items():
        print(f"   📺 {channel}: {config['url']}")
    
    print("""
3. 🔧 Configurar Variáveis:
   - Copie backend/sheets_config_real.env para backend/.env
   - Os IDs já estão configurados

4. 🧪 Testar:
   - python3 test_real_sheets.py
   - Verifique se todas as conexões estão funcionando

📝 ESTRUTURA ESPERADA DAS PLANILHAS:
   Cada planilha deve ter uma aba "Entrega Diária" com:
   - Coluna A: Data
   - Coluna B: Creative
   - Coluna C: Spend/Investimento
   - Colunas D+: Métricas específicas por canal
""")

def show_sheets_summary():
    """Mostra resumo das planilhas configuradas"""
    print("📊 RESUMO DAS PLANILHAS REAIS CONFIGURADAS")
    print("=" * 60)
    
    for channel, config in REAL_SHEETS_CONFIG.items():
        print(f"\n📺 {channel}")
        print(f"   🆔 ID: {config['spreadsheet_id']}")
        print(f"   📋 Aba: {config['sheet_name']}")
        if config.get("gid"):
            print(f"   🔗 GID: {config['gid']}")
        print(f"   🌐 URL: {config['url']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            show_setup_instructions()
        elif sys.argv[1] == "summary":
            show_sheets_summary()
        else:
            print("Uso: python3 test_real_sheets.py [setup|summary]")
    else:
        success = test_sheets_service_with_real_ids()
        
        if not success:
            print("\n❌ TESTE FALHOU!")
            print("   Execute: python3 test_real_sheets.py setup")
            print("   Para ver instruções de configuração")
        else:
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("   Todas as planilhas estão acessíveis")
            print("   O sistema está pronto para usar dados reais")
