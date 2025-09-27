#!/usr/bin/env python3
"""
Servidor Flask com Persistência de Dados SQLite
Versão que mantém dados das campanhas permanentemente
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
from real_google_sheets_extractor import RealGoogleSheetsExtractor
from sqlite_database import db_manager

app = Flask(__name__)
CORS(app)

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CampaignConfig:
    """Configuração de campanha"""
    def __init__(self, campaign_key, client, campaign_name, sheet_id, channel=None):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign = campaign_name
        self.sheet_id = sheet_id
        self.channel = channel

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>South Media - Sistema PERSISTENTE</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0F0F23 0%, #16213E 50%, #1A1A2E 100%);
                color: white;
                min-height: 100vh;
                overflow-x: hidden;
                width: 100%;
                max-width: 100vw;
                position: relative;
            }
            
            .container {
                max-width: 100%;
                width: 100%;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
            }
            
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .logo-icon {
                width: 60px;
                height: 60px;
                border-radius: 15px;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                display: grid;
                place-items: center;
                font-weight: 700;
                font-size: 1.5rem;
            }
            
            .title {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                color: #9CA3AF;
                font-size: 1.1rem;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-bottom: 3rem;
            }
            
            .info-card {
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(139, 92, 246, 0.28);
                border-radius: 14px;
                padding: 2rem;
                backdrop-filter: blur(8px);
            }
            
            .info-card h3 {
                color: #8B5CF6;
                margin-bottom: 1rem;
                font-size: 1.2rem;
            }
            
            .info-card p {
                color: #9CA3AF;
                line-height: 1.6;
                margin-bottom: 1rem;
            }
            
            .info-card ul {
                color: #9CA3AF;
                padding-left: 1.5rem;
            }
            
            .info-card li {
                margin-bottom: 0.5rem;
            }
            
            .endpoints {
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(139, 92, 246, 0.28);
                border-radius: 14px;
                padding: 2rem;
                backdrop-filter: blur(8px);
            }
            
            .endpoints h3 {
                color: #8B5CF6;
                margin-bottom: 1rem;
                font-size: 1.2rem;
            }
            
            .endpoint {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 4px solid #8B5CF6;
            }
            
            .endpoint-method {
                color: #10B981;
                font-weight: 600;
                font-family: monospace;
            }
            
            .endpoint-url {
                color: #F59E0B;
                font-family: monospace;
                margin-left: 0.5rem;
            }
            
            .endpoint-desc {
                color: #9CA3AF;
                margin-top: 0.5rem;
                font-size: 0.9rem;
            }
            
            .database-info {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 8px;
                padding: 1rem;
                margin-top: 2rem;
            }
            
            .database-info h4 {
                color: #10B981;
                margin-bottom: 0.5rem;
            }
            
            .database-info p {
                color: #9CA3AF;
                margin-bottom: 0.5rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">
                    <div class="logo-icon">SM</div>
                    <div>
                        <div class="title">South Media</div>
                        <div class="subtitle">Sistema de Dashboards com Persistência SQLite</div>
                    </div>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>🎯 Sistema REAL</h3>
                    <p>Este servidor carrega dados REAIS do Google Sheets e mantém persistência completa usando SQLite.</p>
                    <ul>
                        <li>✅ Dados reais do Google Sheets</li>
                        <li>✅ Persistência SQLite</li>
                        <li>✅ Cache de dados</li>
                        <li>✅ Geração de dashboards</li>
                    </ul>
                </div>
                
                <div class="info-card">
                    <h3>📊 Funcionalidades</h3>
                    <ul>
                        <li>Gerar dashboards automaticamente</li>
                        <li>Extrair dados de planilhas Google</li>
                        <li>Cache inteligente de dados</li>
                        <li>API REST completa</li>
                        <li>Persistência permanente</li>
                    </ul>
                </div>
            </div>
            
            <div class="endpoints">
                <h3>🔗 Endpoints Disponíveis</h3>
                
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-url">/api/list-campaigns</span>
                    <div class="endpoint-desc">Listar todas as campanhas salvas</div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">POST</span>
                    <span class="endpoint-url">/api/generate-dashboard</span>
                    <div class="endpoint-desc">Gerar novo dashboard com dados reais</div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-url">/api/{campaign_key}/data</span>
                    <div class="endpoint-desc">Obter dados de uma campanha específica</div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-url">/api/database-info</span>
                    <div class="endpoint-desc">Informações sobre o banco de dados</div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-url">/test-generator</span>
                    <div class="endpoint-desc">Interface para gerar dashboards</div>
                </div>
            </div>
            
            <div class="database-info">
                <h4>💾 Informações do Banco de Dados</h4>
                <p>Banco: SQLite (campaigns.db)</p>
                <p>Status: <span id="db-status">Carregando...</span></p>
            </div>
        </div>
        
        <script>
            // Verificar status do banco
            fetch('/api/database-info')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('db-status').textContent = 
                        `${data.active_campaigns} campanhas ativas, ${data.file_size_mb}MB`;
                })
                .catch(error => {
                    document.getElementById('db-status').textContent = 'Erro ao conectar';
                });
        </script>
    </body>
    </html>
    """

