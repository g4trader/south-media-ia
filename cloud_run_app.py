#!/usr/bin/env python3
"""
Aplicação principal para Google Cloud Run
Executa automação do dashboard e serve endpoints HTTP
"""

import os
import json
import logging
import uuid
import subprocess
from flask import Flask, request, jsonify, make_response, send_from_directory
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

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

# Configurar CORS
def configure_cors():
    """Configurar headers CORS"""
    cors_origin = os.environ.get('CORS_ORIGIN', '*')
    return {
        'Access-Control-Allow-Origin': cors_origin,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '3600'
    }

def add_cors_headers(response):
    """Adicionar headers CORS à resposta"""
    cors_headers = configure_cors()
    for key, value in cors_headers.items():
        response.headers[key] = value
    return response

def commit_and_push_dashboard(file_path, dashboard_name):
    """Fazer commit e push do dashboard criado para o Git"""
    try:
        # Configurar Git (se necessário)
        subprocess.run(['git', 'config', '--global', 'user.email', 'g4trader.news@gmail.com'], 
                      capture_output=True, text=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Dashboard Bot'], 
                      capture_output=True, text=True)
        
        # Verificar se é um repositório Git
        result = subprocess.run(['git', 'status'], 
                               capture_output=True, text=True, cwd='/app')
        if result.returncode != 0:
            logger.warning(f"❌ Não é um repositório Git: {result.stderr}")
            return False
        
        # Adicionar arquivo ao Git
        result = subprocess.run(['git', 'add', file_path], 
                               capture_output=True, text=True, cwd='/app')
        if result.returncode != 0:
            logger.warning(f"Erro ao adicionar arquivo ao Git: {result.stderr}")
            return False
        
        # Fazer commit
        commit_message = f"Add dashboard: {dashboard_name}"
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                               capture_output=True, text=True, cwd='/app')
        if result.returncode != 0:
            logger.warning(f"Erro ao fazer commit: {result.stderr}")
            return False
        
        # Fazer push
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                               capture_output=True, text=True, cwd='/app')
        if result.returncode != 0:
            logger.warning(f"Erro ao fazer push: {result.stderr}")
            return False
        
        logger.info(f"✅ Dashboard {dashboard_name} commitado e enviado para o Git")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao fazer commit/push do dashboard: {e}")
        return False

def update_dashboard_list(new_filename):
    """Atualizar lista de dashboards no arquivo auth_system_hybrid.js"""
    try:
        js_file_path = 'auth_system_hybrid.js'
        
        # Ler o arquivo atual
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar a lista de staticFiles
        import re
        pattern = r"const staticFiles = \[(.*?)\];"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Extrair a lista atual
            current_files = match.group(1)
            
            # Verificar se o arquivo já está na lista
            if new_filename not in current_files:
                # Adicionar o novo arquivo à lista (em ordem alfabética)
                files_list = []
                for line in current_files.split('\n'):
                    line = line.strip()
                    if line.startswith("'") and line.endswith("',"):
                        file_name = line[1:-2]  # Remove aspas e vírgula
                        files_list.append(file_name)
                
                # Adicionar o novo arquivo
                files_list.append(new_filename)
                files_list.sort()  # Ordenar alfabeticamente
                
                # Reconstruir a lista
                new_files_list = "[\n"
                for file_name in files_list:
                    new_files_list += f"                '{file_name}',\n"
                new_files_list += "            ]"
                
                # Substituir no conteúdo
                new_content = content.replace(match.group(0), f"const staticFiles = {new_files_list};")
                
                # Salvar o arquivo atualizado
                with open(js_file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Fazer commit e push da atualização
                subprocess.run(['git', 'add', js_file_path], 
                              capture_output=True, text=True, cwd='/app')
                subprocess.run(['git', 'commit', '-m', f'Update dashboard list: add {new_filename}'], 
                              capture_output=True, text=True, cwd='/app')
                subprocess.run(['git', 'push', 'origin', 'main'], 
                              capture_output=True, text=True, cwd='/app')
                
                logger.info(f"✅ Lista de dashboards atualizada com {new_filename}")
                return True
        
        logger.warning(f"❌ Não foi possível encontrar a lista staticFiles no arquivo {js_file_path}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar lista de dashboards: {e}")
        return False

# Handler para OPTIONS requests (CORS preflight)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        return add_cors_headers(response)

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
    response = jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-automation"
    })
    return add_cors_headers(response)

@app.route('/', methods=['OPTIONS'])
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path=None):
    """Manipular requisições OPTIONS para CORS"""
    response = make_response('', 200)
    return add_cors_headers(response)

