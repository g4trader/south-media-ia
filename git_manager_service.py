#!/usr/bin/env python3
"""
Git Manager Microservice
Microserviço dedicado para gerenciar commits automáticos de dashboards
"""

import os
import sys
import time
import logging
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/git_manager.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class GitManager:
    """Gerenciador de operações Git para dashboards"""
    
    def __init__(self):
        self.static_dir = Path('/app/static')
        self.git_dir = Path('/app')
        self.processed_files = set()
        self.last_check = datetime.now()
        
        # Configurar Git
        self._setup_git()
        
        logger.info("🚀 Git Manager inicializado")
    
    def _setup_git(self):
        """Configurar Git com credenciais"""
        try:
            # Verificar se estamos em um repositório Git
            try:
                result = subprocess.run(['git', 'status'], check=True, capture_output=True, text=True, cwd=self.git_dir)
                logger.info(f"✅ Repositório Git encontrado: {self.git_dir}")
            except subprocess.CalledProcessError:
                logger.error(f"❌ Não é um repositório Git: {self.git_dir}")
                raise Exception("Repositório Git não encontrado")
            
            # Configurar usuário Git
            subprocess.run([
                'git', 'config', '--global', 'user.name', 'Dashboard Bot'
            ], check=True, capture_output=True, cwd=self.git_dir)
            
            subprocess.run([
                'git', 'config', '--global', 'user.email', 'dashboard@automatizar.com'
            ], check=True, capture_output=True, cwd=self.git_dir)
            
            # Configurar remote com token se disponível
            github_token = os.environ.get('GITHUB_TOKEN')
            if github_token:
                # Configurar remote com token
                subprocess.run([
                    'git', 'remote', 'set-url', 'origin',
                    f'https://{github_token}@github.com/g4trader/south-media-ia.git'
                ], check=True, capture_output=True, cwd=self.git_dir)
                logger.info("✅ Git configurado com token GitHub")
                
                # Testar conexão
                try:
                    result = subprocess.run([
                        'git', 'fetch', 'origin', 'main'
                    ], check=True, capture_output=True, text=True, cwd=self.git_dir)
                    logger.info("✅ Conexão com GitHub testada com sucesso")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Falha ao testar conexão GitHub: {e.stderr}")
            else:
                logger.warning("⚠️ GITHUB_TOKEN não encontrado, usando credenciais padrão")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao configurar Git: {e}")
            raise
    
    def get_new_files(self) -> List[Path]:
        """Detectar arquivos novos na pasta static"""
        try:
            new_files = []
            
            if not self.static_dir.exists():
                logger.warning(f"⚠️ Pasta static não encontrada: {self.static_dir}")
                return new_files
            
            # Buscar arquivos .html na pasta static
            for file_path in self.static_dir.glob('dash_*.html'):
                if file_path.name not in self.processed_files:
                    # Verificar se o arquivo foi modificado recentemente (últimos 5 minutos)
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime > self.last_check - timedelta(minutes=5):
                        new_files.append(file_path)
                        logger.info(f"📄 Arquivo novo detectado: {file_path.name}")
            
            return new_files
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar arquivos novos: {e}")
            return []
    
    def commit_file(self, file_path: Path) -> bool:
        """Fazer commit de um arquivo específico"""
        try:
            relative_path = file_path.relative_to(self.git_dir)
            
            # Verificar se o arquivo existe
            if not file_path.exists():
                logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
                return False
            
            # Adicionar arquivo ao Git
            logger.info(f"🔧 Adicionando arquivo: {relative_path}")
            result = subprocess.run([
                'git', 'add', str(relative_path)
            ], check=True, capture_output=True, text=True, cwd=self.git_dir)
            
            # Verificar se há mudanças para commitar
            result = subprocess.run([
                'git', 'diff', '--cached', '--quiet'
            ], capture_output=True, cwd=self.git_dir)
            
            if result.returncode == 0:
                logger.info(f"ℹ️ Nenhuma mudança para commitar: {relative_path}")
                return True
            
            # Fazer commit
            commit_message = f"feat: Add dashboard {file_path.stem}"
            logger.info(f"🔧 Fazendo commit: {commit_message}")
            
            result = subprocess.run([
                'git', 'commit', '-m', commit_message
            ], check=True, capture_output=True, text=True, cwd=self.git_dir)
            
            logger.info(f"✅ Commit realizado: {result.stdout.strip()}")
            
            # Fazer push
            logger.info(f"🔧 Fazendo push...")
            result = subprocess.run([
                'git', 'push', 'origin', 'main'
            ], check=True, capture_output=True, text=True, cwd=self.git_dir)
            
            logger.info(f"✅ Push realizado com sucesso: {result.stdout.strip()}")
            
            # Marcar arquivo como processado
            self.processed_files.add(file_path.name)
            
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"❌ Erro no Git: {error_msg}")
            logger.error(f"❌ Comando que falhou: {e.cmd}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def process_new_files(self) -> Dict[str, any]:
        """Processar todos os arquivos novos"""
        try:
            new_files = self.get_new_files()
            
            if not new_files:
                return {
                    "success": True,
                    "message": "Nenhum arquivo novo encontrado",
                    "files_processed": 0,
                    "files": []
                }
            
            processed_files = []
            failed_files = []
            
            for file_path in new_files:
                logger.info(f"🔄 Processando arquivo: {file_path.name}")
                
                if self.commit_file(file_path):
                    processed_files.append(file_path.name)
                    logger.info(f"✅ Arquivo processado com sucesso: {file_path.name}")
                else:
                    failed_files.append(file_path.name)
                    logger.error(f"❌ Falha ao processar arquivo: {file_path.name}")
            
            # Atualizar timestamp da última verificação
            self.last_check = datetime.now()
            
            return {
                "success": len(failed_files) == 0,
                "message": f"Processados {len(processed_files)} arquivos, {len(failed_files)} falharam",
                "files_processed": len(processed_files),
                "files_failed": len(failed_files),
                "processed_files": processed_files,
                "failed_files": failed_files
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar arquivos: {e}")
            return {
                "success": False,
                "message": f"Erro ao processar arquivos: {str(e)}",
                "files_processed": 0,
                "files": []
            }
    
    def get_status(self) -> Dict[str, any]:
        """Obter status do Git Manager"""
        try:
            # Verificar status do Git
            result = subprocess.run([
                'git', 'status', '--porcelain'
            ], capture_output=True, text=True, cwd=self.git_dir)
            
            # Contar arquivos não commitados
            uncommitted_files = len([line for line in result.stdout.strip().split('\n') if line.strip()])
            
            # Verificar último commit
            result = subprocess.run([
                'git', 'log', '-1', '--oneline'
            ], capture_output=True, text=True, cwd=self.git_dir)
            
            last_commit = result.stdout.strip() if result.stdout else "Nenhum commit encontrado"
            
            return {
                "success": True,
                "status": "healthy",
                "uncommitted_files": uncommitted_files,
                "last_commit": last_commit,
                "processed_files_count": len(self.processed_files),
                "last_check": self.last_check.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e)
            }

# Instanciar o Git Manager
git_manager = GitManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check do microserviço"""
    return jsonify({
        "status": "healthy",
        "service": "git-manager",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Obter status do Git Manager"""
    status = git_manager.get_status()
    return jsonify(status)

@app.route('/process', methods=['POST'])
def process_files():
    """Processar arquivos novos"""
    try:
        result = git_manager.process_new_files()
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /process: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/process', methods=['GET'])
def process_files_get():
    """Processar arquivos novos via GET (para Cloud Scheduler)"""
    try:
        result = git_manager.process_new_files()
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /process: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/force-commit', methods=['POST'])
def force_commit():
    """Forçar commit de todos os arquivos não commitados"""
    try:
        data = request.get_json() or {}
        file_pattern = data.get('pattern', 'dash_*.html')
        
        # Buscar todos os arquivos que correspondem ao padrão
        files_to_commit = list(git_manager.static_dir.glob(file_pattern))
        
        if not files_to_commit:
            return jsonify({
                "success": True,
                "message": f"Nenhum arquivo encontrado com padrão: {file_pattern}",
                "files_processed": 0
            })
        
        processed_files = []
        failed_files = []
        
        for file_path in files_to_commit:
            if git_manager.commit_file(file_path):
                processed_files.append(file_path.name)
            else:
                failed_files.append(file_path.name)
        
        return jsonify({
            "success": len(failed_files) == 0,
            "message": f"Processados {len(processed_files)} arquivos, {len(failed_files)} falharam",
            "files_processed": len(processed_files),
            "processed_files": processed_files,
            "failed_files": failed_files
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /force-commit: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando Git Manager Microservice")
    app.run(host='0.0.0.0', port=8080, debug=False)
