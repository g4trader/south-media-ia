from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Usuário administrativo hardcoded para demonstração
ADMIN_USER = {
    'id': 1,
    'username': 'g4trader',
    'password_hash': '$2b$12$LQv3c1yqBwlVHpPjrCeyAuVdcGfNp6vm9EuYU2TNXW7aGAMCOeCbq',  # g4trader@M4nu5
    'email': 'admin@southmedia.com.br',
    'role': 'admin'
}

SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'detail': 'Username e password são obrigatórios'}), 400
        
        # Verificar credenciais
        if username == ADMIN_USER['username'] and password == 'g4trader@M4nu5':
            # Gerar token JWT
            payload = {
                'user_id': ADMIN_USER['id'],
                'username': ADMIN_USER['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'access_token': token,
                'token_type': 'bearer',
                'user': {
                    'id': ADMIN_USER['id'],
                    'username': ADMIN_USER['username'],
                    'email': ADMIN_USER['email'],
                    'role': ADMIN_USER['role']
                }
            }), 200
        else:
            return jsonify({'detail': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'detail': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'detail': 'Token não fornecido'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id == ADMIN_USER['id']:
                return jsonify({
                    'id': ADMIN_USER['id'],
                    'username': ADMIN_USER['username'],
                    'email': ADMIN_USER['email'],
                    'role': ADMIN_USER['role']
                }), 200
            else:
                return jsonify({'detail': 'Usuário não encontrado'}), 404
                
        except jwt.ExpiredSignatureError:
            return jsonify({'detail': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'detail': 'Token inválido'}), 401
            
    except Exception as e:
        return jsonify({'detail': 'Erro interno do servidor'}), 500

