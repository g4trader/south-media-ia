"""
Sistema de Autenticação Multi-Cliente
South Media Dashboard
"""

import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)

class ClientAuthManager:
    """Gerenciador de autenticação para sistema multi-cliente"""
    
    def __init__(self, bigquery_client, secret_key):
        self.bq_client = bigquery_client
        self.secret_key = secret_key
        self.token_expiry_hours = 24
        
    def generate_client_token(self, client_id):
        """
        Gera token JWT para um cliente específico
        """
        try:
            # Verificar se cliente existe e está ativo
            if not self._validate_client_exists(client_id):
                return None
                
            # Payload do token
            payload = {
                'client_id': client_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
                'type': 'client_access'
            }
            
            # Gerar token
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            logger.info(f"Token gerado para cliente: {client_id}")
            return token
            
        except Exception as e:
            logger.error(f"Erro ao gerar token para cliente {client_id}: {str(e)}")
            return None
    
    def validate_client_token(self, token):
        """
        Valida token JWT e retorna client_id se válido
        """
        try:
            # Decodificar token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            client_id = payload.get('client_id')
            token_type = payload.get('type')
            
            # Validações básicas
            if not client_id or token_type != 'client_access':
                return None
                
            # Verificar se cliente ainda está ativo
            if not self._validate_client_exists(client_id):
                return None
                
            return client_id
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro ao validar token: {str(e)}")
            return None
    
    def _validate_client_exists(self, client_id):
        """
        Verifica se cliente existe e está ativo no BigQuery
        """
        try:
            query = """
            SELECT client_id, status 
            FROM `automatizar-452311.south_media_campaigns.clients` 
            WHERE client_id = @client_id AND status = 'active'
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
                ]
            )
            
            results = self.bq_client.query(query, job_config=job_config)
            
            # Se encontrou resultado, cliente existe e está ativo
            for row in results:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erro ao validar cliente {client_id}: {str(e)}")
            return False
    
    def get_client_info(self, client_id):
        """
        Busca informações do cliente no BigQuery
        """
        try:
            query = """
            SELECT 
                client_id,
                client_name,
                client_email,
                client_logo_url,
                contact_person,
                timezone,
                settings
            FROM `automatizar-452311.south_media_campaigns.clients` 
            WHERE client_id = @client_id AND status = 'active'
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
                ]
            )
            
            results = self.bq_client.query(query, job_config=job_config)
            
            for row in results:
                return {
                    'client_id': row.client_id,
                    'client_name': row.client_name,
                    'client_email': row.client_email,
                    'client_logo_url': row.client_logo_url,
                    'contact_person': row.contact_person,
                    'timezone': row.timezone,
                    'settings': row.settings
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar info do cliente {client_id}: {str(e)}")
            return None

# Instância global do gerenciador de auth
auth_manager = None

def init_auth_manager(bigquery_client, secret_key):
    """Inicializa o gerenciador de autenticação"""
    global auth_manager
    auth_manager = ClientAuthManager(bigquery_client, secret_key)

def require_client_auth(f):
    """
    Decorator para proteger rotas que requerem autenticação de cliente
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se auth_manager foi inicializado
        if not auth_manager:
            return jsonify({'error': 'Sistema de autenticação não inicializado'}), 500
        
        # Buscar token no header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de acesso requerido'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validar token
        client_id = auth_manager.validate_client_token(token)
        if not client_id:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        # Verificar se client_id da URL corresponde ao do token
        url_client_id = kwargs.get('client_id')
        if url_client_id and url_client_id != client_id:
            return jsonify({'error': 'Acesso negado para este cliente'}), 403
        
        # Adicionar client_id ao contexto da requisição
        request.client_id = client_id
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_client_access(client_id):
    """
    Valida se o cliente autenticado tem acesso aos dados solicitados
    """
    if not hasattr(request, 'client_id'):
        return False
    
    return request.client_id == client_id

def get_current_client_id():
    """
    Retorna o client_id do cliente autenticado na requisição atual
    """
    return getattr(request, 'client_id', None)

def generate_client_access_url(client_id, base_url="https://dashboard.southmedia.com.br"):
    """
    Gera URL de acesso personalizada para o cliente
    """
    if not auth_manager:
        return None
    
    token = auth_manager.generate_client_token(client_id)
    if not token:
        return None
    
    return f"{base_url}/client/{client_id}?token={token}"

def create_client_session(client_id):
    """
    Cria sessão para cliente (usado em rotas de login)
    """
    if not auth_manager:
        return None
    
    # Gerar token
    token = auth_manager.generate_client_token(client_id)
    if not token:
        return None
    
    # Buscar informações do cliente
    client_info = auth_manager.get_client_info(client_id)
    if not client_info:
        return None
    
    return {
        'token': token,
        'client_info': client_info,
        'expires_in': auth_manager.token_expiry_hours * 3600  # em segundos
    }

# Middleware para logging de acesso
def log_client_access():
    """
    Middleware para registrar acessos de clientes
    """
    client_id = get_current_client_id()
    if client_id:
        logger.info(f"Acesso do cliente {client_id} - {request.method} {request.path}")

# Utilitários para validação de dados
def ensure_client_data_isolation(query, client_id):
    """
    Garante que queries incluam filtro de client_id para isolamento de dados
    """
    if 'WHERE' in query.upper():
        if 'client_id' not in query.lower():
            # Adicionar filtro de client_id se não existir
            query = query.replace('WHERE', f'WHERE client_id = "{client_id}" AND')
    else:
        # Adicionar cláusula WHERE com filtro de client_id
        query += f' WHERE client_id = "{client_id}"'
    
    return query

