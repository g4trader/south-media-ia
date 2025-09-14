#!/usr/bin/env python3
"""
Aplicação Cloud Run específica para atualização de Footfall
Endpoint separado para processar apenas dados de footfall
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variáveis globais para controle
footfall_thread = None
last_run_status = {"status": "never_run", "timestamp": None, "error": None}
is_running = False

def run_footfall_update():
    """Executa uma atualização de footfall"""
    global last_run_status, is_running
    
    is_running = True
    try:
        logger.info("🗺️ Iniciando atualização de footfall...")
        
        # Importar e executar processador de footfall
        from footfall_processor import FootfallProcessor
        
        processor = FootfallProcessor()
        success = processor.run_footfall_update()
        
        last_run_status = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "error": None if success else "Falha na atualização de footfall"
        }
        
        logger.info(f"✅ Atualização de footfall concluída: {'sucesso' if success else 'falha'}")
        
    except Exception as e:
        logger.error(f"❌ Erro na atualização de footfall: {e}")
        last_run_status = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
    finally:
        is_running = False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "footfall-automation"
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint para verificar status da automação de footfall"""
    global last_run_status, is_running
    
    return jsonify({
        "footfall_status": last_run_status,
        "is_running": is_running,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/trigger', methods=['POST'])
def trigger_footfall_update():
    """Endpoint para disparar atualização de footfall"""
    global last_run_status, is_running
    
    if is_running:
        return jsonify({
            "status": "error",
            "message": "Atualização de footfall já está em execução"
        }), 409
    
    try:
        # Executar diretamente em vez de usar thread
        is_running = True
        logger.info("🗺️ Iniciando atualização de footfall...")
        
        # Importar e executar processador de footfall
        from footfall_processor import FootfallProcessor
        
        processor = FootfallProcessor()
        success = processor.run_footfall_update()
        
        last_run_status = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "error": None if success else "Falha na atualização de footfall"
        }
        
        is_running = False
        logger.info(f"✅ Atualização de footfall concluída: {'sucesso' if success else 'falha'}")
        
        return jsonify({
            "status": "completed",
            "message": f"Atualização de footfall {'bem-sucedida' if success else 'falhou'}",
            "timestamp": datetime.now().isoformat(),
            "success": success
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao disparar atualização de footfall: {e}")
        last_run_status = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        is_running = False
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_footfall_config():
    """Endpoint para visualizar configuração de footfall"""
    try:
        from footfall_config import FOOTFALL_UPDATE_CONFIG, FOOTFALL_VALIDATION
        
        safe_config = {
            "update_interval_hours": FOOTFALL_UPDATE_CONFIG.get("update_interval_hours", 6),
            "validation_rules": {
                "lat_range": FOOTFALL_VALIDATION["lat_range"],
                "lon_range": FOOTFALL_VALIDATION["lon_range"],
                "required_fields": FOOTFALL_VALIDATION["required_fields"]
            },
            "auto_update_enabled": FOOTFALL_UPDATE_CONFIG.get("auto_update_enabled", True)
        }
        
        return jsonify(safe_config)
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter configuração de footfall: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test_footfall_connection():
    """Endpoint para testar conexão com dados de footfall"""
    try:
        from footfall_processor import FootfallProcessor
        
        processor = FootfallProcessor()
        footfall_data = processor.get_footfall_data()
        
        if footfall_data:
            return jsonify({
                "status": "success",
                "message": f"Conexão OK - {len(footfall_data)} pontos de footfall encontrados",
                "sample_data": footfall_data[:2] if len(footfall_data) > 2 else footfall_data
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Falha ao conectar com dados de footfall"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de conexão: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Página inicial com informações da API de Footfall"""
    return jsonify({
        "service": "Footfall Automation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "trigger": "/trigger (POST)",
            "config": "/config",
            "test": "/test"
        },
        "timestamp": datetime.now().isoformat()
    })

def scheduled_footfall_update():
    """Executa atualização de footfall agendada a cada 6 horas"""
    logger.info("⏰ Iniciando automação agendada de footfall...")
    
    while True:
        try:
            # Executar atualização
            run_footfall_update()
            
            # Aguardar 6 horas (21600 segundos)
            time.sleep(21600)
            
        except Exception as e:
            logger.error(f"❌ Erro na automação agendada de footfall: {e}")
            # Aguardar 30 minutos antes de tentar novamente
            time.sleep(1800)

def start_scheduled_footfall():
    """Inicia thread de automação agendada de footfall"""
    try:
        scheduler_thread = threading.Thread(target=scheduled_footfall_update)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info("✅ Automação agendada de footfall iniciada (a cada 6 horas)")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar automação agendada de footfall: {e}")

def main():
    """Função principal"""
    logger.info("🗺️ Iniciando aplicação Cloud Run para Footfall...")
    
    # Verificar se deve iniciar automação agendada
    if os.environ.get('FOOTFALL_AUTOMATION_MODE') != 'scheduler':
        start_scheduled_footfall()
    
    # Iniciar Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