@app.route('/api/semana-pescado/latest-file', methods=['GET'])
def get_latest_semana_pescado_file():
    """Retornar o arquivo mais recente do dashboard Semana do Pescado"""
    try:
        import glob
        import os
        
        # Procurar pelo arquivo mais recente
        pattern = '/app/static/dash_semana_do_pescado_FINAL_NO_NETFLIX_*.html'
        files = glob.glob(pattern)
        
        if files:
            # Encontrar o arquivo mais recente
            latest_file = max(files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            
            logger.info(f"📁 Arquivo mais recente encontrado: {filename}")
            
            response = jsonify({
                "success": True,
                "latest_file": filename,
                "file_path": latest_file,
                "timestamp": datetime.now().isoformat()
            })
            return add_cors_headers(response), 200
        else:
            logger.warning("❌ Nenhum arquivo do Semana do Pescado encontrado")
            response = jsonify({
                "success": False,
                "message": "Nenhum arquivo do Semana do Pescado encontrado",
                "timestamp": datetime.now().isoformat()
            })
            return add_cors_headers(response), 404
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar arquivo mais recente: {e}")
        response = jsonify({
            "success": False,
            "message": f"Erro ao buscar arquivo: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        return add_cors_headers(response), 500

@app.route('/api/semana-pescado/sync', methods=['POST'])
def sync_semana_pescado():
    """Sincronizar dados específicos da campanha Semana do Pescado"""
    try:
        logger.info("🔄 Iniciando sincronização da Semana do Pescado")
        
        scripts_to_run = [
            'google_sheets_processor.py',
            'process_daily_data.py',
            'generate_dashboard_final_no_netflix.py'
        ]
        
        results = []
        
        for script in scripts_to_run:
            try:
                logger.info(f"📄 Executando script: {script}")
                result = subprocess.run([
                    'python', script
                ], capture_output=True, text=True, timeout=60, cwd='/app')
                
                results.append({
                    'script': script,
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'error': result.stderr if result.returncode != 0 else None
                })
                
                if result.returncode == 0:
                    logger.info(f"✅ Script {script} executado com sucesso")
                else:
                    logger.error(f"❌ Erro no script {script}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"⏰ Timeout no script {script}")
                results.append({
                    'script': script,
                    'success': False,
                    'error': 'Timeout - script demorou mais de 60 segundos'
                })
            except Exception as e:
                logger.error(f"❌ Exceção no script {script}: {e}")
                results.append({
                    'script': script,
                    'success': False,
                    'error': str(e)
                })
        
        all_success = all(result['success'] for result in results)
        
        import glob
        dashboard_files = glob.glob('/app/static/dash_semana_do_pescado_FINAL_NO_NETFLIX_*.html')
        latest_dashboard = max(dashboard_files, key=lambda x: os.path.getmtime(x)) if dashboard_files else None
        
        logger.info(f"🎯 Sincronização concluída. Sucesso: {all_success}")
        
        response = jsonify({
            "success": all_success,
            "message": "Sincronização da Semana do Pescado concluída" if all_success else "Sincronização parcialmente concluída",
            "timestamp": datetime.now().isoformat(),
            "scripts_results": results,
            "dashboard_file": os.path.basename(latest_dashboard) if latest_dashboard else None,
            "dashboard_path": latest_dashboard if latest_dashboard else None
        })
        return add_cors_headers(response), 200 if all_success else 207
        
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        response = jsonify({
            "success": False,
            "message": f"Erro na sincronização: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        return add_cors_headers(response), 500

@app.route('/')
def serve_dashboard():
    """Servir painel de controle principal"""
    try:
        index_path = os.path.join(os.getcwd(), 'index.html')
        if os.path.exists(index_path):
            response = make_response(send_from_directory(os.getcwd(), 'index.html'))
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return add_cors_headers(response)
        else:
            return jsonify({"error": "Painel de controle não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao servir painel de controle: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos (dashboards HTML)"""
    try:
        static_dir = os.path.join(os.getcwd(), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)
        
        file_path = os.path.join(static_dir, filename)
        if not os.path.exists(file_path):
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        response = make_response(send_from_directory(static_dir, filename))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Erro ao servir arquivo estático {filename}: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint para verificar status da automação"""
    global last_run_status, is_running
    
    response = jsonify({
        "automation_status": last_run_status,
        "is_running": is_running,
        "timestamp": datetime.now().isoformat()
    })
    return add_cors_headers(response)

@app.route('/trigger', methods=['POST'])
def trigger_automation():
    """Endpoint para disparar atualização manual"""
    global last_run_status, is_running
    
    if is_running:
        response = jsonify({
            "status": "error",
            "message": "Automação já está em execução"
        })
        return add_cors_headers(response), 409
    
    try:
        # Executar diretamente em vez de usar thread
        is_running = True
        logger.info("🚀 Iniciando automação...")
        
        # Importar e executar automação
        from dashboard_automation import DashboardAutomation
        
        automation = DashboardAutomation()
        success = automation.run_update()
        
        last_run_status = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "error": None if success else "Falha na atualização"
        }
        
        is_running = False
        logger.info(f"✅ Automação concluída: {'sucesso' if success else 'falha'}")
        
        response = jsonify({
            "status": "completed",
            "message": f"Automação {'bem-sucedida' if success else 'falhou'}",
            "timestamp": datetime.now().isoformat(),
            "success": success
        })
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"❌ Erro ao disparar automação: {e}")
        last_run_status = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        is_running = False
        response = jsonify({
            "status": "error",
            "message": str(e)
        })
        return add_cors_headers(response), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Endpoint para visualizar logs recentes"""
    try:
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)
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

@app.route('/api/dashboards', methods=['POST'])
def create_dashboard():
    """Endpoint para criar novos dashboards via interface web"""
    try:
        data = request.get_json()
        logger.info(f"📊 Recebida requisição para criar dashboard: {data.get('campaignName', 'N/A')}")
        
        # Debug específico para datas
        logger.info(f"🗓️ Debug datas - startDate: '{data.get('startDate')}' (tipo: {type(data.get('startDate'))})")
        logger.info(f"🗓️ Debug datas - endDate: '{data.get('endDate')}' (tipo: {type(data.get('endDate'))})")
        
        # Importar e usar o DashboardBuilder
        try:
            from dashboard_builder_api_enhanced import DashboardBuilderEnhanced
            
            builder = DashboardBuilderEnhanced()
            logger.info(f"🔧 Builder inicializado: {type(builder)}")
            
            # Validar dados da campanha
            validation_result = builder.validate_campaign_data(data)
            logger.info(f"✅ Validação da campanha: {validation_result}")
            if not validation_result['valid']:
                return add_cors_headers(jsonify({
                    "success": False,
                    "message": f"Dados inválidos: {validation_result['errors']}"
                })), 400
            
            # Processar canais
            processed_channels = []
            for channel in data.get('channels', []):
                try:
                    logger.info(f"🔄 Processando canal: {channel.get('name')}")
                    logger.info(f"📄 Dados do canal: {channel}")
                    channel_data = builder.process_channel_data(channel)
                    logger.info(f"✅ Canal processado com sucesso: {channel.get('name')}")
                    processed_channels.append(channel_data)
                except Exception as e:
                    logger.error(f"❌ Erro ao processar canal {channel.get('name')}: {e}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    return add_cors_headers(jsonify({
                        "success": False,
                        "message": f"Erro ao processar canal {channel.get('name')}: {str(e)}"
                    })), 400
            
            # Gerar dashboard
            dashboard_id = str(uuid.uuid4())
            filename = f"dash_{data.get('campaignName', 'campaign').lower().replace(' ', '_')}.html"
            
            # Preparar dados para geração do dashboard
            dashboard_data = {
                'id': dashboard_id,
                'campaignName': data.get('campaignName', 'Campaign'),
                'startDate': data.get('startDate'),
                'endDate': data.get('endDate'),
                'totalBudget': data.get('totalBudget'),
                'reportModel': data.get('reportModel', 'Simples'),
                'kpiType': data.get('kpiType'),
                'kpiValue': data.get('kpiValue'),
                'kpiTarget': data.get('kpiTarget'),
                'strategies': data.get('strategies'),
                'channels': processed_channels
            }
            
            # Gerar HTML do dashboard
            try:
                html_content = builder.generate_dashboard_html(dashboard_data)
                
                # Salvar arquivo HTML na pasta static
                import os
                os.makedirs('static', exist_ok=True)
                filepath = os.path.join('static', filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"✅ Dashboard HTML salvo em: {filepath}")
                
                # Tentar fazer commit e push para o Git (para deploy automático no Vercel)
                git_success = commit_and_push_dashboard(filepath, data.get('campaignName', 'Campaign'))
                
                # Atualizar lista de dashboards no frontend
                list_updated = False
                if git_success:
                    list_updated = update_dashboard_list(filename)
                
                result = {
                    "success": True,
                    "dashboard": {
                        "id": dashboard_id,
                        "name": data.get('campaignName', 'Campaign'),
                        "status": "created",
                        "html_file": filename,
                        "html_path": filepath,
                        "html_content": html_content,  # Incluir conteúdo HTML na resposta
                        "channels": processed_channels,
                        "git_pushed": git_success,
                        "list_updated": list_updated
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ Erro ao gerar HTML do dashboard: {e}")
                return add_cors_headers(jsonify({
                    "success": False,
                    "message": f"Erro ao gerar dashboard: {str(e)}"
                })), 500
            
        except ImportError as e:
            logger.error(f"❌ Erro ao importar DashboardBuilderEnhanced: {e}")
            return add_cors_headers(jsonify({
                "success": False,
                "message": f"Erro ao importar módulo: {str(e)}"
            })), 500
        
        if result.get('success'):
            logger.info(f"✅ Dashboard criado com sucesso: {result.get('dashboard', {}).get('name', 'N/A')}")
            return add_cors_headers(jsonify(result))
        else:
            logger.error(f"❌ Erro ao criar dashboard: {result.get('message', 'Erro desconhecido')}")
            return add_cors_headers(jsonify(result)), 400
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /api/dashboards: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        })), 500

@app.route('/api/dashboards/<dashboard_id>', methods=['GET'])
def get_dashboard(dashboard_id):
    """Endpoint para obter informações de um dashboard específico"""
    try:
        # Implementar lógica para buscar dashboard por ID
        return add_cors_headers(jsonify({
            "success": True,
            "dashboard": {
                "id": dashboard_id,
                "status": "active"
            }
        }))
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dashboard {dashboard_id}: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": str(e)
        })), 500

@app.route('/api/dashboards/<dashboard_id>/download', methods=['GET'])
def download_dashboard(dashboard_id):
    """Endpoint para download de dashboard"""
    try:
        # Implementar lógica de download
        return add_cors_headers(jsonify({
            "success": True,
            "message": "Download implementado"
        }))
    except Exception as e:
        logger.error(f"❌ Erro no download do dashboard {dashboard_id}: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": str(e)
        })), 500

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
            "config": "/config",
            "api_dashboards": "/api/dashboards (POST)",
            "api_dashboard_get": "/api/dashboards/<id> (GET)",
            "api_dashboard_download": "/api/dashboards/<id>/download (GET)"
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

