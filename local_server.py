#!/usr/bin/env python3
"""
Servidor Flask Local para Testar o Sistema de Dashboard
Versão simplificada que funciona 100% localmente
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime
from local_extractor import LocalVideoExtractor, CampaignConfig

app = Flask(__name__)
CORS(app)

# Banco de dados simples em memória
campaigns_db = {}

@app.route('/')
def home():
    return """
    <h1>🚀 Sistema de Dashboard Local</h1>
    <p>Servidor funcionando localmente!</p>
    <ul>
        <li><a href="/api/list-campaigns">📋 Listar Campanhas</a></li>
        <li><a href="/test-generator">🎬 Testar Gerador</a></li>
        <li><a href="/api/copacol_test/data">📊 Testar Dados Copacol</a></li>
    </ul>
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
    """Gerar dashboard localmente"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['client', 'campaign', 'campaign_key']
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
            sheet_id=data.get('sheet_id'),
            tabs=data.get('tabs', {})
        )
        
        # Extrair dados
        extractor = LocalVideoExtractor(config)
        extracted_data = extractor.extract_data()
        
        if not extracted_data:
            return jsonify({
                "success": False,
                "message": "Erro na extração de dados"
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
                "pacing": extracted_data['campaign_summary']['pacing']
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha"""
    if campaign_key not in campaigns_db:
        return jsonify({
            "success": False,
            "message": f"Campanha '{campaign_key}' não encontrada"
        }), 404
    
    campaign_data = campaigns_db[campaign_key]
    
    return jsonify({
        "success": True,
        "data": campaign_data['data'],
        "source": "local_extractor",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/dash-generator-pro')
def dash_generator_pro():
    """Interface de teste do gerador"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎬 Teste do Gerador Local</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
        <h1>🎬 Gerador de Dashboards - Pro Local</h1>
        <p>Gere dashboards profissionalmente em ambiente local</p>
            
            <form id="generatorForm">
                <div class="form-group">
                    <label>Cliente:</label>
                    <input type="text" id="client" value="Copacol" required>
                </div>
                
                <div class="form-group">
                    <label>Campanha:</label>
                    <input type="text" id="campaign" value="Institucional 30s" required>
                </div>
                
                <div class="form-group">
                    <label>Campaign Key:</label>
                    <input type="text" id="campaign_key" value="copacol_test" required>
                </div>
                
                <div class="form-group">
                    <label>Sheet ID (opcional):</label>
                    <input type="text" id="sheet_id" value="1scA5ykf49DLobPTAKSL5fNgGM_iomcJmgSJqXolV679M">
                </div>
                
                <button type="submit">🚀 Gerar Dashboard</button>
            </form>
            
            <div id="result"></div>
        </div>
        
        <script>
            document.getElementById('generatorForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    client: document.getElementById('client').value,
                    campaign: document.getElementById('campaign').value,
                    campaign_key: document.getElementById('campaign_key').value,
                    sheet_id: document.getElementById('sheet_id').value,
                    tabs: {
                        report: "Report",
                        contract: "Informações de contrato",
                        publishers: "Publishers",
                        strategies: "Segmentações"
                    }
                };
                
                try {
                    const response = await fetch('/api/generate-dashboard', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('result').innerHTML = `
                            <div class="result success">
                                <h3>✅ Dashboard Gerado com Sucesso!</h3>
                                <p><strong>Cliente:</strong> ${result.client}</p>
                                <p><strong>Campanha:</strong> ${result.campaign}</p>
                                <p><strong>API:</strong> <a href="${result.api_endpoint}">${result.api_endpoint}</a></p>
                                <p><strong>Dados:</strong> ${result.data_preview.daily_data_count} dias, R$ ${result.data_preview.total_spend.toLocaleString()}, Pacing: ${result.data_preview.pacing}%</p>
                                <p><a href="${result.api_endpoint}" target="_blank">🔗 Testar API de Dados</a></p>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">
                                <h3>❌ Erro</h3>
                                <p>${result.message}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">
                            <h3>❌ Erro de Conexão</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    print("🚀 Iniciando servidor local...")
    print("📊 Acesse: http://localhost:5000")
    print("🎬 Gerador: http://localhost:5000/test-generator")
    print("📋 Campanhas: http://localhost:5000/api/list-campaigns")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

