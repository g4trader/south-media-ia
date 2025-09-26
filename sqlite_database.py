#!/usr/bin/env python3
"""
Gerenciador de banco de dados SQLite para persistência de campanhas
Alternativa mais simples ao PostgreSQL
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# Configurar logging
logger = logging.getLogger(__name__)

class SQLiteDatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path: str = "campaigns.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializar banco de dados e criar tabelas"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Criar tabela de campanhas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_key TEXT UNIQUE NOT NULL,
                        client TEXT NOT NULL,
                        campaign_name TEXT NOT NULL,
                        sheet_id TEXT NOT NULL,
                        channel TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Criar tabela de cache de dados
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campaign_data_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_key TEXT NOT NULL,
                        data_json TEXT NOT NULL,
                        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (campaign_key) REFERENCES campaigns(campaign_key) ON DELETE CASCADE
                    )
                """)
                
                # Criar índices
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_key ON campaigns(campaign_key)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_client ON campaigns(client)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_campaign_key ON campaign_data_cache(campaign_key)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_extracted_at ON campaign_data_cache(extracted_at)")
                
                conn.commit()
                logger.info("✅ Banco SQLite inicializado com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Para retornar dicionários
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, 
                     sheet_id: str, channel: str = None) -> bool:
        """Salvar/atualizar campanha"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Usar INSERT OR REPLACE para upsert
                cursor.execute("""
                    INSERT OR REPLACE INTO campaigns 
                    (campaign_key, client, campaign_name, sheet_id, channel, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
                """, (campaign_key, client, campaign_name, sheet_id, channel))
                
                conn.commit()
                logger.info(f"✅ Campanha '{campaign_key}' salva/atualizada no banco")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar campanha: {e}")
            return False
    
    def get_campaign(self, campaign_key: str) -> Optional[Dict]:
        """Obter campanha por chave"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM campaigns 
                    WHERE campaign_key = ? AND is_active = 1
                """, (campaign_key,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanha: {e}")
            return None
    
    def get_all_campaigns(self) -> List[Dict]:
        """Obter todas as campanhas ativas"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT campaign_key FROM campaigns 
                    WHERE is_active = 1 
                    ORDER BY updated_at DESC
                """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanhas: {e}")
            return []
    
    def delete_campaign(self, campaign_key: str) -> bool:
        """Marcar campanha como inativa (soft delete)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE campaigns 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                    WHERE campaign_key = ?
                """, (campaign_key,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"✅ Campanha '{campaign_key}' marcada como inativa")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao deletar campanha: {e}")
            return False
    
    def cache_campaign_data(self, campaign_key: str, data: Dict) -> bool:
        """Cachear dados extraídos da campanha"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Primeiro, remover cache antigo
                cursor.execute("DELETE FROM campaign_data_cache WHERE campaign_key = ?", (campaign_key,))
                
                # Inserir novo cache
                cursor.execute("""
                    INSERT INTO campaign_data_cache (campaign_key, data_json)
                    VALUES (?, ?)
                """, (campaign_key, json.dumps(data)))
                
                conn.commit()
                logger.info(f"✅ Dados da campanha '{campaign_key}' cacheados")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao cachear dados: {e}")
            return False
    
    def get_cached_data(self, campaign_key: str, max_age_hours: int = 1) -> Optional[Dict]:
        """Obter dados do cache se não estiverem muito antigos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT data_json FROM campaign_data_cache 
                    WHERE campaign_key = ? 
                    AND extracted_at > datetime('now', '-{} hours')
                    ORDER BY extracted_at DESC 
                    LIMIT 1
                """.format(max_age_hours), (campaign_key,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row['data_json'])
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter cache: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Testar conexão com o banco"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                return result['test'] == 1
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão: {e}")
            return False
    
    def get_database_info(self) -> Dict:
        """Obter informações do banco"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Contar campanhas
                cursor.execute("SELECT COUNT(*) as count FROM campaigns WHERE is_active = 1")
                campaigns_count = cursor.fetchone()['count']
                
                # Contar cache
                cursor.execute("SELECT COUNT(*) as count FROM campaign_data_cache")
                cache_count = cursor.fetchone()['count']
                
                # Tamanho do arquivo
                file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    "database_path": self.db_path,
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "active_campaigns": campaigns_count,
                    "cached_datasets": cache_count,
                    "connection_status": "OK"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do banco: {e}")
            return {"connection_status": "ERROR", "error": str(e)}

# Instância global
db_manager = SQLiteDatabaseManager()

