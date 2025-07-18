import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import bigquery
import logging

# Importar módulos do sistema multi-cliente
from src.routes.client_dashboard import client_bp, init_bigquery_client
from src.auth.client_auth import init_auth_manager

# Manter compatibilidade com sistema antigo
from src.models.user import db
from src.routes.user import user_bp
from src.routes.dashboard import dashboard_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../static')

# Configuração
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'south-media-secret-key-2024')

# Configurar CORS para múltiplos domínios
CORS(app, origins=[
    'http://localhost:3000',
    'https://south-media-dashboard.vercel.app',
    'https://dashboard.southmedia.com.br',
    '*'  # Para desenvolvimento - remover em produção
])

# Inicializar BigQuery para sistema multi-cliente
try:
    bq_client = bigquery.Client(project='automatizar-452311')
    init_bigquery_client(bq_client)
    init_auth_manager(bq_client, app.config['SECRET_KEY'])
    logger.info("BigQuery client inicializado com sucesso")
    BIGQUERY_ENABLED = True
except Exception as e:
    logger.error(f"Erro ao inicializar BigQuery: {str(e)}")
    BIGQUERY_ENABLED = False
    # Em desenvolvimento, continuar sem BigQuery
    if os.environ.get('FLASK_ENV') != 'development':
        logger.warning("BigQuery não disponível - algumas funcionalidades podem não funcionar")

# Registrar blueprints
# Sistema multi-cliente (novo)
app.register_blueprint(client_bp)

# Sistema antigo (compatibilidade)
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Configuração do banco SQLite (sistema antigo)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({
        "message": "South Media Dashboard API - Multi-Cliente",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Dashboard multi-cliente com BigQuery",
            "Autenticação por token JWT",
            "APIs dinâmicas por cliente",
            "Sistema legado compatível"
        ],
        "bigquery_status": "enabled" if BIGQUERY_ENABLED else "disabled"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bigquery": "connected" if BIGQUERY_ENABLED else "disconnected",
        "database": "sqlite_connected"
    })

# Endpoint para listar clientes disponíveis (para desenvolvimento)
@app.route('/api/clients', methods=['GET'])
def list_clients():
    """Lista clientes disponíveis (apenas para desenvolvimento)"""
    if not BIGQUERY_ENABLED:
        return jsonify({'error': 'BigQuery não disponível'}), 503
    
    try:
        query = """
        SELECT client_id, client_name, status, created_at
        FROM `automatizar-452311.south_media_campaigns.clients`
        WHERE status = 'active'
        ORDER BY client_name
        """
        
        results = bq_client.query(query)
        clients = []
        
        for row in results:
            clients.append({
                'client_id': row.client_id,
                'client_name': row.client_name,
                'status': row.status,
                'created_at': row.created_at.isoformat()
            })
        
        return jsonify({
            'clients': clients,
            'total': len(clients)
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Middleware para logging de requisições
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")

# Handler de erro global
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Erro não tratado: {str(error)}")
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': str(error) if app.debug else 'Erro interno'
    }), 500

# Rota para servir arquivos estáticos (sistema antigo)
from flask import send_from_directory

@app.route('/static/<path:path>')
def serve_static(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando South Media Dashboard API na porta {port}")
    logger.info(f"BigQuery Status: {'Enabled' if BIGQUERY_ENABLED else 'Disabled'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

