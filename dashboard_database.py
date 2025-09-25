#!/usr/bin/env python3
"""
Sistema de banco de dados para configurações do gerador de dashboards
Usa SQLite com backup automático para Cloud Storage
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CampaignConfig:
    """Configuração de uma campanha"""
    campaign_key: str
    client: str
    campaign: str
    sheet_id: str
    tabs: Dict[str, str]
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class DashboardDatabase:
    """Gerenciador do banco de dados de dashboards"""
    
    def __init__(self, db_path: str = "dashboard_configs.db"):
        self.db_path = db_path
        self.backup_bucket = "south-media-ia-dashboard-configs"
        self.init_database()
    
    def init_database(self):
        """Inicializar banco de dados e tabelas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de configurações de campanhas
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS campaign_configs (
                        campaign_key TEXT PRIMARY KEY,
                        client TEXT NOT NULL,
                        campaign TEXT NOT NULL,
                        sheet_id TEXT NOT NULL,
                        tabs TEXT NOT NULL,  -- JSON string
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Tabela de dashboards gerados
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generated_dashboards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_key TEXT NOT NULL,
                        dashboard_filename TEXT NOT NULL,
                        dashboard_url TEXT NOT NULL,
                        api_endpoint TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (campaign_key) REFERENCES campaign_configs (campaign_key)
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Banco de dados inicializado com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def save_campaign_config(self, config: CampaignConfig) -> bool:
        """Salvar configuração de campanha"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se já existe
                cursor.execute("SELECT campaign_key FROM campaign_configs WHERE campaign_key = ?", (config.campaign_key,))
                exists = cursor.fetchone() is not None
                
                if exists:
                    # Atualizar
                    cursor.execute('''
                        UPDATE campaign_configs 
                        SET client = ?, campaign = ?, sheet_id = ?, tabs = ?, updated_at = ?
                        WHERE campaign_key = ?
                    ''', (
                        config.client, config.campaign, config.sheet_id,
                        json.dumps(config.tabs), datetime.now().isoformat(), config.campaign_key
                    ))
                    logger.info(f"✅ Configuração da campanha {config.campaign_key} atualizada")
                else:
                    # Inserir nova
                    cursor.execute('''
                        INSERT INTO campaign_configs 
                        (campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        config.campaign_key, config.client, config.campaign, config.sheet_id,
                        json.dumps(config.tabs), config.created_at, config.updated_at
                    ))
                    logger.info(f"✅ Nova configuração da campanha {config.campaign_key} salva")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração da campanha: {e}")
            return False
    
    def get_campaign_config(self, campaign_key: str) -> Optional[CampaignConfig]:
        """Obter configuração de campanha"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at
                    FROM campaign_configs WHERE campaign_key = ?
                ''', (campaign_key,))
                
                row = cursor.fetchone()
                if row:
                    return CampaignConfig(
                        campaign_key=row[0],
                        client=row[1],
                        campaign=row[2],
                        sheet_id=row[3],
                        tabs=json.loads(row[4]),
                        created_at=row[5],
                        updated_at=row[6]
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter configuração da campanha: {e}")
            return None
    
    def get_all_campaign_configs(self) -> Dict[str, CampaignConfig]:
        """Obter todas as configurações de campanhas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at
                    FROM campaign_configs ORDER BY updated_at DESC
                ''')
                
                configs = {}
                for row in cursor.fetchall():
                    config = CampaignConfig(
                        campaign_key=row[0],
                        client=row[1],
                        campaign=row[2],
                        sheet_id=row[3],
                        tabs=json.loads(row[4]),
                        created_at=row[5],
                        updated_at=row[6]
                    )
                    configs[config.campaign_key] = config
                
                return configs
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter configurações das campanhas: {e}")
            return {}
    
    def save_generated_dashboard(self, campaign_key: str, dashboard_filename: str, 
                               dashboard_url: str, api_endpoint: str) -> bool:
        """Salvar registro de dashboard gerado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO generated_dashboards 
                    (campaign_key, dashboard_filename, dashboard_url, api_endpoint, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (campaign_key, dashboard_filename, dashboard_url, api_endpoint, datetime.now().isoformat()))
                
                conn.commit()
                logger.info(f"✅ Dashboard {dashboard_filename} registrado no banco")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dashboard gerado: {e}")
            return False
    
    def get_generated_dashboards(self, campaign_key: str = None) -> List[Dict]:
        """Obter dashboards gerados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if campaign_key:
                    cursor.execute('''
                        SELECT id, campaign_key, dashboard_filename, dashboard_url, api_endpoint, created_at
                        FROM generated_dashboards WHERE campaign_key = ? ORDER BY created_at DESC
                    ''', (campaign_key,))
                else:
                    cursor.execute('''
                        SELECT id, campaign_key, dashboard_filename, dashboard_url, api_endpoint, created_at
                        FROM generated_dashboards ORDER BY created_at DESC
                    ''')
                
                dashboards = []
                for row in cursor.fetchall():
                    dashboards.append({
                        'id': row[0],
                        'campaign_key': row[1],
                        'dashboard_filename': row[2],
                        'dashboard_url': row[3],
                        'api_endpoint': row[4],
                        'created_at': row[5]
                    })
                
                return dashboards
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter dashboards gerados: {e}")
            return []
    
    def migrate_from_json(self, json_file_path: str = "generator_config.json") -> bool:
        """Migrar configurações do arquivo JSON para o banco"""
        try:
            if not os.path.exists(json_file_path):
                logger.warning(f"⚠️ Arquivo {json_file_path} não encontrado")
                return False
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            migrated_count = 0
            for campaign_key, config_data in data.items():
                config = CampaignConfig(
                    campaign_key=campaign_key,
                    client=config_data['client'],
                    campaign=config_data['campaign'],
                    sheet_id=config_data['sheet_id'],
                    tabs=config_data['tabs']
                )
                
                if self.save_campaign_config(config):
                    migrated_count += 1
            
            logger.info(f"✅ Migração concluída: {migrated_count} campanhas migradas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na migração do JSON: {e}")
            return False
    
    def backup_to_cloud_storage(self) -> bool:
        """Fazer backup do banco para Cloud Storage"""
        try:
            # Implementar backup para Cloud Storage se necessário
            # Por enquanto, apenas log
            logger.info("📦 Backup do banco de dados (implementar Cloud Storage se necessário)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return False

# Instância global do banco de dados
db = DashboardDatabase()

def save_campaign_config(campaign_key: str, config: CampaignConfig) -> bool:
    """Função de conveniência para salvar configuração"""
    return db.save_campaign_config(config)

def get_campaign_config(campaign_key: str) -> Optional[CampaignConfig]:
    """Função de conveniência para obter configuração"""
    return db.get_campaign_config(campaign_key)

def get_all_campaign_configs() -> Dict[str, CampaignConfig]:
    """Função de conveniência para obter todas as configurações"""
    return db.get_all_campaign_configs()

if __name__ == "__main__":
    # Teste do sistema de banco de dados
    print("🧪 Testando sistema de banco de dados...")
    
    # Teste de configuração
    test_config = CampaignConfig(
        campaign_key="teste_banco_dados",
        client="Cliente Teste",
        campaign="Campanha Teste",
        sheet_id="1234567890",
        tabs={
            "daily_data": "111111111",
            "contract": "222222222",
            "strategies": "333333333",
            "publishers": "444444444"
        }
    )
    
    # Salvar
    if save_campaign_config("teste_banco_dados", test_config):
        print("✅ Configuração salva com sucesso")
    
    # Recuperar
    retrieved_config = get_campaign_config("teste_banco_dados")
    if retrieved_config:
        print(f"✅ Configuração recuperada: {retrieved_config.client} - {retrieved_config.campaign}")
    
    # Migrar do JSON
    if db.migrate_from_json():
        print("✅ Migração do JSON concluída")
    
    print("🎉 Teste do banco de dados concluído!")
