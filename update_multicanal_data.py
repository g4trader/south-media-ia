#!/usr/bin/env python3
"""
Script para atualizar dados do Dashboard Multicanal
Executa a integração e atualiza o dashboard com dados reais das planilhas
"""

import sys
import os
from integrate_multicanal_dashboard import MulticanalDashboardIntegrator

def main():
    """Função principal para atualizar dados"""
    print("🔄 Atualizando dados do Dashboard Multicanal...")
    print("=" * 50)
    
    try:
        # Inicializar integrador
        integrator = MulticanalDashboardIntegrator()
        
        # Verificar configuração do Google Sheets
        if not integrator.sheets_service.is_configured():
            print("⚠️  Google Sheets não configurado.")
            print("📝 Para configurar:")
            print("   1. Baixe o arquivo credentials.json do Google Cloud Console")
            print("   2. Execute: python3 -c \"from google_sheets_service import GoogleSheetsService; GoogleSheetsService()\"")
            print("   3. Execute este script novamente")
            print("\n🔄 Usando dados simulados por enquanto...")
        
        # Gerar dados do dashboard
        dashboard_data = integrator.generate_dashboard_data()
        
        # Exibir resumo detalhado
        print("\n📊 Resumo Detalhado:")
        print("-" * 30)
        
        spotify = dashboard_data['campanhas']['spotify']
        programatica = dashboard_data['campanhas']['programatica']
        
        print(f"🎵 SPOTIFY:")
        print(f"   Impressões: {spotify['impressoes']:,}")
        print(f"   Escutas Completas: {spotify['escutas_completas']:,}")
        print(f"   Investimento: R$ {spotify['gasto']:,.2f}")
        print(f"   CPE: R$ {spotify['cpe']:.2f}")
        print(f"   Taxa de Escuta: {spotify['taxa_escuta_completa']:.1f}%")
        
        print(f"\n📺 PROGRAMÁTICA:")
        print(f"   Impressões: {programatica['impressoes']:,}")
        print(f"   Visualizações 100%: {programatica['visualizacoes_100']:,}")
        print(f"   Cliques: {programatica['cliques']:,}")
        print(f"   Investimento: R$ {programatica['gasto']:,.2f}")
        print(f"   CPV: R$ {programatica['cpv']:.2f}")
        print(f"   CTR: {programatica['ctr']:.2f}%")
        print(f"   VTR100: {programatica['vtr100']:.1f}%")
        
        print(f"\n🌐 SITES PREMIUM: {len(dashboard_data['sites_premium'])} sites")
        print(f"💰 INVESTIMENTO TOTAL: R$ {dashboard_data['consolidado']['total_investimento']:,.2f}")
        print(f"📈 IMPRESSÕES TOTAIS: {dashboard_data['consolidado']['total_impressoes']:,}")
        
        print(f"\n✅ Dashboard atualizado com sucesso!")
        print(f"🌐 Acesse: static/dash_multicanal_spotify_programatica.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar dashboard: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
