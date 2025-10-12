#!/usr/bin/env python3
"""
Sistema de Persistência Definitiva - BigQuery + Firestore
Implementação para substituir SQLite + GCS
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.cloud import bigquery
from google.cloud import firestore

logger = logging.getLogger(__name__)

class BigQueryFirestoreManager:
    """Gerenciador de persistência usando BigQuery + Firestore"""
    
    def __init__(self, project_id: str = None, environment: str = None):
        self.project_id = project_id or os.getenv('PROJECT_ID', 'automatizar-452311')
        self.environment = environment or os.getenv('ENVIRONMENT', 'production')
        
        # Inicializar clientes
        try:
            self.bq_client = bigquery.Client(project=self.project_id)
            self.fs_client = firestore.Client(project=self.project_id)
            
            # Configurações baseadas no ambiente
            if self.environment == 'staging':
                self.dataset_id = 'south_media_dashboards_staging'
                self.campaigns_collection = 'campaigns_staging'
                self.dashboards_collection = 'dashboards_staging'
                logger.info("🧪 Usando ambiente STAGING")
            elif self.environment == 'hml':
                self.dataset_id = 'south_media_dashboards_hml'
                self.campaigns_collection = 'campaigns_hml'
                self.dashboards_collection = 'dashboards_hml'
                logger.info("🔬 Usando ambiente HOMOLOGAÇÃO (HML)")
            else:
                self.dataset_id = 'south_media_dashboards'
                self.campaigns_collection = 'campaigns'
                self.dashboards_collection = 'dashboards'
                logger.info("🚀 Usando ambiente PRODUCTION")
            
            # Tabelas (iguais para ambos ambientes)
            self.campaigns_table = 'campaigns'
            self.dashboards_table = 'dashboards'
            self.metrics_table = 'metrics'
            
            # Inicializar estruturas
            self._init_bigquery()
            
            logger.info("✅ BigQuery + Firestore inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar BigQuery/Firestore: {e}")
            raise
    
    def _init_bigquery(self):
        """Inicializar dataset e tabelas no BigQuery"""
        try:
            # Criar dataset se não existir
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            try:
                self.bq_client.get_dataset(dataset_ref)
                logger.info(f"✅ Dataset {dataset_ref} já existe")
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = self.bq_client.create_dataset(dataset, timeout=30)
                logger.info(f"✅ Dataset {dataset_ref} criado")
            
            # Criar tabela de campanhas
            campaigns_schema = [
                bigquery.SchemaField("campaign_key", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("client", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("campaign_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("sheet_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("channel", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("kpi", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            self._create_table_if_not_exists(self.campaigns_table, campaigns_schema)
            
            # Criar tabela de dashboards
            dashboards_schema = [
                bigquery.SchemaField("dashboard_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("campaign_key", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("dashboard_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("dashboard_url", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_path", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            self._create_table_if_not_exists(self.dashboards_table, dashboards_schema)
            
            # Criar tabela de métricas
            metrics_schema = [
                bigquery.SchemaField("campaign_key", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("spend", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("impressions", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("clicks", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("video_completions", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("video_starts", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("ctr", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("vtr", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("cpm", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("cpc", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("cpv", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            self._create_table_if_not_exists(self.metrics_table, metrics_schema)
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar BigQuery: {e}")
            raise
    
    def _create_table_if_not_exists(self, table_name: str, schema: List[bigquery.SchemaField]):
        """Criar tabela se não existir"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        try:
            self.bq_client.get_table(table_ref)
            logger.info(f"✅ Tabela {table_ref} já existe")
        except Exception:
            table = bigquery.Table(table_ref, schema=schema)
            table = self.bq_client.create_table(table)
            logger.info(f"✅ Tabela {table_ref} criada")
    
    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, 
                     sheet_id: str, channel: str = None, kpi: str = None) -> bool:
        """Salvar campanha no BigQuery e Firestore"""
        try:
            now = datetime.now()
            
            # Salvar no BigQuery
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.campaigns_table}"
            rows_to_insert = [{
                "campaign_key": campaign_key,
                "client": client,
                "campaign_name": campaign_name,
                "sheet_id": sheet_id,
                "channel": channel,
                "kpi": kpi,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }]
            
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                logger.error(f"❌ Erro ao inserir no BigQuery: {errors}")
                return False
            
            # Salvar no Firestore (para consultas rápidas)
            doc_ref = self.fs_client.collection(self.campaigns_collection).document(campaign_key)
            doc_ref.set({
                "campaign_key": campaign_key,
                "client": client,
                "campaign_name": campaign_name,
                "sheet_id": sheet_id,
                "channel": channel,
                "kpi": kpi,
                "created_at": now,
                "updated_at": now,
            })
            
            logger.info(f"✅ Campanha {campaign_key} salva no BigQuery + Firestore")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar campanha: {e}")
            return False
    
    def save_dashboard(self, dashboard_id: str, campaign_key: str, dashboard_name: str,
                      dashboard_url: str, file_path: str, client: str = None, 
                      campaign_name: str = None, channel: str = None, kpi: str = None) -> bool:
        """Salvar dashboard no BigQuery e Firestore"""
        try:
            now = datetime.now()
            
            # Salvar no BigQuery
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.dashboards_table}"
            rows_to_insert = [{
                "dashboard_id": dashboard_id,
                "campaign_key": campaign_key,
                "dashboard_name": dashboard_name,
                "dashboard_url": dashboard_url,
                "file_path": file_path,
                "created_at": now.isoformat(),
            }]
            
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                logger.error(f"❌ Erro ao inserir dashboard no BigQuery: {errors}")
                return False
            
            # Salvar no Firestore com metadados completos
            doc_ref = self.fs_client.collection(self.dashboards_collection).document(dashboard_id)
            doc_ref.set({
                "dashboard_id": dashboard_id,
                "campaign_key": campaign_key,
                "dashboard_name": dashboard_name,
                "dashboard_url": dashboard_url,
                "file_path": file_path,
                "client": client or "N/A",
                "campaign_name": campaign_name or "N/A",
                "channel": channel or "N/A",
                "kpi": kpi or "N/A",
                "created_at": now,
            })
            
            logger.info(f"✅ Dashboard {dashboard_id} salvo no BigQuery + Firestore")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dashboard: {e}")
            return False
    
    def save_metrics(self, campaign_key: str, daily_data: List[Dict[str, Any]]) -> bool:
        """Salvar métricas diárias no BigQuery"""
        try:
            if not daily_data:
                return True
            
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.metrics_table}"
            rows_to_insert = []
            
            for row in daily_data:
                rows_to_insert.append({
                    "campaign_key": campaign_key,
                    "date": row.get('date'),
                    "spend": float(row.get('spend', 0)),
                    "impressions": int(row.get('impressions', 0)),
                    "clicks": int(row.get('clicks', 0)),
                    "video_completions": int(row.get('video_completions', 0)),
                    "video_starts": int(row.get('video_starts', 0)),
                    "ctr": float(row.get('ctr', 0)),
                    "vtr": float(row.get('vtr', 0)),
                    "cpm": float(row.get('cpm', 0)),
                    "cpc": float(row.get('cpc', 0)),
                    "cpv": float(row.get('cpv', 0)),
                    "created_at": datetime.now().isoformat(),
                })
            
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                logger.error(f"❌ Erro ao inserir métricas no BigQuery: {errors}")
                return False
            
            logger.info(f"✅ {len(rows_to_insert)} métricas salvas no BigQuery")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métricas: {e}")
            return False
    
    def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """Obter todas as campanhas do Firestore (rápido)"""
        try:
            campaigns = []
            docs = self.fs_client.collection(self.campaigns_collection).stream()
            
            for doc in docs:
                data = doc.to_dict()
                campaigns.append({
                    "campaign_key": data.get('campaign_key'),
                    "client": data.get('client'),
                    "campaign_name": data.get('campaign_name'),
                    "sheet_id": data.get('sheet_id'),
                    "channel": data.get('channel'),
                    "kpi": data.get('kpi'),
                    "created_at": data.get('created_at'),
                    "updated_at": data.get('updated_at'),
                })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanhas: {e}")
            return []
    
    def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """Obter todos os dashboards do Firestore (rápido)"""
        try:
            dashboards = []
            docs = self.fs_client.collection(self.dashboards_collection).stream()
            
            for doc in docs:
                data = doc.to_dict()
                dashboards.append({
                    "dashboard_id": data.get('dashboard_id'),
                    "campaign_key": data.get('campaign_key'),
                    "dashboard_name": data.get('dashboard_name'),
                    "dashboard_url": data.get('dashboard_url'),
                    "file_path": data.get('file_path'),
                    "created_at": data.get('created_at'),
                })
            
            return dashboards
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter dashboards: {e}")
            return []
    
    def get_persistence_status(self) -> Dict[str, Any]:
        """Obter status da persistência BigQuery + Firestore"""
        try:
            campaigns = self.get_all_campaigns()
            dashboards = self.get_all_dashboards()
            
            # Calcular tamanho total no BigQuery
            query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    SUM(size_bytes) as total_bytes
                FROM `{self.project_id}.{self.dataset_id}.__TABLES__`
            """
            query_job = self.bq_client.query(query)
            results = list(query_job.result())
            
            total_size = results[0].total_bytes if results else 0
            
            return {
                "bigquery_available": True,
                "firestore_available": True,
                "campaigns_count": len(campaigns),
                "dashboards_count": len(dashboards),
                "total_size_bytes": total_size,
                "last_updated": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status de persistência: {e}")
            return {
                "bigquery_available": False,
                "firestore_available": False,
                "error": str(e),
            }

if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    
    manager = BigQueryFirestoreManager()
    
    # Testar salvamento de campanha
    success = manager.save_campaign(
        campaign_key="teste_bq_fs",
        client="Cliente Teste",
        campaign_name="Campanha Teste BigQuery",
        sheet_id="1234567890",
        channel="Netflix",
        kpi="CPV"
    )
    
    print(f"✅ Teste de salvamento: {'Sucesso' if success else 'Falhou'}")
    
    # Testar status
    status = manager.get_persistence_status()
    print(f"📊 Status: {json.dumps(status, indent=2)}")

