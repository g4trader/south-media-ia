#!/usr/bin/env python3
"""
Dashboard Builder - Production API
Sistema robusto para criação de dashboards com dados reais do Google Sheets
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar módulos do sistema
from google_sheets_service import GoogleSheetsService
from dashboard_generator import DashboardGenerator
from campaign_manager import CampaignManager

app = Flask(__name__)
CORS(app)

# Inicializar serviços
sheets_service = GoogleSheetsService()
dashboard_generator = DashboardGenerator()
campaign_manager = CampaignManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar saúde da API"""
    try:
        # Verificar conectividade com Google Sheets
        sheets_status = sheets_service.test_connection()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "services": {
                "google_sheets": sheets_status,
                "dashboard_generator": "ok",
                "campaign_manager": "ok"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Criar nova campanha com dados reais das planilhas"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Dados da campanha não fornecidos"}), 400

        # Validar dados obrigatórios
        required_fields = ['campaignName', 'startDate', 'endDate', 'totalBudget', 'channels']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Campo obrigatório: {field}"}), 400

        # Validar canais
        if not data.get('channels') or len(data['channels']) == 0:
            return jsonify({"success": False, "message": "Pelo menos um canal deve ser configurado"}), 400

        # Verificar se as planilhas existem e são acessíveis
        for channel in data['channels']:
            sheet_id = channel.get('sheet_id')
            if not sheet_id:
                return jsonify({"success": False, "message": f"ID da planilha obrigatório para {channel.get('name')}"}), 400
            
            # Testar acesso à planilha
            if not sheets_service.validate_sheet_access(sheet_id, channel.get('gid')):
                return jsonify({"success": False, "message": f"Não foi possível acessar a planilha {sheet_id} para {channel.get('name')}"}), 400

        # Criar campanha
        campaign_id = str(uuid.uuid4())
        campaign = campaign_manager.create_campaign(campaign_id, data)

        # Gerar dashboard com dados reais
        dashboard_html = dashboard_generator.generate_dashboard(campaign)

        # Salvar dashboard
        filename = f"dash_{data['campaignName'].lower().replace(' ', '_')}.html"
        filepath = os.path.join('static', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)

        return jsonify({
            "success": True,
            "message": f"Campanha '{data['campaignName']}' criada com sucesso!",
            "campaign": {
                "id": campaign_id,
                "name": data['campaignName'],
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "html_file": filename,
                "html_path": filepath
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao criar campanha: {str(e)}"
        }), 500

@app.route('/api/campaigns/<campaign_id>/data', methods=['GET'])
def get_campaign_data(campaign_id):
    """Obter dados atualizados da campanha"""
    try:
        campaign = campaign_manager.get_campaign(campaign_id)
        if not campaign:
            return jsonify({"success": False, "message": "Campanha não encontrada"}), 404

        # Buscar dados atualizados das planilhas
        updated_data = sheets_service.get_campaign_data(campaign)
        
        return jsonify({
            "success": True,
            "campaign_id": campaign_id,
            "data": updated_data,
            "last_updated": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar dados: {str(e)}"
        }), 500

@app.route('/api/campaigns/<campaign_id>/update', methods=['POST'])
def update_campaign_dashboard(campaign_id):
    """Atualizar dashboard com dados mais recentes"""
    try:
        campaign = campaign_manager.get_campaign(campaign_id)
        if not campaign:
            return jsonify({"success": False, "message": "Campanha não encontrada"}), 404

        # Buscar dados atualizados
        updated_data = sheets_service.get_campaign_data(campaign)
        
        # Regenerar dashboard
        dashboard_html = dashboard_generator.generate_dashboard(campaign, updated_data)
        
        # Salvar dashboard atualizado
        filepath = campaign.get('html_path')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)

        return jsonify({
            "success": True,
            "message": "Dashboard atualizado com sucesso!",
            "last_updated": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar dashboard: {str(e)}"
        }), 500

@app.route('/api/campaigns/<campaign_id>/download', methods=['GET'])
def download_campaign_dashboard(campaign_id):
    """Download do dashboard da campanha"""
    try:
        campaign = campaign_manager.get_campaign(campaign_id)
        if not campaign:
            return jsonify({"success": False, "message": "Campanha não encontrada"}), 404

        filepath = campaign.get('html_path')
        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "Arquivo do dashboard não encontrado"}), 404

        return send_file(filepath, as_attachment=True, download_name=campaign.get('html_file'))

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao baixar dashboard: {str(e)}"
        }), 500

@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """Listar todas as campanhas"""
    try:
        campaigns = campaign_manager.list_campaigns()
        return jsonify({
            "success": True,
            "campaigns": campaigns
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar campanhas: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Iniciando Dashboard Builder API v3.0.0...")
    print(f"📊 Google Sheets: {'✅ Configurado' if sheets_service.is_configured() else '❌ Não configurado'}")
    print(f"🌐 Porta: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
