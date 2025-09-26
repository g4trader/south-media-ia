#!/usr/bin/env python3
"""
Script para debugar a extração da planilha Copacol usando o extrator real
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from real_google_sheets_extractor import RealGoogleSheetsExtractor

class Config:
    def __init__(self):
        self.client = "Copacol"
        self.campaign = "Institucional 30s"
        self.sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"

def debug_copacol_real():
    """Debugar extração da planilha Copacol com extrator real"""
    print("🔍 Debugando extração da planilha Copacol com extrator real...")
    
    config = Config()
    
    try:
        # Criar extrator
        extractor = RealGoogleSheetsExtractor(config)
        print("✅ Extrator criado com sucesso")
        
        # Extrair dados
        print("\n🔄 Extraindo dados...")
        data = extractor.extract_data()
        
        if data:
            print("✅ Dados extraídos com sucesso!")
            
            # Mostrar resumo
            campaign = data.get('campaign_summary', {})
            print(f"\n📊 RESUMO DA CAMPANHA:")
            print(f"  Cliente: {campaign.get('client', 'N/A')}")
            print(f"  Campanha: {campaign.get('campaign', 'N/A')}")
            print(f"  Investimento: R$ {campaign.get('investment', 0):,.2f}")
            print(f"  VC Contratadas: {campaign.get('complete_views_contracted', 0):,}")
            print(f"  CPV Contratado: R$ {campaign.get('cpv_contracted', 0):.2f}")
            print(f"  Impressões: {campaign.get('total_impressions', 0):,}")
            print(f"  Cliques: {campaign.get('total_clicks', 0):,}")
            print(f"  VC Realizadas: {campaign.get('total_video_completions', 0):,}")
            print(f"  CPV Atual: R$ {campaign.get('cpv', 0):.2f}")
            print(f"  CTR: {campaign.get('ctr', 0):.2f}%")
            print(f"  VTR: {campaign.get('vtr', 0):.1f}%")
            print(f"  Pacing: {campaign.get('pacing', 0):.1f}%")
            
            # Mostrar dados diários
            daily_data = data.get('daily_data', [])
            print(f"\n📅 DADOS DIÁRIOS: {len(daily_data)} registros")
            
            if daily_data:
                print("\n📋 Primeiros 5 dias:")
                for i, day in enumerate(daily_data[:5]):
                    print(f"  {i+1}. {day.get('date', 'N/A')}: R$ {day.get('spend', 0):,.2f} | {day.get('impressions', 0):,} impressões | {day.get('clicks', 0):,} cliques")
            
            # Mostrar publishers
            publishers = data.get('publishers', [])
            print(f"\n📺 PUBLISHERS: {len(publishers)} publishers")
            
            if publishers:
                print("\n📋 Top 5 publishers:")
                for i, pub in enumerate(publishers[:5]):
                    print(f"  {i+1}. {pub.get('publisher', 'N/A')}: R$ {pub.get('investimento', 0):,.2f} | {pub.get('impressoes', 0):,} impressões")
            
            # Mostrar estratégias
            strategies = data.get('strategies', [])
            print(f"\n🎯 ESTRATÉGIAS: {len(strategies)} estratégias")
            
            if strategies:
                print("\n📋 Estratégias:")
                for i, strat in enumerate(strategies):
                    print(f"  {i+1}. {strat.get('strategy', 'N/A')}: R$ {strat.get('investimento', 0):,.2f} | {strat.get('impressoes', 0):,} impressões")
            
            print(f"\n🔗 Fonte: {data.get('data_source', 'N/A')}")
            print(f"⏰ Atualizado: {data.get('last_updated', 'N/A')}")
            
        else:
            print("❌ Nenhum dado extraído")
            
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_copacol_real()

