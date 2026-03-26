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
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template_string, session, redirect, make_response
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
try:
    from templates_client_admin import get_admin_clients_html, get_client_portal_html
except ImportError:
    get_admin_clients_html = get_client_portal_html = None

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "south-media-dev-secret-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True if is_production() else False
@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.getcwd(), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception:
        return '', 204

@app.route('/assets/<path:filename>')
def assets_files(filename):
    try:
        return send_from_directory(os.path.join(os.getcwd(), 'assets'), filename)
    except Exception:
        return '', 404

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

if bq_fs_manager:
    try:
        # Provisionar superadmins iniciais (idempotente)
        bq_fs_manager.ensure_superadmin_user(
            email="g4trader.news@gmail.com",
            password="south#media@26",
            name="Super Admin"
        )
        bq_fs_manager.ensure_superadmin_user(
            email="operacional@southmedia.com.br",
            password="south#media@26",
            name="Super Admin Operacional"
        )
        logger.info("✅ Superadmins iniciais garantidos")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível provisionar superadmins iniciais: {e}")


def get_current_session_user() -> Optional[Dict[str, Any]]:
    """Retornar dados do usuário autenticado da sessão."""
    if not session.get("user_id"):
        return None
    return {
        "user_id": session.get("user_id"),
        "email": session.get("email"),
        "name": session.get("name"),
        "role": session.get("role"),
        "client_id": session.get("client_id"),
    }


def is_super_admin() -> bool:
    user = get_current_session_user()
    return bool(user and user.get("role") == "super_admin")


