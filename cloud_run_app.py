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
import sys
from flask import Flask, request, jsonify, make_response, send_from_directory
from datetime import datetime
import threading
import time

# Adicionar paths para importar módulos
sys.path.append('static/generator/processors')
sys.path.append('static/generator/config')

# Configurar logging primeiro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar extrator de dados
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'static', 'generator', 'processors'))
    from simple_video_extractor import SimpleVideoExtractor as VideoCampaignDataExtractor
    logger.info("✅ SimpleVideoExtractor importado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar SimpleVideoExtractor: {e}")
    VideoCampaignDataExtractor = None

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

@app.route('/api/debug-google-sheets', methods=['GET'])
def debug_google_sheets():
    """Endpoint para debug do Google Sheets"""
    try:
        import subprocess
        import sys
        
        # Executar o script de debug
        result = subprocess.run([
            sys.executable, 'debug_google_sheets_cloud_run.py'
        ], capture_output=True, text=True, timeout=60)
        
        return add_cors_headers(jsonify({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }))
        
    except Exception as e:
        return add_cors_headers(jsonify({
            "success": False,
            "error": str(e)
        })), 500

@app.route('/api/backup-database', methods=['POST'])
def backup_database():
    """Forçar backup manual do banco de dados"""
    try:
        from persistent_database import force_backup
        
        logger.info("🔄 Forçando backup manual do banco de dados...")
        force_backup()
        
        return add_cors_headers(jsonify({
            "success": True,
            "message": "Backup realizado com sucesso",
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        logger.error(f"❌ Erro no backup manual: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro no backup: {str(e)}"
        })), 500

@app.route('/api/debug-git', methods=['GET', 'POST'])
def debug_git():
    """Debug do sistema Git"""
    try:
        github_token = os.getenv('GITHUB_TOKEN')
        
        debug_info = {
            "github_token_configured": bool(github_token),
            "github_token_length": len(github_token) if github_token else 0,
            "current_directory": os.getcwd(),
            "git_status": None,
            "git_remote": None,
            "git_automation_test": None
        }
        
        # Testar Git local
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=10)
            debug_info["git_status"] = result.stdout.strip()
            
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True, timeout=10)
            debug_info["git_remote"] = result.stdout.strip()
        except Exception as e:
            debug_info["git_error"] = str(e)
        
        # Testar GitAutomation
        try:
            from git_automation import GitAutomation
            git = GitAutomation()
            debug_info["git_automation_test"] = git.test_github_connection()
        except Exception as e:
            debug_info["git_automation_error"] = str(e)
        
        return add_cors_headers(jsonify({
            "success": True,
            "debug_info": debug_info
        }))
        
    except Exception as e:
        logger.error(f"❌ Erro no debug Git: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro no debug: {str(e)}"
        })), 500

@app.route('/api/test-git-commit', methods=['POST', 'OPTIONS'])
def test_git_commit():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    """Testar commit automático"""
    try:
        from git_automation import GitAutomation
        git = GitAutomation()
        
        # Criar arquivo de teste
        test_content = f"""# Teste de Commit Automático

Este é um teste do sistema de commit automático do gerador de dashboards.

- Gerado em: {datetime.now().isoformat()}
- Sistema: Cloud Run
- Objetivo: Verificar se o commit automático está funcionando

Se você está vendo este arquivo, o commit automático está funcionando! 🎉
"""
        
        test_file_path = "test_git_automation.md"
        commit_message = f"🧪 Teste de commit automático - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        success = git.commit_file_to_github(test_file_path, test_content, commit_message)
        
        return add_cors_headers(jsonify({
            "success": success,
            "message": "Teste de commit automático realizado",
            "test_file": test_file_path,
            "commit_message": commit_message
        }))
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de commit: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro no teste: {str(e)}"
        })), 500

@app.route('/api/test-data-access', methods=['POST', 'OPTIONS'])
def test_data_access():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    """Testar acesso aos dados"""
    try:
        data = request.get_json()
        
        if not data:
            return add_cors_headers(jsonify({
                "success": False,
                "message": "Dados JSON não fornecidos"
            })), 400
        
        # Testar acesso aos campos
        test_results = {}
        for field in ['client', 'campaign', 'sheet_id', 'tabs', 'campaign_key']:
            try:
                test_results[field] = data[field]
            except KeyError as e:
                test_results[field] = f"Erro: {str(e)}"
        
        return add_cors_headers(jsonify({
            "success": True,
            "message": "Teste de acesso aos dados realizado",
            "data": test_results
        }))
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de dados: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro no teste: {str(e)}"
        })), 500