@app.route('/api/semana-pescado/latest-file', methods=['GET'])
def get_latest_semana_pescado_file():
    """Retornar o arquivo mais recente do dashboard Semana do Pescado"""
    try:
        import glob
        import os
        
        # Procurar pelo arquivo mais recente
        pattern = '/app/static/dash_semana_do_pescado_FINAL_NO_NETFLIX_*.html'
        files = glob.glob(pattern)
        
        if files:
            # Encontrar o arquivo mais recente
            latest_file = max(files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            
            logger.info(f"📁 Arquivo mais recente encontrado: {filename}")
            
            return jsonify({
                "success": True,
                "latest_file": filename,
                "file_path": latest_file,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            logger.warning("❌ Nenhum arquivo do Semana do Pescado encontrado")
            return jsonify({
                "success": False,
                "message": "Nenhum arquivo do Semana do Pescado encontrado",
                "timestamp": datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar arquivo mais recente: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar arquivo: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/semana-pescado/sync', methods=['POST'])
def sync_semana_pescado():
    """Sincronizar dados específicos da campanha Semana do Pescado"""
    try:
        logger.info("🔄 Iniciando sincronização da Semana do Pescado")
        
        # Executar scripts de processamento específicos para Semana do Pescado
        scripts_to_run = [
            'google_sheets_processor.py',
            'process_daily_data.py',
            'generate_dashboard_final_no_netflix.py'
        ]
        
        results = []
        
        for script in scripts_to_run:
            try:
                logger.info(f"📄 Executando script: {script}")
                result = subprocess.run([
                    'python', script
                ], capture_output=True, text=True, timeout=60, cwd='/app')
                
                results.append({
                    'script': script,
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'error': result.stderr if result.returncode != 0 else None
                })
                
                if result.returncode == 0:
                    logger.info(f"✅ Script {script} executado com sucesso")
                else:
                    logger.error(f"❌ Erro no script {script}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"⏰ Timeout no script {script}")
                results.append({
                    'script': script,
                    'success': False,
                    'error': 'Timeout - script demorou mais de 60 segundos'
                })
            except Exception as e:
                logger.error(f"❌ Exceção no script {script}: {e}")
                results.append({
                    'script': script,
                    'success': False,
                    'error': str(e)
                })
        
        # Verificar se todos os scripts executaram com sucesso
        all_success = all(result['success'] for result in results)
        
        # Buscar o arquivo de dashboard mais recente
        import glob
        dashboard_files = glob.glob('/app/static/dash_semana_do_pescado_FINAL_NO_NETFLIX_*.html')
        latest_dashboard = max(dashboard_files, key=lambda x: os.path.getmtime(x)) if dashboard_files else None
        
        logger.info(f"🎯 Sincronização concluída. Sucesso: {all_success}")
        
        return jsonify({
            "success": all_success,
            "message": "Sincronização da Semana do Pescado concluída" if all_success else "Sincronização parcialmente concluída",
            "timestamp": datetime.now().isoformat(),
            "scripts_results": results,
            "dashboard_file": os.path.basename(latest_dashboard) if latest_dashboard else None,
            "dashboard_path": latest_dashboard if latest_dashboard else None
        }), 200 if all_success else 207  # 207 = Multi-Status
        
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro na sincronização: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

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
