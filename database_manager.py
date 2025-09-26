#!/usr/bin/env python3
"""
Gerenciador de banco de dados PostgreSQL para persistência de campanhas
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# Configurar logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador do banco de dados PostgreSQL"""
    
    def __init__(self):
        self.connection_pool = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializar pool de conexões"""
        try:
            # Configurações do banco (pode ser configurado via variáveis de ambiente)
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'south_media_dashboards'),
                'user': os.getenv('DB_USER', os.getenv('USER', 'lucianoterres')),
                'password': os.getenv('DB_PASSWORD', '')
            }
            
            # Criar pool de conexões
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **db_config
            )
            
            logger.info("✅ Pool de conexões PostgreSQL inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            self.connection_pool = None
    
    def get_connection(self):
        """Obter conexão do pool"""
        if not self.connection_pool:
            raise Exception("Pool de conexões não inicializado")
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Retornar conexão para o pool"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
        """Executar query no banco"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                else:
                    conn.commit()
                    return cursor.rowcount
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, 
                     sheet_id: str, channel: str = None) -> bool:
        """Salvar/atualizar campanha"""
        try:
            query = """
                INSERT INTO campaigns (campaign_key, client, campaign_name, sheet_id, channel)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (campaign_key) 
                DO UPDATE SET 
                    client = EXCLUDED.client,
                    campaign_name = EXCLUDED.campaign_name,
                    sheet_id = EXCLUDED.sheet_id,
                    channel = EXCLUDED.channel,
                    updated_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
            """
            
            self.execute_query(query, (campaign_key, client, campaign_name, sheet_id, channel), fetch=False)
            logger.info(f"✅ Campanha '{campaign_key}' salva/atualizada no banco")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar campanha: {e}")
            return False
    
    def get_campaign(self, campaign_key: str) -> Optional[Dict]:
        """Obter campanha por chave"""
        try:
            query = "SELECT * FROM campaigns WHERE campaign_key = %s AND is_active = TRUE"
            result = self.execute_query(query, (campaign_key,))
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanha: {e}")
            return None
    
    def get_all_campaigns(self) -> List[Dict]:
        """Obter todas as campanhas ativas"""
        try:
            query = "SELECT campaign_key FROM campaigns WHERE is_active = TRUE ORDER BY updated_at DESC"
            result = self.execute_query(query)
            return result or []
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanhas: {e}")
            return []
    
    def delete_campaign(self, campaign_key: str) -> bool:
        """Marcar campanha como inativa (soft delete)"""
        try:
            query = "UPDATE campaigns SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE campaign_key = %s"
            rows_affected = self.execute_query(query, (campaign_key,), fetch=False)
            
            if rows_affected > 0:
                logger.info(f"✅ Campanha '{campaign_key}' marcada como inativa")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao deletar campanha: {e}")
            return False
    
    def cache_campaign_data(self, campaign_key: str, data: Dict) -> bool:
        """Cachear dados extraídos da campanha"""
        try:
            # Primeiro, remover cache antigo
            delete_query = "DELETE FROM campaign_data_cache WHERE campaign_key = %s"
            self.execute_query(delete_query, (campaign_key,), fetch=False)
            
            # Inserir novo cache
            insert_query = """
                INSERT INTO campaign_data_cache (campaign_key, data_json)
                VALUES (%s, %s)
            """
            
            self.execute_query(insert_query, (campaign_key, json.dumps(data)), fetch=False)
            logger.info(f"✅ Dados da campanha '{campaign_key}' cacheados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao cachear dados: {e}")
            return False
    
    def get_cached_data(self, campaign_key: str, max_age_hours: int = 1) -> Optional[Dict]:
        """Obter dados do cache se não estiverem muito antigos"""
        try:
            query = """
                SELECT data_json FROM campaign_data_cache 
                WHERE campaign_key = %s 
                AND extracted_at > (CURRENT_TIMESTAMP - INTERVAL '%s hours')
                ORDER BY extracted_at DESC 
                LIMIT 1
            """
            
            result = self.execute_query(query, (campaign_key, max_age_hours))
            
            if result:
                return json.loads(result[0]['data_json'])
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter cache: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Testar conexão com o banco"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) == 1 and result[0]['test'] == 1
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Criar tabelas se não existirem"""
        try:
            # Ler e executar schema
            with open('database_schema.sql', 'r') as f:
                schema_sql = f.read()
            
            # Dividir em comandos individuais
            commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
            
            for command in commands:
                if command and not command.startswith('--'):
                    try:
                        self.execute_query(command, fetch=False)
                    except Exception as e:
                        # Ignorar erros de tabelas já existentes
                        if 'already exists' not in str(e):
                            logger.warning(f"⚠️ Comando SQL falhou: {e}")
            
            logger.info("✅ Tabelas criadas/verificadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def close(self):
        """Fechar pool de conexões"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ Pool de conexões fechado")

# Instância global
db_manager = DatabaseManager()

