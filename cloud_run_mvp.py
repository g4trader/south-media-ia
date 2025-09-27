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

app = Flask(__name__)
CORS(app)

# Configuração do ambiente
PORT = get_port()
DEBUG = is_debug()

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
            git_manager_url = get_git_manager_url()
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
                <option value="YouTube">YouTube</option>
                <option value="Netflix">Netflix</option>
                <option value="Disney">Disney</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Pinterest">Pinterest</option>
                <option value="Spotify">Spotify</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="kpi">KPI Contratado:</label>
            <select id="kpi" name="kpi" required>
                <option value="CPV">CPV - Custo por View (Complete Views)</option>
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
                /\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
                /\/d\/([a-zA-Z0-9-_]+)/,
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
        
        # Salvar campanha no banco
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel):
            return jsonify({"success": False, "message": "Erro ao salvar configuração da campanha"}), 500
        
        # Gerar dashboard
        result = generate_dashboard(campaign_key, client, campaign_name, sheet_id, channel, kpi)
        
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
    logger.info(f"🌍 Ambiente: {'Produção' if is_production() else 'Desenvolvimento'}")
    logger.info(f"🔗 API Endpoint: {get_api_endpoint()}")
    logger.info(f"🚪 Porta: {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
