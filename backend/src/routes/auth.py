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

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200  # Permitir preflight CORS

    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'detail': 'Username e password são obrigatórios'}), 400

        if username == ADMIN_USER['username'] and password == 'g4trader@M4nu5':
            payload = {
                'user_id': ADMIN_USER['id'],
                'role': ADMIN_USER['role'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'access_token': token})
        else:
            return jsonify({'detail': 'Credenciais inválidas'}), 401

    except Exception as e:
        return jsonify({'detail': 'Erro interno'}), 500
