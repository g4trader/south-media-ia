#!/usr/bin/env python3
"""
Servidor Flask com Extrator REAL do Google Sheets
Versão que carrega dados reais ou falha com erro claro
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from real_google_sheets_extractor import RealGoogleSheetsExtractor, CampaignConfig

app = Flask(__name__)
CORS(app)

# Banco de dados simples em memória
campaigns_db = {}

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>South Media - Sistema REAL</title>
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
                padding: 1rem;
                box-sizing: border-box;
            }
            
            @media (min-width: 768px) {
                .container {
                    max-width: 1200px;
                    padding: 2rem;
                }
            }
            
            .card {
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(139, 92, 246, 0.3);
                backdrop-filter: blur(10px);
                box-sizing: border-box;
                width: 100%;
                border-radius: 12px;
                margin-bottom: 1.5rem;
                padding: 2rem;
            }
            
            .header {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                margin-bottom: 1.5rem;
                padding: 1.5rem;
                box-sizing: border-box;
                width: 100%;
            }
            
            .logo {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
                justify-content: center;
                width: 100%;
            }
            
            .logo-icon {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                margin-right: 12px;
            }
            
            .logo h1 {
                font-size: 1.8rem;
                font-weight: 700;
                background: linear-gradient(135deg, #8B5CF6, #EC4899);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .nav-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .nav-link {
                padding: 12px 20px;
                background: rgba(139, 92, 246, 0.2);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                text-decoration: none;
                color: white;
                text-align: center;
                transition: all 0.3s ease;
                font-weight: 600;
            }
            
            .nav-link:hover {
                background: rgba(139, 92, 246, 0.3);
                border-color: rgba(139, 92, 246, 0.5);
                transform: translateY(-2px);
            }
            
            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 15px;
                background: #22c55e;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">
                    <div class="logo-icon">🎬</div>
                    <h1>South Media - Sistema REAL</h1>
                </div>
                <div class="status-badge">✅ Extrator REAL Ativo</div>
            </div>
            
            <div class="card">
                <h2>🚀 Sistema REAL de Dashboard</h2>
                <p>Servidor com extrator REAL do Google Sheets - Carrega dados reais ou falha com erro claro!</p>
                
                <div class="nav-grid">
                    <a href="/api/list-campaigns" class="nav-link">📋 Listar Campanhas</a>
                    <a href="/test-generator" class="nav-link">🎬 Testar Gerador REAL</a>
                    <a href="/api/copacol_real_test/data" class="nav-link">📊 Testar Dados REAIS</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/list-campaigns', methods=['GET'])
def list_campaigns():
    """Listar campanhas cadastradas"""
    return jsonify({
        "success": True,
        "campaigns": list(campaigns_db.keys()),
        "count": len(campaigns_db)
    })

@app.route('/api/generate-dashboard', methods=['POST'])
def generate_dashboard():
    """Gerar dashboard com dados REAIS"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['client', 'campaign', 'campaign_key', 'sheet_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório não fornecido: {field}"
                }), 400
        
        # Criar configuração
        config = CampaignConfig(
            client=data['client'],
            campaign=data['campaign'],
            campaign_key=data['campaign_key'],
            sheet_id=data['sheet_id'],
            tabs=data.get('tabs', {
                "report": "Report",
                "contract": "Informações de contrato",
                "publishers": "Lista de publishers",
                "strategies": "Estratégias"
            })
        )
        
        # Extrair dados REAIS
        extractor = RealGoogleSheetsExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({
                "success": False,
                "message": "Erro na extração de dados REAIS"
            }), 500
        
        # Salvar no banco local
        campaigns_db[config.campaign_key] = {
            "config": {
                "client": config.client,
                "campaign": config.campaign,
                "campaign_key": config.campaign_key,
                "sheet_id": config.sheet_id,
                "tabs": config.tabs
            },
            "data": extracted_data,
            "created_at": datetime.now().isoformat()
        }
        
        # Criar arquivo HTML do dashboard
        dashboard_filename = f"dash_{config.campaign_key}.html"
        dashboard_path = os.path.join("static", dashboard_filename)
        
        # Ler o template genérico
        template_path = "static/dash_generic_template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Preparar dados para substituição
            campaign_data = {
                "client_name": config.client,
                "campaign_name": config.campaign,
                "campaign_status": "ATIVA",
                "campaign_period": "01/01/2024 a 31/01/2024",
                "campaign_description": "Performance do Canal - Complete View",
                "campaign_objectives": "Objetivos da campanha",
                "total_budget": "0,00",
                "budget_used": "0,00",
                "pacing_percentage": "0",
                "target_vc": "0",
                "cpv_contracted": "0,00",
                "cpv_current": "0,00",
                "primary_channel": "YOUTUBE",
                "channel_badges": '<span style="background:rgba(255,107,53,0.2); padding:6px 12px; border-radius:20px; font-size:0.9rem">YOUTUBE</span>',
                "segmentation_strategy": '<li><strong>🎯 Segmentação:</strong> Estratégia focada em canais específicos</li>',
                "creative_strategy": '<li><strong>📱 Criativos:</strong> Testar variações focando nos primeiros segundos</li>',
                "format_specifications": '<li>Complete View (30s) para máxima atenção</li>',
                "api_endpoint": f"http://localhost:5001/api/{config.campaign_key}/data",
                "campaign_key": config.campaign_key,
                "original_html": "<!-- HTML original será inserido aqui -->"
            }
            
            # Substituir variáveis
            dashboard_content = template_content
            for placeholder, value in campaign_data.items():
                dashboard_content = dashboard_content.replace(f"{{{{{placeholder.upper()}}}}}", str(value))
            
            # Salvar o dashboard
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            
            print(f"✅ Dashboard HTML criado: {dashboard_path}")
        else:
            print(f"⚠️ Template não encontrado: {template_path}")
            dashboard_path = None
        
        return jsonify({
            "success": True,
            "message": f"Dashboard gerado com sucesso para {config.client} - {config.campaign}",
            "campaign_key": config.campaign_key,
            "client": config.client,
            "campaign": config.campaign,
            "api_endpoint": f"/api/{config.campaign_key}/data",
            "dashboard_url": f"/static/dash_{config.campaign_key}.html",
            "data_preview": {
                "daily_data_count": len(extracted_data['daily_data']),
                "total_spend": extracted_data['campaign_summary']['total_spend'],
                "total_impressions": extracted_data['campaign_summary']['total_impressions'],
                "total_clicks": extracted_data['campaign_summary']['total_clicks'],
                "pacing": extracted_data['campaign_summary']['pacing'],
                "data_source": extracted_data['data_source']
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados REAIS de uma campanha"""
    if campaign_key not in campaigns_db:
        return jsonify({
            "success": False,
            "message": f"Campanha '{campaign_key}' não encontrada"
        }), 404
    
    campaign_data = campaigns_db[campaign_key]
    
    return jsonify({
        "success": True,
        "data": campaign_data['data'],
        "source": "google_sheets_real",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/dash-generator-pro')
def dash_generator_pro():
    """Interface do gerador REAL - Usando design correto"""
    with open('correct_generator.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos (dashboards HTML)"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🚀 Iniciando servidor REAL...")
    print("📊 Acesse: http://localhost:5001")
    print("🎬 Gerador REAL: http://localhost:5001/test-generator")
    print("📋 Campanhas: http://localhost:5001/api/list-campaigns")
    print("🔗 Dados REAIS do Google Sheets!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
