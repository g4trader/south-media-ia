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

app = Flask(__name__)
CORS(app)

# Configuração do Cloud Run
PORT = int(os.environ.get('PORT', 8080))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

class CampaignConfig:
    """Configuração de uma campanha"""
    def __init__(self, campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: Optional[str] = None, tabs: Optional[Dict] = None):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign_name = campaign_name
        self.sheet_id = sheet_id
        self.channel = channel or "Video Programática"
        self.tabs = tabs or {
            'report': 'Report',
            'contract': 'Informações de contrato',
            'publishers': 'Lista de publishers',
            'strategies': 'Estratégias'
        }

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

    def save_campaign(self, campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: Optional[str] = None) -> bool:
        """Salvar ou atualizar uma campanha no banco de dados"""
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

    def get_campaign(self, campaign_key: str) -> Optional[Dict[str, Any]]:
        """Obter uma campanha do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT campaign_key, client, campaign_name, sheet_id, channel, created_at, updated_at
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
                    'created_at': result[5],
                    'updated_at': result[6]
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

# Instanciar gerenciador de banco
db_manager = CloudRunDatabaseManager()

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

def generate_dashboard(campaign_key: str, client: str, campaign_name: str, sheet_id: str, channel: str = "Video Programática") -> Dict[str, Any]:
    """Gerar dashboard a partir do template"""
    try:
        # Carregar template
        template_path = 'static/dash_generic_template.html'
        if not os.path.exists(template_path):
            raise Exception(f"Template não encontrado: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Substituir placeholders
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_KEY_PLACEHOLDER}}', campaign_key)
        dashboard_content = dashboard_content.replace('{{CLIENT_NAME}}', client)
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_NAME}}', campaign_name)
        dashboard_content = dashboard_content.replace('{{API_ENDPOINT}}', f'https://mvp-dashboard-builder-609095880025.us-central1.run.app')
        
        # Substituir placeholders adicionais
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_STATUS}}', 'Ativa')
        dashboard_content = dashboard_content.replace('{{CAMPAIGN_DESCRIPTION}}', f'Dashboard de performance para a campanha {campaign_name} do cliente {client}')
        dashboard_content = dashboard_content.replace('{{PRIMARY_CHANNEL}}', channel)
        
        # Salvar dashboard
        os.makedirs('static', exist_ok=True)
        dashboard_filename = f"dash_{campaign_key}.html"
        dashboard_path = os.path.join('static', dashboard_filename)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        logger.info(f"✅ Dashboard gerado: {dashboard_filename}")
        
        # Notificar o microserviço Git Manager sobre o novo arquivo
        try:
            import requests
            git_manager_url = "https://git-manager-609095880025.us-central1.run.app"
            notification_data = {
                "action": "dashboard_created",
                "file_path": dashboard_path,
                "campaign_key": campaign_key,
                "client": client,
                "campaign_name": campaign_name
            }
            
            response = requests.post(
                f"{git_manager_url}/notify",
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Microserviço Git Manager notificado")
            else:
                logger.warning(f"⚠️ Falha ao notificar Git Manager: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao notificar Git Manager: {e}")
        
        return {
            "success": True,
            "dashboard_filename": dashboard_filename,
            "dashboard_path": dashboard_path,
            "dashboard_url": f"/static/{dashboard_filename}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "mvp-dashboard-builder",
        "timestamp": datetime.now().isoformat()
    })

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
        
        # Testar extração de contrato
        contract_data = extractor._extract_contract_data()
        
        return jsonify({
            "success": True,
            "message": "Extrator funcionando",
            "contract_data": contract_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar extrator: {e}")
        import traceback
        return jsonify({
            "success": False,
            "message": f"Erro no extrator: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/test-generator', methods=['GET'])
def test_generator():
    """Interface de teste do gerador"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador de Dashboards - Teste</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .loading { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
    </style>
</head>
<body>
    <h1>🎯 Gerador de Dashboards - Teste</h1>
    
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
            <label for="sheetId">ID da Planilha Google Sheets:</label>
            <input type="text" id="sheetId" name="sheet_id" required>
        </div>
        
        <div class="form-group">
            <label for="channel">Canal:</label>
            <select id="channel" name="channel">
                <option value="Video Programática">Video Programática</option>
                <option value="YouTube">YouTube</option>
                <option value="Netflix">Netflix</option>
                <option value="Disney">Disney</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Pinterest">Pinterest</option>
            </select>
        </div>
        
        <button type="submit" id="generateButton">🚀 Gerar Dashboard</button>
    </form>
    
    <div id="result"></div>
    
    <script>
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
        required_fields = ['client', 'campaign_name', 'sheet_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Campo obrigatório: {field}"}), 400
        
        client = data['client']
        campaign_name = data['campaign_name']
        sheet_id = data['sheet_id']
        channel = data.get('channel', 'Video Programática')
        
        # Gerar campaign_key automaticamente
        campaign_key = generate_campaign_key(client, campaign_name)
        
        # Salvar campanha no banco
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel):
            return jsonify({"success": False, "message": "Erro ao salvar configuração da campanha"}), 500
        
        # Gerar dashboard
        result = generate_dashboard(campaign_key, client, campaign_name, sheet_id, channel)
        
        if not result['success']:
            return jsonify({"success": False, "message": f"Erro ao gerar dashboard: {result['error']}"}), 500
        
        return jsonify({
            "success": True,
            "message": "Dashboard gerado com sucesso",
            "campaign_key": campaign_key,
            "dashboard_name": f"{client} - {campaign_name}",
            "dashboard_url": result['dashboard_url'],
            "file_path": result['dashboard_path']
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/generate-dashboard: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

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
            channel=campaign.get('channel')
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
    """Servir arquivos estáticos"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    logger.info("🚀 Iniciando MVP Dashboard Builder (Versão Simplificada)")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
