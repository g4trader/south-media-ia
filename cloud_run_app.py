#!/usr/bin/env python3
"""
Aplicação principal para Google Cloud Run
Executa automação do dashboard e serve endpoints HTTP
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
automation_thread = None
last_run_status = {"status": "never_run", "timestamp": None, "error": None}
is_running = False

def run_automation_update():
    """Executa uma atualização do dashboard"""
    global last_run_status, is_running
    
    try:
        is_running = True
        logger.info("🚀 Iniciando atualização automática...")
        
        # Importar e executar automação
        from dashboard_automation import DashboardAutomation
        
        automation = DashboardAutomation()
        success = automation.run_update()
        
        last_run_status = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "error": None if success else "Falha na atualização"
        }
        
        logger.info(f"✅ Atualização concluída: {'sucesso' if success else 'falha'}")
        
    except Exception as e:
        logger.error(f"❌ Erro na atualização: {e}")
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
        "service": "dashboard-automation"
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint para verificar status da automação"""
    global last_run_status, is_running
    
    return jsonify({
        "automation_status": last_run_status,
        "is_running": is_running,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/trigger', methods=['POST'])
def trigger_automation():
    """Endpoint para disparar atualização manual"""
    global automation_thread, is_running
    
    if is_running:
        return jsonify({
            "status": "error",
            "message": "Automação já está em execução"
        }), 409
    
    try:
        # Iniciar thread para execução
        automation_thread = threading.Thread(target=run_automation_update)
        automation_thread.daemon = True
        automation_thread.start()
        
        return jsonify({
            "status": "triggered",
            "message": "Automação iniciada",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao disparar automação: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Endpoint para visualizar logs recentes"""
    try:
        log_file = 'logs/dashboard_automation.log'
        
        if not os.path.exists(log_file):
            return jsonify({"logs": [], "message": "Arquivo de log não encontrado"})
        
        # Ler últimas 100 linhas
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_logs = lines[-100:] if len(lines) > 100 else lines
        
        return jsonify({
            "logs": [line.strip() for line in recent_logs],
            "total_lines": len(lines),
            "recent_lines": len(recent_logs)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao ler logs: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Endpoint para visualizar configuração atual"""
    try:
        from config import GOOGLE_SHEETS_CONFIG, AUTOMATION_CONFIG
        
        # Ocultar informações sensíveis
        safe_config = {
            "channels": list(GOOGLE_SHEETS_CONFIG.keys()),
            "update_interval_hours": AUTOMATION_CONFIG.get("update_interval_hours", 3),
            "dashboard_file": AUTOMATION_CONFIG.get("dashboard_file"),
            "backup_enabled": AUTOMATION_CONFIG.get("backup_enabled", True)
        }
        
        return jsonify(safe_config)
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter configuração: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Página inicial com informações da API"""
    return jsonify({
        "service": "Dashboard Automation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status", 
            "trigger": "/trigger (POST)",
            "logs": "/logs",
            "config": "/config"
        },
        "timestamp": datetime.now().isoformat()
    })

def scheduled_automation():
    """Executa automação agendada a cada 3 horas"""
    logger.info("⏰ Iniciando automação agendada...")
    
    while True:
        try:
            # Executar automação
            run_automation_update()
            
            # Aguardar 3 horas (10800 segundos)
            time.sleep(10800)
            
        except Exception as e:
            logger.error(f"❌ Erro na automação agendada: {e}")
            # Aguardar 30 minutos antes de tentar novamente
            time.sleep(1800)

def start_scheduled_automation():
    """Inicia thread de automação agendada"""
    try:
        scheduler_thread = threading.Thread(target=scheduled_automation)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info("✅ Automação agendada iniciada (a cada 3 horas)")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar automação agendada: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando aplicação Cloud Run...")
    
    # Verificar se deve iniciar automação agendada
    # (apenas se não estiver sendo chamada via Cloud Scheduler)
    if os.environ.get('AUTOMATION_MODE') != 'scheduler':
        start_scheduled_automation()
    
    # Iniciar Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
