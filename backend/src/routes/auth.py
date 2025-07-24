from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import check_password_hash
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__)

# Usuário administrativo hardcoded para demonstração
ADMIN_USER = {
    "id": 1,
    "username": "g4trader",
    "password_hash": "$2b$12$LQv3c1yqBwlVHpPjrCeyAuVdcGfNp6vm9EuYU2TNXW7aGAMCOeCbq",  # senha: g4trader@M4nu5
    "email": "admin@southmedia.com.br",
    "role": "admin",
}

SECRET_KEY = os.getenv("SECRET_KEY", "asdf#FGSgvasgf$5$WGT")
ALLOWED_ORIGINS = ["https://dash.iasouth.tech"]

def cors_response(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "POST,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return cors_response(make_response("", 200))

    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            response = jsonify({"detail": "Username e password são obrigatórios"})
            return cors_response(make_response(response, 400))

        if username == ADMIN_USER["username"] and password == "g4trader@M4nu5":
            payload = {
                "user_id": ADMIN_USER["id"],
                "role": ADMIN_USER["role"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            response = jsonify({"access_token": token, "user": ADMIN_USER})
            return cors_response(make_response(response, 200))
        else:
            response = jsonify({"detail": "Credenciais inválidas"})
            return cors_response(make_response(response, 401))

    except Exception as e:
        print(f"Erro interno ao fazer login: {str(e)}")
        response = jsonify({"detail": "Erro interno"})
        return cors_response(make_response(response, 500))


@auth_bp.route("/me", methods=["GET", "OPTIONS"])
def me():
    if request.method == "OPTIONS":
        return cors_response(make_response("", 200))

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        response = jsonify({"detail": "Token de acesso requerido"})
        return cors_response(make_response(response, 401))

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        role = payload.get("role")

        if user_id == ADMIN_USER["id"] and role == ADMIN_USER["role"]:
            response = jsonify(ADMIN_USER)
            return cors_response(make_response(response, 200))
        else:
            response = jsonify({"detail": "Token inválido ou usuário não encontrado"})
            return cors_response(make_response(response, 401))

    except jwt.ExpiredSignatureError:
        response = jsonify({"detail": "Token expirado"})
        return cors_response(make_response(response, 401))
    except jwt.InvalidTokenError:
        response = jsonify({"detail": "Token inválido"})
        return cors_response(make_response(response, 401))
    except Exception as e:
        print(f"Erro interno ao validar token: {str(e)}")
        response = jsonify({"detail": "Erro interno"})
        return cors_response(make_response(response, 500))