@app.route('/api/migrate-to-database', methods=['POST'])
def migrate_to_database():
    """Migrar configurações do JSON para o banco de dados"""
    try:
        from persistent_database import db
        
        logger.info("🔄 Iniciando migração do JSON para banco de dados...")
        
        # Migrar configurações
        success = db.migrate_from_json()
        
        if success:
            # Contar campanhas migradas
            campaigns = db.get_all_campaign_configs()
            count = len(campaigns)
            
            return add_cors_headers(jsonify({
                "success": True,
                "message": f"Migração concluída com sucesso! {count} campanhas migradas para o banco de dados.",
                "campaigns_migrated": count
            }))
        else:
            return add_cors_headers(jsonify({
                "success": False,
                "message": "Erro na migração para o banco de dados"
            })), 500
            
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        })), 500

@app.after_request
def after_request(response):
    """Aplicar headers CORS a todas as respostas"""
    return add_cors_headers(response)

def commit_and_push_dashboard(file_path, dashboard_name):
    """Fazer commit e push do dashboard criado para o Git"""
    try:
        # Configurar Git (se necessário)
        subprocess.run(['git', 'config', '--global', 'user.email', 'g4trader.news@gmail.com'], 
                      capture_output=True, text=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Dashboard Bot'], 
                      capture_output=True, text=True)
        
        # No Cloud Run, usar /app como diretório de trabalho
        import os
        current_dir = '/app'
        logger.info(f"📁 Diretório de trabalho: {current_dir}")
        
        # Verificar se é um repositório Git
        result = subprocess.run(['git', 'status'], 
                               capture_output=True, text=True, cwd=current_dir)
        if result.returncode != 0:
            logger.warning(f"❌ Não é um repositório Git: {result.stderr}")
            return False
        
        # Adicionar arquivo ao Git
        logger.info(f"📝 Adicionando arquivo ao Git: {file_path}")
        result = subprocess.run(['git', 'add', file_path], 
                               capture_output=True, text=True, cwd=current_dir)
        if result.returncode != 0:
            logger.warning(f"❌ Erro ao adicionar arquivo ao Git: {result.stderr}")
            return False
        logger.info(f"✅ Arquivo adicionado ao Git: {result.stdout}")
        
        # Fazer commit
        commit_message = f"Add dashboard: {dashboard_name}"
        logger.info(f"📝 Fazendo commit: {commit_message}")
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                               capture_output=True, text=True, cwd=current_dir)
        if result.returncode != 0:
            logger.warning(f"❌ Erro ao fazer commit: {result.stderr}")
            return False
        logger.info(f"✅ Commit realizado: {result.stdout}")
        
        # Fazer push
        logger.info(f"📤 Fazendo push para origin main...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                               capture_output=True, text=True, cwd=current_dir)
        if result.returncode != 0:
            logger.warning(f"❌ Erro ao fazer push: {result.stderr}")
            return False
        logger.info(f"✅ Push realizado: {result.stdout}")
        
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

@app.route('/api/debug-extractor/<campaign_key>', methods=['GET'])
def debug_extractor(campaign_key):
    """Debug específico do extrator de dados"""
    try:
        logger.info(f"🔍 Debug do extrator para campanha: {campaign_key}")
        
        # Importar configuração do banco de dados
        from persistent_database import get_campaign_config
        
        # Obter configuração da campanha do banco de dados
        config = get_campaign_config(campaign_key)
        if not config:
            return add_cors_headers(jsonify({
                "success": False,
                "message": f"Campanha '{campaign_key}' não encontrada"
            })), 404
        
        debug_info = {
            "campaign_key": campaign_key,
            "config_found": True,
            "config": {
                "client": config.client,
                "campaign": config.campaign,
                "sheet_id": config.sheet_id,
                "tabs": config.tabs
            },
            "extractor_available": VideoCampaignDataExtractor is not None,
            "extraction_result": None,
            "error": None
        }
        
        if VideoCampaignDataExtractor:
            try:
                logger.info(f"🔄 Criando extrator para debug...")
                extractor = VideoCampaignDataExtractor(config)
                logger.info("🔄 Extrator criado, iniciando extração de debug...")
                data = extractor.extract_data()
                debug_info["extraction_result"] = {
                    "success": data is not None,
                    "data_type": type(data).__name__ if data else None,
                    "data_size": len(str(data)) if data else 0,
                    "has_daily_data": bool(data and data.get("daily_data")) if data else False,
                    "daily_data_count": len(data.get("daily_data", [])) if data else 0
                }
                logger.info(f"✅ Debug do extrator concluído: {debug_info['extraction_result']}")
            except Exception as e:
                debug_info["error"] = str(e)
                debug_info["extraction_result"] = {"success": False, "error": str(e)}
                logger.error(f"❌ Erro no debug do extrator: {e}")
                import traceback
                debug_info["traceback"] = traceback.format_exc()
        
        return add_cors_headers(jsonify({
            "success": True,
            "debug_info": debug_info
        }))
        
    except Exception as e:
        logger.error(f"❌ Erro no debug do extrator: {e}")
        return add_cors_headers(jsonify({
            "success": False,
            "message": f"Erro no debug: {str(e)}"
        })), 500

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

@app.route('/api/<campaign_key>/data', methods=['GET'])
def get_campaign_data(campaign_key):
    """Obter dados de uma campanha específica"""
    try:
        logger.info(f"📊 Carregando dados da campanha: {campaign_key}")
        
        # Importar configuração do banco de dados
        from persistent_database import get_campaign_config
        
        # Obter configuração da campanha do banco de dados
        config = get_campaign_config(campaign_key)
        if not config:
            return jsonify({
                "success": False,
                "message": f"Campanha '{campaign_key}' não encontrada"
            }), 404
        
        # Tentar carregar dados reais primeiro
        data = None
        source = "test_data"
        
        if VideoCampaignDataExtractor:
            try:
                logger.info(f"🔄 Criando extrator para campanha: {config.campaign_key}")
                extractor = VideoCampaignDataExtractor(config)
                logger.info("🔄 Extrator criado, iniciando extração...")
                data = extractor.extract_data()
                logger.info(f"🔄 Extração concluída. Dados: {type(data)}, Tamanho: {len(str(data)) if data else 0}")
                if data:
                    source = "google_sheets"
                    logger.info("✅ Dados reais carregados do Google Sheets")
                else:
                    logger.warning("⚠️ Extrator retornou dados vazios")
            except Exception as e:
                logger.error(f"❌ Erro na extração: {e}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
        else:
            logger.warning("⚠️ VideoCampaignDataExtractor não disponível")
        
        # Se não conseguiu dados reais, usar dados de teste
        if not data:
            logger.info("🔄 Usando dados de teste - Google Sheets não acessível (credenciais não configuradas)")
            try:
                from static.generator.processors.test_video_campaign_data import create_test_data
                data = create_test_data(config)
                # Adicionar flag indicando que são dados de teste
                data["test_mode"] = True
                data["test_message"] = "Dados de demonstração - Configure credenciais do Google Sheets para dados reais"
            except ImportError as e:
                logger.error(f"❌ Erro ao importar create_test_data: {e}")
                # Usar dados básicos como fallback
                fallback_data = {
                    "contract": {
                        "client": config.client,
                        "campaign": config.campaign,
                        "status": "Em andamento"
                    },
                    "daily_data": [],
                    "strategies": {
                        "segmentation": ["Segmentação A", "Segmentação B"],
                        "objectives": ["Objetivo 1", "Objetivo 2"]
                    },
                    "publishers": [
                        {"name": "Publisher A", "type": "Site: publisher-a.com"},
                        {"name": "Publisher B", "type": "Site: publisher-b.com"}
                    ],
                    "test_mode": True,
                    "test_message": "Dados de demonstração - Configure credenciais do Google Sheets para dados reais"
                }
                data = fallback_data
        
        if data:
            return jsonify({
                "success": True,
                "data": {
                    "campaign_name": data.get("campaign_name", f"{config.client} - {config.campaign}"),
                    "dashboard_title": data.get("dashboard_title", f"Dashboard {config.client} - {config.campaign}"),
                    "channel": data.get("channel", "Prográmatica"),
                    "creative_type": data.get("creative_type", "Video"),
                    "period": data.get("period", "15/09/2025 - 30/09/2025"),
                    "metrics": {
                        "budget_contracted": data.get("budget_contracted", 31000),
                        "spend": data.get("metrics", {}).get("spend", 0),
                        "impressions": data.get("metrics", {}).get("impressions", 0),
                        "impressions_contracted": 193750,  # Valor contratado
                        "clicks": data.get("metrics", {}).get("clicks", 0),
                        "ctr": data.get("metrics", {}).get("ctr", 0),
                        "q100": data.get("metrics", {}).get("q100", 0),
                        "starts": data.get("metrics", {}).get("starts", 0),
                        "vtr": data.get("metrics", {}).get("vtr", 0),
                        "cpv": data.get("metrics", {}).get("cpv", 0),
                        "cpm": data.get("metrics", {}).get("cpm", 0),
                        "pacing": data.get("metrics", {}).get("pacing", 0),
                        "vc_contracted": data.get("metrics", {}).get("vc_contracted", 0),
                        "vc_delivered": data.get("metrics", {}).get("vc_delivered", 0),
                        "vc_pacing": data.get("metrics", {}).get("vc_pacing", 0)
                    },
                    "daily_data": data.get("daily_data", []),
                    "per_data": data.get("per_data", []),
                    "contract": data.get("contract", {}),
                    "strategies": data.get("strategies", {}),
                    "publishers": data.get("publishers", [])
                },
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "test_mode": data.get("test_mode", False),
                "test_message": data.get("test_message", "")
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Nenhum dado encontrado para {config.client}"
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados da campanha {campaign_key}: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """Listar todas as campanhas disponíveis (estáticas + dinâmicas)"""
    try:
        from persistent_database import get_all_campaign_configs
        
        campaigns = get_all_campaign_configs()
        campaign_list = []
        
        for key, config in campaigns.items():
            campaign_list.append({
                "key": key,
                "client": config.client,
                "campaign": config.campaign,
                "slug": key,  # Usar campaign_key como slug
                "api_endpoint": f"/api/{key}/data",
                "dashboard_url": f"/static/dash_{key}.html",
                "created_at": config.created_at,
                "updated_at": config.updated_at
            })
        
        return jsonify({
            "success": True,
            "campaigns": campaign_list,
            "total": len(campaign_list)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar campanhas: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/commit-dashboard', methods=['POST', 'OPTIONS'])
def commit_dashboard():
    """Fazer commit e push de um dashboard específico"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        dashboard_filename = data.get('filename')
        
        if not dashboard_filename:
            return jsonify({
                "success": False,
                "message": "Nome do arquivo não fornecido"
            }), 400
        
        # Verificar se o arquivo existe
        filepath = os.path.join('static', dashboard_filename)
        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "message": f"Arquivo não encontrado: {dashboard_filename}"
            }), 404
        
        # Fazer commit e push
        dashboard_name = dashboard_filename.replace('dash_', '').replace('.html', '').replace('_', ' ').title()
        git_success = commit_and_push_dashboard(filepath, dashboard_name)
        
        if git_success:
            return jsonify({
                "success": True,
                "message": f"Dashboard {dashboard_name} commitado e enviado para o Git com sucesso!",
                "dashboard_url": f"https://dash.iasouth.tech/static/{dashboard_filename}"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Erro ao fazer commit/push do dashboard"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro ao fazer commit do dashboard: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/generate-dashboard', methods=['POST', 'OPTIONS'])
def generate_dashboard():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    """Gerar novo dashboard de campanha"""
    try:
        import os
        import shutil
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['campaign_key', 'client', 'campaign', 'sheet_id', 'tabs']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório não fornecido: {field}"
                }), 400
        
        # Gerar nome do arquivo do dashboard
        dashboard_filename = f"dash_{data['campaign_key']}.html"
        dashboard_path = f"static/{dashboard_filename}"
        
        # URL fixa do Cloud Run
        CLOUD_RUN_URL = "https://south-media-ia-609095880025.us-central1.run.app"
        
        # Verificar se já existe e remover se necessário
        if os.path.exists(dashboard_path):
            os.remove(dashboard_path)
        
        # Copiar template genérico
        template_path = "static/dash_video_programmatic_template.html"
        if not os.path.exists(template_path):
            return jsonify({
                "success": False,
                "message": "Template genérico não encontrado"
            }), 500
        
        # Copiar arquivo
        shutil.copy2(template_path, dashboard_path)
        logger.info(f"✅ Dashboard criado: {dashboard_path}")
        
        # Personalizar o arquivo para a campanha específica
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir placeholder do campaign_key pelo específico
        content = content.replace(
            'let campaignKey = \'CAMPAIGN_KEY_PLACEHOLDER\';',
            f'let campaignKey = \'{data["campaign_key"]}\'; // Definido para {data["client"]}'
        )
        
        # Substituir título da página
        content = content.replace(
            'Carregando Dashboard...',
            f'Dashboard {data["client"]} - {data["campaign"]}'
        )
        
        # Salvar arquivo personalizado
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Dashboard personalizado para {data['client']}")
        
        # Salvar campanha no banco de dados
        from persistent_database import CampaignConfig, save_campaign_config
        campaign_config = CampaignConfig(
            campaign_key=data['campaign_key'],
            client=data['client'],
            campaign=data['campaign'],
            sheet_id=data['sheet_id'],
            tabs=data['tabs']
        )
        
        if save_campaign_config(data['campaign_key'], campaign_config):
            logger.info(f"✅ Campanha {data['campaign_key']} salva no banco de dados")
        else:
            logger.warning(f"⚠️ Erro ao salvar campanha {data['campaign_key']} no banco de dados")
        
        # Fazer commit automático via GitHub API (como dashboard_automation.py)
        git_committed = False
        try:
            logger.info("🔄 Iniciando commit automático via GitHub API...")
            
            # Ler o arquivo gerado
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validação simplificada - verificar se arquivo não está vazio
            if not content.strip():
                logger.error("❌ Arquivo vazio, commit cancelado")
            else:
                logger.info("✅ Template validado, prosseguindo com commit seguro...")
                
                # Fazer commit direto via GitHub API (como dashboard_automation.py)
                import base64
                import requests
                
                # Configurar token do GitHub
                token = os.getenv('GITHUB_TOKEN')
                if not token:
                    logger.error("❌ Token do GitHub não configurado")
                else:
                    # Fazer commit
                    url = f"https://api.github.com/repos/g4trader/south-media-ia/contents/{dashboard_path}"
                    headers = {
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                    
                    # Obter SHA do arquivo atual (se existir)
                    response = requests.get(url, headers=headers)
                    current_sha = None
                    if response.status_code == 200:
                        current_sha = response.json()["sha"]
                        logger.info(f"✅ Arquivo existente encontrado, SHA: {current_sha[:8]}...")
                    elif response.status_code == 404:
                        logger.info("ℹ️ Arquivo não existe, será criado novo")
                    else:
                        logger.warning(f"⚠️ Erro ao verificar arquivo existente: {response.status_code}")
                    
                    # Fazer commit
                    commit_data = {
                        "message": f"🤖 Dashboard gerado: {data['client']} - {data['campaign']} ({datetime.now().strftime('%d/%m/%Y %H:%M')})",
                        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    }
                    
                    if current_sha:
                        commit_data["sha"] = current_sha
                    
                    response = requests.put(url, headers=headers, json=commit_data)
                    if response.status_code == 200:
                        commit_info = response.json()
                        logger.info("✅ Dashboard atualizado no GitHub com sucesso")
                        logger.info(f"   - SHA: {commit_info['commit']['sha'][:8]}...")
                        logger.info(f"   - URL: {commit_info['content']['html_url']}")
                        git_committed = True
                    else:
                        logger.error(f"❌ Erro no commit: {response.status_code} - {response.text}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit/push via GitHub API: {e}")
        
        if not git_committed:
            logger.info("ℹ️ Dashboard criado no Cloud Run - commit manual necessário para Vercel")
        
        return jsonify({
            "success": True,
            "message": f"Dashboard gerado com sucesso para {data['client']} - {data['campaign']}",
            "dashboard_url": f"/static/{dashboard_filename}",
            "dashboard_url_cloud_run": f"{CLOUD_RUN_URL}/static/{dashboard_filename}",
            "api_endpoint": f"/api/{data['campaign_key']}/data",
            "campaign_key": data['campaign_key'],
            "client": data['client'],
            "campaign": data['campaign'],
            "git_committed": git_committed,
            "note": "Dashboard disponível no Cloud Run. Commit automático via GitHub API ativado (se GITHUB_TOKEN configurado)."
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

# Manter compatibilidade com endpoint antigo
@app.route('/api/sebrae/data', methods=['GET'])
def get_sebrae_data():
    """Endpoint de compatibilidade para SEBRAE"""
    return get_campaign_data('sebrae_pr')

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
            
            # Gerar HTML do dashboard usando o sistema de geração de dashboards
            try:
                import shutil
                
                # Copiar template genérico
                template_path = "static/dash_video_programmatic_template.html"
                if not os.path.exists(template_path):
                    return jsonify({
                        "success": False,
                        "message": "Template genérico não encontrado"
                    }), 500
                
                # Criar arquivo do dashboard
                filepath = os.path.join('static', filename)
                shutil.copy2(template_path, filepath)
                logger.info(f"✅ Template copiado para: {filepath}")
                
                # Personalizar o arquivo para a campanha específica
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Substituir campaign_key genérico pelo específico
                content = content.replace(
                    'let campaignKey = urlParams.get(\'campaign\') || \'sebrae_pr\';',
                    f'let campaignKey = \'{data["campaign_key"]}\'; // Definido para {data["client"]}'
                )
                
                # Substituir título da página
                content = content.replace(
                    'Carregando Dashboard...',
                    f'Dashboard {data["client"]} - {data["campaign"]}'
                )
                
                # Salvar arquivo personalizado
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Dashboard personalizado salvo em: {filepath}")
                
                # Salvar campanha na configuração
                from generator_config import save_campaign
                config = CampaignConfig(
                    client=data['client'],
                    campaign=data['campaign'],
                    sheet_id=data['sheet_id'],
                    tabs=data['tabs']
                )
                
                if save_campaign(data['campaign_key'], config):
                    logger.info(f"✅ Campanha {data['campaign_key']} salva na configuração")
                else:
                    logger.warning(f"⚠️ Erro ao salvar campanha {data['campaign_key']} na configuração")
                
                # Fazer commit e push para o Git (para deploy automático no Vercel)
                git_success = commit_and_push_dashboard(filepath, data.get('campaign', 'Campaign'))
                
                # Atualizar lista de dashboards no frontend
                list_updated = False
                if git_success:
                    list_updated = update_dashboard_list(filename)
                
                result = {
                    "success": True,
                    "message": f"Dashboard gerado com sucesso para {data['client']} - {data['campaign']}",
                    "dashboard_url": f"/static/{filename}",
                    "api_endpoint": f"/api/{data['campaign_key']}/data",
                    "campaign_key": data['campaign_key'],
                    "client": data['client'],
                    "campaign": data['campaign'],
                    "git_committed": git_success,
                    "list_updated": list_updated
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

@app.route('/api/remove-dashboard', methods=['POST'])
def remove_dashboard():
    """Endpoint para remover qualquer dashboard"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({
                "success": False,
                "message": "Nome do arquivo não fornecido"
            }), 400
        
        filename = data['filename']
        if not filename.endswith('.html'):
            filename += '.html'
        
        dashboard_path = f"static/{filename}"
        if os.path.exists(dashboard_path):
            os.remove(dashboard_path)
            return jsonify({
                "success": True,
                "message": f"Dashboard {filename} removido com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Dashboard {filename} não encontrado"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao remover dashboard: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Configuração para desenvolvimento local
    logger.info("🚀 Iniciando servidor Flask para desenvolvimento local...")
    logger.info("📊 Dashboard SEBRAE disponível em: http://localhost:5000/static/dash_sebrae_programatica_video_sync.html")
    logger.info("🔗 API SEBRAE disponível em: http://localhost:5000/api/sebrae/data")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

