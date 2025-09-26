#!/usr/bin/env python3
"""
MVP Dashboard Builder para Google Cloud Run
Versão otimizada do persistent_server.py para produção
"""

import os
import sys
import logging
import json
import sqlite3
import tempfile
import subprocess
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

app = Flask(__name__)
CORS(app)

# Configuração do Cloud Run
PORT = int(os.environ.get('PORT', 8080))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

def git_commit_and_push(file_path: str, commit_message: str) -> bool:
    """Fazer commit e push automático de um arquivo para o Git"""
    try:
        # Verificar se estamos em um repositório Git
        try:
            subprocess.run(['git', 'status'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Não é um repositório Git, pulando commit automático")
            return False
        
        # Configurar Git (usar token do GitHub se disponível)
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            # Configurar autenticação
            subprocess.run([
                'git', 'config', '--global', 'user.name', 'Cloud Run Bot'
            ], check=True, capture_output=True)
            subprocess.run([
                'git', 'config', '--global', 'user.email', 'cloudrun@automatizar.com'
            ], check=True, capture_output=True)
            subprocess.run([
                'git', 'remote', 'set-url', 'origin', 
                f'https://{github_token}@github.com/g4trader/south-media-ia.git'
            ], check=True, capture_output=True)
        
        # Adicionar arquivo
        logger.info(f"🔧 Executando: git add {file_path}")
        result = subprocess.run(['git', 'add', file_path], check=True, capture_output=True, text=True)
        logger.info(f"✅ git add executado com sucesso")
        
        # Commit
        logger.info(f"🔧 Executando: git commit -m '{commit_message}'")
        result = subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True, text=True)
        logger.info(f"✅ git commit executado com sucesso: {result.stdout}")
        
        # Push
        logger.info(f"🔧 Executando: git push origin main")
        result = subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
        logger.info(f"✅ git push executado com sucesso: {result.stdout}")
        
        logger.info(f"✅ Git commit/push realizado: {file_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro no Git: {e.stderr if e.stderr else str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado no Git: {e}")
        return False

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///campaigns.db')

class CloudRunDatabaseManager:
    """Gerenciador de banco para Cloud Run com persistência"""
    
    def __init__(self):
        # Usar diretório persistente do Cloud Run
        self.db_path = os.path.join('/tmp', 'campaigns.db')
        self.gcs_bucket = 'south-media-ia-database-452311'
        self.gcs_db_path = 'campaigns.db'
        self.init_database()
        self._load_from_gcs()
    
    def init_database(self):
        """Inicializar banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela de campanhas
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
            
            # Criar tabela de cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_data (
                    campaign_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_key) REFERENCES campaigns (campaign_key)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de dados inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco: {e}")
    
    def _load_from_gcs(self):
        """Carregar banco de dados do Google Cloud Storage"""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_db_path)
            
            if blob.exists():
                blob.download_to_filename(self.db_path)
                logger.info("✅ Banco de dados carregado do GCS")
            else:
                logger.info("📝 Banco de dados não encontrado no GCS, criando novo")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar do GCS: {e}")
    
    def _save_to_gcs(self):
        """Salvar banco de dados no Google Cloud Storage"""
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(self.gcs_db_path)
            
            blob.upload_from_filename(self.db_path)
            logger.info("✅ Banco de dados salvo no GCS")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no GCS: {e}")
    
    def get_campaign(self, campaign_key: str) -> Optional[Dict]:
        """Obter campanha por chave"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM campaigns WHERE campaign_key = ?', (campaign_key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return {
                    'campaign_key': row[0],
                    'client': row[1],
                    'campaign_name': row[2],
                    'sheet_id': row[3],
                    'channel': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter campanha: {e}")
            return None
    
    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, 
                     sheet_id: str, channel: str = None) -> bool:
        """Salvar nova campanha"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO campaigns 
                (campaign_key, client, campaign_name, sheet_id, channel, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (campaign_key, client, campaign_name, sheet_id, channel))
            
            conn.commit()
            conn.close()
            
            # Salvar no GCS após commit local
            self._save_to_gcs()
            
            logger.info(f"✅ Campanha salva: {campaign_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar campanha: {e}")
            return False
    
    def list_campaigns(self) -> list:
        """Listar todas as campanhas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM campaigns ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            
            conn.close()
            
            campaigns = []
            for row in rows:
                campaigns.append({
                    'campaign_key': row[0],
                    'client': row[1],
                    'campaign_name': row[2],
                    'sheet_id': row[3],
                    'channel': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar campanhas: {e}")
            return []
    
    def get_cached_data(self, campaign_key: str, max_age_hours: int = 1) -> Optional[Dict]:
        """Obter dados do cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cursor.execute('''
                SELECT data FROM cache_data 
                WHERE campaign_key = ? AND cached_at > ?
            ''', (campaign_key, cutoff_time))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter cache: {e}")
            return None
    
    def update_cache(self, campaign_key: str, data: Dict) -> bool:
        """Atualizar cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_data (campaign_key, data, cached_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (campaign_key, json.dumps(data)))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar cache: {e}")
            return False

# Inicializar gerenciador de banco
db_manager = CloudRunDatabaseManager()

class CampaignConfig:
    """Configuração de campanha"""
    def __init__(self, campaign_key: str, client: str, campaign_name: str, 
                 sheet_id: str, channel: str = None):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign_name = campaign_name
        self.sheet_id = sheet_id
        self.channel = channel

@app.route('/')
def home():
    """Página inicial"""
    return jsonify({
        "service": "MVP Dashboard Builder",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate-dashboard",
            "data": "/api/<campaign_key>/data",
            "list": "/api/list-campaigns",
            "generator": "/test-generator"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Cloud Run"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mvp-dashboard-builder"
    })

@app.route('/api/generate-dashboard', methods=['POST'])
def generate_dashboard():
    """Gerar dashboard com dados reais"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        # Validar campos obrigatórios
        required_fields = ['client', 'campaign_name', 'sheet_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Campo obrigatório: {field}"}), 400
        
        # Gerar campaign_key automaticamente se não fornecido
        campaign_key = data.get('campaign_key')
        if not campaign_key:
            import re
            client_slug = re.sub(r'[^a-zA-Z0-9]', '_', data['client'].lower())
            campaign_slug = re.sub(r'[^a-zA-Z0-9]', '_', data['campaign_name'].lower())
            campaign_key = f"{client_slug}_{campaign_slug}"
        client = data['client']
        campaign_name = data['campaign_name']
        sheet_id = data['sheet_id']
        channel = data.get('channel', 'Video Programática')
        
        logger.info(f"🔄 Gerando dashboard: {campaign_key}")
        
        # Salvar campanha no banco
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel):
            return jsonify({"success": False, "message": "Erro ao salvar campanha"}), 500
        
        # Gerar arquivo HTML
        dashboard_filename = f"dash_{campaign_key}.html"
        dashboard_path = os.path.join('static', dashboard_filename)
        
        # Ler template
        template_path = os.path.join('static', 'dash_generic_template.html')
        if not os.path.exists(template_path):
            return jsonify({"success": False, "message": "Template não encontrado"}), 500
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Substituir placeholders
        dashboard_content = template_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        dashboard_content = dashboard_content.replace('{{CLIENT_NAME}}', client)
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        dashboard_content = dashboard_content.replace('{{API_ENDPOINT}}', f'https://mvp-dashboard-builder-609095880025.us-central1.run.app')
        
        # Substituir placeholders adicionais
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard de performance para a campanha {campaign_name} do cliente {client}')
        dashboard_content = dashboard_content.replace('{{PRIMARY_CHANNEL}}', channel)
        
        # Salvar dashboard
        os.makedirs('static', exist_ok=True)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        logger.info(f"✅ Dashboard gerado: {dashboard_filename}")
        
        # Commit e push para o Git (para deploy no Vercel)
        logger.info(f"🔧 ANTES DE CHAMAR git_commit_and_push")
        logger.info(f"🔧 Iniciando processo de commit automático para: {dashboard_path}")
        try:
            result = git_commit_and_push(dashboard_path, f"feat: Add dashboard for {campaign_name} ({campaign_key})")
            if result:
                logger.info(f"✅ Dashboard {dashboard_filename} commitado e enviado para o Git.")
            else:
                logger.warning(f"⚠️ Commit automático falhou para: {dashboard_filename}")
        except Exception as e:
            logger.error(f"❌ Erro ao commitar e enviar dashboard para o Git: {e}")
            # Continuar mesmo com erro no Git, mas logar
        
        return jsonify({
            "success": True,
            "message": "Dashboard gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": f"/static/{dashboard_filename}",
            "file_path": dashboard_path
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha específica"""
    try:
        campaign = db_manager.get_campaign(campaign_key)
        if not campaign:
            return jsonify({"success": False, "message": f"Campanha '{campaign_key}' não encontrada"}), 404
        
        # Sempre extrair dados frescos da planilha (sem cache)
        logger.info(f"🔄 Extraindo dados frescos da planilha para: {campaign_key}")
        
        config = CampaignConfig(
            campaign_key=campaign_key,
            client=campaign['client'],
            campaign_name=campaign['campaign_name'],
            sheet_id=campaign['sheet_id'],
            channel=campaign.get('channel')
        )
        
        extractor = RealGoogleSheetsExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({"success": False, "message": "Falha ao extrair dados da planilha"}), 500
        
        # Atualizar cache com os novos dados
        db_manager.update_cache(campaign_key, extracted_data)
        
        return jsonify({"success": True, "data": extracted_data})
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados da campanha {campaign_key}: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/list-campaigns', methods=['GET'])
def list_campaigns():
    """Listar todas as campanhas"""
    try:
        campaigns = db_manager.list_campaigns()
        return jsonify({"success": True, "campaigns": campaigns})
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/test-generator')
def test_generator():
    """Interface para testar o gerador"""
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gerador de Dashboards - MVP</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0F0F23 0%, #16213E 50%, #1A1A2E 100%);
                color: white;
                margin: 0;
                padding: 2rem;
                min-height: 100vh;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
            }
            .form-group {
                margin-bottom: 1.5rem;
            }
            label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 600;
            }
            input, select {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.06);
                color: white;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 1rem;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
            }
            button:hover {
                opacity: 0.9;
            }
            .result {
                margin-top: 2rem;
                padding: 1rem;
                border-radius: 8px;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Gerador de Dashboards - MVP</h1>
            <p>Crie dashboards programáticos em segundos!</p>
            
            <form id="generatorForm">
                <div class="form-group">
                    <label for="campaign_key">Campaign Key (identificador único):</label>
                    <input type="text" id="campaign_key" name="campaign_key" placeholder="ex: cliente_campanha" required>
                </div>
                
                <div class="form-group">
                    <label for="client">Cliente:</label>
                    <input type="text" id="client" name="client" placeholder="ex: Copacol" required>
                </div>
                
                <div class="form-group">
                    <label for="campaign_name">Nome da Campanha:</label>
                    <input type="text" id="campaign_name" name="campaign_name" placeholder="ex: Institucional 30s" required>
                </div>
                
                <div class="form-group">
                    <label for="sheet_id">ID da Planilha Google Sheets:</label>
                    <input type="text" id="sheet_id" name="sheet_id" placeholder="ex: 1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8" required>
                </div>
                
                <div class="form-group">
                    <label for="channel">Canal:</label>
                    <select id="channel" name="channel">
                        <option value="Video Programática">Video Programática</option>
                        <option value="YouTube">YouTube</option>
                        <option value="LinkedIn">LinkedIn</option>
                        <option value="Facebook">Facebook</option>
                    </select>
                </div>
                
                <button type="submit">🚀 Gerar Dashboard</button>
            </form>
            
            <div id="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('generatorForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = Object.fromEntries(formData.entries());
                
                try {
                    const response = await fetch('/api/generate-dashboard', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const resultDiv = document.getElementById('result');
                    
                    if (result.success) {
                        resultDiv.innerHTML = `
                            <h3>✅ Dashboard Gerado com Sucesso!</h3>
                            <p><strong>Nome:</strong> ${result.dashboard_name}</p>
                            <p><strong>URL:</strong> <a href="${result.dashboard_url}" target="_blank">${result.dashboard_url}</a></p>
                            <p><strong>Arquivo:</strong> ${result.file_path}</p>
                        `;
                        resultDiv.style.display = 'block';
                    } else {
                        resultDiv.innerHTML = `<h3>❌ Erro:</h3><p>${result.message}</p>`;
                        resultDiv.style.display = 'block';
                    }
                } catch (error) {
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = `<h3>❌ Erro de Conexão:</h3><p>${error.message}</p>`;
                    resultDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/static/<filename>')
def serve_static(filename):
    """Servir arquivos estáticos"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    logger.info(f"🚀 Iniciando MVP Dashboard Builder na porta {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
