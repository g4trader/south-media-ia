#!/usr/bin/env python3
"""
Script para verificar configurações da planilha (Sheet ID e GIDs)
"""

import requests
import json

def check_campaign_sheet_config(campaign_key):
    """Verificar configurações da planilha via API"""
    try:
        # Fazer requisição para obter configuração completa
        url = f"https://south-media-ia-609095880025.us-central1.run.app/api/campaigns"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            campaigns = data.get('campaigns', [])
            
            # Encontrar a campanha específica
            campaign = None
            for c in campaigns:
                if c.get('key') == campaign_key:
                    campaign = c
                    break
            
            if campaign:
                print(f"📊 CONFIGURAÇÃO DA PLANILHA PARA: {campaign_key}")
                print(f"┌─────────────────────────────────────────────────────────┐")
                print(f"│ Cliente: {campaign.get('client', 'N/A'):<45} │")
                print(f"│ Campanha: {campaign.get('campaign', 'N/A'):<44} │")
                print(f"└─────────────────────────────────────────────────────────┘")
                
                # Agora vamos tentar obter os dados para ver o Sheet ID
                data_url = f"https://south-media-ia-609095880025.us-central1.run.app/api/{campaign_key}/data"
                data_response = requests.get(data_url)
                
                if data_response.status_code == 200:
                    data_info = data_response.json()
                    print(f"\n📋 INFORMAÇÕES DA PLANILHA:")
                    
                    # Verificar se há informações sobre a planilha nos dados
                    if 'data' in data_info:
                        campaign_data = data_info['data']
                        print(f"  • Nome da campanha: {campaign_data.get('campaign_name', 'N/A')}")
                        print(f"  • Canal: {campaign_data.get('channel', 'N/A')}")
                        
                        # Verificar se há informações de contrato
                        contract = campaign_data.get('contract', {})
                        if contract:
                            print(f"  • Investimento: R$ {contract.get('investment', 'N/A')}")
                            print(f"  • VC Contratado: {contract.get('complete_views_contracted', 'N/A')}")
                            print(f"  • CPV Contratado: R$ {contract.get('cpv_contracted', 'N/A')}")
                
                return True
            else:
                print(f"❌ Campanha '{campaign_key}' não encontrada")
                return False
        else:
            print(f"❌ Erro ao acessar API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def check_database_schema():
    """Verificar schema do banco de dados para ver onde estão os GIDs"""
    try:
        from dashboard_database import db
        import sqlite3
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(campaign_configs)")
            columns = cursor.fetchall()
            
            print(f"\n🗄️ ESTRUTURA DA TABELA CAMPAIGN_CONFIGS:")
            print(f"┌─────────────────────────────────────────────────────────┐")
            print(f"│ {'Coluna':<20} │ {'Tipo':<15} │ {'Nullable':<10} │")
            print(f"├─────────────────────────────────────────────────────────┤")
            
            for col in columns:
                col_name = col[1][:20] if len(col[1]) > 20 else col[1]
                col_type = col[2][:15] if len(col[2]) > 15 else col[2]
                nullable = "SIM" if col[3] == 0 else "NÃO"
                print(f"│ {col_name:<20} │ {col_type:<15} │ {nullable:<10} │")
            
            print(f"└─────────────────────────────────────────────────────────┘")
            
            # Verificar se há dados na tabela
            cursor.execute("SELECT COUNT(*) FROM campaign_configs")
            count = cursor.fetchone()[0]
            print(f"\n📊 Total de campanhas no banco local: {count}")
            
            if count > 0:
                # Mostrar uma campanha como exemplo
                cursor.execute("SELECT campaign_key, sheet_id, tabs FROM campaign_configs LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"\n📋 EXEMPLO DE CONFIGURAÇÃO:")
                    print(f"  • Campaign Key: {row[0]}")
                    print(f"  • Sheet ID: {row[1]}")
                    print(f"  • Tabs (GIDs): {row[2]}")
                    
                    # Parsear tabs
                    try:
                        tabs = json.loads(row[2])
                        print(f"\n🔗 GIDs DAS ABAS:")
                        for tab_name, gid in tabs.items():
                            print(f"  • {tab_name}: {gid}")
                    except:
                        print(f"  • Erro ao parsear tabs: {row[2]}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar schema: {e}")

if __name__ == "__main__":
    campaign_key = "sebrae_pr_feira_do_empreendedor"
    
    print("🔍 VERIFICANDO CONFIGURAÇÕES DA PLANILHA")
    print("=" * 60)
    
    check_campaign_sheet_config(campaign_key)
    
    print("\n" + "=" * 60)
    print("🗄️ VERIFICANDO BANCO DE DADOS LOCAL")
    print("=" * 60)
    
    check_database_schema()
    
    print("\n" + "=" * 60)
    print("✅ Verificação concluída!")
