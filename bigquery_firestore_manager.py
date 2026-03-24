#!/usr/bin/env python3
"""
Sistema de Persistência Definitiva - BigQuery + Firestore
Implementação para substituir SQLite + GCS
"""

import os
import json
import logging
import re
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.cloud import bigquery
from google.cloud import firestore
from werkzeug.security import check_password_hash, generate_password_hash

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
                self.clients_collection = 'clients_staging'
                self.users_collection = 'users_staging'
                logger.info("🧪 Usando ambiente STAGING")
            elif self.environment == 'hml':
                self.dataset_id = 'south_media_dashboards_hml'
                self.campaigns_collection = 'campaigns_hml'
                self.dashboards_collection = 'dashboards_hml'
                self.clients_collection = 'clients_hml'
                self.users_collection = 'users_hml'
                logger.info("🔬 Usando ambiente HOMOLOGAÇÃO (HML)")
            else:
                self.dataset_id = 'south_media_dashboards'
                self.campaigns_collection = 'campaigns'
                self.dashboards_collection = 'dashboards'
                self.clients_collection = 'clients'
                self.users_collection = 'users'
                logger.info("🚀 Usando ambiente PRODUCTION")
            
            # Coleções de clientes e usuários (compartilhadas por ambiente)
            self.clients_collection = 'clients'
            self.client_users_collection = 'client_users'
            
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
    
    # --- Clientes e vínculo de dashboards ---
    def create_client(self, name: str, slug: str = None) -> Optional[str]:
        """Criar cliente. Retorna client_id."""
        try:
            import uuid
            client_id = slug or str(uuid.uuid4())[:8]
            client_id = "".join(c for c in client_id if c.isalnum() or c in "-_").lower() or str(uuid.uuid4())[:8]
            doc_ref = self.fs_client.collection(self.clients_collection).document(client_id)
            if doc_ref.get().exists:
                client_id = f"{client_id}_{str(uuid.uuid4())[:4]}"
                doc_ref = self.fs_client.collection(self.clients_collection).document(client_id)
            now = datetime.now()
            doc_ref.set({
                "client_id": client_id,
                "name": name,
                "slug": client_id,
                "created_at": now,
                "updated_at": now,
            })
            logger.info(f"✅ Cliente criado: {client_id}")
            return client_id
        except Exception as e:
            logger.error(f"❌ Erro ao criar cliente: {e}")
            return None
    
    def list_clients(self) -> List[Dict[str, Any]]:
        """Listar todos os clientes."""
        try:
            out = []
            for doc in self.fs_client.collection(self.clients_collection).stream():
                d = doc.to_dict()
                d["client_id"] = doc.id
                out.append(d)
            return out
        except Exception as e:
            logger.error(f"❌ Erro ao listar clientes: {e}")
            return []
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Obter um cliente por ID."""
        try:
            doc = self.fs_client.collection(self.clients_collection).document(client_id).get()
            if not doc.exists:
                return None
            d = doc.to_dict()
            d["client_id"] = doc.id
            return d
        except Exception as e:
            logger.error(f"❌ Erro ao obter cliente: {e}")
            return None
    
    def update_client(self, client_id: str, name: str = None, slug: str = None) -> bool:
        """Atualizar cliente."""
        try:
            ref = self.fs_client.collection(self.clients_collection).document(client_id)
            if not ref.get().exists:
                return False
            data = {"updated_at": datetime.now()}
            if name is not None:
                data["name"] = name
            if slug is not None:
                data["slug"] = slug
            ref.update(data)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar cliente: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Remover cliente (não remove vínculos de dashboard; opcionalmente desvincula)."""
        try:
            self.fs_client.collection(self.clients_collection).document(client_id).delete()
            logger.info(f"✅ Cliente removido: {client_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover cliente: {e}")
            return False
    
    def add_client_user(self, client_id: str, email: str, name: str = None, role: str = "viewer", password: str = None) -> Optional[str]:
        """Adicionar usuário ao cliente. Retorna user_id."""
        try:
            import uuid
            user_id = str(uuid.uuid4())[:12]
            ref = self.fs_client.collection(self.client_users_collection).document(user_id)
            now = datetime.now()
            payload = {
                "client_id": client_id,
                "email": email.strip().lower(),
                "name": name or "",
                "role": role,
                "status": "active",
                "created_at": now,
                "updated_at": now,
            }
            if password:
                payload["password_hash"] = generate_password_hash(password)
            ref.set(payload)
            return user_id
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar usuário: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Buscar usuário (client_users) por e-mail."""
        try:
            email_norm = (email or "").strip().lower()
            if not email_norm:
                return None

            query = (
                self.fs_client
                .collection(self.client_users_collection)
                .where("email", "==", email_norm)
                .limit(1)
                .stream()
            )
            for doc in query:
                data = doc.to_dict() or {}
                data["user_id"] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário por e-mail: {e}")
            return None

    def verify_user_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Validar credenciais de usuário (hash + fallback legado em texto plano)."""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None

            if user.get("status", "active") != "active":
                return None

            password_hash = user.get("password_hash")
            password_plain = user.get("password")
            is_valid = False

            if password_hash:
                is_valid = check_password_hash(password_hash, password or "")
            elif password_plain is not None:
                # Compatibilidade com usuários antigos em texto plano
                is_valid = str(password_plain) == str(password or "")
                if is_valid:
                    # Migrar automaticamente para hash
                    self.fs_client.collection(self.client_users_collection).document(user["user_id"]).update({
                        "password_hash": generate_password_hash(password or ""),
                        "updated_at": datetime.now(),
                    })

            if not is_valid:
                return None

            # Atualizar último login
            self.fs_client.collection(self.client_users_collection).document(user["user_id"]).update({
                "last_login": datetime.now(),
                "updated_at": datetime.now(),
            })
            return user
        except Exception as e:
            logger.error(f"❌ Erro ao verificar credenciais: {e}")
            return None

    def ensure_superadmin_user(self, email: str, password: str, name: str = None) -> Optional[str]:
        """Criar/atualizar usuário superadmin."""
        try:
            import uuid
            email_norm = (email or "").strip().lower()
            if not email_norm or not password:
                return None

            existing = self.get_user_by_email(email_norm)
            now = datetime.now()
            payload = {
                "email": email_norm,
                "name": name or email_norm,
                "role": "super_admin",
                "status": "active",
                "password_hash": generate_password_hash(password),
                "updated_at": now,
            }

            if existing:
                # Superadmin não deve ficar preso a client_id
                payload["client_id"] = None
                self.fs_client.collection(self.client_users_collection).document(existing["user_id"]).set(payload, merge=True)
                return existing["user_id"]

            user_id = str(uuid.uuid4())[:12]
            payload.update({
                "client_id": None,
                "created_at": now,
            })
            self.fs_client.collection(self.client_users_collection).document(user_id).set(payload)
            return user_id
        except Exception as e:
            logger.error(f"❌ Erro ao garantir superadmin {email}: {e}")
            return None

    def get_dashboard(self, campaign_key: str) -> Optional[Dict[str, Any]]:
        """Buscar dashboard por campaign_key (id do documento)."""
        try:
            doc = self.fs_client.collection(self.dashboards_collection).document(campaign_key).get()
            if not doc.exists:
                return None
            data = doc.to_dict() or {}
            data["campaign_key"] = doc.id
            return data
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dashboard {campaign_key}: {e}")
            return None
    
    def list_client_users(self, client_id: str) -> List[Dict[str, Any]]:
        """Listar usuários do cliente."""
        try:
            out = []
            for doc in self.fs_client.collection(self.client_users_collection).where("client_id", "==", client_id).stream():
                d = doc.to_dict()
                d["user_id"] = doc.id
                out.append(d)
            return out
        except Exception as e:
            logger.error(f"❌ Erro ao listar usuários do cliente: {e}")
            return []
    
    def remove_client_user(self, user_id: str) -> bool:
        """Remover usuário do cliente."""
        try:
            self.fs_client.collection(self.client_users_collection).document(user_id).delete()
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover usuário: {e}")
            return False

    def list_all_users(self) -> List[Dict[str, Any]]:
        """Listar todos os usuários (superadmin + clientes)."""
        try:
            out = []
            for doc in self.fs_client.collection(self.client_users_collection).stream():
                d = doc.to_dict() or {}
                d["user_id"] = doc.id
                out.append(d)
            return out
        except Exception as e:
            logger.error(f"❌ Erro ao listar usuários: {e}")
            return []

    def update_user_role(self, user_id: str, role: str) -> bool:
        """Atualizar role de um usuário."""
        try:
            ref = self.fs_client.collection(self.client_users_collection).document(user_id)
            if not ref.get().exists:
                return False
            ref.update({
                "role": role,
                "updated_at": datetime.now(),
            })
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar role do usuário: {e}")
            return False

    def reset_user_password(self, user_id: str, new_password: str) -> bool:
        """Resetar senha de usuário."""
        try:
            ref = self.fs_client.collection(self.client_users_collection).document(user_id)
            if not ref.get().exists:
                return False
            ref.update({
                "password_hash": generate_password_hash(new_password),
                "updated_at": datetime.now(),
            })
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao resetar senha do usuário: {e}")
            return False
    
    def set_dashboard_client(self, campaign_key: str, client_id: Optional[str]) -> bool:
        """Vincular ou desvincular dashboard ao cliente. client_id=None para remover vínculo."""
        try:
            ref = self.fs_client.collection(self.dashboards_collection).document(campaign_key)
            if not ref.get().exists:
                return False
            if client_id is None:
                ref.update({u"client_id": firestore.DELETE_FIELD})
            else:
                ref.update({"client_id": client_id, "updated_at": datetime.now()})
            logger.info(f"✅ Dashboard {campaign_key} vinculado ao cliente: {client_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao vincular dashboard: {e}")
            return False
    
    def get_dashboards_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        """Listar dashboards vinculados ao cliente."""
        try:
            out = []
            for doc in self.fs_client.collection(self.dashboards_collection).where("client_id", "==", client_id).stream():
                data = doc.to_dict()
                data["campaign_key"] = doc.id
                out.append(data)
            return out
        except Exception as e:
            logger.error(f"❌ Erro ao listar dashboards do cliente: {e}")
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

    # ======================
    # Multi-tenant auth/client helpers
    # ======================
    def _slugify(self, value: str) -> str:
        raw = (value or "").strip().lower()
        raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
        return raw or f"client-{uuid.uuid4().hex[:8]}"

    def _normalize_email(self, email: str) -> str:
        return (email or "").strip().lower()

    def _query_first_by_field(self, collection_name: str, field_name: str, value: str):
        query = self.fs_client.collection(collection_name).where(field_name, "==", value).limit(1)
        docs = list(query.stream())
        return docs[0] if docs else None

    def _user_collections(self) -> List[str]:
        # Backward compatibility for legacy environments/data migrations.
        base = [self.users_collection, "users", "users_hml", "users_staging"]
        deduped = []
        for name in base:
            if name not in deduped:
                deduped.append(name)
        return deduped

    def _check_password_compat(self, stored_hash: str, password: str) -> bool:
        if not stored_hash:
            return False

        # Werkzeug hashes (pbkdf2/scrypt) from current stack.
        try:
            if check_password_hash(stored_hash, password):
                return True
        except Exception:
            pass

        # Legacy plaintext or deterministic hash fallback.
        if stored_hash == password:
            return True
        if hashlib.sha256(password.encode("utf-8")).hexdigest() == stored_hash:
            return True

        # Optional bcrypt fallback for legacy rows.
        try:
            import bcrypt  # type: ignore
            if stored_hash.startswith("$2") and bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                return True
        except Exception:
            pass

        return False

    def ensure_superadmin_user(self, email: str, password: str, name: str = "Super Admin") -> str:
        email_norm = self._normalize_email(email)
        existing = self._query_first_by_field(self.users_collection, "email", email_norm)
        now = datetime.now()
        password_hash = generate_password_hash(password)

        if existing:
            user_id = existing.id
            self.fs_client.collection(self.users_collection).document(user_id).set({
                "email": email_norm,
                "name": name or "Super Admin",
                "role": "super_admin",
                "password_hash": password_hash,
                "updated_at": now,
            }, merge=True)
            return user_id

        user_id = f"user_{uuid.uuid4().hex[:16]}"
        self.fs_client.collection(self.users_collection).document(user_id).set({
            "user_id": user_id,
            "email": email_norm,
            "name": name or "Super Admin",
            "role": "super_admin",
            "client_id": None,
            "password_hash": password_hash,
            "created_at": now,
            "updated_at": now,
        })
        return user_id

    def verify_user_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        email_norm = self._normalize_email(email)
        for collection_name in self._user_collections():
            doc = self._query_first_by_field(collection_name, "email", email_norm)
            if not doc:
                continue

            user = doc.to_dict() or {}
            stored_hash = user.get("password_hash") or ""
            stored_plain = user.get("password") or ""
            valid = self._check_password_compat(stored_hash, password)
            if not valid and stored_plain:
                valid = stored_plain == password
            if not valid:
                continue

            return {
                "user_id": user.get("user_id") or doc.id,
                "email": user.get("email") or email_norm,
                "name": user.get("name") or "",
                "role": user.get("role") or "viewer",
                "client_id": user.get("client_id"),
            }
        return None

    def reset_user_password(self, user_id: str, new_password: str) -> bool:
        try:
            self.fs_client.collection(self.users_collection).document(user_id).set({
                "password_hash": generate_password_hash(new_password),
                "updated_at": datetime.now(),
            }, merge=True)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao resetar senha ({user_id}): {e}")
            return False

    def update_user_role(self, user_id: str, role: str) -> bool:
        try:
            self.fs_client.collection(self.users_collection).document(user_id).set({
                "role": role,
                "updated_at": datetime.now(),
            }, merge=True)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar role ({user_id}): {e}")
            return False

    def list_all_users(self) -> List[Dict[str, Any]]:
        users = []
        try:
            docs = self.fs_client.collection(self.users_collection).stream()
            for doc in docs:
                u = doc.to_dict() or {}
                users.append({
                    "user_id": u.get("user_id") or doc.id,
                    "email": u.get("email") or "",
                    "name": u.get("name") or "",
                    "role": u.get("role") or "viewer",
                    "client_id": u.get("client_id"),
                })
            users.sort(key=lambda x: (x.get("email") or ""))
        except Exception as e:
            logger.error(f"❌ Erro ao listar usuários: {e}")
        return users

    def create_client(self, name: str, slug: Optional[str] = None) -> str:
        client_id = self._slugify(slug or name)
        now = datetime.now()
        doc_ref = self.fs_client.collection(self.clients_collection).document(client_id)
        if doc_ref.get().exists:
            client_id = f"{client_id}-{uuid.uuid4().hex[:6]}"
            doc_ref = self.fs_client.collection(self.clients_collection).document(client_id)
        doc_ref.set({
            "client_id": client_id,
            "name": (name or "").strip(),
            "slug": client_id,
            "created_at": now,
            "updated_at": now,
        })
        return client_id

    def list_clients(self) -> List[Dict[str, Any]]:
        clients = []
        try:
            docs = self.fs_client.collection(self.clients_collection).stream()
            for doc in docs:
                c = doc.to_dict() or {}
                clients.append({
                    "client_id": c.get("client_id") or doc.id,
                    "name": c.get("name") or c.get("client_id") or doc.id,
                    "slug": c.get("slug") or c.get("client_id") or doc.id,
                })
            clients.sort(key=lambda x: (x.get("name") or "").lower())
        except Exception as e:
            logger.error(f"❌ Erro ao listar clientes: {e}")
        return clients

    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        doc = self.fs_client.collection(self.clients_collection).document(client_id).get()
        if not doc.exists:
            return None
        c = doc.to_dict() or {}
        return {
            "client_id": c.get("client_id") or doc.id,
            "name": c.get("name") or c.get("client_id") or doc.id,
            "slug": c.get("slug") or c.get("client_id") or doc.id,
        }

    def update_client(self, client_id: str, name: Optional[str] = None, slug: Optional[str] = None) -> bool:
        try:
            payload = {"updated_at": datetime.now()}
            if name is not None:
                payload["name"] = name
            if slug is not None:
                payload["slug"] = self._slugify(slug)
            self.fs_client.collection(self.clients_collection).document(client_id).set(payload, merge=True)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar cliente ({client_id}): {e}")
            return False

    def delete_client(self, client_id: str) -> bool:
        try:
            self.fs_client.collection(self.clients_collection).document(client_id).delete()
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao excluir cliente ({client_id}): {e}")
            return False

    def list_client_users(self, client_id: str) -> List[Dict[str, Any]]:
        users = []
        try:
            docs = self.fs_client.collection(self.users_collection).where("client_id", "==", client_id).stream()
            for doc in docs:
                u = doc.to_dict() or {}
                users.append({
                    "user_id": u.get("user_id") or doc.id,
                    "email": u.get("email") or "",
                    "name": u.get("name") or "",
                    "role": u.get("role") or "viewer",
                    "client_id": u.get("client_id"),
                })
            users.sort(key=lambda x: (x.get("email") or ""))
        except Exception as e:
            logger.error(f"❌ Erro ao listar usuários do cliente ({client_id}): {e}")
        return users

    def add_client_user(self, client_id: str, email: str, name: str = "", role: str = "viewer", password: str = "") -> str:
        email_norm = self._normalize_email(email)
        existing = self._query_first_by_field(self.users_collection, "email", email_norm)
        now = datetime.now()
        user_id = existing.id if existing else f"user_{uuid.uuid4().hex[:16]}"
        payload = {
            "user_id": user_id,
            "email": email_norm,
            "name": (name or "").strip(),
            "role": role or "viewer",
            "client_id": client_id,
            "updated_at": now,
        }
        if password:
            payload["password_hash"] = generate_password_hash(password)
        if not existing:
            payload["created_at"] = now
        self.fs_client.collection(self.users_collection).document(user_id).set(payload, merge=True)
        return user_id

    def remove_client_user(self, user_id: str) -> bool:
        try:
            self.fs_client.collection(self.users_collection).document(user_id).delete()
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao remover usuário ({user_id}): {e}")
            return False

    def set_dashboard_client(self, campaign_key: str, client_id: str) -> bool:
        try:
            now = datetime.now()
            self.fs_client.collection(self.dashboards_collection).document(campaign_key).set({
                "client_id": client_id,
                "updated_at": now,
            }, merge=True)
            self.fs_client.collection(self.campaigns_collection).document(campaign_key).set({
                "client_id": client_id,
                "updated_at": now,
            }, merge=True)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao vincular dashboard ({campaign_key}) ao cliente ({client_id}): {e}")
            return False

    def get_dashboards_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        dashboards = []
        try:
            docs = self.fs_client.collection(self.dashboards_collection).where("client_id", "==", client_id).stream()
            for doc in docs:
                d = doc.to_dict() or {}
                dashboards.append({
                    "campaign_key": d.get("campaign_key") or doc.id,
                    "dashboard_name": d.get("dashboard_name") or d.get("campaign_name") or doc.id,
                    "campaign_name": d.get("campaign_name") or d.get("dashboard_name"),
                    "channel": d.get("channel"),
                    "kpi": d.get("kpi"),
                    "client_id": d.get("client_id"),
                    "created_at": d.get("created_at"),
                    "updated_at": d.get("updated_at"),
                    "start_date": d.get("start_date"),
                    "end_date": d.get("end_date"),
                    "investment": d.get("investment"),
                    # Budget utilizado (mini-dashboards do portal) — pode vir do Firestore ou ser preenchido na API
                    "budget_used": d.get("budget_used")
                        or d.get("total_spend")
                        or d.get("used_budget")
                        or d.get("Budget Utilizado (R$)"),
                    "total_spend": d.get("total_spend") or d.get("budget_used"),
                    "impressions": d.get("impressions"),
                    "kpi_target": d.get("kpi_target"),
                })
            dashboards.sort(key=lambda x: (x.get("dashboard_name") or "").lower())
        except Exception as e:
            logger.error(f"❌ Erro ao listar dashboards do cliente ({client_id}): {e}")
        return dashboards

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

