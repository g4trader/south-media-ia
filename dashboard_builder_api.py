#!/usr/bin/env python3
"""
API para criação e gerenciamento de dashboards dinâmicos
Sistema de Dashboard Builder
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from typing import Dict, List, Optional
import uuid
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar CORS
def configure_cors():
    """Configurar headers CORS"""
    cors_origin = os.environ.get('CORS_ORIGIN', '*')
    return {
        'Access-Control-Allow-Origin': cors_origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '3600'
    }

def add_cors_headers(response):
    """Adicionar headers CORS à resposta"""
    cors_headers = configure_cors()
    for key, value in cors_headers.items():
        response.headers[key] = value
    return response

# Handler para OPTIONS requests (CORS preflight)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        return add_cors_headers(response)

# Armazenamento em memória (em produção, usar banco de dados)
DASHBOARDS_DB = {}
CAMPAIGNS_DB = {}

class DashboardBuilder:
    """Classe principal para construção de dashboards dinâmicos"""
    
    def __init__(self):
        self.templates_dir = "templates"
        self.static_dir = "static"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Garantir que os diretórios necessários existam"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs("campaigns", exist_ok=True)
    
    def validate_campaign_data(self, data: Dict) -> tuple[bool, str]:
        """Validar dados da campanha"""
        try:
            required_fields = [
                'campaignName', 'startDate', 'endDate', 'totalBudget',
                'reportModel', 'kpiType', 'kpiValue', 'kpiTarget', 'strategies', 'channels'
            ]
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return False, f"Campo obrigatório '{field}' não fornecido"
            
            # Validar datas
            start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
            end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
            
            if end_date <= start_date:
                return False, "Data de fim deve ser posterior à data de início"
            
            # Validar orçamento
            if data['totalBudget'] <= 0:
                return False, "Orçamento deve ser maior que zero"
            
            # Validar KPI
            if data['kpiValue'] <= 0 or data['kpiTarget'] <= 0:
                return False, "Valores de KPI devem ser maiores que zero"
            
            # Validar canais
            if not data['channels'] or len(data['channels']) == 0:
                return False, "Pelo menos um canal deve ser selecionado"
            
            for channel in data['channels']:
                if not channel.get('sheetId'):
                    return False, f"Planilha não configurada para o canal {channel.get('displayName', 'desconhecido')}"
                
                if not channel.get('budget') or channel.get('budget', 0) <= 0:
                    return False, f"Orçamento não configurado para o canal {channel.get('displayName', 'desconhecido')}"
                
                if not channel.get('quantity') or channel.get('quantity', 0) <= 0:
                    return False, f"Quantidade não configurada para o canal {channel.get('displayName', 'desconhecido')}"
            
            return True, "Dados válidos"
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"
    
    def generate_dashboard_id(self, campaign_name: str) -> str:
        """Gerar ID único para o dashboard"""
        # Criar slug a partir do nome da campanha
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', campaign_name.lower())
        slug = re.sub(r'\s+', '_', slug.strip())
        
        # Adicionar timestamp para garantir unicidade
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"dash_{slug}_{timestamp}"
    
    def create_dashboard_config(self, data: Dict) -> Dict:
        """Criar configuração do dashboard"""
        dashboard_id = self.generate_dashboard_id(data['campaignName'])
        
        config = {
            'id': dashboard_id,
            'campaignName': data['campaignName'],
            'startDate': data['startDate'],
            'endDate': data['endDate'],
            'totalBudget': data['totalBudget'],
            'reportModel': data['reportModel'],
            'kpiType': data['kpiType'],
            'kpiValue': data['kpiValue'],
            'kpiTarget': data['kpiTarget'],
            'strategies': data['strategies'],
            'channels': data['channels'],
            'status': 'created',  # created, validated, active, completed
            'createdAt': datetime.now().isoformat(),
            'validatedAt': None,
            'activatedAt': None,
            'completedAt': None,
            'fileName': f"{dashboard_id}.html",
            'schedulerJobId': None,
            'lastUpdate': None,
            'updateCount': 0
        }
        
        return config
    
    def generate_dashboard_html(self, config: Dict) -> str:
        """Gerar HTML do dashboard baseado no template"""
        try:
            template_type = config['reportModel']
            
            if template_type == 'simple':
                return self.generate_dashboard_from_template(config, 'template_simple.html')
            elif template_type == 'multichannel':
                return self.generate_dashboard_from_template(config, 'template_multichannel.html')
            else:
                raise ValueError(f"Tipo de template não suportado: {template_type}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar HTML do dashboard: {e}")
            raise
    
    def generate_dashboard_from_template(self, config: Dict, template_file: str) -> str:
        """Gerar dashboard a partir de template existente"""
        try:
            template_path = os.path.join(self.templates_dir, template_file)
            
            if not os.path.exists(template_path):
                logger.error(f"❌ Template não encontrado: {template_path}")
                raise FileNotFoundError(f"Template {template_file} não encontrado")
            
            # Ler template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Substituir variáveis no template
            html_content = self.replace_template_variables(template_content, config)
            
            logger.info(f"✅ Dashboard gerado a partir do template {template_file}")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dashboard do template: {e}")
            raise
    
    def replace_template_variables(self, template_content: str, config: Dict) -> str:
        """Substituir variáveis no template"""
        try:
            # Variáveis básicas
            replacements = {
                '{{CAMPAIGN_NAME}}': config['campaignName'],
                '{{CAMPAIGN_ID}}': config['id'],
                '{{START_DATE}}': config['startDate'],
                '{{END_DATE}}': config['endDate'],
                '{{TOTAL_BUDGET}}': f"{config['totalBudget']:,.2f}",
                '{{KPI_TYPE}}': config['kpiType'].upper(),
                '{{KPI_VALUE}}': f"{config['kpiValue']:.2f}",
                '{{KPI_TARGET}}': f"{config['kpiTarget']:,}",
                '{{STRATEGIES}}': config['strategies'],
                '{{STATUS}}': config['status'],
                '{{CREATED_AT}}': config['createdAt']
            }
            
            # Aplicar substituições
            html_content = template_content
            for placeholder, value in replacements.items():
                html_content = html_content.replace(placeholder, str(value))
            
            # Gerar configuração JavaScript
            js_config = self.generate_js_config(config)
            html_content = html_content.replace('{{JS_CONFIG}}', js_config)
            
            # Gerar configuração de canais
            channels_config = self.generate_channels_config(config)
            html_content = html_content.replace('{{CHANNELS_CONFIG}}', channels_config)
            
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao substituir variáveis do template: {e}")
            raise
    
    def generate_js_config(self, config: Dict) -> str:
        """Gerar configuração JavaScript para o dashboard"""
        js_config = {
            'campaign': {
                'id': config['id'],
                'name': config['campaignName'],
                'startDate': config['startDate'],
                'endDate': config['endDate'],
                'totalBudget': config['totalBudget'],
                'kpiType': config['kpiType'],
                'kpiValue': config['kpiValue'],
                'kpiTarget': config['kpiTarget'],
                'strategies': config['strategies'],
                'status': config['status']
            },
            'channels': config['channels'],
            'reportModel': config['reportModel']
        }
        
        return json.dumps(js_config, ensure_ascii=False, indent=2)
    
    def generate_channels_config(self, config: Dict) -> str:
        """Gerar configuração de canais para Google Sheets"""
        channels_config = {}
        
        for channel in config['channels']:
            channels_config[channel['name']] = {
                'sheet_id': channel['sheetId'],
                'gid': channel['gid'],
                'display_name': channel['displayName'],
                'budget': channel.get('budget', 0),
                'quantity': channel.get('quantity', 0)
            }
        
        return json.dumps(channels_config, ensure_ascii=False, indent=2)
    
    def generate_simple_dashboard(self, config: Dict) -> str:
        """Gerar dashboard simples"""
        dashboard_id = config['id']
        campaign_name = config['campaignName']
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{campaign_name} - Dashboard Simples</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0f0f23;
            --bg2: #1a1a2e;
            --panel: #16213e;
            --stroke: rgba(148,163,184,.25);
            --muted: rgba(148,163,184,.8);
            --grad: linear-gradient(135deg,#ff6b35,#8b5cf6);
            --accent: #00ff88;
            --danger: #ff4757;
            --warning: #ffa726;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: Inter, system-ui, -apple-system, sans-serif; 
            color: #fff;
            background: linear-gradient(135deg, var(--bg) 0%, var(--bg2) 50%, var(--panel) 100%);
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 32px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 2.5rem; font-weight: 800; background: var(--grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .header p {{ color: var(--muted); font-size: 1.1rem; margin-top: 8px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ 
            background: rgba(26,26,46,.8); 
            border: 1px solid var(--stroke); 
            border-radius: 16px; 
            padding: 24px; 
            text-align: center;
            backdrop-filter: blur(8px);
        }}
        .stat-number {{ font-size: 2.5rem; font-weight: 800; background: var(--grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stat-label {{ color: var(--muted); font-size: .9rem; text-transform: uppercase; letter-spacing: .1em; margin-top: 8px; }}
        .chart-container {{ 
            background: rgba(26,26,46,.8); 
            border: 1px solid var(--stroke); 
            border-radius: 16px; 
            padding: 24px; 
            margin-bottom: 20px;
        }}
        .chart-title {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 20px; color: #fff; }}
        .campaign-info {{ 
            background: rgba(26,26,46,.8); 
            border: 1px solid var(--stroke); 
            border-radius: 16px; 
            padding: 24px; 
            margin-bottom: 20px;
        }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
        .info-item {{ }}
        .info-label {{ color: var(--muted); font-size: .9rem; text-transform: uppercase; letter-spacing: .1em; }}
        .info-value {{ color: #fff; font-size: 1.1rem; font-weight: 600; margin-top: 4px; }}
        .status-badge {{ 
            display: inline-block; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: .8rem; 
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-created {{ background: rgba(255,167,38,.2); border: 1px solid rgba(255,167,38,.4); color: var(--warning); }}
        .status-validated {{ background: rgba(0,255,136,.2); border: 1px solid rgba(0,255,136,.4); color: var(--accent); }}
        .status-active {{ background: rgba(0,255,136,.2); border: 1px solid rgba(0,255,136,.4); color: var(--accent); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{campaign_name}</h1>
            <p>Dashboard Simples - {config['startDate']} a {config['endDate']}</p>
        </div>

        <div class="campaign-info">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Orçamento Total</div>
                    <div class="info-value">R$ {config['totalBudget']:,.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">KPI Negociado</div>
                    <div class="info-value">{config['kpiType'].upper()} - R$ {config['kpiValue']:.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Meta KPI</div>
                    <div class="info-value">{config['kpiTarget']:,}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">
                        <span class="status-badge status-{config['status']}">{config['status'].title()}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="totalSpend">R$ 0,00</div>
                <div class="stat-label">Total Investido</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalImpressions">0</div>
                <div class="stat-label">Impressões</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalClicks">0</div>
                <div class="stat-label">Cliques</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="kpiProgress">0%</div>
                <div class="stat-label">Progresso KPI</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">📊 Performance por Canal</div>
            <canvas id="channelChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">📈 Evolução Diária</div>
            <canvas id="dailyChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        // Dados da campanha
        const CAMPAIGN_CONFIG = {json.dumps(config, ensure_ascii=False, indent=2)};
        
        // Dados vazios inicialmente (serão preenchidos pela automação)
        const DAILY_DATA = [];
        const CHANNEL_DATA = [];
        
        // Inicializar gráficos
        function initCharts() {{
            // Gráfico de canais
            const channelCtx = document.getElementById('channelChart').getContext('2d');
            new Chart(channelCtx, {{
                type: 'doughnut',
                data: {{
                    labels: CHANNEL_DATA.map(ch => ch.name),
                    datasets: [{{
                        data: CHANNEL_DATA.map(ch => ch.spend),
                        backgroundColor: [
                            '#ff6b35', '#8b5cf6', '#00ff88', '#ffa726', '#ff4757'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
            
            // Gráfico diário
            const dailyCtx = document.getElementById('dailyChart').getContext('2d');
            new Chart(dailyCtx, {{
                type: 'line',
                data: {{
                    labels: DAILY_DATA.map(d => d.date),
                    datasets: [{{
                        label: 'Investimento Diário',
                        data: DAILY_DATA.map(d => d.spend),
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0,255,136,0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#fff' }} }},
                        y: {{ ticks: {{ color: '#fff' }} }}
                    }}
                }}
            }});
        }}
        
        // Atualizar estatísticas
        function updateStats() {{
            const totalSpend = DAILY_DATA.reduce((sum, d) => sum + d.spend, 0);
            const totalImpressions = DAILY_DATA.reduce((sum, d) => sum + d.impressions, 0);
            const totalClicks = DAILY_DATA.reduce((sum, d) => sum + d.clicks, 0);
            
            document.getElementById('totalSpend').textContent = `R$ ${{totalSpend.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}`;
            document.getElementById('totalImpressions').textContent = totalImpressions.toLocaleString();
            document.getElementById('totalClicks').textContent = totalClicks.toLocaleString();
            
            // Calcular progresso do KPI
            const kpiProgress = (totalSpend / CAMPAIGN_CONFIG.totalBudget) * 100;
            document.getElementById('kpiProgress').textContent = `${{kpiProgress.toFixed(1)}}%`;
        }}
        
        // Inicializar quando carregar
        document.addEventListener('DOMContentLoaded', function() {{
            initCharts();
            updateStats();
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def generate_multichannel_dashboard(self, config: Dict) -> str:
        """Gerar dashboard multicanal (baseado no template existente)"""
        # Por enquanto, usar o template simples como base
        # Em uma implementação completa, aqui seria carregado o template multicanal
        return self.generate_simple_dashboard(config)
    
    def save_dashboard_file(self, config: Dict, html_content: str) -> bool:
        """Salvar arquivo HTML do dashboard"""
        try:
            file_path = os.path.join(self.static_dir, config['fileName'])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Dashboard salvo: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dashboard: {e}")
            return False
    
    def save_campaign_config(self, config: Dict) -> bool:
        """Salvar configuração da campanha"""
        try:
            config_file = os.path.join("campaigns", f"{config['id']}.json")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Configuração da campanha salva: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
            return False

# Instância global do builder
dashboard_builder = DashboardBuilder()

# ===== API ENDPOINTS =====

@app.route('/api/dashboards', methods=['POST'])
def create_dashboard():
    """Criar novo dashboard"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        # Validar dados
        is_valid, message = dashboard_builder.validate_campaign_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Criar configuração
        config = dashboard_builder.create_dashboard_config(data)
        
        # Gerar HTML
        html_content = dashboard_builder.generate_dashboard_html(config)
        
        # Salvar arquivos
        if not dashboard_builder.save_dashboard_file(config, html_content):
            return jsonify({
                'success': False,
                'message': 'Erro ao salvar arquivo do dashboard'
            }), 500
        
        if not dashboard_builder.save_campaign_config(config):
            return jsonify({
                'success': False,
                'message': 'Erro ao salvar configuração da campanha'
            }), 500
        
        # Armazenar na memória
        DASHBOARDS_DB[config['id']] = config
        CAMPAIGNS_DB[config['id']] = config
        
        logger.info(f"🎉 Dashboard criado: {config['id']}")
        
        return jsonify({
            'success': True,
            'message': 'Dashboard criado com sucesso',
            'dashboard': {
                'id': config['id'],
                'fileName': config['fileName'],
                'status': config['status'],
                'url': f"/static/{config['fileName']}"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar dashboard: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/dashboards/<dashboard_id>/validate', methods=['POST'])
def validate_dashboard(dashboard_id):
    """Validar dashboard"""
    try:
        if dashboard_id not in DASHBOARDS_DB:
            return jsonify({
                'success': False,
                'message': 'Dashboard não encontrado'
            }), 404
        
        config = DASHBOARDS_DB[dashboard_id]
        
        if config['status'] != 'created':
            return jsonify({
                'success': False,
                'message': f'Dashboard já foi validado (status: {config["status"]})'
            }), 400
        
        # Atualizar status
        config['status'] = 'validated'
        config['validatedAt'] = datetime.now().isoformat()
        
        # Salvar configuração atualizada
        dashboard_builder.save_campaign_config(config)
        
        logger.info(f"✅ Dashboard validado: {dashboard_id}")
        
        return jsonify({
            'success': True,
            'message': 'Dashboard validado com sucesso',
            'dashboard': {
                'id': config['id'],
                'status': config['status'],
                'validatedAt': config['validatedAt']
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao validar dashboard: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/dashboards', methods=['GET'])
def list_dashboards():
    """Listar todos os dashboards"""
    try:
        dashboards = []
        
        for dashboard_id, config in DASHBOARDS_DB.items():
            dashboards.append({
                'id': config['id'],
                'campaignName': config['campaignName'],
                'startDate': config['startDate'],
                'endDate': config['endDate'],
                'totalBudget': config['totalBudget'],
                'status': config['status'],
                'fileName': config['fileName'],
                'createdAt': config['createdAt'],
                'validatedAt': config['validatedAt'],
                'url': f"/static/{config['fileName']}"
            })
        
        return jsonify({
            'success': True,
            'dashboards': dashboards,
            'total': len(dashboards)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar dashboards: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/dashboards/<dashboard_id>', methods=['GET'])
def get_dashboard(dashboard_id):
    """Obter detalhes de um dashboard"""
    try:
        if dashboard_id not in DASHBOARDS_DB:
            return jsonify({
                'success': False,
                'message': 'Dashboard não encontrado'
            }), 404
        
        config = DASHBOARDS_DB[dashboard_id]
        
        return jsonify({
            'success': True,
            'dashboard': config
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dashboard: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-builder-api"
    })

if __name__ == "__main__":
    logger.info("🚀 Iniciando Dashboard Builder API...")
    app.run(host='0.0.0.0', port=8081, debug=True)