def get_fallback_superadmin(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Emergency fallback auth for bootstrap superadmins when Firestore users are inconsistent.
    Format env SUPERADMIN_FALLBACKS: email:password:name;email2:password2:name2
    """
    entries = os.getenv(
        "SUPERADMIN_FALLBACKS",
        "g4trader.news@gmail.com:south#media@26:Super Admin;"
        "operacional@southmedia.com.br:south#media@26:Super Admin Operacional",
    )
    for raw in entries.split(";"):
        item = raw.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) < 2:
            continue
        sa_email = parts[0].strip().lower()
        sa_password = parts[1]
        sa_name = parts[2].strip() if len(parts) > 2 else "Super Admin"
        if email == sa_email and password == sa_password:
            return {
                "user_id": f"fallback-superadmin-{sa_email}",
                "email": sa_email,
                "name": sa_name,
                "role": "super_admin",
                "client_id": None,
            }
    return None


def login_required_api(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_current_session_user():
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        return fn(*args, **kwargs)
    return wrapper


def superadmin_required_api(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_current_session_user():
            return jsonify({"success": False, "message": "Não autenticado"}), 401
        if not is_super_admin():
            return jsonify({"success": False, "message": "Acesso negado"}), 403
        return fn(*args, **kwargs)
    return wrapper


def login_required_page(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_current_session_user():
            return redirect("/login?redirect=" + request.path)
        return fn(*args, **kwargs)
    return wrapper


def superadmin_required_page(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_current_session_user():
            return redirect("/login?redirect=" + request.path)
        if not is_super_admin():
            return "<h1>Acesso negado</h1>", 403
        return fn(*args, **kwargs)
    return wrapper


def with_superadmin_sidebar(page_html: str, active_menu: str = "") -> str:
    """Inject persistent superadmin sidebar into full HTML pages."""
    if not page_html or "<html" not in page_html or "<body" not in page_html:
        return page_html
    user = get_current_session_user() or {}
    user_label = user.get("name") or user.get("email") or "Usuário"

    nav_items = [
        ("panel", "/panel", '<svg class="nav-icon" viewBox="0 0 24 24"><path d="M3 10.5 12 3l9 7.5"></path><path d="M5 9.5V21h14V9.5"></path></svg>', "Painel"),
        ("dashboards", "/dashboards-list", '<svg class="nav-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>', "Dashboards"),
        ("generator", "/dash-generator-pro", '<svg class="nav-icon" viewBox="0 0 24 24"><path d="m13 3-7 10h5l-1 8 8-12h-5l1-6z"></path></svg>', "Gerador"),
        ("multichannel", "/dash-generator-pro-multicanal", '<svg class="nav-icon" viewBox="0 0 24 24"><circle cx="6" cy="6" r="2"></circle><circle cx="18" cy="6" r="2"></circle><circle cx="12" cy="18" r="2"></circle><path d="M8 7.5 10.7 15M16 7.5 13.3 15M8 6h8"></path></svg>', "Gerador Multicanal"),
        ("clients", "/admin/clients", '<svg class="nav-icon" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"></circle><path d="M3.5 19a5.5 5.5 0 0 1 11 0"></path><circle cx="17.5" cy="9" r="2.5"></circle><path d="M16 14.8a4.5 4.5 0 0 1 4.5 4.2"></path></svg>', "Clientes"),
        ("users", "/admin/users", '<svg class="nav-icon" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>', "Usuários"),
        ("me", "/me/dashboards", '<svg class="nav-icon" viewBox="0 0 24 24"><path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H10l2 2h6.5A2.5 2.5 0 0 1 21 8.5v9A2.5 2.5 0 0 1 18.5 20h-13A2.5 2.5 0 0 1 3 17.5z"></path></svg>', "Meus Dashboards"),
        ("logout", "/logout", '<svg class="nav-icon" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>', "Sair"),
    ]
    nav_links = []
    for key, href, icon, label in nav_items:
        class_attr = ' class="active"' if key == active_menu else ""
        nav_links.append(f'<a{class_attr} href="{href}">{icon} {label}</a>')
    nav_html = "".join(nav_links)

    style_block = """
<style id="superadmin-shell-style">
  :root{
    --bg:#0F1023;
    --bg2:#16213E;
    --panel:#1A1A2E;
    --muted:#9CA3AF;
    --stroke:rgba(139,92,246,.28);
    --grad:linear-gradient(135deg,#8B5CF6,#EC4899);
    --orange:#f97316;
  }
  body{
    margin:0!important;
    padding:0!important;
    font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif!important;
    color:#fff!important;
    background:linear-gradient(135deg,var(--bg) 0%,var(--bg2) 50%,var(--panel) 100%)!important;
    min-height:100vh;
  }
  .sa-shell{display:grid;grid-template-columns:260px 1fr;min-height:100vh}
  .sa-sidebar{background:linear-gradient(180deg,#0c1323 0%,#111827 100%);border-right:1px solid rgba(148,163,184,.25);padding:22px 18px;position:sticky;top:0;height:100vh;z-index:20;display:flex;flex-direction:column}
  .sa-brand{margin-bottom:20px;display:flex;justify-content:center}
  .sa-logo{width:100%;max-width:180px;height:auto;object-fit:contain;filter:drop-shadow(0 8px 24px rgba(0,0,0,.35))}
  .sa-menu{display:flex;flex-direction:column;gap:8px}
  .sa-menu a{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:10px;color:#f8fafc;text-decoration:none;background:transparent;border:1px solid transparent;transition:all .18s ease}
  .sa-menu a:hover{border-color:rgba(249,115,22,.35);background:rgba(249,115,22,.06);color:var(--orange)}
  .sa-menu a.active{color:var(--orange);border-color:rgba(249,115,22,.55);background:rgba(249,115,22,.10);box-shadow:inset 0 0 0 1px rgba(249,115,22,.08)}
  .sa-menu .nav-icon{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;flex:none}
  .sa-footer{margin-top:auto;padding-top:14px;border-top:1px solid rgba(148,163,184,.22);color:#cbd5e1;display:flex;align-items:center;gap:9px;font-size:.9rem}
  .sa-footer-icon{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
  .sa-footer-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .sa-content{padding:24px}

  /* unify page visuals to multicanal style */
  .sa-content .container{
    max-width:1100px;
    margin:0 auto;
    background:rgba(26,26,46,.8);
    border:1px solid var(--stroke);
    border-radius:14px;
    padding:2rem;
    backdrop-filter:blur(8px);
    box-shadow:0 20px 40px rgba(0,0,0,.3);
  }
  .sa-content .card,.sa-content .stat-card,.sa-content .filters,.sa-content .dashboard-card{
    background:rgba(0,0,0,.20)!important;
    border:1px solid rgba(148,163,184,.14)!important;
    border-radius:12px!important;
    backdrop-filter:blur(8px);
  }
  .sa-content h1{color:#8B5CF6!important}
  .sa-content .subtitle,.sa-content .sub,.sa-content p{color:var(--muted)}
  .sa-content input,.sa-content select,.sa-content button{
    border:1px solid rgba(148,163,184,.2)!important;
    border-radius:8px!important;
    background:rgba(255,255,255,.04)!important;
    color:#fff!important;
  }
  .sa-content button,.sa-content .btn-primary{
    background:var(--grad)!important;
    border:none!important;
    color:#fff!important;
  }
  .sa-content .view-dashboards-btn,.sa-content .admin-links a,.sa-content .back-link,.sa-content .nav-link{
    color:#8B5CF6!important;
  }
  .sa-content .view-dashboards-btn:hover,.sa-content .admin-links a:hover,.sa-content .back-link:hover,.sa-content .nav-link:hover{
    color:var(--orange)!important;
  }
  @media (max-width:900px){
    .sa-shell{grid-template-columns:1fr}
    .sa-sidebar{position:relative;height:auto}
    .sa-content{padding:14px}
    .sa-content .container{padding:1rem}
  }
</style>
"""
    shell_start = f"<div class=\"sa-shell\"><aside class=\"sa-sidebar\"><div class=\"sa-brand\"><img src=\"/assets/logo_southmedia.png\" alt=\"\" class=\"sa-logo\" onerror=\"this.style.display='none'\" /></div><nav class=\"sa-menu\">{nav_html}</nav><div class=\"sa-footer\"><svg class=\"sa-footer-icon\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"8\" r=\"3.5\"></circle><path d=\"M4 20a8 8 0 0 1 16 0\"></path></svg><span class=\"sa-footer-name\">{user_label}</span></div></aside><main class=\"sa-content\">"
    shell_end = "</main></div>"

    html = page_html
    # Remove menus internos duplicados; navegação fica exclusivamente na sidebar.
    html = re.sub(r'<div class="admin-links">.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<a[^>]*class="[^"]*back-link[^"]*"[^>]*>.*?</a>', '', html, flags=re.DOTALL)
    html = re.sub(r'<a[^>]*class="[^"]*view-dashboards-btn[^"]*"[^>]*>.*?</a>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*style="[^"]*margin-top:10px[^"]*flex-wrap:wrap[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    if "</head>" in html and "superadmin-shell-style" not in html:
        html = html.replace("</head>", style_block + "</head>", 1)
    if "<body>" in html:
        html = html.replace("<body>", "<body>" + shell_start, 1)
    if "</body>" in html:
        html = html.replace("</body>", shell_end + "</body>", 1)
    return html

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

    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: Optional[str] = None, kpi: Optional[str] = None, use_quartiles: bool = False, use_footfall: bool = False) -> bool:
        """Salvar ou atualizar uma campanha no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Adicionar coluna kpi se não existir
            try:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN kpi TEXT')
            except:
                pass  # Coluna já existe
            
            # Adicionar coluna use_quartiles se não existir
            try:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN use_quartiles INTEGER DEFAULT 0')
            except:
                pass  # Coluna já existe
            
            # Adicionar coluna use_footfall se não existir
            try:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN use_footfall INTEGER DEFAULT 0')
            except:
                pass  # Coluna já existe
            
            cursor.execute('''
                INSERT OR REPLACE INTO campaigns 
                (campaign_key, client, campaign_name, sheet_id, channel, kpi, use_quartiles, use_footfall, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (campaign_key, client, campaign_name, sheet_id, channel, kpi, 1 if use_quartiles else 0, 1 if use_footfall else 0))
            
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
                SELECT campaign_key, client, campaign_name, sheet_id, channel, kpi, use_quartiles, use_footfall, created_at, updated_at
                FROM campaigns WHERE campaign_key = ?
            ''', (campaign_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Mapear resultado considerando que use_quartiles pode não existir em campanhas antigas
                campaign_dict = {
                    'campaign_key': result[0],
                    'client': result[1],
                    'campaign_name': result[2],
                    'sheet_id': result[3],
                    'channel': result[4],
                    'kpi': result[5] if len(result) > 5 else None,
                }
                
                # use_quartiles está na posição 6 se existir, senão default 0
                if len(result) > 6:
                    campaign_dict['use_quartiles'] = result[6]
                    campaign_dict['use_footfall'] = result[7] if len(result) > 7 else 0
                    campaign_dict['created_at'] = result[8] if len(result) > 8 else None
                    campaign_dict['updated_at'] = result[9] if len(result) > 9 else None
                else:
                    campaign_dict['use_quartiles'] = 0
                    campaign_dict['use_footfall'] = 0
                    campaign_dict['created_at'] = result[6] if len(result) > 6 else None
                    campaign_dict['updated_at'] = result[7] if len(result) > 7 else None
                
                return campaign_dict
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

def generate_dashboard(campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: str = "Video Programática", kpi: str = "CPV", use_quartiles: bool = False, use_footfall: bool = False) -> Dict[str, Any]:
    """Gerar dashboard a partir do template"""
    try:
        # Determinar template baseado no KPI
        template_path = 'static/dash_generic_template.html'
        
        # Selecionar template baseado no KPI / flags especiais
        if use_footfall:
            template_path = 'static/dash_footfall_template.html'
            logger.info(f"🎯 Usando template FOOTFALL para: {campaign_name}")
        elif kpi.upper() == 'CPM':
            if use_quartiles:
                template_path = 'static/dash_cpm_with_quartiles_template.html'
                logger.info(f"🎯 Usando template CPM com quartis para: {campaign_name} (KPI: {kpi})")
            else:
                template_path = 'static/dash_remarketing_cpm_template.html'
                logger.info(f"🎯 Usando template CPM para: {campaign_name} (KPI: {kpi})")
        elif kpi.upper() == 'CPV':
            template_path = 'static/dash_generic_template.html'
            logger.info(f"🎯 Usando template CPV para: {campaign_name} (KPI: {kpi})")
        elif kpi.upper() == 'CPE':
            template_path = 'static/dash_generic_cpe_template.html'
            logger.info(f"🎯 Usando template CPE para: {campaign_name} (KPI: {kpi})")
        elif kpi.upper() == 'CPD':
            template_path = 'static/dash_generic_cpd_template.html'
            logger.info(f"🎯 Usando template CPD para: {campaign_name} (KPI: {kpi})")
        else:
            logger.info(f"🎯 Usando template genérico para: {campaign_name} (KPI: {kpi})")
        
        if not os.path.exists(template_path):
            raise Exception(f"Template não encontrado: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Extrair dados da planilha e popular no dashboard
        logger.info(f"📊 Extraindo dados da planilha para popular o dashboard...")
        try:
            config = CampaignConfig(
                campaign_key=campaign_key,
                client=client,
                campaign_name=campaign_name,
                sheet_id=sheet_id,
                channel=channel,
                kpi=kpi
            )
            config.use_footfall = bool(use_footfall)
            extractor = RealGoogleSheetsExtractor(config)
            extracted_data = extractor.extract_data()
            
            if extracted_data:
                # Converter dados para JSON e inserir no HTML
                data_json = json.dumps(extracted_data, ensure_ascii=False, default=str)
                embedded_data_script = f'<script>window.EMBEDDED_CAMPAIGN_DATA = {data_json};</script>'
                
                # Inserir dados embutidos antes do fechamento do </head> ou no início do <body>
                if '</head>' in dashboard_content:
                    dashboard_content = dashboard_content.replace('</head>', f'{embedded_data_script}\n</head>')
                elif '<body>' in dashboard_content:
                    dashboard_content = dashboard_content.replace('<body>', f'<body>\n{embedded_data_script}')
                else:
                    # Se não encontrar, inserir antes do primeiro <script>
                    first_script_pos = dashboard_content.find('<script')
                    if first_script_pos > 0:
                        dashboard_content = dashboard_content[:first_script_pos] + embedded_data_script + '\n' + dashboard_content[first_script_pos:]
                
                logger.info(f"✅ Dados da planilha extraídos e embutidos no dashboard ({len(extracted_data.get('daily_data', []))} registros diários)")
            else:
                logger.warning(f"⚠️ Não foi possível extrair dados da planilha, dashboard usará API dinâmica")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao extrair dados da planilha: {e}. Dashboard usará API dinâmica como fallback")
        
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
    """Health check endpoint para Cloud Run"""
    try:
        # Verificar se o serviço está funcionando
        status = {
            "status": "healthy",
            "service": "mvp-dashboard-builder",
            "timestamp": datetime.now().isoformat(),
            "bq_fs_manager": bq_fs_manager is not None
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

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

@app.route('/login', methods=['GET'])
def login_page():
    """Página de login server-side."""
    redirect_to = request.args.get("redirect", "")
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login - South Media IA</title>
  <style>
    body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px}
    .card{background:#111827;border:1px solid #334155;border-radius:12px;padding:24px;min-width:320px;max-width:360px;width:100%}
    .logo-wrap{display:flex;justify-content:center;margin-bottom:14px}
    .logo{width:100%;max-width:180px;height:auto;object-fit:contain}
    input,button{width:100%;padding:10px;margin-top:8px;border-radius:8px;border:1px solid #334155;background:#1f2937;color:#fff}
    button{background:#7c3aed;border:none;font-weight:600;cursor:pointer}
    .msg{margin-top:12px;color:#fca5a5}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo-wrap"><img src="/assets/logo_southmedia.png" alt="" class="logo" onerror="this.style.display='none'" /></div>
    <label>E-mail</label>
    <input id="email" type="email" autocomplete="username" />
    <label>Senha</label>
    <input id="password" type="password" autocomplete="current-password" />
    <button id="btnLogin">Entrar</button>
    <div id="msg" class="msg"></div>
  </div>
  <script>
    document.getElementById('btnLogin').addEventListener('click', async () => {
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const msg = document.getElementById('msg');
      msg.textContent = '';
      const r = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ email, password })
      });
      const j = await r.json();
      if (!j.success) {
        msg.textContent = j.message || 'Falha no login';
        return;
      }
      const redirectTo = {{ redirect_to|tojson }};
      const fallback = (j.user && j.user.role === 'super_admin')
        ? '/panel'
        : '/me/dashboards';
      window.location.href = redirectTo || fallback;
    });
  </script>
</body>
</html>
    """, redirect_to=redirect_to)


@app.route('/logout', methods=['GET'])
def logout_page():
    session.clear()
    return redirect("/login")


@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Auth indisponível"}), 503
    try:
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            return jsonify({"success": False, "message": "E-mail e senha são obrigatórios"}), 400

        user = bq_fs_manager.verify_user_credentials(email=email, password=password)
        if not user:
            user = get_fallback_superadmin(email=email, password=password)
        if not user:
            return jsonify({"success": False, "message": "Credenciais inválidas"}), 401

        session.clear()
        session["user_id"] = user.get("user_id")
        session["email"] = user.get("email")
        session["name"] = user.get("name", "")
        session["role"] = user.get("role", "viewer")
        session["client_id"] = user.get("client_id")

        return jsonify({
            "success": True,
            "user": {
                "user_id": user.get("user_id"),
                "email": user.get("email"),
                "name": user.get("name", ""),
                "role": user.get("role", "viewer"),
                "client_id": user.get("client_id"),
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return jsonify({"success": False, "message": "Erro interno no login"}), 500


@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    session.clear()
    return jsonify({"success": True})


@app.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    user = get_current_session_user()
    if not user:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    return jsonify({"success": True, "user": user})


@app.route('/api/auth/change-password', methods=['POST'])
@login_required_api
def api_auth_change_password():
    """Trocar senha do usuário logado."""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Auth indisponível"}), 503
    try:
        data = request.get_json() or {}
        current_password = data.get("current_password") or ""
        new_password = data.get("new_password") or ""
        if not current_password or not new_password:
            return jsonify({"success": False, "message": "Senha atual e nova senha são obrigatórias"}), 400
        if len(new_password) < 8:
            return jsonify({"success": False, "message": "Nova senha deve ter pelo menos 8 caracteres"}), 400

        me = get_current_session_user()
        user = bq_fs_manager.verify_user_credentials(email=me.get("email"), password=current_password)
        if not user:
            return jsonify({"success": False, "message": "Senha atual inválida"}), 401

        ok = bq_fs_manager.reset_user_password(user_id=me.get("user_id"), new_password=new_password)
        if not ok:
            return jsonify({"success": False, "message": "Falha ao atualizar senha"}), 500
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"❌ Erro ao trocar senha: {e}")
        return jsonify({"success": False, "message": "Erro interno"}), 500


@app.route('/api/admin/users', methods=['GET'])
@superadmin_required_api
def api_admin_list_users():
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    users = bq_fs_manager.list_all_users()
    sanitized = []
    for u in users:
        sanitized.append({
            "user_id": u.get("user_id"),
            "email": u.get("email"),
            "name": u.get("name"),
            "role": u.get("role", "viewer"),
            "client_id": u.get("client_id"),
            "status": u.get("status", "active"),
            "last_login": u.get("last_login"),
        })
    return jsonify({"success": True, "users": sanitized})


@app.route('/api/admin/users/<user_id>/password', methods=['PUT'])
@superadmin_required_api
def api_admin_reset_user_password(user_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    data = request.get_json() or {}
    new_password = data.get("new_password") or ""
    if len(new_password) < 8:
        return jsonify({"success": False, "message": "Senha deve ter pelo menos 8 caracteres"}), 400
    ok = bq_fs_manager.reset_user_password(user_id=user_id, new_password=new_password)
    if not ok:
        return jsonify({"success": False, "message": "Usuário não encontrado"}), 404
    return jsonify({"success": True})


@app.route('/api/admin/users/<user_id>/role', methods=['PUT'])
@superadmin_required_api
def api_admin_update_user_role(user_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    data = request.get_json() or {}
    role = (data.get("role") or "").strip()
    allowed_roles = {"super_admin", "admin", "manager", "viewer"}
    if role not in allowed_roles:
        return jsonify({"success": False, "message": "Role inválida"}), 400
    ok = bq_fs_manager.update_user_role(user_id=user_id, role=role)
    if not ok:
        return jsonify({"success": False, "message": "Usuário não encontrado"}), 404
    return jsonify({"success": True})


@app.route('/dash-generator-pro', methods=['GET'])
@superadmin_required_page
def dash_generator_pro():
    """Interface de teste do gerador"""
    from html import escape as html_escape

    clients_for_select = []
    if bq_fs_manager:
        try:
            clients_for_select = bq_fs_manager.list_clients() or []
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar clientes para o gerador: {e}")

    client_options_html = ''.join(
        '<option value="{client_id}" data-client-name="{client_name}">{client_name} ({client_id})</option>'.format(
            client_id=html_escape(str(c.get("client_id") or "")),
            client_name=html_escape(str(c.get("name") or c.get("client_id") or "")),
        )
        for c in clients_for_select
        if c.get("client_id")
    )

    page_html = render_template_string(''' 
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
            <div class="persistence-badge">Persistência Definitiva - BigQuery + Firestore</div>
            <a href="/dashboards-list" class="view-dashboards-btn" style="display:inline-flex;align-items:center;gap:8px">
                <svg style="width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>
                Ver Todos os Dashboards
            </a>
            <div style="margin-top:10px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
                <a href="/admin/clients" class="view-dashboards-btn" style="margin:0;display:inline-flex;align-items:center;gap:8px"><svg style="width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"></circle><path d="M3.5 19a5.5 5.5 0 0 1 11 0"></path><circle cx="17.5" cy="9" r="2.5"></circle><path d="M16 14.8a4.5 4.5 0 0 1 4.5 4.2"></path></svg>Clientes</a>
                <a href="/admin/users" class="view-dashboards-btn" style="margin:0;display:inline-flex;align-items:center;gap:8px"><svg style="width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>Usuários</a>
                <a href="/logout" class="view-dashboards-btn" style="margin:0;display:inline-flex;align-items:center;gap:8px"><svg style="width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>Sair</a>
            </div>
        </div>
        
        <form id="generatorForm">
        <div class="form-group">
            <label for="clientName">Cliente (nome para geração):</label>
            <input type="text" id="clientName" name="client" required>
            <small>Se selecionar um cliente existente abaixo, este campo será preenchido automaticamente.</small>
        </div>

        <div class="form-group">
            <label for="clientId">Vincular ao Cliente (opcional):</label>
            <select id="clientId" name="client_id">
                <option value="">Sem vínculo (vincule depois)</option>
                {{client_options_html|safe}}
            </select>
            <small>O vínculo será gravado no momento da criação do dashboard.</small>
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
                <option value="HBO">HBO</option>
                <option value="HHS">HHS</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Pinterest">Pinterest</option>
                <option value="Spotify">Spotify</option>
                <option value="Geofence">Geofence</option>
                <option value="Waze">Waze</option>
                <option value="CTV">CTV</option>
                <option value="Push">Push</option>
                <option value="Richmedia">Richmedia</option>
                <option value="OHS">OHS</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="kpi">KPI Contratado:</label>
            <select id="kpi" name="kpi" required>
                <option value="CPV">CPV - Custo por View (Complete Views)</option>
                <option value="CPE">CPE - Custo por Escuta (Audio Listens)</option>
                <option value="CPD">CPD - Custo por Disparo</option>
                <option value="CPM">CPM - Custo por Mil Impressões</option>
                <option value="CPC">CPC - Custo por Clique</option>
                <option value="CPA">CPA - Custo por Aquisição</option>
            </select>
            <small>Métrica principal contratada (define o layout do dashboard)</small>
        </div>
        
        <div class="form-group" id="quartilesGroup" style="display: none;">
            <label>
                <input type="checkbox" id="useQuartiles" name="use_quartiles" value="1">
                Usar quartis de vídeo/escuta (quando KPI for CPM mas a campanha for de vídeo/escuta)
            </label>
            <small>Marque esta opção se a campanha CPM utiliza métricas de quartis de vídeo/escuta</small>
        </div>

        <div class="form-group">
            <label>
                <input type="checkbox" id="useFootfall" name="use_footfall" value="1">
                Gerar com template Footfall
            </label>
            <small>Use esta opção para campanhas Drive-to-Store/Footfall.</small>
        </div>
        
        <button type="submit" id="generateButton">Gerar Dashboard</button>
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

        // Auto-preencher "client" quando usuário selecionar um client_id existente
        const clientIdSelect = document.getElementById('clientId');
        const clientNameInput = document.getElementById('clientName');
        if (clientIdSelect && clientNameInput) {
            clientIdSelect.addEventListener('change', function() {
                const opt = this.options[this.selectedIndex];
                const clientName = opt ? opt.dataset.clientName : '';
                if (clientName) clientNameInput.value = clientName;
            });

            // Se o usuário editar manualmente o nome, removemos o vínculo
            clientNameInput.addEventListener('input', function() {
                if (clientIdSelect.value) clientIdSelect.value = '';
            });
        }
        
        function isImpressionCpmChannel(channelValue) {
            const v = (channelValue || '').trim().toUpperCase();
            return v === 'HHS' || v === 'OHS';
        }

        // Mostrar/ocultar opção de quartis
        // - Apenas quando KPI for CPM E a campanha for de vídeo/escuta (HHS/OHS são impressões -> não usa quartis)
        document.getElementById('kpi').addEventListener('change', function() {
            const quartilesGroup = document.getElementById('quartilesGroup');
            const channelValue = document.getElementById('channel').value;
            if (this.value === 'CPM' && !isImpressionCpmChannel(channelValue)) {
                quartilesGroup.style.display = 'block';
            } else {
                quartilesGroup.style.display = 'none';
                document.getElementById('useQuartiles').checked = false;
            }
        });

        // Forçar KPI=CPM para HHS/OHS (Impressões/CPM)
        document.getElementById('channel').addEventListener('change', function() {
            const isImprCpm = isImpressionCpmChannel(this.value);
            const kpiSelect = document.getElementById('kpi');
            const quartilesGroup = document.getElementById('quartilesGroup');

            if (isImprCpm) {
                kpiSelect.value = 'CPM';
                quartilesGroup.style.display = 'none';
                document.getElementById('useQuartiles').checked = false;
            } else {
                // Reaplicar regra de exibição do quartis conforme KPI atual
                const kpiVal = kpiSelect.value;
                if (kpiVal === 'CPM') {
                    quartilesGroup.style.display = 'block';
                } else {
                    quartilesGroup.style.display = 'none';
                    document.getElementById('useQuartiles').checked = false;
                }
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
                
                // Adicionar flag de quartis se checkbox estiver marcado
                data.use_quartiles = document.getElementById('useQuartiles').checked ? '1' : '0';
                data.use_footfall = document.getElementById('useFootfall').checked ? '1' : '0';
                
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
    ''', client_options_html=client_options_html)
    return with_superadmin_sidebar(page_html, active_menu="generator")

@app.route('/api/generate-dashboard', methods=['POST'])
@superadmin_required_api
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
        client_id = data.get('client_id')
        if isinstance(client_id, str) and client_id.strip() == '':
            client_id = None
        campaign_name = data['campaign_name']
        sheet_id = data['sheet_id']
        channel = (data.get('channel', 'Video Programática') or '').strip()
        kpi = data.get('kpi', 'CPV')

        # HHS/OHS são por Impressões e devem usar KPI=CPM
        if str(channel).strip().upper() in ('HHS', 'OHS'):
            channel = str(channel).strip().upper()
            kpi = 'CPM'
        use_quartiles = data.get('use_quartiles', '0') == '1' or data.get('use_quartiles', False) == True
        use_footfall = data.get('use_footfall', '0') == '1' or data.get('use_footfall', False) == True
        if str(channel).strip().upper() in ('HHS', 'OHS'):
            use_quartiles = False
        
        # Gerar campaign_key automaticamente
        campaign_key = generate_campaign_key(client, campaign_name)
        
        # Salvar campanha no banco (SQLite + GCS)
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel, kpi, use_quartiles, use_footfall):
            return jsonify({"success": False, "message": "Erro ao salvar configuração da campanha"}), 500
        
        # Salvar também no BigQuery + Firestore se disponível
        if bq_fs_manager:
            try:
                bq_fs_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel, kpi, use_footfall=use_footfall)
                logger.info(f"✅ Campanha {campaign_key} salva no BigQuery + Firestore")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar no BigQuery/Firestore: {e}")
        
        # Gerar dashboard
        result = generate_dashboard(campaign_key, client, campaign_name, sheet_id, channel, kpi, use_quartiles, use_footfall)
        
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
                # Se um client_id foi informado, persistir o vínculo do dashboard com o cliente
                if client_id:
                    bq_fs_manager.set_dashboard_client(campaign_key, client_id=client_id)
                logger.info(f"✅ Dashboard {dashboard_id} salvo no BigQuery + Firestore")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar dashboard no BigQuery/Firestore: {e}")
        
        return jsonify({
            "success": True,
            "message": "Dashboard gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": result['dashboard_url'],
            "dashboard_url_full": f"{request.host_url.rstrip('/')}{result['dashboard_url']}"
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/generate-dashboard: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/dashboard/<campaign_key>', methods=['GET'])
def get_dashboard_html(campaign_key):
    """Obter dashboard HTML dinâmico (réplica da produção)"""
    try:
        user = get_current_session_user()

        # Controle de acesso por client_id apenas quando houver sessão (superadmin vê tudo).
        # Dashboards devem ser acessíveis por link direto (sem login) para compartilhamento.
        if user and (not is_super_admin()) and bq_fs_manager:
            linked_dashboard = bq_fs_manager.get_dashboard(campaign_key)
            linked_client_id = (linked_dashboard or {}).get("client_id")
            user_client_id = user.get("client_id")
            if linked_client_id and linked_client_id != user_client_id:
                return "<h1>Acesso negado</h1>", 403

        def _load_published_dashboard_fallback() -> Optional[str]:
            """Try loading previously published dashboard HTML from local static or GCS."""
            dashboard_filename = f"dash_{campaign_key}.html"
            local_path = os.path.join("static", dashboard_filename)

            try:
                if os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8") as f:
                        logger.info(f"✅ Dashboard fallback local carregado: {local_path}")
                        return f.read()
            except Exception as local_err:
                logger.warning(f"⚠️ Falha ao ler fallback local ({local_path}): {local_err}")

            try:
                from google.cloud import storage
                client_storage = storage.Client()
                bucket = client_storage.bucket('south-media-ia-database-452311')
                gcs_path = f"dashboards/{dashboard_filename}"
                blob = bucket.blob(gcs_path)
                if blob.exists():
                    html_content = blob.download_as_text()
                    logger.info(f"✅ Dashboard fallback carregado do GCS: {gcs_path}")
                    return html_content
            except Exception as gcs_err:
                logger.warning(f"⚠️ Falha ao carregar fallback do GCS para {campaign_key}: {gcs_err}")

            return None

        # Obter dados da campanha do Firestore primeiro
        campaign = None
        if bq_fs_manager:
            doc = bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).document(campaign_key).get()
            if doc.exists:
                campaign = doc.to_dict()
        
        # Se não encontrou no Firestore ou faltam flags, buscar do SQLite local
        if not campaign or 'use_quartiles' not in campaign or 'use_footfall' not in campaign:
            logger.info(f"🔄 Buscando campanha {campaign_key} no SQLite local...")
            campaign_local = db_manager.get_campaign(campaign_key)
            if campaign_local:
                # Merge: Firestore tem prioridade, mas SQLite complementa campos faltantes
                if campaign:
                    # Obter use_quartiles do SQLite (pode ser int ou string)
                    use_quartiles_sqlite = campaign_local.get('use_quartiles', 0)
                    # Converter para int se for string
                    if isinstance(use_quartiles_sqlite, str):
                        use_quartiles_sqlite = 1 if use_quartiles_sqlite == '1' or use_quartiles_sqlite == 1 else 0
                    campaign['use_quartiles'] = int(use_quartiles_sqlite)
                    use_footfall_sqlite = campaign_local.get('use_footfall', 0)
                    if isinstance(use_footfall_sqlite, str):
                        use_footfall_sqlite = 1 if use_footfall_sqlite == '1' or use_footfall_sqlite.lower() == 'true' else 0
                    campaign['use_footfall'] = int(use_footfall_sqlite)
                    logger.info(f"✅ use_quartiles obtido do SQLite: {campaign['use_quartiles']} (tipo: {type(campaign['use_quartiles'])})")
                else:
                    campaign = campaign_local
                    # Garantir que use_quartiles é int
                    if 'use_quartiles' in campaign:
                        use_quartiles_val = campaign.get('use_quartiles', 0)
                        if isinstance(use_quartiles_val, str):
                            campaign['use_quartiles'] = 1 if use_quartiles_val == '1' or use_quartiles_val == 1 else 0
                        else:
                            campaign['use_quartiles'] = int(use_quartiles_val)
                    use_footfall_val = campaign.get('use_footfall', 0)
                    if isinstance(use_footfall_val, str):
                        campaign['use_footfall'] = 1 if use_footfall_val == '1' or use_footfall_val.lower() == 'true' else 0
                    else:
                        campaign['use_footfall'] = int(use_footfall_val)
                    logger.info(f"✅ Campanha encontrada no SQLite local, use_quartiles: {campaign.get('use_quartiles', 0)}")
        
        if not campaign:
            return f"<html><body><h1>Campanha '{campaign_key}' não encontrada</h1></body></html>", 404
        
        # Normalizar campanha (Firestore pode não ter campaign_key no body; doc.id = campaign_key)
        campaign['campaign_key'] = campaign.get('campaign_key') or campaign_key
        campaign.setdefault('client', '')
        campaign.setdefault('campaign_name', '')
        campaign.setdefault('sheet_id', '')
        
        # Garantir que use_quartiles existe e é int (default 0 se não existir)
        if 'use_quartiles' not in campaign:
            campaign['use_quartiles'] = 0
        else:
            # Converter para int se necessário
            use_quartiles_val = campaign.get('use_quartiles', 0)
            if isinstance(use_quartiles_val, str):
                campaign['use_quartiles'] = 1 if use_quartiles_val == '1' or use_quartiles_val == 1 else 0
            else:
                campaign['use_quartiles'] = int(use_quartiles_val)
        
        logger.info(f"🔍 DEBUG: Campanha {campaign_key} - KPI: {campaign.get('kpi')}, use_quartiles: {campaign.get('use_quartiles')} (tipo: {type(campaign.get('use_quartiles'))})")
        
        # Verificar se é dashboard multicanal
        is_multicanal = (
            campaign.get('channel') == 'Multicanal' or 
            not campaign.get('sheet_id') or 
            campaign.get('sheet_id') == ''
        )
        
        if is_multicanal:
            # Para dashboards multicanal, tentar carregar do GCS
            try:
                from google.cloud import storage
                client_storage = storage.Client()
                bucket = client_storage.bucket('south-media-ia-database-452311')
                
                dashboard_filename = f"dash_{campaign_key}.html"
                gcs_path = f"dashboards/{dashboard_filename}"
                blob = bucket.blob(gcs_path)
                
                if blob.exists():
                    html_content = blob.download_as_text()
                    logger.info(f"✅ Dashboard multicanal carregado do GCS: {gcs_path}")
                    return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
                else:
                    logger.warning(f"⚠️ Dashboard multicanal não encontrado no GCS: {gcs_path}")
                    return f"""<html><body>
                        <h1>Dashboard Multicanal</h1>
                        <p>Este dashboard multicanal não foi encontrado.</p>
                        <p>Por favor, use o endpoint <code>/api/generate-dashboard-multicanal</code> para gerar o dashboard novamente.</p>
                        <p><strong>Campanha:</strong> {campaign.get('campaign_name', 'N/A')}</p>
                        <p><strong>Cliente:</strong> {campaign.get('client', 'N/A')}</p>
                    </body></html>""", 404, {'Content-Type': 'text/html; charset=utf-8'}
            except Exception as e:
                logger.error(f"❌ Erro ao carregar dashboard multicanal do GCS: {e}")
                return f"""<html><body>
                    <h1>Erro ao Carregar Dashboard Multicanal</h1>
                    <p>Erro: {str(e)}</p>
                    <p>Por favor, use o endpoint <code>/api/generate-dashboard-multicanal</code> para gerar o dashboard novamente.</p>
                </body></html>""", 500, {'Content-Type': 'text/html; charset=utf-8'}
        
        # Para dashboards normais, extrair dados frescos da planilha
        logger.info(f"🔄 Extraindo dados frescos da planilha para: {campaign_key}")
        config = CampaignConfig(
            campaign_key=campaign_key,
            client=campaign['client'],
            campaign_name=campaign['campaign_name'],
            sheet_id=campaign['sheet_id'],
            channel=campaign.get('channel'),
            kpi=campaign.get('kpi')
        )
        config.use_footfall = bool(campaign.get("use_footfall"))
        
        extractor = RealGoogleSheetsExtractor(config)
        data = None
        try:
            data = extractor.extract_data()
        except Exception as extraction_err:
            logger.warning(f"⚠️ Erro na extração em tempo real para {campaign_key}: {extraction_err}")

        if not data:
            fallback_html = _load_published_dashboard_fallback()
            if fallback_html:
                return fallback_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
            return f"<html><body><h1>Falha ao extrair dados da planilha para '{campaign_key}'</h1></body></html>", 500
        
        # Garantir que o KPI da campanha sobrescreva o do contrato
        campaign_kpi = campaign.get('kpi')
        if campaign_kpi and data.get('contract'):
            data['contract']['kpi'] = campaign_kpi
            logger.info(f"✅ KPI da campanha ({campaign_kpi}) aplicado ao contrato")
        
        # Gerar HTML dinâmico baseado no template
        html_content = generate_dynamic_dashboard_html(campaign, data)
        
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard HTML para {campaign_key}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"<html><body><h1>Erro ao carregar dashboard</h1><p>{str(e)}</p></body></html>", 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha específica"""
    try:
        user = get_current_session_user()

        # Controle de acesso por client_id apenas quando houver sessão.
        # Permitimos acesso público para dashboards compartilháveis.
        if user and (not is_super_admin()) and bq_fs_manager:
            linked_dashboard = bq_fs_manager.get_dashboard(campaign_key)
            linked_client_id = (linked_dashboard or {}).get("client_id")
            user_client_id = user.get("client_id")
            if linked_client_id and linked_client_id != user_client_id:
                return jsonify({"success": False, "message": "Acesso negado"}), 403

        # Buscar campanha do Firestore
        campaign = None
        if bq_fs_manager:
            doc = bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).document(campaign_key).get()
            if doc.exists:
                campaign = doc.to_dict()
        
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
        config.use_footfall = bool(campaign.get("use_footfall"))
        
        extractor = RealGoogleSheetsExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({"success": False, "message": "Falha ao extrair dados da planilha"}), 500
        
        # Garantir que o KPI da campanha sobrescreva o do contrato (CRÍTICO!)
        campaign_kpi = campaign.get('kpi')
        if campaign_kpi and extracted_data.get('contract'):
            extracted_data['contract']['kpi'] = campaign_kpi
            logger.info(f"✅ KPI da campanha ({campaign_kpi}) aplicado ao contrato na API /data")
        
        return jsonify({"success": True, "data": extracted_data})
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados da campanha {campaign_key}: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/campaigns', methods=['GET'])
@superadmin_required_api
def list_campaigns():
    """Listar todas as campanhas"""
    try:
        campaigns = db_manager.list_campaigns()
        return jsonify({"success": True, "campaigns": campaigns})
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

# --- API Clientes e vínculo de dashboards ---
@app.route('/api/clients', methods=['GET'])
@superadmin_required_api
def api_list_clients():
    """Listar todos os clientes"""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        clients = bq_fs_manager.list_clients()
        return jsonify({"success": True, "clients": clients})
    except Exception as e:
        logger.error(f"❌ Erro ao listar clientes: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients', methods=['POST'])
@superadmin_required_api
def api_create_client():
    """Criar cliente. Body: { name, slug? }"""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        data = request.get_json() or {}
        name = data.get('name') or (request.form.get('name') if request.form else None)
        if not name:
            return jsonify({"success": False, "message": "Campo 'name' obrigatório"}), 400
        slug = data.get('slug') or request.form.get('slug')
        client_id = bq_fs_manager.create_client(name=name.strip(), slug=slug.strip() if slug else None)
        if not client_id:
            return jsonify({"success": False, "message": "Falha ao criar cliente"}), 500
        return jsonify({"success": True, "client_id": client_id, "client": bq_fs_manager.get_client(client_id)})
    except Exception as e:
        logger.error(f"❌ Erro ao criar cliente: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>', methods=['GET'])
@superadmin_required_api
def api_get_client(client_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        client = bq_fs_manager.get_client(client_id)
        if not client:
            return jsonify({"success": False, "message": "Cliente não encontrado"}), 404
        return jsonify({"success": True, "client": client})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>', methods=['PUT'])
@superadmin_required_api
def api_update_client(client_id):
    """Atualizar cliente. Body: { name?, slug? }"""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        data = request.get_json() or {}
        name = data.get('name')
        slug = data.get('slug')
        ok = bq_fs_manager.update_client(client_id, name=name, slug=slug)
        if not ok:
            return jsonify({"success": False, "message": "Cliente não encontrado"}), 404
        return jsonify({"success": True, "client": bq_fs_manager.get_client(client_id)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>', methods=['DELETE'])
@superadmin_required_api
def api_delete_client(client_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        ok = bq_fs_manager.delete_client(client_id)
        if not ok:
            return jsonify({"success": False, "message": "Cliente não encontrado"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>/users', methods=['GET'])
@superadmin_required_api
def api_list_client_users(client_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        users = bq_fs_manager.list_client_users(client_id)
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>/users', methods=['POST'])
@superadmin_required_api
def api_add_client_user(client_id):
    """Body: { email, name?, role? }"""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        data = request.get_json() or {}
        email = (data.get('email') or request.form.get('email') or '').strip()
        if not email:
            return jsonify({"success": False, "message": "Campo 'email' obrigatório"}), 400
        name = data.get('name') or request.form.get('name')
        role = data.get('role') or request.form.get('role') or 'viewer'
        password = data.get('password') or request.form.get('password')
        user_id = bq_fs_manager.add_client_user(client_id, email=email, name=name, role=role, password=password)
        if not user_id:
            return jsonify({"success": False, "message": "Falha ao adicionar usuário"}), 500
        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clients/<client_id>/users/<user_id>', methods=['DELETE'])
@superadmin_required_api
def api_remove_client_user(client_id, user_id):
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        ok = bq_fs_manager.remove_client_user(user_id)
        if not ok:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Cache curto para não repetir extração da planilha ao abrir /client/.../dashboards várias vezes seguidas
_PORTAL_SHEET_METRICS_CACHE: Dict[str, tuple] = {}
_PORTAL_SHEET_CACHE_TTL_SEC = 300


def _extract_portal_metrics_for_campaign(campaign_key: str) -> Optional[Dict[str, Any]]:
    """Lê investimento e gasto (budget utilizado) da mesma fonte do dashboard (planilha)."""
    if not campaign_key or not bq_fs_manager:
        return None
    now = time.time()
    cached = _PORTAL_SHEET_METRICS_CACHE.get(campaign_key)
    if cached and (now - cached[0]) < _PORTAL_SHEET_CACHE_TTL_SEC:
        return cached[1]

    try:
        doc = bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).document(campaign_key).get()
        if not doc.exists:
            return None
        campaign = doc.to_dict() or {}
        sheet_id = (campaign.get("sheet_id") or "").strip()
        if not sheet_id:
            return None

        config = CampaignConfig(
            campaign_key=campaign_key,
            client=campaign.get("client") or "",
            campaign_name=campaign.get("campaign_name") or "",
            sheet_id=sheet_id,
            channel=campaign.get("channel"),
            kpi=campaign.get("kpi"),
        )
        extractor = RealGoogleSheetsExtractor(config)
        data = extractor.extract_data()
        if not data:
            return None
        summary = data.get("campaign_summary") or {}
        contract = data.get("contract") or {}
        spend = summary.get("total_spend")
        inv = contract.get("investment")
        payload = {
            "total_spend": spend,
            "investment": inv,
        }
        _PORTAL_SHEET_METRICS_CACHE[campaign_key] = (now, payload)
        return payload
    except Exception as e:
        logger.warning(f"⚠️ Métricas do portal (planilha) para {campaign_key}: {e}")
        return None


def enrich_client_portal_dashboards_from_sheets(dashboards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Preenche budget_used / total_spend (e investment se faltar) a partir da planilha."""
    if not dashboards:
        return dashboards
    keys = [d.get("campaign_key") for d in dashboards if d.get("campaign_key")]
    if not keys:
        return dashboards

    metrics_by_key: Dict[str, Dict[str, Any]] = {}
    max_workers = min(3, max(1, len(keys)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(_extract_portal_metrics_for_campaign, k): k for k in keys}
        for fut in as_completed(future_map):
            ck = future_map[fut]
            try:
                m = fut.result()
                if m:
                    metrics_by_key[ck] = m
            except Exception as e:
                logger.warning(f"⚠️ Enriquecimento portal {ck}: {e}")

    for d in dashboards:
        ck = d.get("campaign_key")
        m = metrics_by_key.get(ck)
        if not m:
            continue
        ts = m.get("total_spend")
        if ts is not None:
            d["budget_used"] = ts
            d["total_spend"] = ts
        inv = m.get("investment")
        if inv is not None and (d.get("investment") in (None, "", 0, "0")):
            d["investment"] = inv
    return dashboards


@app.route('/api/clients/<client_id>/dashboards', methods=['GET'])
@login_required_api
def api_list_client_dashboards(client_id):
    user = get_current_session_user()
    if not user:
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    if not is_super_admin() and user.get("client_id") != client_id:
        return jsonify({"success": False, "message": "Acesso negado"}), 403
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        dashboards = bq_fs_manager.get_dashboards_by_client(client_id)
        dashboards = enrich_client_portal_dashboards_from_sheets(dashboards)
        return jsonify({"success": True, "dashboards": dashboards})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/dashboards/<campaign_key>/client', methods=['PUT'])
@superadmin_required_api
def api_link_dashboard_client(campaign_key):
    """Vincular ou desvincular dashboard ao cliente. Body: { client_id } (null para remover)"""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        data = request.get_json() or {}
        client_id = data.get('client_id')
        if client_id is not None and client_id == '':
            client_id = None
        ok = bq_fs_manager.set_dashboard_client(campaign_key, client_id=client_id)
        if not ok:
            return jsonify({"success": False, "message": "Dashboard não encontrado"}), 404
        return jsonify({"success": True, "campaign_key": campaign_key, "client_id": client_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def _render_admin_clients():
    if get_admin_clients_html:
        return get_admin_clients_html()
    return "<h1>Templates não disponíveis</h1>"

def _render_client_portal(client, dashboards):
    if get_client_portal_html:
        return get_client_portal_html(client, dashboards)
    return "<h1>Templates não disponíveis</h1>"

@app.route('/admin/clients')
@superadmin_required_page
def admin_clients():
    """Página de gerenciamento de clientes e usuários"""
    if not bq_fs_manager:
        return "<h1>Firestore não disponível</h1>", 503
    return with_superadmin_sidebar(_render_admin_clients(), active_menu="clients")


@app.route('/admin/users')
@superadmin_required_page
def admin_users():
    """Página de gerenciamento global de usuários."""
    page_html = render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Administração de Usuários</title>
  <style>
    body{font-family:Inter,Arial,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:24px}
    .container{max-width:1100px;margin:0 auto}
    a{color:#8B5CF6;text-decoration:none}
    .card{background:rgba(255,255,255,.05);border:1px solid rgba(148,163,184,.2);border-radius:12px;padding:16px;margin-top:16px}
    table{width:100%;border-collapse:collapse}
    th,td{padding:10px;border-bottom:1px solid rgba(148,163,184,.2);font-size:.9rem}
    input,select,button{padding:8px;border-radius:8px;border:1px solid rgba(148,163,184,.3);background:rgba(255,255,255,.1);color:#fff}
    button{cursor:pointer;background:rgba(139,92,246,.4);border-color:#8B5CF6}
  </style>
</head>
<body>
  <div class="container">
    <h1 style="display:flex;align-items:center;gap:10px"><svg style="width:24px;height:24px;stroke:#fff;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>Administração de Usuários</h1>
    <p style="color:#9CA3AF">Gerencie roles e reset de senha de todos os usuários.</p>
    <div class="card">
      <table id="usersTable">
        <thead><tr><th>E-mail</th><th>Nome</th><th>Role</th><th>Cliente</th><th>Ações</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
  <script>
    const api = (path, opts={}) => fetch(path, {headers:{'Content-Type':'application/json'}, ...opts}).then(r=>r.json());
    function esc(v){ const d=document.createElement('div'); d.textContent=v||''; return d.innerHTML; }
    async function loadUsers(){
      const r = await api('/api/admin/users');
      const tb = document.querySelector('#usersTable tbody');
      if(!r.success){ tb.innerHTML = '<tr><td colspan="5">Erro ao carregar usuários</td></tr>'; return; }
      tb.innerHTML = r.users.map(u => `
        <tr>
          <td>${esc(u.email)}</td>
          <td>${esc(u.name||'')}</td>
          <td>
            <select data-role-user="${u.user_id}">
              ${['viewer','manager','admin','super_admin'].map(role => `<option value="${role}" ${u.role===role?'selected':''}>${role}</option>`).join('')}
            </select>
          </td>
          <td>${esc(u.client_id||'-')}</td>
          <td>
            <button data-save-role="${u.user_id}">Salvar role</button>
            <button data-reset-pass="${u.user_id}">Resetar senha</button>
          </td>
        </tr>
      `).join('');

      document.querySelectorAll('[data-save-role]').forEach(btn=>{
        btn.onclick = async ()=>{
          const userId = btn.dataset.saveRole;
          const role = document.querySelector(`[data-role-user="${userId}"]`).value;
          const j = await api('/api/admin/users/'+userId+'/role',{method:'PUT',body:JSON.stringify({role})});
          alert(j.success ? 'Role atualizada' : (j.message || 'Erro'));
        };
      });

      document.querySelectorAll('[data-reset-pass]').forEach(btn=>{
        btn.onclick = async ()=>{
          const userId = btn.dataset.resetPass;
          const newPassword = prompt('Nova senha (mínimo 8 caracteres):');
          if(!newPassword) return;
          const j = await api('/api/admin/users/'+userId+'/password',{method:'PUT',body:JSON.stringify({new_password:newPassword})});
          alert(j.success ? 'Senha resetada' : (j.message || 'Erro'));
        };
      });
    }
    loadUsers();
  </script>
</body>
</html>
    """)
    return with_superadmin_sidebar(page_html, active_menu="users")

@app.route('/client/<client_id>/dashboards')
@login_required_page
def client_dashboards(client_id):
    """Painel do cliente: listagem de dashboards vinculados a este cliente"""
    user = get_current_session_user()
    if not user:
        return redirect("/login?redirect=/client/" + client_id + "/dashboards")
    if not is_super_admin() and user.get("client_id") != client_id:
        return "<h1>Acesso negado</h1>", 403
    if not bq_fs_manager:
        return "<h1>Firestore não disponível</h1>", 503
    try:
        client = bq_fs_manager.get_client(client_id)
        if not client:
            return "<h1>Cliente não encontrado</h1>", 404
        dashboards = bq_fs_manager.get_dashboards_by_client(client_id)
        dashboards = enrich_client_portal_dashboards_from_sheets(dashboards)
    except Exception as e:
        logger.error(f"Erro ao listar dashboards do cliente: {e}")
        client = {}
        dashboards = []
    page_html = _render_client_portal(client, dashboards)
    if is_super_admin():
        page_html = with_superadmin_sidebar(page_html, active_menu="dashboards")

    # Avoid stale cached HTML/JS in the client mini-dashboard portal.
    response = make_response(page_html)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/me/dashboards')
@login_required_page
def my_dashboards():
    """Atalho para o painel de dashboards do usuário logado."""
    user = get_current_session_user()
    if not user:
        return redirect("/login?redirect=/me/dashboards")

    if is_super_admin():
        return redirect("/panel")

    client_id = user.get("client_id")
    if not client_id:
        return "<h1>Usuário sem empresa vinculada</h1><p>Solicite ao superadmin a vinculação do seu usuário a um cliente.</p>", 403

    return redirect(f"/client/{client_id}/dashboards")


@app.route('/panel')
@superadmin_required_page
def admin_panel():
    """Painel principal do superusuário com menu lateral e cards de clientes."""
    clients = []
    dashboards_by_client = {}
    total_linked_dashboards = 0

    if bq_fs_manager:
        try:
            clients = bq_fs_manager.list_clients() or []
            for client in clients:
                client_id = client.get("client_id")
                if not client_id:
                    continue
                linked = bq_fs_manager.get_dashboards_by_client(client_id) or []
                dashboards_by_client[client_id] = len(linked)
                total_linked_dashboards += len(linked)
        except Exception as e:
            logger.error(f"❌ Erro ao montar painel admin: {e}")

    cards_html = ""
    for client in clients:
        client_id = client.get("client_id", "")
        client_name = client.get("name") or client_id
        count = dashboards_by_client.get(client_id, 0)
        cards_html += f"""
        <a class="client-card" href="/client/{client_id}/dashboards">
            <div class="client-name">{client_name}</div>
            <div class="client-id">{client_id}</div>
            <div class="client-count">{count} dashboard(s)</div>
        </a>
        """

    if not cards_html:
        cards_html = '<div class="empty">Nenhum cliente cadastrado ainda.</div>'

    page_html = render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Painel Superadmin</title>
  <style>
    *{box-sizing:border-box}
    .container{max-width:1100px;margin:0 auto}
    .header h1{margin:0 0 6px 0}
    .header p{margin:0;color:#9CA3AF}
    .stats{margin-top:16px;display:flex;gap:12px;flex-wrap:wrap}
    .stat{background:rgba(0,0,0,.20);border:1px solid rgba(148,163,184,.14);border-radius:12px;padding:12px 14px}
    .cards{margin-top:22px;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
    .client-card{display:block;text-decoration:none;color:#fff;background:rgba(0,0,0,.20);border:1px solid rgba(148,163,184,.14);border-radius:12px;padding:16px;transition:.2s}
    .client-card:hover{transform:translateY(-2px);border-color:rgba(139,92,246,.6)}
    .client-name{font-weight:700;font-size:1rem}
    .client-id{color:#9CA3AF;font-size:.85rem;margin-top:4px}
    .client-count{margin-top:10px;color:#c4b5fd;font-weight:600}
    .empty{color:#9CA3AF;background:rgba(0,0,0,.20);border:1px dashed rgba(148,163,184,.35);border-radius:10px;padding:18px}
  </style>
</head>
<body>
  <div class="container">
      <div class="header">
        <h1>Visão Geral de Clientes</h1>
        <p>Clique em um cliente para abrir a listagem de dashboards vinculados.</p>
      </div>
      <div class="stats">
        <div class="stat"><strong>{{ clients_count }}</strong><br>Clientes</div>
        <div class="stat"><strong>{{ total_dashboards }}</strong><br>Dashboards vinculados</div>
      </div>
      <section class="cards">{{ cards_html|safe }}</section>
  </div>
</body>
</html>
    """, clients_count=len(clients), total_dashboards=total_linked_dashboards, cards_html=cards_html)
    return with_superadmin_sidebar(page_html, active_menu="panel")

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
        # Selecionar template baseado no KPI da campanha e flags
        kpi = campaign.get('kpi', 'CPV')
        # Converter use_quartiles para boolean de forma robusta
        use_quartiles_val = campaign.get('use_quartiles', 0)
        if isinstance(use_quartiles_val, str):
            use_quartiles = use_quartiles_val == '1' or use_quartiles_val == 1
        else:
            use_quartiles = int(use_quartiles_val) == 1 or use_quartiles_val == True
        use_footfall_val = campaign.get('use_footfall', 0)
        if isinstance(use_footfall_val, str):
            use_footfall = use_footfall_val == '1' or use_footfall_val.lower() == 'true'
        else:
            use_footfall = int(use_footfall_val) == 1 or use_footfall_val is True
        
        logger.info(f"🔍 DEBUG generate_dynamic_dashboard_html: KPI={kpi}, use_quartiles={use_quartiles}, use_footfall={use_footfall}")
        
        if use_footfall:
            template_path = os.path.join('static', 'dash_footfall_template.html')
            logger.info(f"🎯 Usando template FOOTFALL para dashboard dinâmico: {campaign['campaign_name']}")
        elif kpi.upper() == 'CPM':
            if use_quartiles:
                template_path = os.path.join('static', 'dash_cpm_with_quartiles_template.html')
                logger.info(f"🎯 Usando template CPM com quartis para dashboard dinâmico: {campaign['campaign_name']}")
            else:
                template_path = os.path.join('static', 'dash_remarketing_cpm_template.html')
                logger.info(f"🎯 Usando template CPM para dashboard dinâmico: {campaign['campaign_name']}")
        elif kpi.upper() == 'CPE':
            template_path = os.path.join('static', 'dash_generic_cpe_template.html')
            logger.info(f"🎯 Usando template CPE para dashboard dinâmico: {campaign['campaign_name']}")
        elif kpi.upper() == 'CPD':
            template_path = os.path.join('static', 'dash_generic_cpd_template.html')
            logger.info(f"🎯 Usando template CPD para dashboard dinâmico: {campaign['campaign_name']}")
        else:
            template_path = os.path.join('static', 'dash_generic_template.html')
            logger.info(f"🎯 Usando template genérico para dashboard dinâmico: {campaign['campaign_name']}")
        
        # Ler o template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Substituir variáveis dinâmicas (usar .get para evitar KeyError com dados do Firestore)
        campaign_key = campaign.get('campaign_key', '')
        client = campaign.get('client', '')
        campaign_name = campaign.get('campaign_name', '')
        
        # Substituir no HTML usando os placeholders corretos do template
        html_content = html_content.replace('{{CLIENT_NAME}}', client)
        html_content = html_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        html_content = html_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        
        # Substituir placeholders adicionais
        html_content = html_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        html_content = html_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard de performance para a campanha {campaign_name} do cliente {client}')
        html_content = html_content.replace('{{PRIMARY_CHANNEL}}', campaign.get('channel', 'Video Programática'))
        
        # Usar o endpoint configurado do config.py
        api_endpoint = get_api_endpoint()
        
        html_content = html_content.replace('{{API_ENDPOINT}}', api_endpoint)
        
        # Dashboards devem abrir limpos, sem shell/sidebar administrativa.
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
@superadmin_required_api
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
                if 'youtube' in channel or 'video programática' in channel or 'ctv' in channel or 'hbo' in channel:
                    kpi = 'CPV'
                elif 'display' in channel or 'native' in channel or 'linkedin' in channel or 'netflix' in channel or 'push' in channel or 'richmedia' in channel:
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
@superadmin_required_page
def dashboards_list():
    """Página de listagem de dashboards"""
    try:
        # Buscar todos os dashboards do BigQuery/Firestore usando o manager correto
        dashboards = []
        
        # Usar bq_fs_manager se disponível (respeita ENVIRONMENT)
        if bq_fs_manager:
            try:
                # Buscar diretamente do Firestore usando a coleção correta do ambiente
                # Limitar a 500 dashboards para evitar timeout e melhorar performance
                dashboard_docs = bq_fs_manager.fs_client.collection(bq_fs_manager.dashboards_collection).limit(500).stream()
                
                for doc in dashboard_docs:
                    try:
                        data = doc.to_dict()
                        # Filtrar dashboards de teste
                        client = data.get('client', 'N/A')
                        if client and str(client).lower().startswith('teste'):
                            continue
                        
                        dashboards.append({
                            'campaign_key': doc.id,
                            'client': client or 'N/A',
                            'campaign_name': data.get('campaign_name', 'N/A'),
                            'channel': data.get('channel', 'N/A'),
                            'kpi': data.get('kpi', 'N/A'),
                            'created_at': data.get('created_at', 'N/A'),
                            'client_id': data.get('client_id')  # vínculo com cliente (painel por cliente)
                        })
                    except Exception as doc_error:
                        logger.warning(f"Erro ao processar documento {doc.id}: {doc_error}")
                        continue
            except Exception as e:
                logger.error(f"Erro ao buscar dashboards do Firestore: {e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            # Fallback para Firestore de produção (quando bq_fs_manager não está disponível)
            try:
                from google.cloud import firestore
                firestore_client = firestore.Client()
                
                dashboard_docs = firestore_client.collection('dashboards').limit(100).stream()
                
                for doc in dashboard_docs:
                    data = doc.to_dict()
                    dashboards.append({
                        'campaign_key': doc.id,
                        'client': data.get('client', 'N/A'),
                        'campaign_name': data.get('campaign_name', 'N/A'),
                        'channel': data.get('channel', 'N/A'),
                        'kpi': data.get('kpi', 'N/A'),
                        'created_at': data.get('created_at', 'N/A'),
                        'client_id': data.get('client_id')
                    })
            except Exception as e:
                logger.error(f"Erro ao buscar dashboards do Firestore (fallback): {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Buscar clientes para o seletor de vínculo
        clients_for_link = []
        if bq_fs_manager:
            try:
                clients_for_link = bq_fs_manager.list_clients()
            except Exception:
                pass
        
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
        
        .admin-links {{
            margin-bottom: 20px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .admin-links a {{
            color: #8B5CF6;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .admin-links a:hover {{
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
        
        .client-select, .btn-link, .btn-unlink {{
            margin-right: 8px;
            margin-bottom: 6px;
        }}
        .client-select {{
            max-width: 180px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(148,163,184,.3);
            border-radius: 6px;
            padding: 6px 8px;
            color: #fff;
            font-size: 0.85rem;
        }}
        .btn-link, .btn-unlink {{
            background: rgba(139,92,246,0.3);
            border: 1px solid rgba(139,92,246,0.6);
            color: #C4B5FD;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
        }}
        .btn-unlink {{
            background: rgba(239,68,68,0.2);
            border-color: rgba(239,68,68,0.5);
            color: #FCA5A5;
        }}
        .btn-link:hover, .btn-unlink:hover {{
            opacity: 0.9;
        }}
        .client-link-info {{
            color: #9CA3AF;
            font-size: 0.9rem;
            margin-bottom: 8px;
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
            <div class="admin-links">
                <a href="/admin/clients" style="display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"></circle><path d="M3.5 19a5.5 5.5 0 0 1 11 0"></path><circle cx="17.5" cy="9" r="2.5"></circle><path d="M16 14.8a4.5 4.5 0 0 1 4.5 4.2"></path></svg>Gerenciar clientes e usuários</a>
                <a href="/admin/users" style="display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>Administrar usuários</a>
                <a href="/me/dashboards" style="display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>Meus dashboards</a>
                <a href="/logout" style="display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>Sair</a>
            </div>
            <h1>Dashboards Gerados</h1>
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
                        <option value="CPD">CPD</option>
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
            linked_client_id = dashboard.get('client_id') or ''
            linked_client_name = next((c.get('name') or c.get('client_id') for c in clients_for_link if (c.get('client_id') or c.get('slug')) == linked_client_id), linked_client_id) if linked_client_id else ''
            
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
            
            # Seletor de clientes para vínculo (opções HTML)
            client_options = ''.join(f'<option value="{c.get("client_id") or c.get("slug")}">{c.get("name") or c.get("client_id")}</option>' for c in clients_for_link)
            link_section = ''
            if linked_client_id:
                link_section = f'<div class="client-link-info">Vinculado a: <strong>{linked_client_name or linked_client_id}</strong></div><button type="button" class="btn-unlink" data-campaign-key="{campaign_key}">Remover vínculo</button>'
            else:
                link_section = f'<select class="client-select" data-campaign-key="{campaign_key}"><option value="">Vincular ao cliente...</option>{client_options}</select><button type="button" class="btn-link" data-campaign-key="{campaign_key}">Vincular</button>'
            html_content += f"""
            <div class="dashboard-card" data-client="{client_str}" data-channel="{channel_str}" data-kpi="{kpi_str}" data-search="{search_text}" data-client-id="{linked_client_id}">
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
                <div class="dashboard-client-link" style="margin-top:12px; padding-top:12px; border-top:1px solid rgba(148,163,184,.2);">
                    {link_section}
                </div>
                <div class="dashboard-actions">
                    <a href="/api/dashboard/{campaign_key}" class="btn-primary" target="_blank" rel="noopener noreferrer">
                        Ver Dashboard
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
        
        // Vincular dashboard ao cliente
        async function linkDashboard(campaignKey, clientId) {
            try {
                const r = await fetch('/api/dashboards/' + campaignKey + '/client', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: clientId })
                });
                const j = await r.json();
                if (j.success) location.reload();
                else alert(j.message || 'Erro ao vincular');
            } catch (e) { alert('Erro: ' + e.message); }
        }
        async function unlinkDashboard(campaignKey) {
            try {
                const r = await fetch('/api/dashboards/' + campaignKey + '/client', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: null })
                });
                const j = await r.json();
                if (j.success) location.reload();
                else alert(j.message || 'Erro ao remover vínculo');
            } catch (e) { alert('Erro: ' + e.message); }
        }
        document.querySelectorAll('.btn-link').forEach(btn => {
            btn.addEventListener('click', function() {
                const key = this.dataset.campaignKey;
                const sel = this.closest('.dashboard-client-link').querySelector('.client-select');
                const clientId = sel && sel.value ? sel.value : null;
                if (!clientId) { alert('Selecione um cliente'); return; }
                linkDashboard(key, clientId);
            });
        });
        document.querySelectorAll('.btn-unlink').forEach(btn => {
            btn.addEventListener('click', function() {
                if (!confirm('Remover vínculo deste dashboard com o cliente?')) return;
                unlinkDashboard(this.dataset.campaignKey);
            });
        });
        
        // Adicionar event listeners
        document.getElementById('clientFilter').addEventListener('change', filterDashboards);
        document.getElementById('channelFilter').addEventListener('change', filterDashboards);
        document.getElementById('kpiFilter').addEventListener('change', filterDashboards);
        document.getElementById('searchInput').addEventListener('input', filterDashboards);
    </script>
</body>
</html>
        """
        
        return with_superadmin_sidebar(html_content, active_menu="dashboards")
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar listagem de dashboards: {e}")
        return f"<h1>Erro ao carregar dashboards</h1><p>Erro: {str(e)}</p>", 500

@app.route('/dash-generator-pro-multicanal', methods=['GET'])
@superadmin_required_page
def dash_generator_pro_multicanal():
    """Interface do gerador multicanal - permite múltiplos canais com planilhas distintas"""
    page_html = render_template_string(r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador de Dashboards - Multicanal</title>
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
            max-width: 1000px;
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
        
        .multichannel-badge {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(139,92,246,.15);
            border: 1px solid rgba(139,92,246,.3);
            border-radius: 8px;
            color: #8B5CF6;
            font-weight: 600;
            font-size: 0.85rem;
            margin-top: 1rem;
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
        
        small {
            color: var(--muted);
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
        }
        
        .channels-container {
            margin: 2rem 0;
        }
        
        .channel-card {
            background: rgba(0,0,0,.2);
            border: 1px solid rgba(148,163,184,.1);
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            position: relative;
        }
        
        .channel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .channel-title {
            color: #8B5CF6;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .remove-channel {
            background: rgba(239,68,68,.2);
            border: 1px solid rgba(239,68,68,.4);
            color: #EF4444;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }
        
        .remove-channel:hover {
            background: rgba(239,68,68,.3);
        }
        
        .channel-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .channel-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .add-channel-btn {
            background: rgba(16,185,129,.2);
            border: 1px solid rgba(16,185,129,.4);
            color: #10B981;
            padding: 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            text-align: center;
            transition: all 0.2s ease;
            margin-top: 1rem;
        }
        
        .add-channel-btn:hover {
            background: rgba(16,185,129,.3);
            transform: translateY(-2px);
        }
        
        button[type="submit"] {
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
            margin-top: 2rem;
        }
        
        button[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(139,92,246,.35);
        }
        
        button[type="submit"]:disabled {
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
        
        .result a {
            color: #10B981;
            text-decoration: none;
            font-weight: 600;
        }
        
        .result a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SM</div>
            <h1>Gerador de Dashboards Multicanal</h1>
            <p class="subtitle">Configure múltiplos canais, cada um com sua própria planilha</p>
            <div class="multichannel-badge">Múltiplos Canais - Planilhas Independentes</div>
            <div style="margin-top:10px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
                <a href="/dashboards-list" style="color:#8B5CF6;text-decoration:none;display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="1.5"></rect><rect x="13" y="3" width="8" height="5" rx="1.5"></rect><rect x="13" y="10" width="8" height="11" rx="1.5"></rect><rect x="3" y="13" width="8" height="8" rx="1.5"></rect></svg>Dashboards</a>
                <a href="/admin/clients" style="color:#8B5CF6;text-decoration:none;display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"></circle><path d="M3.5 19a5.5 5.5 0 0 1 11 0"></path><circle cx="17.5" cy="9" r="2.5"></circle><path d="M16 14.8a4.5 4.5 0 0 1 4.5 4.2"></path></svg>Clientes</a>
                <a href="/admin/users" style="color:#8B5CF6;text-decoration:none;display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><path d="M7 11V8a5 5 0 0 1 10 0v3"></path></svg>Usuários</a>
                <a href="/logout" style="color:#8B5CF6;text-decoration:none;display:inline-flex;align-items:center;gap:8px"><svg style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path></svg>Sair</a>
            </div>
        </div>
        
        <form id="generatorForm">
            <div class="form-group">
                <label for="clientName">Cliente:</label>
                <input type="text" id="clientName" name="client" required autocomplete="off" data-lpignore="true">
            </div>
            
            <div class="form-group">
                <label for="campaignName">Nome da Campanha:</label>
                <input type="text" id="campaignName" name="campaign_name" required autocomplete="off" data-lpignore="true">
            </div>

            <div class="card" style="margin: 18px 0; padding: 16px;">
                <label style="margin-bottom: 10px; display:block;">Modo de Criação:</label>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button type="button" id="modeManual" class="tab active" style="flex:1;">Planilhas por Canal (manual)</button>
                    <button type="button" id="modeFromExisting" class="tab" style="flex:1;">Baseado em Dashboards Existentes</button>
                </div>
                <p class="muted" style="margin-top:10px;">No modo “existentes”, você seleciona campanhas já criadas e o sistema consolida tudo em um multicanal.</p>
            </div>
            
            <div class="channels-container" id="manualMode">
                <label style="margin-bottom: 1rem;">Canais:</label>
                <div id="channelsList"></div>
                <div class="add-channel-btn" onclick="addChannel()">+ Adicionar Canal</div>
            </div>

            <div class="channels-container hidden" id="existingMode" style="margin-top: 10px;">
                <label style="margin-bottom: .75rem;">Selecione os dashboards existentes:</label>
                <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom: 10px;">
                    <input type="text" id="existingSearch" placeholder="Buscar por cliente/campanha/canal/KPI..." style="flex: 1; min-width: 240px;">
                    <button type="button" id="btnLoadExisting" style="width:auto; padding:.7rem 1rem;">Carregar</button>
                    <span class="muted" id="existingCount" style="font-size:.9rem;"></span>
                </div>
                <div id="existingList" style="display:grid; gap:10px;"></div>
            </div>
            
            <button type="submit" id="generateButton">Gerar Dashboard Multicanal</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <script>
        let channelCount = 0;
        
        function extractSheetId(url) {
            if (!url) return '';
            // Usar strings e RegExp para evitar problemas de escape
            const patterns = [
                new RegExp('/spreadsheets/d/([a-zA-Z0-9-_]+)'),
                new RegExp('/d/([a-zA-Z0-9-_]+)'),
                new RegExp('id=([a-zA-Z0-9-_]+)')
            ];
            for (const pattern of patterns) {
                const match = url.match(pattern);
                if (match && match[1]) return match[1];
            }
            return '';
        }
        
        function addChannel() {
            channelCount++;
            const channelsList = document.getElementById('channelsList');
            const channelCard = document.createElement('div');
            channelCard.className = 'channel-card';
            channelCard.id = `channel-${channelCount}`;
            channelCard.innerHTML = `
                <div class="channel-header">
                    <div class="channel-title">Canal ${channelCount}</div>
                    <button type="button" class="remove-channel" onclick="removeChannel(${channelCount})">Remover</button>
                </div>
                <div class="channel-grid">
                    <div class="form-group">
                        <label>Nome do Canal:</label>
                        <select name="channels[${channelCount}][channel_name]" required onchange="syncKpiForChannel(${channelCount}, this.value)">
                            <option value="">Selecione um canal</option>
                            <option value="Video Programática">Video Programática</option>
                            <option value="Display Programática">Display Programática</option>
                            <option value="Native Programática">Native Programática</option>
                            <option value="YouTube">YouTube</option>
                            <option value="TikTok">TikTok</option>
                            <option value="Facebook">Facebook</option>
                            <option value="Instagram">Instagram</option>
                            <option value="Netflix">Netflix</option>
                            <option value="Disney">Disney</option>
                            <option value="HBO">HBO</option>
                            <option value="HHS">HHS</option>
                            <option value="LinkedIn">LinkedIn</option>
                            <option value="Pinterest">Pinterest</option>
                            <option value="Spotify">Spotify</option>
                            <option value="Geofence">Geofence</option>
                            <option value="Waze">Waze</option>
                            <option value="CTV">CTV</option>
                            <option value="Footfall Display">Footfall Display</option>
                            <option value="Push">Push</option>
                            <option value="Richmedia">Richmedia</option>
                            <option value="OHS">OHS</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Descrição da Ação:</label>
                        <input type="text" name="channels[${channelCount}][action_description]" placeholder="Ex: Ação 1, Inverno 2025, etc." autocomplete="off" data-lpignore="true">
                    </div>
                    <div class="form-group">
                        <label>KPI:</label>
                        <select name="channels[${channelCount}][kpi]" required>
                            <option value="CPV">CPV - Custo por View</option>
                            <option value="CPE">CPE - Custo por Escuta</option>
                            <option value="CPD">CPD - Custo por Disparo</option>
                            <option value="CPM">CPM - Custo por Mil Impressões</option>
                            <option value="CPC">CPC - Custo por Clique</option>
                            <option value="CPA">CPA - Custo por Aquisição</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label style="display:flex; gap:10px; align-items:center;">
                            <input type="checkbox" name="channels[${channelCount}][use_footfall]" value="1">
                            Incluir Footfall (aba + mapa)
                        </label>
                        <small>Marque se esta planilha possui a aba <b>Footfall</b> com lat/long.</small>
                    </div>
                    <div class="form-group">
                        <label>URL da Planilha:</label>
                        <input type="url" name="channels[${channelCount}][sheet_url]" placeholder="https://docs.google.com/spreadsheets/d/..." required oninput="updateSheetId(${channelCount}, this.value)" autocomplete="off" data-lpignore="true" data-form-type="other">
                    </div>
                    <div class="form-group">
                        <label>ID da Planilha (Auto):</label>
                        <input type="text" name="channels[${channelCount}][sheet_id]" readonly autocomplete="off" data-lpignore="true">
                    </div>
                </div>
            `;
            channelsList.appendChild(channelCard);
        }
        
        function removeChannel(id) {
            const channelCard = document.getElementById(`channel-${id}`);
            if (channelCard) {
                channelCard.remove();
            }
        }
        
        function updateSheetId(channelId, url) {
            const sheetIdInput = document.querySelector(`#channel-${channelId} input[name*="[sheet_id]"]`);
            if (sheetIdInput) {
                const sheetId = extractSheetId(url);
                sheetIdInput.value = sheetId;
                sheetIdInput.style.color = sheetId ? '#10B981' : '#666';
            }
        }

        // HHS/OHS: Impressões/CPM (forçar KPI=CPM quando selecionado)
        function syncKpiForChannel(channelId, channelValue) {
            const v = (channelValue || '').trim().toUpperCase();
            const card = document.getElementById(`channel-${channelId}`);
            if (!card) return;
            const kpiSelect = card.querySelector('select[name*="[kpi]"]');
            if (!kpiSelect) return;
            if (v === 'HHS' || v === 'OHS') {
                kpiSelect.value = 'CPM';
            }
        }
        
        // Garantir que as funções estejam no escopo global
        window.addChannel = addChannel;
        window.removeChannel = removeChannel;
        window.updateSheetId = updateSheetId;
        window.extractSheetId = extractSheetId;
        window.syncKpiForChannel = syncKpiForChannel;
        
        // Adicionar primeiro canal por padrão quando o DOM estiver pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                addChannel();
            });
        } else {
            addChannel();
        }
        
        let generatorMode = 'manual'; // 'manual' | 'existing'
        let existingItems = [];

        function setMode(mode) {
            generatorMode = mode;
            const manual = document.getElementById('manualMode');
            const existing = document.getElementById('existingMode');
            const btnManual = document.getElementById('modeManual');
            const btnExisting = document.getElementById('modeFromExisting');
            if (mode === 'existing') {
                manual.classList.add('hidden');
                existing.classList.remove('hidden');
                btnManual.classList.remove('active');
                btnExisting.classList.add('active');
            } else {
                existing.classList.add('hidden');
                manual.classList.remove('hidden');
                btnExisting.classList.remove('active');
                btnManual.classList.add('active');
            }
        }

        document.getElementById('modeManual').addEventListener('click', () => setMode('manual'));
        document.getElementById('modeFromExisting').addEventListener('click', () => setMode('existing'));

        function esc(s){ const d=document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

        function renderExistingList(filterText='') {
            const q = (filterText || '').trim().toLowerCase();
            const list = document.getElementById('existingList');
            const items = !q ? existingItems : existingItems.filter(it => (it.search||'').includes(q));
            document.getElementById('existingCount').textContent = existingItems.length ? `${items.length}/${existingItems.length} exibidos` : '';
            list.innerHTML = items.map(it => `
                <label class="card" style="padding:12px; margin:0; display:flex; gap:12px; align-items:flex-start; cursor:pointer;">
                    <input type="checkbox" class="js-existing-item" value="${esc(it.campaign_key)}" style="margin-top:4px;">
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
                            <div style="font-weight:800;">${esc(it.client || 'N/A')} — ${esc(it.campaign_name || it.campaign_key)}</div>
                            <div class="muted" style="font-size:.85rem;">${esc(it.channel || '')} ${it.kpi ? '• ' + esc(it.kpi) : ''}</div>
                        </div>
                        <div class="muted" style="margin-top:6px; font-size:.85rem;">
                            <span>ID: ${esc(it.campaign_key)}</span>
                            ${it.updated_at ? ` • <span>Atualizado: ${esc(it.updated_at)}</span>` : ''}
                        </div>
                    </div>
                </label>
            `).join('') || `<div class="muted">Nenhum item encontrado.</div>`;
        }

        async function loadExisting() {
            const btn = document.getElementById('btnLoadExisting');
            btn.disabled = true;
            btn.textContent = 'Carregando...';
            try {
                const r = await fetch('/api/admin/campaigns-picker');
                const j = await r.json();
                if (!j.success) throw new Error(j.message || 'Falha ao carregar');
                existingItems = (j.items || []).map(it => ({
                    ...it,
                    search: `${it.client||''} ${it.campaign_name||''} ${it.channel||''} ${it.kpi||''} ${it.campaign_key||''}`.toLowerCase()
                }));
                renderExistingList(document.getElementById('existingSearch').value);
            } catch (e) {
                alert('Erro: ' + e.message);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Carregar';
            }
        }

        document.getElementById('btnLoadExisting').addEventListener('click', loadExisting);
        document.getElementById('existingSearch').addEventListener('input', (e)=> renderExistingList(e.target.value));

        document.getElementById('generatorForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            const generateButton = document.getElementById('generateButton');
            
            resultDiv.innerHTML = '<div class="loading">🔄 Gerando dashboard multicanal...</div>';
            resultDiv.style.display = 'block';
            generateButton.disabled = true;
            
            try {
                const formData = new FormData(this);
                const data = {
                    client: formData.get('client'),
                    campaign_name: formData.get('campaign_name'),
                    channels: []
                };

                let endpoint = '/api/generate-dashboard-multicanal';

                if (generatorMode === 'existing') {
                    endpoint = '/api/generate-dashboard-multicanal-from-existing';
                    const selected = Array.from(document.querySelectorAll('.js-existing-item:checked')).map(i => i.value);
                    if (!selected.length) throw new Error('Selecione pelo menos um dashboard existente');
                    data.source_campaign_keys = selected;
                    delete data.channels;
                } else {
                    // Coletar dados dos canais (manual)
                    const channelInputs = document.querySelectorAll('.channel-card');
                    channelInputs.forEach(card => {
                        const channelName = card.querySelector('select[name*="[channel_name]"]').value;
                        const actionDescription = card.querySelector('input[name*="[action_description]"]').value || '';
                        const kpi = card.querySelector('select[name*="[kpi]"]').value;
                        const useFootfall = !!(card.querySelector('input[name*="[use_footfall]"]') && card.querySelector('input[name*="[use_footfall]"]').checked);
                        const sheetId = card.querySelector('input[name*="[sheet_id]"]').value;
                        if (channelName && sheetId) {
                            data.channels.push({
                                channel_name: channelName,
                                action_description: actionDescription,
                                kpi: kpi,
                                sheet_id: sheetId,
                                use_footfall: useFootfall ? 1 : 0
                            });
                        }
                    });
                    if (data.channels.length === 0) throw new Error('Adicione pelo menos um canal');
                }

                const response = await fetch(endpoint, {
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
                            <h3>✅ Dashboard Multicanal Gerado com Sucesso!</h3>
                            <p><strong>Campanha:</strong> ${result.campaign_key}</p>
                            <p><strong>Nome:</strong> ${result.dashboard_name}</p>
                            <p><strong>Canais:</strong> ${result.channels_count}</p>
                            <p><strong>URL:</strong> <a href="${result.dashboard_url}" target="_blank">${result.dashboard_url}</a></p>
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
    return with_superadmin_sidebar(page_html, active_menu="multichannel")

@app.route('/api/generate-dashboard-multicanal', methods=['POST'])
@superadmin_required_api
def generate_dashboard_multicanal():
    """Gerar dashboard multicanal com múltiplos canais e planilhas distintas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        # Validar campos obrigatórios
        if not data.get('client') or not data.get('campaign_name'):
            return jsonify({"success": False, "message": "Cliente e nome da campanha são obrigatórios"}), 400
        
        if not data.get('channels') or len(data.get('channels', [])) == 0:
            return jsonify({"success": False, "message": "Adicione pelo menos um canal"}), 400
        
        client = data['client']
        campaign_name = data['campaign_name']
        channels_config = data['channels']
        
        # Gerar campaign_key
        campaign_key = generate_campaign_key(client, campaign_name)
        
        logger.info(f"🔄 Gerando dashboard multicanal: {client} - {campaign_name}")
        logger.info(f"📊 Canais configurados: {len(channels_config)}")
        
        # Extrair dados de cada canal
        all_daily_data = []
        all_channels_data = []
        all_publishers = []
        all_strategies = []
        all_insights = []
        total_investment = 0.0
        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        total_video_completions = 0
        total_video_starts = 0
        total_complete_views_contracted = 0
        total_q25 = 0
        total_q50 = 0
        total_q75 = 0
        
        all_footfall_points = []
        footfall_sources = []

        for channel_config in channels_config:
            channel_name = channel_config.get('channel_name', 'Canal')
            action_description = channel_config.get('action_description', '').strip()
            sheet_id = channel_config.get('sheet_id')
            kpi = channel_config.get('kpi', 'CPV')
            if str(channel_name).strip().upper() in ('HHS', 'OHS'):
                channel_name = str(channel_name).strip().upper()
                kpi = 'CPM'  # HHS/OHS: Impressões/CPM
            use_footfall = channel_config.get('use_footfall', 0) in (1, True, '1', 'true', 'True') or ('footfall' in (channel_name or '').lower())
            
            if not sheet_id:
                logger.warning(f"⚠️ Canal {channel_name} sem sheet_id, pulando...")
                continue
            
            try:
                # Criar label do canal: "Canal - Descrição" ou apenas "Canal" se não houver descrição
                channel_display_name = f"{channel_name} - {action_description}" if action_description else channel_name
                logger.info(f"📊 Extraindo dados do canal: {channel_display_name} (KPI: {kpi})")
                
                # Criar config para este canal
                config = CampaignConfig(
                    campaign_key=f"{campaign_key}_{channel_name.lower().replace(' ', '_')}",
                    client=client,
                    campaign_name=campaign_name,
                    sheet_id=sheet_id,
                    channel=channel_name,
                    kpi=kpi
                )
                config.use_footfall = bool(use_footfall)
                
                # Extrair dados
                extractor = RealGoogleSheetsExtractor(config)
                channel_data = extractor.extract_data()
                
                if channel_data:
                    # Adicionar nome do canal (com descrição) aos dados diários
                    daily_data = channel_data.get('daily_data', [])
                    for record in daily_data:
                        record['channel'] = channel_display_name
                        all_daily_data.append(record)
                    
                    # Agregar métricas
                    summary = channel_data.get('campaign_summary', {})
                    contract = channel_data.get('contract', {})
                    
                    total_investment += contract.get('investment', 0) or 0
                    total_spend += summary.get('total_spend', 0) or 0
                    total_impressions += summary.get('total_impressions', 0) or 0
                    total_clicks += summary.get('total_clicks', 0) or 0
                    total_video_completions += summary.get('total_video_completions', 0) or 0
                    total_video_starts += summary.get('total_video_starts', 0) or 0
                    total_complete_views_contracted += contract.get('complete_views_contracted', 0) or 0
                    
                    # Quartis
                    for record in daily_data:
                        total_q25 += record.get('video_25', 0) or 0
                        total_q50 += record.get('video_50', 0) or 0
                        total_q75 += record.get('video_75', 0) or 0
                    
                    # Agregar publishers, strategies e insights
                    channel_publishers = channel_data.get('publishers', [])
                    if channel_publishers:
                        all_publishers.extend(channel_publishers)
                    
                    channel_strategies = channel_data.get('strategies', [])
                    if channel_strategies:
                        all_strategies.extend(channel_strategies)
                    
                    channel_insights = channel_data.get('insights', [])
                    if channel_insights:
                        all_insights.extend(channel_insights)
                    
                    # Armazenar dados do canal (incluindo display_name)
                    all_channels_data.append({
                        'channel_name': channel_name,
                        'channel_display_name': channel_display_name,
                        'action_description': action_description,
                        'kpi': kpi,
                        'sheet_id': sheet_id,
                        'data': channel_data
                    })

                    # Footfall points (se existirem)
                    fpts = channel_data.get("footfall_points") if isinstance(channel_data, dict) else None
                    if isinstance(fpts, list) and fpts:
                        all_footfall_points.extend(fpts)
                        # Uma aba Footfall por planilha/canal marcado
                        footfall_sources.append({
                            "key": channel_display_name,
                            "label": channel_display_name,
                            "channel": channel_name,
                            "points": fpts,
                        })
                    
                    logger.info(f"✅ Canal {channel_name} processado: {len(daily_data)} registros")
                else:
                    logger.warning(f"⚠️ Nenhum dado extraído do canal {channel_name}")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Erro ao processar canal {channel_name}: {error_msg}")
                import traceback
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                
                # Se for o primeiro erro e não houver canais processados, retornar erro detalhado
                if len(all_channels_data) == 0:
                    # Verificar se é erro de planilha não encontrada
                    if "404" in error_msg or "not found" in error_msg.lower() or "Requested entity was not found" in error_msg:
                        return jsonify({
                            "success": False, 
                            "message": f"Planilha não encontrada para o canal '{channel_name}'. Verifique se o ID da planilha ({sheet_id}) está correto e se a planilha está acessível."
                        }), 400
                    else:
                        return jsonify({
                            "success": False, 
                            "message": f"Erro ao processar canal '{channel_name}': {error_msg}"
                        }), 500
                continue
        
        if len(all_channels_data) == 0:
            return jsonify({
                "success": False, 
                "message": "Nenhum canal foi processado com sucesso. Verifique os logs para mais detalhes."
            }), 500
        
        # Calcular métricas consolidadas
        total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        total_vtr = (total_video_completions / total_video_starts * 100) if total_video_starts > 0 else 0.0
        total_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0.0
        pacing = (total_spend / total_investment * 100) if total_investment > 0 else 0.0
        
        # Determinar KPI principal (usar o primeiro canal como referência)
        primary_kpi = channels_config[0].get('kpi', 'CPV')
        
        # Remover duplicatas de publishers e strategies (usando set com tuplas)
        unique_publishers = []
        seen_publishers = set()
        for pub in all_publishers:
            pub_key = (pub.get('publisher') or pub.get('name') or '', pub.get('channel') or '')
            if pub_key not in seen_publishers:
                seen_publishers.add(pub_key)
                unique_publishers.append(pub)
        
        unique_strategies = []
        seen_strategies = set()
        for strat in all_strategies:
            strat_key = (strat.get('strategy') or strat.get('name') or '', strat.get('type') or '')
            if strat_key not in seen_strategies:
                seen_strategies.add(strat_key)
                unique_strategies.append(strat)
        
        # Preparar dados consolidados
        consolidated_data = {
            "campaign_summary": {
                "client": client,
                "campaign": campaign_name,
                "status": "Ativa",
                "total_spend": total_spend,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_video_completions": total_video_completions,
                "total_video_starts": total_video_starts,
                "ctr": total_ctr,
                "vtr": total_vtr,
                "cpm": total_cpm,
                "pacing": pacing
            },
            "contract": {
                "client": client,
                "campaign": campaign_name,
                "investment": total_investment,
                "complete_views_contracted": total_complete_views_contracted,
                "canal": "Multicanal",
                "kpi": primary_kpi
            },
            "daily_data": all_daily_data,
            "channels": all_channels_data,
            "publishers": unique_publishers if unique_publishers else [],
            "strategies": unique_strategies if unique_strategies else [],
            "insights": all_insights if all_insights else [],
            "footfall_points": [],
            "footfall_sources": [],
            "last_updated": datetime.now().isoformat(),
            "data_source": "google_sheets_multicanal"
        }

        # Deduplicar footfall_points por (name,lat,lon)
        if all_footfall_points:
            seen = set()
            dedup = []
            for p in all_footfall_points:
                try:
                    key = (str(p.get("name") or ""), float(p.get("lat")), float(p.get("lon")))
                except Exception:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                dedup.append(p)
            consolidated_data["footfall_points"] = dedup

        # Footfall por canal/planilha (abas dinâmicas no template)
        if footfall_sources:
            consolidated_data["footfall_sources"] = footfall_sources
        
        # Gerar dashboard
        result = generate_dashboard_multicanal_html(campaign_key, client, campaign_name, consolidated_data, primary_kpi)
        
        if not result['success']:
            return jsonify({"success": False, "message": f"Erro ao gerar dashboard: {result.get('error')}"}), 500
        
        # Salvar campanha no banco
        if bq_fs_manager:
            try:
                bq_fs_manager.save_campaign(campaign_key, client, campaign_name, "", "Multicanal", primary_kpi)
                logger.info(f"✅ Campanha multicanal {campaign_key} salva no BigQuery + Firestore")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar no BigQuery/Firestore: {e}")
        
        return jsonify({
            "success": True,
            "message": "Dashboard multicanal gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": result['dashboard_url'],
            "dashboard_url_full": f"{request.host_url.rstrip('/')}{result['dashboard_url']}",
            "channels_count": len(all_channels_data),
            "channels": [ch['channel_name'] for ch in all_channels_data]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/generate-dashboard-multicanal: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500


@app.route('/api/admin/campaigns-picker', methods=['GET'])
@superadmin_required_api
def api_admin_campaigns_picker():
    """Lista campanhas do Firestore para seleção no multicanal (requer sheet_id)."""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        items = []
        docs = bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).limit(500).stream()
        for doc in docs:
            d = doc.to_dict() or {}
            sheet_id = (d.get("sheet_id") or "").strip()
            if not sheet_id:
                continue
            items.append({
                "campaign_key": d.get("campaign_key") or doc.id,
                "client": d.get("client"),
                "campaign_name": d.get("campaign_name"),
                "channel": d.get("channel"),
                "kpi": d.get("kpi"),
                "sheet_id": sheet_id,
                "updated_at": (d.get("updated_at").isoformat() if hasattr(d.get("updated_at"), "isoformat") else (d.get("updated_at") or "")),
            })
        items.sort(key=lambda x: (str(x.get("client") or ""), str(x.get("campaign_name") or "")))
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/generate-dashboard-multicanal-from-existing', methods=['POST'])
@superadmin_required_api
def generate_dashboard_multicanal_from_existing():
    """Gerar multicanal consolidando campanhas já existentes (por campaign_key)."""
    if not bq_fs_manager:
        return jsonify({"success": False, "message": "Firestore não disponível"}), 503
    try:
        data = request.get_json() or {}
        client = data.get("client")
        campaign_name = data.get("campaign_name")
        source_keys = data.get("source_campaign_keys") or []
        if not client or not campaign_name:
            return jsonify({"success": False, "message": "Cliente e nome da campanha são obrigatórios"}), 400
        if not isinstance(source_keys, list) or not source_keys:
            return jsonify({"success": False, "message": "Selecione ao menos um dashboard existente"}), 400

        campaign_key = generate_campaign_key(client, campaign_name)
        logger.info(f"🔄 Gerando multicanal (existentes): {client} - {campaign_name} ({len(source_keys)} fontes)")

        # Consolidadores (mesma lógica do multicanal atual)
        all_daily_data = []
        all_channels_data = []
        all_publishers = []
        all_strategies = []
        all_insights = []
        all_footfall_points = []
        footfall_sources = []
        total_investment = 0.0
        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        total_video_completions = 0
        total_video_starts = 0
        total_complete_views_contracted = 0
        total_q25 = 0
        total_q50 = 0
        total_q75 = 0

        # Carregar campanhas fonte do Firestore (sheet_id, channel, kpi)
        sources = []
        for sk in source_keys:
            sk_norm = (sk or "").strip()
            if not sk_norm:
                continue
            doc = bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).document(sk_norm).get()
            if not doc.exists:
                continue
            c = doc.to_dict() or {}
            sheet_id = (c.get("sheet_id") or "").strip()
            if not sheet_id:
                continue
            sources.append({
                "campaign_key": sk_norm,
                "client": c.get("client"),
                "campaign_name": c.get("campaign_name"),
                "channel": c.get("channel") or "Canal",
                "kpi": c.get("kpi") or "CPV",
                "sheet_id": sheet_id,
                "use_footfall": bool(c.get("use_footfall")),
            })

        if not sources:
            return jsonify({"success": False, "message": "Nenhuma fonte válida (com sheet_id) encontrada"}), 400

        for src in sources:
            channel_name = src["channel"]
            channel_display_name = f"{channel_name} — {src.get('campaign_name') or src['campaign_key']}"
            kpi = src["kpi"]
            if str(channel_name).strip().upper() in ('HHS', 'OHS'):
                channel_name = str(channel_name).strip().upper()
                channel_display_name = f"{channel_name} — {src.get('campaign_name') or src['campaign_key']}"
                kpi = 'CPM'  # HHS/OHS: Impressões/CPM
            sheet_id = src["sheet_id"]
            try:
                config = CampaignConfig(
                    campaign_key=f"{campaign_key}_{src['campaign_key']}",
                    client=client,
                    campaign_name=campaign_name,
                    sheet_id=sheet_id,
                    channel=channel_name,
                    kpi=kpi,
                )
                config.use_footfall = bool(src.get("use_footfall")) or ("footfall" in (channel_name or "").lower())
                extractor = RealGoogleSheetsExtractor(config)
                channel_data = extractor.extract_data()
                if not channel_data:
                    continue

                daily_data = channel_data.get("daily_data", []) or []
                for record in daily_data:
                    record["channel"] = channel_display_name
                    all_daily_data.append(record)

                summary = channel_data.get("campaign_summary", {}) or {}
                contract = channel_data.get("contract", {}) or {}
                total_investment += contract.get("investment", 0) or 0
                total_spend += summary.get("total_spend", 0) or 0
                total_impressions += summary.get("total_impressions", 0) or 0
                total_clicks += summary.get("total_clicks", 0) or 0
                total_video_completions += summary.get("total_video_completions", 0) or 0
                total_video_starts += summary.get("total_video_starts", 0) or 0
                total_complete_views_contracted += contract.get("complete_views_contracted", 0) or 0

                for record in daily_data:
                    total_q25 += record.get("video_25", 0) or 0
                    total_q50 += record.get("video_50", 0) or 0
                    total_q75 += record.get("video_75", 0) or 0

                pubs = channel_data.get("publishers", []) or []
                if pubs:
                    all_publishers.extend(pubs)
                strats = channel_data.get("strategies", []) or []
                if strats:
                    all_strategies.extend(strats)
                ins = channel_data.get("insights", []) or []
                if ins:
                    all_insights.extend(ins)

                all_channels_data.append({
                    "channel_name": channel_name,
                    "channel_display_name": channel_display_name,
                    "action_description": src.get("campaign_name") or "",
                    "kpi": kpi,
                    "sheet_id": sheet_id,
                    "source_campaign_key": src["campaign_key"],
                    "data": channel_data,
                })

                fpts = channel_data.get("footfall_points") if isinstance(channel_data, dict) else None
                if isinstance(fpts, list) and fpts:
                    all_footfall_points.extend(fpts)
                    footfall_sources.append({
                        "key": channel_display_name,
                        "label": channel_display_name,
                        "channel": channel_name,
                        "points": fpts,
                    })
            except Exception as ex:
                logger.warning(f"⚠️ Fonte {src['campaign_key']} falhou: {ex}")
                continue

        if not all_channels_data:
            return jsonify({"success": False, "message": "Nenhuma fonte foi processada com sucesso"}), 500

        total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        total_vtr = (total_video_completions / total_video_starts * 100) if total_video_starts > 0 else 0.0
        total_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0.0
        pacing = (total_spend / total_investment * 100) if total_investment > 0 else 0.0
        primary_kpi = all_channels_data[0].get("kpi") or "CPV"

        consolidated_data = {
            "campaign_summary": {
                "client": client,
                "campaign": campaign_name,
                "status": "Ativa",
                "total_spend": total_spend,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_video_completions": total_video_completions,
                "total_video_starts": total_video_starts,
                "ctr": total_ctr,
                "vtr": total_vtr,
                "cpm": total_cpm,
                "pacing": pacing,
                "q25": total_q25,
                "q50": total_q50,
                "q75": total_q75,
            },
            "contract": {
                "client": client,
                "campaign": campaign_name,
                "investment": total_investment,
                "complete_views_contracted": total_complete_views_contracted,
                "canal": "Multicanal",
                "kpi": primary_kpi,
            },
            "daily_data": all_daily_data,
            "channels": all_channels_data,
            "publishers": all_publishers,
            "strategies": all_strategies,
            "insights": all_insights,
            "footfall_points": [],
            "footfall_sources": [],
            "last_updated": datetime.now().isoformat(),
            "data_source": "multicanal_from_existing",
            "sources": [s["campaign_key"] for s in sources],
        }

        if all_footfall_points:
            seen = set()
            dedup = []
            for p in all_footfall_points:
                try:
                    key = (str(p.get("name") or ""), float(p.get("lat")), float(p.get("lon")))
                except Exception:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                dedup.append(p)
            consolidated_data["footfall_points"] = dedup

        if footfall_sources:
            consolidated_data["footfall_sources"] = footfall_sources

        result = generate_dashboard_multicanal_html(campaign_key, client, campaign_name, consolidated_data, primary_kpi)
        if not result.get("success"):
            return jsonify({"success": False, "message": result.get("error") or "Falha ao gerar HTML"}), 500

        # Persistir campanha multicanal (sem sheet_id, como o padrão atual)
        try:
            bq_fs_manager.save_campaign(campaign_key, client, campaign_name, "", "Multicanal", primary_kpi)
            # Guardar fontes para auditoria
            bq_fs_manager.fs_client.collection(bq_fs_manager.campaigns_collection).document(campaign_key).set({
                "channel": "Multicanal",
                "sheet_id": "",
                "multicanal_sources": [s["campaign_key"] for s in sources],
                "updated_at": datetime.now(),
            }, merge=True)
        except Exception as e:
            logger.warning(f"⚠️ Falha ao persistir campanha multicanal: {e}")

        return jsonify({
            "success": True,
            "message": "Dashboard multicanal (existentes) gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": result["dashboard_url"],
            "dashboard_url_full": f"{request.host_url.rstrip('/')}{result['dashboard_url']}",
            "sources_count": len(sources),
        })
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/generate-dashboard-multicanal-from-existing: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def generate_dashboard_multicanal_html(campaign_key: str, client: str, campaign_name: str, consolidated_data: Dict[str, Any], kpi: str) -> Dict[str, Any]:
    """Gerar HTML do dashboard multicanal"""
    try:
        # Template multicanal com abas de Footfall por planilha/canal (data-driven).
        footfall_sources = consolidated_data.get("footfall_sources") if isinstance(consolidated_data, dict) else None
        has_footfall_sources = isinstance(footfall_sources, list) and len(footfall_sources) > 0

        if has_footfall_sources:
            template_path = 'static/dash_multicanal_footfall_tabs_template.html'
        else:
            # Sem Footfall: manter template atual por KPI
            template_path = 'static/dash_generic_template.html'
            if kpi.upper() == 'CPM':
                template_path = 'static/dash_remarketing_cpm_template.html'
            elif kpi.upper() == 'CPE':
                template_path = 'static/dash_generic_cpe_template.html'
        
        if not os.path.exists(template_path):
            raise Exception(f"Template não encontrado: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Converter dados para JSON e inserir no HTML
        data_json = json.dumps(consolidated_data, ensure_ascii=False, default=str)
        embedded_data_script = f'<script>window.EMBEDDED_CAMPAIGN_DATA = {data_json};</script>'
        
        # Inserir dados embutidos
        if '</head>' in dashboard_content:
            dashboard_content = dashboard_content.replace('</head>', f'{embedded_data_script}\n</head>')
        elif '<body>' in dashboard_content:
            dashboard_content = dashboard_content.replace('<body>', f'<body>\n{embedded_data_script}')
        
        # Substituir placeholders
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        dashboard_content = dashboard_content.replace('{{CLIENT_NAME}}', client)
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        dashboard_content = dashboard_content.replace('{{API_ENDPOINT}}', get_api_endpoint())
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard multicanal de performance para a campanha {campaign_name} do cliente {client}')
        dashboard_content = dashboard_content.replace('{{PRIMARY_CHANNEL}}', 'Multicanal')
        
        # Salvar no Google Cloud Storage (backup)
        try:
            from google.cloud import storage
            client_storage = storage.Client()
            bucket = client_storage.bucket('south-media-ia-database-452311')
            
            # Upload do dashboard para GCS como backup
            dashboard_filename = f"dash_{campaign_key}.html"
            gcs_path = f"dashboards/{dashboard_filename}"
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(dashboard_content, content_type='text/html')
            
            logger.info(f"💾 Dashboard multicanal persistido no GCS: {gcs_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar dashboard multicanal no GCS: {e}")
        
        logger.info(f"✅ Dashboard multicanal configurado para: {campaign_key}")
        
        return {
            "success": True,
            "campaign_key": campaign_key,
            "dashboard_url": f"/api/dashboard/{campaign_key}",
            "dashboard_url_full": f"{get_api_endpoint()}/api/dashboard/{campaign_key}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard multicanal: {e}")
        return {
            "success": False,
            "error": str(e)
        }