@app.route('/api/generate-dashboard', methods=['POST'])
def generate_dashboard():
    """Gerar dashboard com dados reais e salvar no banco"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        campaign_key = data.get('campaign_key')
        client = data.get('client')
        campaign_name = data.get('campaign')
        sheet_id = data.get('sheet_id')
        channel = data.get('channel', 'Video Programática')
        
        if not all([campaign_key, client, campaign_name, sheet_id]):
            return jsonify({"success": False, "message": "Dados obrigatórios não fornecidos"}), 400
        
        logger.info(f"🔄 Gerando dashboard para: {client} - {campaign_name}")
        
        # Salvar campanha no banco
        if not db_manager.save_campaign(campaign_key, client, campaign_name, sheet_id, channel):
            return jsonify({"success": False, "message": "Erro ao salvar campanha no banco"}), 500
        
        # Extrair dados reais
        config = CampaignConfig(campaign_key, client, campaign_name, sheet_id, channel)
        extractor = RealGoogleSheetsExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({"success": False, "message": "Erro ao extrair dados do Google Sheets"}), 500
        
        # Cachear dados
        db_manager.cache_campaign_data(campaign_key, extracted_data)
        
        # Gerar arquivo HTML
        dashboard_filename = f"dash_{campaign_key}.html"
        dashboard_path = os.path.join("static", dashboard_filename)
        
        # Ler template
        template_path = "static/dash_generic_template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Substituir variáveis
            campaign_summary = extracted_data.get('campaign_summary', {})
            
            # Obter dados de contrato para valores corretos
            contract_data = extracted_data.get('contract', {})
            
            # Calcular pacing correto baseado no investimento contratado vs gasto real
            investment_contracted = contract_data.get('investment', 0)
            total_spend = campaign_summary.get('total_spend', 0)
            correct_pacing = (total_spend / investment_contracted * 100) if investment_contracted > 0 else 0
            
            replacements = {
                '{{CLIENT_NAME}}': campaign_summary.get('client', client),
                '{{CAMPAIGN_NAME}}': campaign_summary.get('campaign', campaign_name),
                '{{CAMPAIGN_STATUS}}': 'ATIVA',
                '{{CAMPAIGN_PERIOD}}': campaign_summary.get('period', 'N/A'),
                '{{CAMPAIGN_DESCRIPTION}}': f"Performance do {channel} - Complete View",
                '{{CAMPAIGN_OBJECTIVES}}': f"Fortalecer a marca {campaign_summary.get('client', client)} e comunicar valores através de vídeo programático",
                '{{TOTAL_BUDGET}}': f"{investment_contracted:,.2f}",  # Investimento contratado
                '{{BUDGET_USED}}': f"{total_spend:,.2f}",  # Gasto real
                '{{PACING_PERCENTAGE}}': f"{correct_pacing:.1f}",  # Pacing correto
                '{{TARGET_VC}}': f"{contract_data.get('complete_views_contracted', 0):,}",  # VC contratadas
                '{{CPV_CONTRACTED}}': f"{contract_data.get('cpv_contracted', 0):.2f}",  # CPV contratado
                '{{CPV_CURRENT}}': f"{campaign_summary.get('cpv', 0):.4f}",  # CPV atual
                '{{PRIMARY_CHANNEL}}': channel.upper(),
                '{{CHANNEL_BADGES}}': f'<span style="background:rgba(255,107,53,0.2); padding:6px 12px; border-radius:20px; font-size:0.9rem">{channel.upper()}</span>',
                '{{SEGMENTATION_STRATEGY}}': '<li>Lookalike audiences</li><li>Interesse comportamental</li><li>Retargeting</li>',
                '{{CREATIVE_STRATEGY}}': '<li>Vídeo 30s institucional</li><li>Call-to-action claro</li><li>Mensagem de marca</li>',
                '{{FORMAT_SPECIFICATIONS}}': '<li>16:9 e 9:16</li><li>Com legendas</li><li>Branding consistente</li>',
                '{{API_ENDPOINT}}': f"/api/{campaign_key}/data",
                '{{CAMPAIGN_KEY}}': campaign_key,
                'CAMPAIGN_KEY_PLACEHOLDER': campaign_key
            }
            
            # Aplicar substituições
            for placeholder, value in replacements.items():
                template_content = template_content.replace(placeholder, str(value))
            
            # Salvar arquivo
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"✅ Dashboard HTML criado: {dashboard_path}")
            
            # Retornar resposta
            return jsonify({
                "success": True,
                "message": f"Dashboard gerado com sucesso para {client} - {campaign_name}",
                "campaign_key": campaign_key,
                "client": client,
                "campaign": campaign_name,
                "dashboard_url": f"/static/{dashboard_filename}",
                "api_endpoint": f"/api/{campaign_key}/data",
                "data_preview": {
                    "total_spend": campaign_summary.get('total_spend', 0),
                    "total_impressions": campaign_summary.get('total_impressions', 0),
                    "total_clicks": campaign_summary.get('total_clicks', 0),
                    "daily_data_count": len(extracted_data.get('daily_data', [])),
                    "data_source": "google_sheets_real"
                }
            })
        else:
            return jsonify({"success": False, "message": "Template não encontrado"}), 500
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha específica"""
    try:
        # Verificar se campanha existe no banco
        campaign = db_manager.get_campaign(campaign_key)
        if not campaign:
            return jsonify({"success": False, "message": f"Campanha '{campaign_key}' não encontrada"}), 404
        
        # Sempre extrair dados frescos da planilha (sem cache)
        # cached_data = db_manager.get_cached_data(campaign_key, max_age_hours=1)
        
        # if cached_data:
        #     logger.info(f"✅ Dados obtidos do cache para: {campaign_key}")
        #     return jsonify({"success": True, "data": cached_data})
        
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
            return jsonify({"success": False, "message": "Erro ao extrair dados do Google Sheets"}), 500
        
        # Cachear dados frescos
        db_manager.cache_campaign_data(campaign_key, extracted_data)
        
        return jsonify({"success": True, "data": extracted_data})
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados da campanha: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/list-campaigns', methods=['GET'])
def list_campaigns():
    """Listar todas as campanhas salvas"""
    try:
        campaigns = db_manager.get_all_campaigns()
        return jsonify({
            "success": True,
            "campaigns": [c['campaign_key'] for c in campaigns],
            "count": len(campaigns)
        })
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/api/database-info', methods=['GET'])
def database_info():
    """Obter informações sobre o banco de dados"""
    try:
        info = db_manager.get_database_info()
        return jsonify({"success": True, **info})
    except Exception as e:
        logger.error(f"❌ Erro ao obter info do banco: {e}")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500

