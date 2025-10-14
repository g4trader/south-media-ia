#!/usr/bin/env python3
"""
MVP Dashboard Builder para Google Cloud Run - Versão Simplificada
Foca apenas na geração de dashboards, sem lógica de commit
"""

import os
import sys
import logging
import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar paths
sys.path.append(os.path.dirname(__file__))

# Importar módulos do MVP
from real_google_sheets_extractor import RealGoogleSheetsExtractor
from google_sheets_service import GoogleSheetsService
from config import get_api_endpoint, get_git_manager_url, is_production, is_development, get_port, is_debug
from bigquery_firestore_manager import BigQueryFirestoreManager

app = Flask(__name__)
CORS(app)

# Configuração do ambiente
PORT = get_port()
DEBUG = is_debug()

# Inicializar BigQuery + Firestore Manager
try:
    bq_fs_manager = BigQueryFirestoreManager()
    logger.info("✅ BigQuery + Firestore Manager inicializado")
except Exception as e:
    logger.warning(f"⚠️ BigQuery + Firestore não disponível: {e}")
    bq_fs_manager = None

class CampaignConfig:
    """Configuração de uma campanha"""
    def __init__(self, campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: Optional[str] = None, kpi: Optional[str] = None, tabs: Optional[Dict] = None):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign_name = campaign_name
        self.sheet_id = sheet_id
        self.channel = channel or "Video Programática"
        self.kpi = kpi or "CPV"
        self.tabs = tabs or {
            'report': 'Report',
            'contract': 'Informações de contrato',
            'publishers': 'Lista de publishers',
            'strategies': 'Estratégias'
        }

