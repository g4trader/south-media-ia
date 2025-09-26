#!/usr/bin/env python3
"""
Teste do Extrator Real do Google Sheets
"""

import os
import sys
from real_google_sheets_extractor import RealGoogleSheetsExtractor, CampaignConfig

def test_extractor():
    """Testar o extrator real"""
    
    print("🧪 Testando Extrator Real do Google Sheets")
    print("=" * 50)
    
    # Configuração da campanha Copacol
    config = CampaignConfig(
        client="Copacol",
        campaign="Institucional 30s",
        campaign_key="copacol_real_test",
        sheet_id="1scA5ykf49DLobPTAKSL5fNgGM_iomcJmgSJqXolV679M",
        tabs={
            "report": "Report",
            "contract": "Informações de contrato",
            "publishers": "Publishers",
            "strategies": "Segmentações"
        }
    )
    
    print(f"📊 Sheet ID: {config.sheet_id}")
    print(f"👤 Cliente: {config.client}")
    print(f"📋 Campanha: {config.campaign}")
    
    try:
        print("\n🔄 Iniciando extração...")
        extractor = RealGoogleSheetsExtractor(config)
        
        print("🔄 Extraindo dados...")
        data = extractor.extract_data()
        
        if data:
            print("\n✅ EXTRAÇÃO REAL BEM-SUCEDIDA!")
            print("=" * 50)
            print(f"📊 Cliente: {data['campaign_summary']['client']}")
            print(f"💰 Investimento: R$ {data['campaign_summary']['investment']:,.2f}")
            print(f"📈 Pacing: {data['campaign_summary']['pacing']:.1f}%")
            print(f"🎯 CPV: R$ {data['campaign_summary']['cpv']:.2f}")
            print(f"📺 VTR: {data['campaign_summary']['vtr']:.1f}%")
            print(f"📅 Dados diários: {len(data['daily_data'])} dias")
            print(f"🔗 Fonte: {data['data_source']}")
            print(f"⏰ Atualizado: {data['last_updated']}")
            
            print("\n📊 Resumo dos Dados:")
            print(f"  • Total investido: R$ {data['campaign_summary']['total_spend']:,.2f}")
            print(f"  • Impressões: {data['campaign_summary']['total_impressions']:,}")
            print(f"  • Cliques: {data['campaign_summary']['total_clicks']:,}")
            print(f"  • VC entregues: {data['campaign_summary']['total_video_completions']:,}")
            
            print("\n🎯 Insights:")
            for insight in data['insights']:
                print(f"  • {insight}")
            
            return True
        else:
            print("❌ Extração retornou dados vazios")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO NA EXTRAÇÃO REAL:")
        print(f"   {e}")
        print("\n🔧 Possíveis soluções:")
        print("1. Verificar se as credenciais estão configuradas")
        print("2. Verificar se a planilha está compartilhada com a service account")
        print("3. Verificar se os nomes das abas estão corretos")
        print("4. Verificar se a planilha tem dados")
        return False

def check_credentials():
    """Verificar configuração de credenciais"""
    print("\n🔍 Verificando Credenciais...")
    
    # Verificar arquivo local
    if os.path.exists("credentials.json"):
        print("✅ Arquivo credentials.json encontrado")
        return True
    
    # Verificar variável de ambiente
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        print("✅ Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS_JSON encontrada")
        return True
    
    # Verificar variável padrão do Google
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        print("✅ Variável GOOGLE_APPLICATION_CREDENTIALS encontrada")
        return True
    
    print("❌ Nenhuma credencial encontrada")
    print("\n📋 Para configurar credenciais:")
    print("1. Execute: python3 setup_credentials.py")
    print("2. Ou configure a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS_JSON")
    print("3. Ou coloque o arquivo credentials.json no diretório atual")
    
    return False

if __name__ == "__main__":
    print("🚀 Teste do Extrator Real do Google Sheets")
    print("Este teste irá tentar carregar dados REAIS da planilha Copacol\n")
    
    # Verificar credenciais primeiro
    if not check_credentials():
        print("\n⚠️  Configure as credenciais antes de continuar")
        sys.exit(1)
    
    # Testar extrator
    success = test_extractor()
    
    if success:
        print("\n🎉 SUCESSO! O extrator real está funcionando!")
        print("📈 Agora você pode usar este extrator no sistema de dashboards")
    else:
        print("\n💥 FALHA! O extrator não conseguiu carregar dados reais")
        print("🔧 Corrija os problemas antes de continuar")