@app.route('/dash-generator-pro')
def dash_generator_pro():
    """Interface para testar o gerador"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gerador de Dashboards - South Media</title>
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
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(139, 92, 246, 0.28);
                border-radius: 14px;
                padding: 2rem;
                backdrop-filter: blur(8px);
            }
            
            .header {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .logo {
                width: 60px;
                height: 60px;
                border-radius: 15px;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                display: grid;
                place-items: center;
                font-weight: 700;
                font-size: 1.5rem;
                margin: 0 auto 1rem;
            }
            
            h1 {
                color: #8B5CF6;
                margin-bottom: 0.5rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            label {
                display: block;
                margin-bottom: 0.5rem;
                color: #9CA3AF;
                font-weight: 600;
            }
            
            input, select {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.04);
                color: white;
                font-size: 1rem;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #8B5CF6;
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
            }
            
            button {
                width: 100%;
                padding: 1rem;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35);
            }
            
            .result {
                margin-top: 2rem;
                padding: 1rem;
                border-radius: 8px;
                display: none;
            }
            
            .success {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: #10B981;
            }
            
            .error {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                color: #EF4444;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">SM</div>
                <h1>Gerador de Dashboards</h1>
                <p style="color: #9CA3AF;">Sistema com persistência SQLite</p>
            </div>
            
            <form id="generatorForm">
                <div class="form-group">
                    <label for="campaign_key">Chave da Campanha:</label>
                    <input type="text" id="campaign_key" name="campaign_key" 
                           value="copacol_institucional_30s" required>
                </div>
                
                <div class="form-group">
                    <label for="client">Cliente:</label>
                    <input type="text" id="client" name="client" 
                           value="Copacol" required>
                </div>
                
                <div class="form-group">
                    <label for="campaign">Nome da Campanha:</label>
                    <input type="text" id="campaign" name="campaign" 
                           value="Institucional 30s" required>
                </div>
                
                <div class="form-group">
                    <label for="sheet_id">ID da Planilha Google Sheets:</label>
                    <input type="text" id="sheet_id" name="sheet_id" 
                           value="1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8" required>
                </div>
                
                <div class="form-group">
                    <label for="channel">Canal:</label>
                    <select id="channel" name="channel">
                        <option value="Video Programática">Video Programática</option>
                        <option value="YouTube">YouTube</option>
                        <option value="Display">Display</option>
                    </select>
                </div>
                
                <button type="submit">Gerar Dashboard</button>
            </form>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            document.getElementById('generatorForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '⏳ Gerando dashboard...';
                resultDiv.className = 'result';
                
                try {
                    const response = await fetch('/api/generate-dashboard', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            ✅ Dashboard gerado com sucesso!<br>
                            📊 Cliente: ${result.client}<br>
                            📺 Campanha: ${result.campaign}<br>
                            🌐 <a href="${result.dashboard_url}" target="_blank" style="color: #10B981;">Abrir Dashboard</a><br>
                            🔗 API: ${result.api_endpoint}
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `❌ Erro: ${result.message}`;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `❌ Erro de conexão: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/static/<filename>')
def serve_static(filename):
    """Servir arquivos estáticos"""
    return send_from_directory('static', filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    db_status = db_manager.test_connection()
    return jsonify({
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.now().isoformat(),
        "service": "persistent-dashboard-server"
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor com PERSISTÊNCIA SQLite...")
    print("📊 Acesse: http://localhost:5002")
    print("🎬 Gerador: http://localhost:5002/test-generator")
    print("📋 Campanhas: http://localhost:5002/api/list-campaigns")
    print("💾 Banco: SQLite (campaigns.db)")
    print("🔗 Dados REAIS do Google Sheets com persistência!")
    
    # Testar conexão com banco
    if db_manager.test_connection():
        print("✅ Banco SQLite conectado")
    else:
        print("❌ Erro ao conectar com banco SQLite")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
