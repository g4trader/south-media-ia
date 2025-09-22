#!/usr/bin/env python3
"""
Teste direto com as planilhas reais fornecidas
"""

import os
import json
from google_sheets_processor import GoogleSheetsProcessor

def test_real_sheets():
    """Testar leitura das planilhas reais"""
    print("🧪 Testando Planilhas Reais")
    print("=" * 50)
    
    # Configuração das planilhas fornecidas
    sheets_config = {
        "YouTube": {
            "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
            "gid": "304137877",
            "columns": {
                "date": "Day",
                "creative": "Creative", 
                "spend": "Valor",
                "impressions": "Impressions",
                "clicks": "Clicks",
                "visits": "Visits"
            }
        },
        "Programática Video": {
            "sheet_id": "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o",
            "gid": "1489416055", 
            "columns": {
                "date": "Day",
                "creative": "Creative",
                "spend": "Valor", 
                "impressions": "Impressions",
                "clicks": "Clicks",
                "visits": "Visits"
            }
        }
    }
    
    try:
        # Inicializar processador
        processor = GoogleSheetsProcessor()
        print("✅ Processador inicializado")
        
        all_data = []
        
        for channel_name, config in sheets_config.items():
            print(f"\n📊 Processando: {channel_name}")
            print(f"🔗 Sheet ID: {config['sheet_id']}")
            print(f"🔗 GID: {config['gid']}")
            
            # Processar dados
            channel_data = processor.process_channel_data(channel_name, config)
            
            if channel_data:
                print(f"✅ {len(channel_data)} registros encontrados")
                
                # Calcular totais
                total_impressions = sum(record.get('impressions', 0) for record in channel_data)
                total_clicks = sum(record.get('clicks', 0) for record in channel_data)
                total_spend = sum(record.get('spend', 0) for record in channel_data)
                
                print(f"📈 Impressões: {total_impressions:,}")
                print(f"👆 Cliques: {total_clicks:,}")
                print(f"💰 Gasto: R$ {total_spend:,.2f}")
                
                if total_impressions > 0:
                    ctr = (total_clicks / total_impressions * 100)
                    cpv = (total_spend / total_impressions)
                    print(f"📊 CTR: {ctr:.2f}%")
                    print(f"📊 CPV: R$ {cpv:.2f}")
                
                all_data.extend(channel_data)
            else:
                print("❌ Nenhum dado encontrado")
        
        # Totais consolidados
        if all_data:
            print(f"\n🎯 TOTAIS CONSOLIDADOS:")
            total_impressions = sum(record.get('impressions', 0) for record in all_data)
            total_clicks = sum(record.get('clicks', 0) for record in all_data)
            total_spend = sum(record.get('spend', 0) for record in all_data)
            
            print(f"📈 Total Impressões: {total_impressions:,}")
            print(f"👆 Total Cliques: {total_clicks:,}")
            print(f"💰 Total Gasto: R$ {total_spend:,.2f}")
            
            if total_impressions > 0:
                ctr = (total_clicks / total_impressions * 100)
                cpv = (total_spend / total_impressions)
                print(f"📊 CTR Total: {ctr:.2f}%")
                print(f"📊 CPV Total: R$ {cpv:.2f}")
            
            # Salvar dados para uso no dashboard
            with open('real_sheets_data.json', 'w') as f:
                json.dump(all_data, f, indent=2, default=str)
            print(f"\n💾 Dados salvos em: real_sheets_data.json")
            
        return all_data
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

if __name__ == "__main__":
    test_real_sheets()



