#!/usr/bin/env python3
"""
Sistema de banco de dados persistente para Cloud Run
Usa Google Cloud Storage para backup/restore automático do SQLite
"""

import sqlite3
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import storage
import logging

# Configuração
DB_FILE = 'dashboard_configs.db'
GCS_BUCKET = 'south-media-ia-database'  # Bucket para backup do banco
GCS_DB_PATH = 'dashboard_configs.db'

logger = logging.getLogger(__name__)

class CampaignConfig:
    def __init__(self, campaign_key: str, client: str, campaign: str, sheet_id: str, tabs: Dict[str, str],
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign = campaign
        self.sheet_id = sheet_id
        self.tabs = tabs
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.updated_at = updated_at if updated_at else datetime.now().isoformat()

    def to_dict(self):
        return {
            "campaign_key": self.campaign_key,
            "client": self.client,
            "campaign": self.campaign,
            "sheet_id": self.sheet_id,
            "tabs": self.tabs,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class PersistentDatabase:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.gcs_client = None
        self.bucket = None
        
        # Inicializar GCS
        self._initialize_gcs()
        
        # Restaurar banco do GCS se existir
        self._restore_from_gcs()
        
        # Inicializar banco
        self._initialize_db()
        
        # Fazer backup inicial
        self._backup_to_gcs()

    def _initialize_gcs(self):
        """Inicializar cliente do Google Cloud Storage"""
        try:
            self.gcs_client = storage.Client()
            self.bucket = self.gcs_client.bucket(GCS_BUCKET)
            logger.info(f"✅ GCS inicializado - Bucket: {GCS_BUCKET}")
        except Exception as e:
            logger.warning(f"⚠️ GCS não disponível: {e}")
            self.gcs_client = None
            self.bucket = None

    def _restore_from_gcs(self):
        """Restaurar banco de dados do Google Cloud Storage"""
        if not self.gcs_client or not self.bucket:
            logger.info("⚠️ GCS não disponível - iniciando com banco vazio")
            return

        try:
            blob = self.bucket.blob(GCS_DB_PATH)
            if blob.exists():
                # Download do banco do GCS
                blob.download_to_filename(self.db_path)
                logger.info(f"✅ Banco restaurado do GCS: {GCS_DB_PATH}")
            else:
                logger.info("ℹ️ Nenhum backup encontrado no GCS - iniciando com banco vazio")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao restaurar do GCS: {e}")

    def _backup_to_gcs(self):
        """Fazer backup do banco para Google Cloud Storage"""
        if not self.gcs_client or not self.bucket:
            logger.warning("⚠️ GCS não disponível - backup não realizado")
            return

        if not os.path.exists(self.db_path):
            logger.warning("⚠️ Arquivo de banco não existe - backup não realizado")
            return

        try:
            blob = self.bucket.blob(GCS_DB_PATH)
            blob.upload_from_filename(self.db_path)
            logger.info(f"✅ Backup realizado para GCS: {GCS_DB_PATH}")
        except Exception as e:
            logger.error(f"❌ Erro no backup para GCS: {e}")

    def _initialize_db(self):
        """Inicializar o banco de dados e criar as tabelas se não existirem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_configs (
                    campaign_key TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    campaign TEXT NOT NULL,
                    sheet_id TEXT NOT NULL,
                    tabs TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_dashboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_key TEXT NOT NULL,
                    dashboard_filename TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY (campaign_key) REFERENCES campaign_configs (campaign_key)
                )
            """)
            conn.commit()

    def save_campaign_config(self, config: CampaignConfig) -> bool:
        """Salva ou atualiza uma configuração de campanha no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                config.updated_at = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO campaign_configs (campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    config.campaign_key,
                    config.client,
                    config.campaign,
                    config.sheet_id,
                    json.dumps(config.tabs),
                    config.created_at,
                    config.updated_at
                ))
                conn.commit()
            
            # Backup após salvar
            self._backup_to_gcs()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração da campanha: {e}")
            return False

    def get_campaign_config(self, campaign_key: str) -> Optional[CampaignConfig]:
        """Obtém uma configuração de campanha pelo campaign_key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at FROM campaign_configs WHERE campaign_key = ?", (campaign_key,))
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

    def get_all_campaign_configs(self) -> Dict[str, CampaignConfig]:
        """Obtém todas as configurações de campanha"""
        campaigns = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT campaign_key, client, campaign, sheet_id, tabs, created_at, updated_at FROM campaign_configs")
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
                campaigns[config.campaign_key] = config
        return campaigns

    def delete_campaign_config(self, campaign_key: str) -> bool:
        """Deleta uma configuração de campanha e seus dashboards gerados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM generated_dashboards WHERE campaign_key = ?", (campaign_key,))
                cursor.execute("DELETE FROM campaign_configs WHERE campaign_key = ?", (campaign_key,))
                conn.commit()
            
            # Backup após deletar
            self._backup_to_gcs()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar campanha: {e}")
            return False

    def record_generated_dashboard(self, campaign_key: str, dashboard_filename: str) -> bool:
        """Registra um dashboard gerado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO generated_dashboards (campaign_key, dashboard_filename, generated_at)
                    VALUES (?, ?, ?)
                """, (campaign_key, dashboard_filename, datetime.now().isoformat()))
                conn.commit()
            
            # Backup após registrar
            self._backup_to_gcs()
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar dashboard gerado: {e}")
            return False

    def force_backup(self):
        """Força um backup manual"""
        self._backup_to_gcs()

# Instância global do banco de dados persistente
db = PersistentDatabase()

# Funções de conveniência para a API
def save_campaign_config(campaign_key: str, config: CampaignConfig) -> bool:
    return db.save_campaign_config(config)

def get_campaign_config(campaign_key: str) -> Optional[CampaignConfig]:
    return db.get_campaign_config(campaign_key)

def get_all_campaign_configs() -> Dict[str, CampaignConfig]:
    return db.get_all_campaign_configs()

def delete_campaign_config(campaign_key: str) -> bool:
    return db.delete_campaign_config(campaign_key)

def record_generated_dashboard(campaign_key: str, dashboard_filename: str) -> bool:
    return db.record_generated_dashboard(campaign_key, dashboard_filename)

def force_backup():
    """Força um backup manual"""
    db.force_backup()

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 Testando sistema de banco persistente...")
    
    # Criar campanha de teste
    test_campaign = CampaignConfig(
        campaign_key="test_persistent",
        client="Test Client",
        campaign="Test Campaign",
        sheet_id="test_sheet",
        tabs={"daily": "gid1", "contract": "gid2"}
    )
    
    # Salvar
    if save_campaign_config("test_persistent", test_campaign):
        print("✅ Campanha salva com sucesso")
        
        # Recuperar
        retrieved = get_campaign_config("test_persistent")
        if retrieved:
            print(f"✅ Campanha recuperada: {retrieved.to_dict()}")
        
        # Forçar backup
        force_backup()
        print("✅ Backup forçado realizado")
        
        # Deletar
        if delete_campaign_config("test_persistent"):
            print("✅ Campanha deletada com sucesso")
    
    print("🎯 Teste concluído!")
