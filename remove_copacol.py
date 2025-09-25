#!/usr/bin/env python3
"""
Script para remover campanha Copacol do banco de dados
"""

import sqlite3
from dashboard_database import db

def remove_copacol():
    """Remover campanha Copacol do banco"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            campaign_key = "copacol_institucional_30s"
            
            # Remover dashboards gerados
            cursor.execute("DELETE FROM generated_dashboards WHERE campaign_key = ?", (campaign_key,))
            print(f"✅ Dashboards gerados removidos para {campaign_key}")
            
            # Remover configuração da campanha
            cursor.execute("DELETE FROM campaign_configs WHERE campaign_key = ?", (campaign_key,))
            print(f"✅ Configuração removida para {campaign_key}")
            
            conn.commit()
            print(f"🎉 Campanha {campaign_key} removida com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao remover campanha: {e}")
        return False

if __name__ == "__main__":
    print("🗑️ Removendo campanha Copacol...")
    
    if remove_copacol():
        print("✅ Remoção concluída com sucesso!")
    else:
        print("❌ Erro na remoção!")
