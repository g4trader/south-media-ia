#!/usr/bin/env python3
"""
API simplificada para criação de dashboards
"""

import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class SimpleDashboardBuilder:
    def __init__(self):
        self.dashboards_file = 'simple_dashboards.json'
        self.output_dir = 'static'

    def load_dashboards(self):
        """Carregar dashboards existentes"""
        if os.path.exists(self.dashboards_file):
            with open(self.dashboards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_dashboards(self, dashboards):
        """Salvar dashboards"""
        with open(self.dashboards_file, 'w', encoding='utf-8') as f:
            json.dump(dashboards, f, ensure_ascii=False, indent=2)

    def validate_data(self, data):
        """Validar dados básicos"""
        errors = []
        
        required_fields = ['campaignName', 'startDate', 'endDate', 'totalBudget', 'kpiType', 'kpiValue', 'reportModel']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Campo obrigatório: {field}")
        
        return errors

    def create_simple_html(self, config):
        """Criar HTML simples do dashboard"""
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - {config.get('campaignName', 'Campanha')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .info-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .info-card h3 {{
            color: #3b82f6;
            margin-bottom: 15px;
        }}
        .channels-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .channel-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }}
        .status-created {{ background: #3b82f6; }}
        .status-validated {{ background: #10b981; }}
        .status-active {{ background: #f59e0b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {config.get('campaignName', 'Dashboard')}</h1>
            <p>Dashboard criado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>

        <div class="info-grid">
            <div class="info-card">
                <h3>📅 Período da Campanha</h3>
                <p><strong>Início:</strong> {config.get('startDate', 'N/A')}</p>
                <p><strong>Fim:</strong> {config.get('endDate', 'N/A')}</p>
            </div>
            
            <div class="info-card">
                <h3>💰 Orçamento</h3>
                <p><strong>Total:</strong> R$ {config.get('totalBudget', 0):,.2f}</p>
                <p><strong>KPI:</strong> {config.get('kpiType', 'N/A')} - R$ {config.get('kpiValue', 0):,.2f}</p>
            </div>
            
            <div class="info-card">
                <h3>📋 Configuração</h3>
                <p><strong>Modelo:</strong> {config.get('reportModel', 'N/A')}</p>
                <p><strong>Status:</strong> <span class="status status-created">Criado</span></p>
            </div>
        </div>

        <div class="channels-section">
            <h3>📺 Canais de Mídia</h3>
            {self.generate_channels_html(config.get('channels', []))}
        </div>

        <div class="info-card">
            <h3>📝 Estratégias</h3>
            <p>{config.get('strategies', 'Nenhuma estratégia definida.')}</p>
        </div>
    </div>
</body>
</html>
        """
        return html_content

    def generate_channels_html(self, channels):
        """Gerar HTML dos canais"""
        if not channels:
            return "<p>Nenhum canal configurado.</p>"
        
        html = ""
        for channel in channels:
            html += f"""
            <div class="channel-item">
                <h4>📺 {channel.get('name', 'Canal')}</h4>
                <p><strong>Orçamento:</strong> R$ {channel.get('budget', 0):,.2f}</p>
                <p><strong>Meta:</strong> {channel.get('quantity', 0):,} {'visualizações' if 'YouTube' in channel.get('name', '') else 'impressões'}</p>
                <p><strong>Planilha:</strong> {channel.get('sheet_id', 'N/A')}</p>
            </div>
            """
        return html

# Inicializar builder
builder = SimpleDashboardBuilder()

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-simple'
    })

@app.route('/api/dashboards', methods=['GET'])
def list_dashboards():
    """Listar todos os dashboards"""
    try:
        dashboards = builder.load_dashboards()
        return jsonify({
            'success': True,
            'dashboards': dashboards,
            'count': len(dashboards)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards', methods=['POST'])
def create_dashboard():
    """Criar novo dashboard"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Validar dados
        validation_errors = builder.validate_data(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Dados inválidos',
                'details': validation_errors
            }), 400
        
        # Gerar ID único
        dashboard_id = str(uuid.uuid4())
        
        # Criar configuração do dashboard
        dashboard_config = {
            'id': dashboard_id,
            'name': data.get('campaignName'),
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'config': data
        }
        
        # Gerar HTML
        try:
            html_content = builder.create_simple_html(data)
            
            # Salvar arquivo HTML
            filename = f"dash_{data.get('campaignName', 'campaign').lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(builder.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            dashboard_config['html_file'] = filename
            dashboard_config['html_path'] = filepath
            
        except Exception as e:
            print(f"Erro ao gerar HTML: {e}")
            dashboard_config['html_error'] = str(e)
        
        # Salvar dashboard
        dashboards = builder.load_dashboards()
        dashboards.append(dashboard_config)
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_config,
            'message': 'Dashboard criado com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao criar dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/validate', methods=['POST'])
def validate_dashboard(dashboard_id):
    """Validar dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        dashboard['status'] = 'validated'
        dashboard['validated_at'] = datetime.now().isoformat()
        
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'message': 'Dashboard validado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/activate', methods=['POST'])
def activate_dashboard(dashboard_id):
    """Ativar dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        dashboard['status'] = 'active'
        dashboard['activated_at'] = datetime.now().isoformat()
        
        builder.save_dashboards(dashboards)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'message': 'Dashboard ativado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboards/<dashboard_id>/download', methods=['GET'])
def download_dashboard(dashboard_id):
    """Download do arquivo HTML do dashboard"""
    try:
        dashboards = builder.load_dashboards()
        dashboard = next((d for d in dashboards if d['id'] == dashboard_id), None)
        
        if not dashboard:
            return jsonify({
                'success': False,
                'error': 'Dashboard não encontrado'
            }), 404
        
        html_file = dashboard.get('html_file')
        if not html_file:
            return jsonify({
                'success': False,
                'error': 'Arquivo HTML não encontrado'
            }), 404
        
        filepath = os.path.join(builder.output_dir, html_file)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Arquivo HTML não existe no sistema'
            }), 404
        
        return send_file(filepath, as_attachment=True, download_name=html_file)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Builder API Simple...")
    print(f"📁 Output: {builder.output_dir}")
    
    app.run(host='0.0.0.0', port=8083, debug=True)
