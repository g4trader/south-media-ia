#!/usr/bin/env python3
"""
Script para remover campanhas específicas do banco de dados
"""

import sys
from dashboard_database import db

def remove_campaigns(campaign_keys):
    """Remover campanhas específicas do banco"""
    try:
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            for campaign_key in campaign_keys:
                # Remover dashboards gerados
                cursor.execute("DELETE FROM generated_dashboards WHERE campaign_key = ?", (campaign_key,))
                print(f"✅ Dashboards gerados removidos para {campaign_key}")
                
                # Remover configuração da campanha
                cursor.execute("DELETE FROM campaign_configs WHERE campaign_key = ?", (campaign_key,))
                print(f"✅ Configuração removida para {campaign_key}")
            
            conn.commit()
            print(f"🎉 {len(campaign_keys)} campanhas removidas com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao remover campanhas: {e}")
        return False

if __name__ == "__main__":
    # Campanhas SEBRAE para remover
    campaigns_to_remove = [
        "sebrae_pr_feira_do_empreendedor",
        "sebrae_pr_institucional_setembro"
    ]
    
    print(f"🗑️ Removendo campanhas: {', '.join(campaigns_to_remove)}")
    
    if remove_campaigns(campaigns_to_remove):
        print("✅ Remoção concluída com sucesso!")
    else:
        print("❌ Erro na remoção!")
        sys.exit(1)