class CloudRunDatabaseManager:
    """Gerenciador de banco para Cloud Run com persistência robusta"""
    
    def __init__(self):
        # Usar diretório persistente do Cloud Run
        self.db_path = os.path.join('/tmp', 'campaigns.db')
        self.gcs_bucket = 'south-media-ia-database-452311'
        self.gcs_db_path = 'campaigns.db'
        self.backup_path = f"{self.db_path}.backup"
        
        # Carregar do GCS primeiro, depois inicializar se necessário
        self._load_from_gcs()
        self.init_database()
        
        # Salvar backup inicial
        self._save_to_gcs()
    
    def init_database(self):
        """Inicializar banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_key TEXT PRIMARY KEY,
                    client TEXT NOT NULL,
                    campaign_name TEXT NOT NULL,
                    sheet_id TEXT NOT NULL,
                    channel TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de dados inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
    
    def _load_from_gcs(self):
        """Carregar banco de dados do Google Cloud Storage com fallback"""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_db_path)
            
            if blob.exists():
                # Fazer download para arquivo temporário primeiro
                temp_path = f"{self.db_path}.temp"
                blob.download_to_filename(temp_path)
                
                # Verificar se o arquivo é válido
                try:
                    test_conn = sqlite3.connect(temp_path)
                    test_cursor = test_conn.cursor()
                    test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = test_cursor.fetchall()
                    test_conn.close()
                    
                    if tables:  # Se tem tabelas, é válido
                        import shutil
                        shutil.move(temp_path, self.db_path)
                        logger.info("✅ Banco de dados carregado do GCS com sucesso")
                        
                        # Contar registros
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM campaigns")
                        count = cursor.fetchone()[0]
                        conn.close()
                        logger.info(f"📊 Banco carregado com {count} campanhas")
                    else:
                        logger.warning("⚠️ Arquivo do GCS está vazio, criando novo")
                        os.remove(temp_path)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Arquivo do GCS corrompido: {e}, criando novo")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                logger.info("📝 Banco de dados não encontrado no GCS, criando novo")
                
        except ImportError as e:
            logger.warning(f"⚠️ Google Cloud Storage não disponível: {e}")
            logger.info("📝 Continuando sem persistência GCS")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar do GCS: {e}")
            logger.info("📝 Continuando com banco local")
    
    def _save_to_gcs(self):
        """Salvar banco de dados no Google Cloud Storage com backup"""
        try:
            from google.cloud import storage
            
            # Verificar se o arquivo existe
            if not os.path.exists(self.db_path):
                logger.warning("⚠️ Arquivo de banco não existe, não é possível salvar")
                return False
            
            # Fazer backup local
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
            
            # Upload para GCS
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_db_path)
            
            # Upload com retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    blob.upload_from_filename(self.db_path)
                    
                    # Verificar se o upload foi bem-sucedido
                    if blob.exists():
                        # Obter metadados
                        blob.reload()
                        size = blob.size
                        logger.info(f"✅ Banco de dados salvo no GCS ({size:,} bytes)")
                        
                        # Contar registros salvos
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM campaigns")
                        count = cursor.fetchone()[0]
                        conn.close()
                        logger.info(f"📊 {count} campanhas persistidas")
                        return True
                    else:
                        raise Exception("Upload não confirmado")
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Tentativa {attempt + 1} falhou: {e}, tentando novamente...")
                        time.sleep(1)
                    else:
                        raise e
                        
        except ImportError as e:
            logger.warning(f"⚠️ Google Cloud Storage não disponível: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar no GCS: {e}")
            logger.info("💾 Backup local mantido em caso de problemas")
        
        return False

    def get_persistence_status(self):
        """Verificar status da persistência"""
        status = {
            "local_db_exists": os.path.exists(self.db_path),
            "backup_exists": os.path.exists(self.backup_path),
            "gcs_available": False,
            "gcs_file_exists": False,
            "local_campaigns": 0,
            "gcs_size": 0
        }
        
        try:
            # Contar campanhas locais
            if status["local_db_exists"]:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM campaigns")
                status["local_campaigns"] = cursor.fetchone()[0]
                conn.close()
            
            # Verificar GCS
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_db_path)
            
            status["gcs_available"] = True
            status["gcs_file_exists"] = blob.exists()
            
            if blob.exists():
                blob.reload()
                status["gcs_size"] = blob.size
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar persistência: {e}")
        
        return status

    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: Optional[str] = None, kpi: Optional[str] = None) -> bool:
        """Salvar ou atualizar uma campanha no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Adicionar coluna kpi se não existir
            try:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN kpi TEXT')
            except:
                pass  # Coluna já existe
            
            cursor.execute('''
                INSERT OR REPLACE INTO campaigns 
                (campaign_key, client, campaign_name, sheet_id, channel, kpi, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (campaign_key, client, campaign_name, sheet_id, channel, kpi))
            
            conn.commit()
            conn.close()
            
            # Salvar no GCS após commit local
            gcs_success = self._save_to_gcs()
            
            logger.info(f"✅ Campanha salva: {campaign_key}")
            if gcs_success:
                logger.info("💾 Dados persistidos no GCS com sucesso")
            else:
                logger.warning("⚠️ Dados salvos localmente, mas falha na persistência GCS")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar campanha: {e}")
            return False

    def get_campaign(self, campaign_key: str) -> Optional[Dict[str, Any]]:
        """Obter uma campanha do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT campaign_key, client, campaign_name, sheet_id, channel, kpi, created_at, updated_at
                FROM campaigns WHERE campaign_key = ?
            ''', (campaign_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'campaign_key': result[0],
                    'client': result[1],
                    'campaign_name': result[2],
                    'sheet_id': result[3],
                    'channel': result[4],
                    'kpi': result[5],
                    'created_at': result[6],
                    'updated_at': result[7]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanha: {e}")
            return None

    def list_campaigns(self) -> list:
        """Listar todas as campanhas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT campaign_key, client, campaign_name, sheet_id, channel, created_at, updated_at
                FROM campaigns ORDER BY updated_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            campaigns = []
            for result in results:
                campaigns.append({
                    'campaign_key': result[0],
                    'client': result[1],
                    'campaign_name': result[2],
                    'sheet_id': result[3],
                    'channel': result[4],
                    'created_at': result[5],
                    'updated_at': result[6]
                })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar campanhas: {e}")
            return []

# Inicializar gerenciador de banco de dados
db_manager = CloudRunDatabaseManager()

# Sistema de backup automático
import threading
import time

def backup_worker():
    """Worker para backup automático do banco"""
    while True:
        try:
            # Backup a cada 5 minutos
            time.sleep(300)
            
            # Verificar se há campanhas para fazer backup
            status = db_manager.get_persistence_status()
            if status["local_campaigns"] > 0:
                logger.info("🔄 Executando backup automático...")
                success = db_manager._save_to_gcs()
                if success:
                    logger.info("✅ Backup automático concluído")
                else:
                    logger.warning("⚠️ Falha no backup automático")
        except Exception as e:
            logger.error(f"❌ Erro no backup automático: {e}")

# Sistema de sincronização de dashboards
def sync_dashboards_from_gcs():
    """Sincronizar dashboards do GCS para o sistema local"""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket('south-media-ia-database-452311')
        
        # Listar todos os dashboards no GCS
        blobs = bucket.list_blobs(prefix='dashboards/')
        dashboard_count = 0
        
        for blob in blobs:
            if blob.name.endswith('.html') and blob.name.startswith('dashboards/dash_'):
                filename = blob.name.split('/')[-1]  # Extrair apenas o nome do arquivo
                local_path = os.path.join('static', filename)
                
                # Se não existir localmente, baixar do GCS
                if not os.path.exists(local_path):
                    os.makedirs('static', exist_ok=True)
                    content = blob.download_as_text()
                    
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    dashboard_count += 1
                    logger.info(f"📥 Dashboard sincronizado: {filename}")
        
        if dashboard_count > 0:
            logger.info(f"🔄 {dashboard_count} dashboards sincronizados do GCS")
        else:
            logger.info("✅ Todos os dashboards já estão sincronizados")
            
    except Exception as e:
        logger.warning(f"⚠️ Erro ao sincronizar dashboards do GCS: {e}")

# Sincronizar dashboards na inicialização
sync_dashboards_from_gcs()

# Iniciar thread de backup em produção
if is_production():
    backup_thread = threading.Thread(target=backup_worker, daemon=True)
    backup_thread.start()
    logger.info("🔄 Sistema de backup automático iniciado")

def generate_campaign_key(client: str, campaign_name: str) -> str:
    """Gerar chave única para a campanha"""
    import re
    from unidecode import unidecode
    
    # Normalizar texto
    client_clean = unidecode(client.lower())
    campaign_clean = unidecode(campaign_name.lower())
    
    # Remover caracteres especiais e espaços
    client_clean = re.sub(r'[^a-z0-9]', '_', client_clean)
    campaign_clean = re.sub(r'[^a-z0-9]', '_', campaign_clean)
    
    # Remover underscores duplos e no início/fim
    client_clean = re.sub(r'_+', '_', client_clean).strip('_')
    campaign_clean = re.sub(r'_+', '_', campaign_clean).strip('_')
    
    return f"{client_clean}_{campaign_clean}"

def generate_dashboard(campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: str = "Video Programática", kpi: str = "CPV") -> Dict[str, Any]:
    """Gerar dashboard a partir do template"""
    try:
        # Determinar template baseado no KPI
        template_path = 'static/dash_generic_template.html'
        
        # Selecionar template baseado no KPI
        if kpi.upper() == 'CPM':
            template_path = 'static/dash_remarketing_cpm_template.html'
            logger.info(f"🎯 Usando template CPM para: {campaign_name} (KPI: {kpi})")
        elif kpi.upper() == 'CPV':
            template_path = 'static/dash_generic_template.html'
            logger.info(f"🎯 Usando template CPV para: {campaign_name} (KPI: {kpi})")
        elif kpi.upper() == 'CPE':
            template_path = 'static/dash_generic_cpe_template.html'
            logger.info(f"🎯 Usando template CPE para: {campaign_name} (KPI: {kpi})")
        else:
            logger.info(f"🎯 Usando template genérico para: {campaign_name} (KPI: {kpi})")
        
        if not os.path.exists(template_path):
            raise Exception(f"Template não encontrado: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Substituir placeholders
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        dashboard_content = dashboard_content.replace('{{CLIENT_NAME}}', client)
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        dashboard_content = dashboard_content.replace('{{API_ENDPOINT}}', get_api_endpoint())
        
        # Substituir placeholders adicionais
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard de performance para a campanha {campaign_name} do cliente {client}')
        dashboard_content = dashboard_content.replace('{{PRIMARY_CHANNEL}}', channel)
        
        # Dashboard será servido dinamicamente via /api/dashboard/{campaign_key}
        # Não precisamos mais salvar arquivos estáticos
        
        logger.info(f"✅ Dashboard configurado para: {campaign_key}")
        
        # Salvar no Google Cloud Storage (backup)
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket('south-media-ia-database-452311')
            
            # Upload do dashboard para GCS como backup
            dashboard_filename = f"dash_{campaign_key}.html"
            gcs_path = f"dashboards/{dashboard_filename}"
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(dashboard_content, content_type='text/html')
            
            logger.info(f"💾 Dashboard persistido no GCS: {gcs_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar dashboard no GCS: {e}")
        
        # Git Manager desativado para evitar instabilidade
        # Notificação ao Git Manager removida
        
        return {
            "success": True,
            "campaign_key": campaign_key,
            "dashboard_url": f"/api/dashboard/{campaign_key}",
            "dashboard_url_full": f"{get_api_endpoint()}/api/dashboard/{campaign_key}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/persistence-status', methods=['GET'])
def persistence_status():
    """Status da persistência BigQuery + Firestore"""
    try:
        if bq_fs_manager:
            status = bq_fs_manager.get_persistence_status()
            return jsonify({
                "success": True,
                "persistence_status": status,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Fallback para SQLite + GCS
            db_manager = CloudRunDatabaseManager()
            return jsonify({
                "success": True,
                "persistence_status": {
                    "gcs_available": True,
                    "local_db_exists": os.path.exists(db_manager.db_path),
                    "local_campaigns": len(db_manager.get_all_campaigns()),
                    "gcs_file_exists": db_manager._check_gcs_backup_exists(),
                    "gcs_size": db_manager._get_gcs_file_size() if db_manager._check_gcs_backup_exists() else 0,
                    "backup_exists": db_manager._check_gcs_backup_exists(),
                },
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"❌ Erro ao obter status de persistência: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "mvp-dashboard-builder",
        "timestamp": datetime.now().isoformat()
    })

# Endpoint persistence-status já definido acima

@app.route('/force-save', methods=['POST'])
def force_save():
    """Forçar salvamento do banco no GCS"""
    try:
        success = db_manager._save_to_gcs()
        if success:
            return jsonify({
                "success": True,
                "message": "Banco de dados salvo com sucesso no GCS",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "Falha ao salvar banco no GCS",
                "timestamp": datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"❌ Erro ao forçar salvamento: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/dashboard-status', methods=['GET'])
def dashboard_status():
    """Verificar status dos dashboards"""
    try:
        # Contar dashboards locais
        local_dashboards = []
        if os.path.exists('static'):
            for file in os.listdir('static'):
                if file.startswith('dash_') and file.endswith('.html'):
                    local_dashboards.append(file)
        
        # Contar dashboards no GCS
        gcs_dashboards = []
        gcs_count = 0
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket('south-media-ia-database-452311')
            
            blobs = bucket.list_blobs(prefix='dashboards/')
            for blob in blobs:
                if blob.name.endswith('.html') and blob.name.startswith('dashboards/dash_'):
                    filename = blob.name.split('/')[-1]
                    gcs_dashboards.append(filename)
                    gcs_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Erro ao listar dashboards no GCS: {e}")
        
        return jsonify({
            "success": True,
            "local_dashboards": {
                "count": len(local_dashboards),
                "files": local_dashboards
            },
            "gcs_dashboards": {
                "count": gcs_count,
                "files": gcs_dashboards
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status dos dashboards: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test-credentials', methods=['GET'])
def test_credentials():
    """Testar credenciais Google Sheets"""
    try:
        # Criar serviço Google Sheets
        service = GoogleSheetsService()
        
        # Testar conexão
        status = service.test_connection()
        
        if status == "connected":
            return jsonify({
                "success": True,
                "message": "Credenciais funcionando",
                "status": status
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Problema nas credenciais: {status}",
                "status": status
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar credenciais: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro nas credenciais: {str(e)}"
        }), 500

@app.route('/test-extractor', methods=['GET'])
def test_extractor():
    """Testar extrator específico"""
    try:
        # Configurar campanha de teste
        config = CampaignConfig(
            campaign_key='test_extractor',
            client='Copacol',
            campaign_name='Institucional 30s',
            sheet_id='1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8',
            tabs={
                'report': 'Report',
                'contract': 'Informações de contrato',
                'publishers': 'Lista de publishers',
                'strategies': 'Estratégias'
            }
        )
        
        # Criar extrator
        extractor = RealGoogleSheetsExtractor(config)
        
        # Verificar se o extrator está configurado
        is_configured = extractor.service is not None
        
        # Testar extração de contrato
        contract_data = extractor._extract_contract_data()
        
        return jsonify({
            "success": True,
            "message": "Extrator funcionando",
            "is_configured": is_configured,
            "contract_data": contract_data,
            "config_tabs": config.tabs
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar extrator: {e}")
        import traceback
        return jsonify({
            "success": False,
            "message": f"Erro no extrator: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/dash-generator-pro', methods=['GET'])
def dash_generator_pro():
    """Interface de teste do gerador"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador de Dashboards - Pro</title>
    <style>
        :root {
            --bg: #0F1023;
            --bg2: #16213E;
            --panel: #1A1A2E;
            --muted: #9CA3AF;
            --stroke: rgba(139,92,246,.28);
            --grad: linear-gradient(135deg,#8B5CF6,#EC4899);
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
            color: #fff;
            background: linear-gradient(135deg, var(--bg) 0%, var(--bg2) 50%, var(--panel) 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(26,26,46,.8);
            border: 1px solid var(--stroke);
            border-radius: 14px;
            padding: 2rem;
            backdrop-filter: blur(8px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo {
            width: 60px;
            height: 60px;
            border-radius: 15px;
            background: var(--grad);
            display: grid;
            place-items: center;
            font-weight: 700;
            font-size: 1.5rem;
            margin: 0 auto 1rem;
        }
        
        h1 {
            color: #8B5CF6;
            margin-bottom: 0.5rem;
            font-size: 2rem;
            font-weight: 800;
        }
        
        .subtitle {
            color: var(--muted);
            font-size: 1rem;
        }
        
        .persistence-badge {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(16,185,129,.15);
            border: 1px solid rgba(16,185,129,.3);
            border-radius: 8px;
            color: #10B981;
            font-weight: 600;
            font-size: 0.85rem;
            margin-top: 1rem;
        }
        
        .view-dashboards-btn {
            display: block;
            width: auto;
            padding: 0.6rem 1.5rem;
            margin: 1rem auto 0;
            background: rgba(59,130,246,.2);
            border: 1px solid rgba(59,130,246,.4);
            color: #3B82F6;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            text-align: center;
        }
        
        .view-dashboards-btn:hover {
            background: rgba(59,130,246,.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59,130,246,.25);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.82rem;
        }
        
        input, select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(148,163,184,.2);
            border-radius: 8px;
            background: rgba(255,255,255,.04);
            color: white;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #8B5CF6;
            box-shadow: 0 0 0 3px rgba(139,92,246,.1);
        }
        
        input[readonly] {
            background: rgba(255,255,255,.02);
            color: var(--muted);
        }
        
        small {
            color: var(--muted);
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
        }
        
        button {
            width: 100%;
            padding: 1rem;
            background: var(--grad);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(139,92,246,.35);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result {
            margin-top: 2rem;
            padding: 1.5rem;
            border-radius: 12px;
            display: none;
        }
        
        .success {
            background: rgba(16,185,129,.1);
            border: 1px solid rgba(16,185,129,.3);
            color: #10B981;
        }
        
        .error {
            background: rgba(239,68,68,.1);
            border: 1px solid rgba(239,68,68,.3);
            color: #EF4444;
        }
        
        .loading {
            background: rgba(59,130,246,.1);
            border: 1px solid rgba(59,130,246,.3);
            color: #3B82F6;
        }
        
        .result h3 {
            margin-bottom: 1rem;
            font-size: 1.25rem;
            font-weight: 700;
        }
        
        .result p {
            margin-bottom: 0.5rem;
        }
        
        .result a {
            color: #10B981;
            text-decoration: none;
            font-weight: 600;
        }
        
        .result a:hover {
            text-decoration: underline;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(139,92,246,.2);
            border: 1px solid rgba(139,92,246,.4);
            font-weight: 600;
            color: #8B5CF6;
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SM</div>
            <h1>Gerador de Dashboards</h1>
            <p class="subtitle">Sistema Profissional de Geração de Dashboards</p>
            <div class="persistence-badge">🎯 Persistência Definitiva - BigQuery + Firestore</div>
            <a href="/dashboards-list" class="view-dashboards-btn">📊 Ver Todos os Dashboards</a>
        </div>
        
        <form id="generatorForm">
        <div class="form-group">
            <label for="clientName">Cliente:</label>
            <input type="text" id="clientName" name="client" required>
        </div>
        
        <div class="form-group">
            <label for="campaignName">Nome da Campanha:</label>
            <input type="text" id="campaignName" name="campaign_name" required>
        </div>
        
        <div class="form-group">
            <label for="sheetUrl">URL da Planilha Google Sheets:</label>
            <input type="url" id="sheetUrl" name="sheet_url" placeholder="https://docs.google.com/spreadsheets/d/1ABC.../edit" required>
            <small>Cole a URL completa da planilha (o ID será extraído automaticamente)</small>
        </div>
        
        <div class="form-group">
            <label for="sheetId">ID da Planilha (Auto-extraído):</label>
            <input type="text" id="sheetId" name="sheet_id" readonly>
            <small>ID extraído automaticamente da URL</small>
        </div>
        
        <div class="form-group">
            <label for="channel">Canal:</label>
            <select id="channel" name="channel">
                <option value="Video Programática">Video Programática</option>
                <option value="Display Programática">Display Programática</option>
                <option value="Native Programática">Native Programática</option>
                <option value="YouTube">YouTube</option>
                <option value="TikTok">TikTok</option>
                <option value="Facebook">Facebook</option>
                <option value="Instagram">Instagram</option>
                <option value="Netflix">Netflix</option>
                <option value="Disney">Disney</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Pinterest">Pinterest</option>
                <option value="Spotify">Spotify</option>
                <option value="Geofence">Geofence</option>
                <option value="Waze">Waze</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="kpi">KPI Contratado:</label>
            <select id="kpi" name="kpi" required>
                <option value="CPV">CPV - Custo por View (Complete Views)</option>
                <option value="CPE">CPE - Custo por Escuta (Audio Listens)</option>
                <option value="CPM">CPM - Custo por Mil Impressões</option>
                <option value="CPC">CPC - Custo por Clique</option>
                <option value="CPA">CPA - Custo por Aquisição</option>
            </select>
            <small>Métrica principal contratada (define o layout do dashboard)</small>
        </div>
        
        <button type="submit" id="generateButton">🚀 Gerar Dashboard</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        // Função para extrair ID da planilha da URL
        function extractSheetId(url) {
            if (!url) return '';
            
            // Padrões de URL do Google Sheets
            const patterns = [
                /\\/spreadsheets\\/d\\/([a-zA-Z0-9-_]+)/,
                /\\/d\\/([a-zA-Z0-9-_]+)/,
                /id=([a-zA-Z0-9-_]+)/
            ];
            
            for (const pattern of patterns) {
                const match = url.match(pattern);
                if (match && match[1]) {
                    return match[1];
                }
            }
            
            return '';
        }
        
        // Event listener para extrair ID automaticamente
        document.getElementById('sheetUrl').addEventListener('input', function() {
            const url = this.value;
            const sheetId = extractSheetId(url);
            const sheetIdField = document.getElementById('sheetId');
            
            if (sheetId) {
                sheetIdField.value = sheetId;
                sheetIdField.style.color = '#28a745'; // Verde para sucesso
            } else {
                sheetIdField.value = '';
                sheetIdField.style.color = '#666';
            }
        });

        document.getElementById('generatorForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            const generateButton = document.getElementById('generateButton');
            
            // Mostrar loading
            resultDiv.innerHTML = '<div class="loading">🔄 Gerando dashboard...</div>';
            generateButton.disabled = true;
            
            try {
                const formData = new FormData(this);
                const data = Object.fromEntries(formData);
                
                const response = await fetch('/api/generate-dashboard', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="success">
                            <h3>✅ Dashboard Gerado com Sucesso!</h3>
                            <p><strong>Campanha:</strong> ${result.campaign_key}</p>
                            <p><strong>Nome:</strong> ${result.dashboard_name}</p>
                            <p><strong>URL:</strong> <a href="${result.dashboard_url}" target="_blank">${result.dashboard_url}</a></p>
                            <p><strong>Arquivo:</strong> ${result.file_path}</p>
                            <p><em>💡 O arquivo será commitado automaticamente pelo Git Manager em até 2 minutos.</em></p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error">
                            <h3>❌ Erro ao Gerar Dashboard</h3>
                            <p>${result.message}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="error">
                        <h3>❌ Erro de Conexão</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            } finally {
                generateButton.disabled = false;
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/api/generate-dashboard', methods=['POST'])
def generate_dashboard_endpoint():
    """Gerar dashboard via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        # Validar campos obrigatórios
        required_fields = ['client', 'campaign_name', 'sheet_id', 'kpi']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Campo obrigatório: {field}"}), 400
        
        client = data['client']
        campaign_name = data['campaign_name']
        sheet_id = data['sheet_id']
        channel = data.get('channel', 'Video Programática')
        kpi = data.get('kpi', 'CPV')
        
        # Gerar campaign_key automaticamente
        campaign_key = generate_campaign_key(client, campaign_name)
        
        # Salvar campanha no banco (SQLite + GCS)
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel, kpi):
            return jsonify({"success": False, "message": "Erro ao salvar configuração da campanha"}), 500
        
        # Salvar também no BigQuery + Firestore se disponível
        if bq_fs_manager:
            try:
                bq_fs_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel, kpi)
                logger.info(f"✅ Campanha {campaign_key} salva no BigQuery + Firestore")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar no BigQuery/Firestore: {e}")
        
        # Gerar dashboard
        result = generate_dashboard(campaign_key, client, campaign_name, sheet_id, channel, kpi)
        
        if not result['success']:
            return jsonify({"success": False, "message": f"Erro ao gerar dashboard: {result['error']}"}), 500
        
        # Salvar dashboard no BigQuery + Firestore se disponível
        if bq_fs_manager:
            try:
                dashboard_id = campaign_key
                dashboard_name_full = f"{client} - {campaign_name}"
                bq_fs_manager.save_dashboard(
                    dashboard_id=dashboard_id,
                    campaign_key=campaign_key,
                    dashboard_name=dashboard_name_full,
                    dashboard_url=result['dashboard_url'],
                    file_path=result['dashboard_url'],  # Usar URL dinâmica ao invés de arquivo
                    client=client,
                    campaign_name=campaign_name,
                    channel=channel,
                    kpi=kpi
                )
                logger.info(f"✅ Dashboard {dashboard_id} salvo no BigQuery + Firestore")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar dashboard no BigQuery/Firestore: {e}")
        
        return jsonify({
            "success": True,
            "message": "Dashboard gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": result['dashboard_url'],
            "dashboard_url_full": result['dashboard_url_full']
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/generate-dashboard: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/dashboard/<campaign_key>', methods=['GET'])
def get_dashboard_html(campaign_key):
    """Obter dashboard HTML dinâmico (réplica da produção)"""
    try:
        # Obter dados da campanha
        campaign = db_manager.get_campaign(campaign_key)
        if not campaign:
            return f"<html><body><h1>Campanha '{campaign_key}' não encontrada</h1></body></html>", 404
        
        # Extrair dados frescos da planilha (mesma lógica do get_campaign_data)
        logger.info(f"🔄 Extraindo dados frescos da planilha para: {campaign_key}")
        config = CampaignConfig(
            campaign_key=campaign_key,
            client=campaign['client'],
            campaign_name=campaign['campaign_name'],
            sheet_id=campaign['sheet_id'],
            channel=campaign.get('channel'),
            kpi=campaign.get('kpi')
        )
        
        extractor = RealGoogleSheetsExtractor(config)
        data = extractor.extract_data()
        
        if not data:
            return f"<html><body><h1>Falha ao extrair dados da planilha para '{campaign_key}'</h1></body></html>", 500
        
        # Gerar HTML dinâmico baseado no template
        html_content = generate_dynamic_dashboard_html(campaign, data)
        
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard HTML para {campaign_key}: {e}")
        return f"<html><body><h1>Erro ao carregar dashboard</h1><p>{str(e)}</p></body></html>", 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha específica"""
    try:
        campaign = db_manager.get_campaign(campaign_key)
        if not campaign:
            return jsonify({"success": False, "message": f"Campanha '{campaign_key}' não encontrada"}), 404
        
        # Sempre extrair dados frescos da planilha
        logger.info(f"🔄 Extraindo dados frescos da planilha para: {campaign_key}")
        config = CampaignConfig(
            campaign_key=campaign_key,
            client=campaign['client'],
            campaign_name=campaign['campaign_name'],
            sheet_id=campaign['sheet_id'],
            channel=campaign.get('channel'),
            kpi=campaign.get('kpi')
        )
        
        extractor = RealGoogleSheetsExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({"success": False, "message": "Falha ao extrair dados da planilha"}), 500
        
        return jsonify({"success": True, "data": extracted_data})
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados da campanha {campaign_key}: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """Listar todas as campanhas"""
    try:
        campaigns = db_manager.list_campaigns()
        return jsonify({"success": True, "campaigns": campaigns})
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos com fallback para GCS"""
    try:
        # Primeiro, tentar servir do diretório local
        if os.path.exists(os.path.join('static', filename)):
            return send_from_directory('static', filename)
        
        # Se não existir localmente, tentar carregar do GCS
        logger.info(f"📥 Arquivo não encontrado localmente: {filename}, tentando GCS...")
        
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket('south-media-ia-database-452311')
        
        # Verificar se é um dashboard
        if filename.startswith('dash_') and filename.endswith('.html'):
            gcs_path = f"dashboards/{filename}"
            blob = bucket.blob(gcs_path)
            
            if blob.exists():
                # Baixar do GCS e salvar localmente
                content = blob.download_as_text()
                
                # Criar diretório se não existir
                os.makedirs('static', exist_ok=True)
                
                # Salvar localmente para próximas requisições
                local_path = os.path.join('static', filename)
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Dashboard carregado do GCS: {filename}")
                return send_from_directory('static', filename)
            else:
                logger.warning(f"❌ Dashboard não encontrado no GCS: {gcs_path}")
        
        # Se chegou até aqui, arquivo não encontrado
        return "File not found", 404
        
    except Exception as e:
        logger.error(f"❌ Erro ao servir arquivo {filename}: {e}")
        return "Internal server error", 500

def generate_dynamic_dashboard_html(campaign, data):
    """Gerar HTML dinâmico do dashboard (réplica da produção)"""
    try:
        # Selecionar template baseado no KPI da campanha
        kpi = campaign.get('kpi', 'CPV').upper()
        if kpi == 'CPM':
            template_path = os.path.join('static', 'dash_remarketing_cpm_template.html')
            logger.info(f"🎯 Usando template CPM para dashboard dinâmico: {campaign['campaign_name']}")
        elif kpi == 'CPE':
            template_path = os.path.join('static', 'dash_generic_cpe_template.html')
            logger.info(f"🎯 Usando template CPE para dashboard dinâmico: {campaign['campaign_name']}")
        else:
            template_path = os.path.join('static', 'dash_generic_template.html')
            logger.info(f"🎯 Usando template genérico para dashboard dinâmico: {campaign['campaign_name']}")
        
        # Ler o template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Substituir variáveis dinâmicas
        campaign_key = campaign['campaign_key']
        client = campaign['client']
        campaign_name = campaign['campaign_name']
        
        # Substituir no HTML usando os placeholders corretos do template
        html_content = html_content.replace('{{CLIENT_NAME}}', client)
        html_content = html_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        html_content = html_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        
        # Substituir placeholders adicionais
        html_content = html_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        html_content = html_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard de performance para a campanha {campaign_name} do cliente {client}')
        html_content = html_content.replace('{{PRIMARY_CHANNEL}}', campaign.get('channel', 'Video Programática'))
        
        # Definir o apiEndpoint correto baseado no ambiente
        environment = os.environ.get('ENVIRONMENT', 'staging')
        if environment == 'production':
            api_endpoint = 'https://gen-dashboard-ia-609095880025.us-central1.run.app'
        elif environment == 'hml':
            api_endpoint = 'https://hml-gen-dashboard-ia-609095880025.us-central1.run.app'
        else:  # staging
            api_endpoint = 'https://stg-gen-dashboard-ia-609095880025.us-central1.run.app'
        
        html_content = html_content.replace('{{API_ENDPOINT}}', api_endpoint)
        
        return html_content
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar HTML dinâmico: {e}")
        return f"<html><body><h1>Erro ao gerar dashboard</h1><p>{str(e)}</p></body></html>"

if __name__ == '__main__':
    logger.info("🚀 Iniciando MVP Dashboard Builder (Versão Simplificada)")
    logger.info(f"🌍 Ambiente: {'Produção' if is_production() else 'Desenvolvimento'}")
    logger.info(f"🔗 API Endpoint: {get_api_endpoint()}")
    logger.info(f"🚪 Porta: {PORT}")
    
    if is_production():
        # Para produção (Cloud Run), usar Gunicorn
        logger.info("🐳 Iniciando com Gunicorn para produção")
        # O Gunicorn será iniciado pelo Dockerfile
        pass
    else:
        # Para desenvolvimento, usar servidor Flask
        logger.info("🔧 Iniciando servidor Flask para desenvolvimento")
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG)

@app.route('/api/cleanup-orphans', methods=['POST'])
def cleanup_orphans():
    """Limpar dados órfãos - SOLUÇÃO DEFINITIVA"""
    try:
        logger.info("🧹 INICIANDO LIMPEZA DEFINITIVA DE DADOS ÓRFÃOS")
        
        # Identificar campanhas de teste
        test_keywords = ['teste', 'test', 'debug', 'local', 'git', 'commit', 'e2e', 'validação', 'interface', 'logs']
        
        campaigns = bq_fs_manager.get_all_campaigns()
        test_campaigns = []
        production_campaigns = []
        
        for campaign in campaigns:
            client = campaign.get('client', '').lower()
            campaign_name = campaign.get('campaign_name', '').lower()
            
            is_test = any(keyword in client or keyword in campaign_name for keyword in test_keywords)
            
            if is_test:
                test_campaigns.append(campaign)
            else:
                production_campaigns.append(campaign)
        
        logger.info(f"📊 Campanhas de teste: {len(test_campaigns)}")
        logger.info(f"📊 Campanhas de produção: {len(production_campaigns)}")
        
        # Remover campanhas de teste
        removed_count = 0
        for campaign in test_campaigns:
            try:
                campaign_key = campaign.get('campaign_key')
                if campaign_key:
                    # Remover do Firestore
                    bq_fs_manager.fs_client.collection('campaigns').document(campaign_key).delete()
                    removed_count += 1
                    logger.info(f"✅ Removida: {campaign_key}")
            except Exception as e:
                logger.error(f"❌ Erro ao remover {campaign_key}: {e}")
        
        # Corrigir KPIs das campanhas de produção
        updated_count = 0
        for campaign in production_campaigns:
            try:
                channel = campaign.get('channel', '').lower()
                campaign_key = campaign.get('campaign_key')
                
                # Determinar KPI baseado no canal
                if 'youtube' in channel or 'video programática' in channel:
                    kpi = 'CPV'
                elif 'display' in channel or 'native' in channel or 'linkedin' in channel or 'netflix' in channel:
                    kpi = 'CPM'
                else:
                    kpi = 'CPV'
                
                # Atualizar KPI
                if campaign_key:
                    bq_fs_manager.fs_client.collection('campaigns').document(campaign_key).update({'kpi': kpi})
                    updated_count += 1
                    logger.info(f"✅ KPI atualizado: {campaign_key} -> {kpi}")
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar {campaign_key}: {e}")
        
        logger.info(f"🎉 LIMPEZA CONCLUÍDA: {removed_count} removidas, {updated_count} atualizadas")
        
        return jsonify({
            'success': True,
            'removed_campaigns': removed_count,
            'updated_campaigns': updated_count,
            'message': f'Limpeza definitiva concluída: {removed_count} campanhas de teste removidas, {updated_count} KPIs corrigidos'
        })
    
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboards-list')
def dashboards_list():
    """Página de listagem de dashboards"""
    try:
        # Buscar todos os dashboards do BigQuery/Firestore usando o manager correto
        dashboards = []
        
        # Usar bq_fs_manager se disponível (respeita ENVIRONMENT)
        if bq_fs_manager:
            try:
                # Buscar diretamente do Firestore usando a coleção correta do ambiente
                dashboard_docs = bq_fs_manager.fs_client.collection(bq_fs_manager.dashboards_collection).stream()
                
                for doc in dashboard_docs:
                    data = doc.to_dict()
                    # Filtrar dashboards de teste
                    client = data.get('client', 'N/A')
                    if client.lower().startswith('teste'):
                        continue
                    
                    dashboards.append({
                        'campaign_key': doc.id,
                        'client': client,
                        'campaign_name': data.get('campaign_name', 'N/A'),
                        'channel': data.get('channel', 'N/A'),
                        'kpi': data.get('kpi', 'N/A'),
                        'created_at': data.get('created_at', 'N/A')
                    })
            except Exception as e:
                logger.error(f"Erro ao buscar dashboards do Firestore: {e}")
        else:
            # Fallback para Firestore de produção (quando bq_fs_manager não está disponível)
            from google.cloud import firestore
            firestore_client = firestore.Client()
            
            dashboard_docs = firestore_client.collection('dashboards').stream()
            
            for doc in dashboard_docs:
                data = doc.to_dict()
                dashboards.append({
                    'campaign_key': doc.id,
                    'client': data.get('client', 'N/A'),
                    'campaign_name': data.get('campaign_name', 'N/A'),
                    'channel': data.get('channel', 'N/A'),
                    'kpi': data.get('kpi', 'N/A'),
                    'created_at': data.get('created_at', 'N/A')
                })
        
        # Gerar HTML da página
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboards Gerados</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .back-link {{
            display: inline-block;
            color: #8B5CF6;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        
        .back-link:hover {{
            color: #EC4899;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #8B5CF6, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #9CA3AF;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 800;
            color: #8B5CF6;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #9CA3AF;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .filters {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .filters-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            color: #9CA3AF;
            font-size: 0.9rem;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        
        .filter-group select,
        .filter-group input {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            padding: 10px;
            color: #fff;
            font-size: 0.9rem;
        }}
        
        .filter-group select:focus,
        .filter-group input:focus {{
            outline: none;
            border-color: #8B5CF6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }}
        
        .dashboards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .dashboard-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(139, 92, 246, 0.5);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.1);
        }}
        
        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .client-name {{
            font-weight: 700;
            font-size: 1.1rem;
            color: #fff;
        }}
        
        .channel-tag {{
            background: linear-gradient(135deg, #8B5CF6, #EC4899);
            color: #fff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .campaign-title {{
            font-size: 1rem;
            color: #E5E7EB;
            margin-bottom: 15px;
            line-height: 1.4;
        }}
        
        .dashboard-meta {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            color: #9CA3AF;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}
        
        .meta-value {{
            color: #fff;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .dashboard-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .btn-primary {{
            flex: 1;
            background: linear-gradient(135deg, #8B5CF6, #EC4899);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: 600;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(139, 92, 246, 0.3);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: #9CA3AF;
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            padding: 10px;
            text-decoration: none;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #9CA3AF;
        }}
        
        .no-results h3 {{
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #fff;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .filters-row {{
                grid-template-columns: 1fr;
            }}
            
            .dashboards-grid {{
                grid-template-columns: 1fr;
            }}
            
            .dashboard-meta {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/" class="back-link">← Voltar ao Gerador</a>
            <h1>📊 Dashboards Gerados</h1>
            <p class="subtitle">Gerencie e acesse todos os dashboards criados</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(dashboards)}</div>
                <div class="stat-label">Total de Dashboards</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(str(d.get('client', '') or '') for d in dashboards if d.get('client')))}</div>
                <div class="stat-label">Clientes Únicos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(str(d.get('channel', '') or '') for d in dashboards if d.get('channel')))}</div>
                <div class="stat-label">Canais Únicos</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filters-row">
                <div class="filter-group">
                    <label for="clientFilter">Cliente</label>
                    <select id="clientFilter">
                        <option value="">Todos os clientes</option>
        """
        
        # Adicionar opções de clientes únicos
        unique_clients = sorted(set(str(d.get('client', '') or '') for d in dashboards if d.get('client')))
        for client in unique_clients:
            if client:  # Só adicionar se não for vazio
                html_content += f'<option value="{client}">{client}</option>'
        
        html_content += """
                    </select>
                </div>
                <div class="filter-group">
                    <label for="channelFilter">Canal</label>
                    <select id="channelFilter">
                        <option value="">Todos os canais</option>
        """
        
        # Adicionar opções de canais únicos
        unique_channels = sorted(set(str(d.get('channel', '') or '') for d in dashboards if d.get('channel')))
        for channel in unique_channels:
            if channel:  # Só adicionar se não for vazio
                html_content += f'<option value="{channel}">{channel}</option>'
        
        html_content += """
                    </select>
                </div>
                <div class="filter-group">
                    <label for="kpiFilter">KPI</label>
                    <select id="kpiFilter">
                        <option value="">Todos os KPIs</option>
                        <option value="CPM">CPM</option>
                        <option value="CPV">CPV</option>
                        <option value="CPE">CPE</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="searchInput">Buscar</label>
                    <input type="text" id="searchInput" placeholder="Buscar por cliente, campanha...">
                </div>
            </div>
        </div>
        
        <div class="dashboards-grid" id="dashboardsGrid">
        """
        
        # Adicionar cards de dashboards
        for dashboard in dashboards:
            client = dashboard.get('client', 'N/A') or 'N/A'
            campaign_name = dashboard.get('campaign_name', 'N/A') or 'N/A'
            channel = dashboard.get('channel', 'N/A') or 'N/A'
            kpi = dashboard.get('kpi', 'N/A') or 'N/A'
            created_at = dashboard.get('created_at', 'N/A')
            campaign_key = dashboard.get('campaign_key', '') or ''
            
            # Garantir que os valores são strings antes de usar .lower()
            client_str = str(client) if client else 'N/A'
            campaign_name_str = str(campaign_name) if campaign_name else 'N/A'
            channel_str = str(channel) if channel else 'N/A'
            kpi_str = str(kpi) if kpi else 'N/A'
            
            # Formatar data
            if created_at and created_at != 'N/A':
                try:
                    from datetime import datetime
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        dt = created_at
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = str(created_at)[:10]
            else:
                formatted_date = 'N/A'
            
            # Criar string de busca segura
            search_text = f"{client_str.lower()} {campaign_name_str.lower()} {channel_str.lower()}"
            
            html_content += f"""
            <div class="dashboard-card" data-client="{client_str}" data-channel="{channel_str}" data-kpi="{kpi_str}" data-search="{search_text}">
                <div class="dashboard-header">
                    <div class="client-name">{client_str}</div>
                    <div class="channel-tag">{channel_str.upper()}</div>
                </div>
                <div class="campaign-title">{campaign_name_str}</div>
                <div class="dashboard-meta">
                    <div class="meta-item">
                        <div class="meta-label">KPI</div>
                        <div class="meta-value">{kpi_str}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Período</div>
                        <div class="meta-value">N/A</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Criado</div>
                        <div class="meta-value">{formatted_date}</div>
                    </div>
                </div>
                <div class="dashboard-actions">
                    <a href="/api/dashboard/{campaign_key}" class="btn-primary">
                        📊 Ver Dashboard
                    </a>
                    <a href="#" class="btn-secondary" onclick="copyToClipboard('/api/dashboard/{campaign_key}')">
                        📋 Copiar URL
                    </a>
                </div>
            </div>
            """
        
        html_content += """
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            <h3>🔍 Nenhum dashboard encontrado</h3>
            <p>Tente ajustar os filtros ou termo de busca</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(window.location.origin + text).then(() => {
                alert('URL copiada para a área de transferência!');
            });
        }
        
        function filterDashboards() {
            const clientFilter = document.getElementById('clientFilter').value.toLowerCase();
            const channelFilter = document.getElementById('channelFilter').value.toLowerCase();
            const kpiFilter = document.getElementById('kpiFilter').value.toLowerCase();
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            
            const cards = document.querySelectorAll('.dashboard-card');
            const noResults = document.getElementById('noResults');
            let visibleCount = 0;
            
            cards.forEach(card => {
                const client = card.dataset.client.toLowerCase();
                const channel = card.dataset.channel.toLowerCase();
                const kpi = card.dataset.kpi.toLowerCase();
                const search = card.dataset.search;
                
                const matchesClient = !clientFilter || client.includes(clientFilter);
                const matchesChannel = !channelFilter || channel.includes(channelFilter);
                const matchesKpi = !kpiFilter || kpi.includes(kpiFilter);
                const matchesSearch = !searchInput || search.includes(searchInput);
                
                if (matchesClient && matchesChannel && matchesKpi && matchesSearch) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            if (visibleCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
        }
        
        // Adicionar event listeners
        document.getElementById('clientFilter').addEventListener('change', filterDashboards);
        document.getElementById('channelFilter').addEventListener('change', filterDashboards);
        document.getElementById('kpiFilter').addEventListener('change', filterDashboards);
        document.getElementById('searchInput').addEventListener('input', filterDashboards);
    </script>
</body>
</html>
        """
        
        return html_content
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar listagem de dashboards: {e}")
        return f"<h1>Erro ao carregar dashboards</h1><p>Erro: {str(e)}</p>", 500

        return f"<h1>Erro ao carregar dashboards</h1><p>Erro: {str(e)}</p>", 500
