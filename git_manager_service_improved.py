#!/usr/bin/env python3
"""
Git Manager Microservice - Versão Melhorada
Microserviço dedicado para gerenciar commits automáticos de dashboards
Com retry logic e melhor tratamento de paths
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
        logging.FileHandler('/tmp/git_manager_improved.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class ImprovedGitManager:
    """Gerenciador de operações Git para dashboards - Versão Melhorada"""
    
    def __init__(self):
        # Detectar ambiente: produção (Cloud Run) vs desenvolvimento
        if os.path.exists('/app'):
            # Ambiente Cloud Run
            self.static_dir = Path('/app/static')
            self.git_dir = Path('/app')
            logger.info("🌍 Ambiente: Cloud Run (Produção)")
        else:
            # Ambiente local/desenvolvimento
            self.static_dir = Path.cwd() / 'static'
            self.git_dir = Path.cwd()
            logger.info("🌍 Ambiente: Desenvolvimento Local")
        
        self.processed_files = set()
        self.last_check = datetime.now()
        self.max_retries = 3
        self.retry_delay = 2  # segundos
        
        # Configurar Git
        self._setup_git()
        
        logger.info("🚀 Git Manager Melhorado inicializado")
        logger.info(f"📁 Diretório Git: {self.git_dir}")
        logger.info(f"📁 Diretório Static: {self.static_dir}")
    
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
    
    def _wait_for_file(self, file_path: Path, max_wait: int = 30) -> bool:
        """Aguardar arquivo existir com retry logic"""
        wait_time = 0
        while wait_time < max_wait:
            if file_path.exists():
                # Verificar se arquivo não está sendo escrito (tamanho estável)
                try:
                    size1 = file_path.stat().st_size
                    time.sleep(1)
                    size2 = file_path.stat().st_size
                    if size1 == size2 and size1 > 0:
                        logger.info(f"✅ Arquivo estável: {file_path.name} ({size1} bytes)")
                        return True
                except OSError:
                    pass
            
            logger.info(f"⏳ Aguardando arquivo: {file_path.name} ({wait_time}s)")
            time.sleep(2)
            wait_time += 2
        
        logger.warning(f"⚠️ Timeout aguardando arquivo: {file_path.name}")
        return False
    
    def _normalize_path(self, file_path: str) -> Path:
        """Normalizar path do arquivo"""
        # Se é path absoluto, usar como está
        if os.path.isabs(file_path):
            return Path(file_path)
        
        # Se é path relativo, assumir que está em static/
        if file_path.startswith('static/'):
            return self.git_dir / file_path
        else:
            return self.static_dir / file_path
    
    def commit_file_with_retry(self, file_path: Path) -> bool:
        """Fazer commit de um arquivo com retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Tentativa {attempt + 1}/{self.max_retries} para: {file_path.name}")
                
                # Aguardar arquivo existir
                if not self._wait_for_file(file_path):
                    logger.warning(f"⚠️ Arquivo não encontrado após aguardar: {file_path}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                
                # Verificar se o arquivo existe e é acessível
                if not file_path.exists():
                    logger.warning(f"⚠️ Arquivo não existe: {file_path}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                
                # Verificar permissões
                if not os.access(file_path, os.R_OK):
                    logger.warning(f"⚠️ Sem permissão de leitura: {file_path}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                
                # Tentar fazer commit
                if self._commit_file_internal(file_path):
                    logger.info(f"✅ Commit realizado com sucesso: {file_path.name}")
                    self.processed_files.add(file_path.name)
                    return True
                else:
                    logger.warning(f"⚠️ Falha no commit: {file_path.name}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False
        
        logger.error(f"❌ Todas as tentativas falharam para: {file_path.name}")
        return False
    
    def _commit_file_internal(self, file_path: Path) -> bool:
        """Fazer commit interno de um arquivo"""
        try:
            relative_path = file_path.relative_to(self.git_dir)
            
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
            
            # Fazer push (apenas em produção)
            if os.path.exists('/app'):  # Ambiente Cloud Run
                logger.info(f"🔧 Fazendo push...")
                result = subprocess.run([
                    'git', 'push', 'origin', 'main'
                ], check=True, capture_output=True, text=True, cwd=self.git_dir)
                
                logger.info(f"✅ Push realizado com sucesso: {result.stdout.strip()}")
            else:
                logger.info("ℹ️ Ambiente local - pulando push")
            
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"❌ Erro no Git: {error_msg}")
            logger.error(f"❌ Comando que falhou: {e.cmd}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def notify_dashboard_created(self, file_path: str, campaign_key: str, client: str, campaign_name: str) -> Dict[str, any]:
        """Notificar que um novo dashboard foi criado - versão melhorada"""
        try:
            logger.info(f"🔔 Notificação recebida: Dashboard criado para {client} - {campaign_name}")
            logger.info(f"📄 Arquivo: {file_path}")
            
            # Normalizar path
            normalized_path = self._normalize_path(file_path)
            logger.info(f"📁 Path normalizado: {normalized_path}")
            
            # Tentar fazer commit com retry
            if self.commit_file_with_retry(normalized_path):
                logger.info(f"✅ Commit realizado com sucesso para: {normalized_path.name}")
                return {
                    "success": True,
                    "message": "Dashboard commitado com sucesso",
                    "file_committed": normalized_path.name,
                    "file_path": str(normalized_path)
                }
            else:
                logger.warning(f"⚠️ Falha no commit para: {normalized_path.name}")
                return {
                    "success": False,
                    "message": "Falha no commit após todas as tentativas",
                    "file_path": str(normalized_path)
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar notificação: {e}")
            return {
                "success": False,
                "message": f"Erro interno: {str(e)}",
                "file_path": file_path
            }

# Instanciar o Git Manager Melhorado
improved_git_manager = ImprovedGitManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check do microserviço"""
    return jsonify({
        "status": "healthy",
        "service": "git-manager-improved",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0",
        "git_dir": str(improved_git_manager.git_dir),
        "static_dir": str(improved_git_manager.static_dir),
        "environment": "production" if os.path.exists('/app') else "development"
    })

@app.route('/notify', methods=['POST'])
def notify_dashboard_created():
    """Notificar que um novo dashboard foi criado - versão melhorada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        action = data.get('action')
        if action == 'dashboard_created':
            file_path = data.get('file_path')
            campaign_key = data.get('campaign_key')
            client = data.get('client')
            campaign_name = data.get('campaign_name')
            
            result = improved_git_manager.notify_dashboard_created(
                file_path, campaign_key, client, campaign_name
            )
            
            return jsonify(result)
        
        return jsonify({
            "success": False,
            "message": "Ação não reconhecida"
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /notify: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/test-file', methods=['POST'])
def test_file_access():
    """Testar acesso a um arquivo específico"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        file_path = data.get('file_path')
        if not file_path:
            return jsonify({"success": False, "message": "file_path não fornecido"}), 400
        
        normalized_path = improved_git_manager._normalize_path(file_path)
        
        result = {
            "original_path": file_path,
            "normalized_path": str(normalized_path),
            "exists": normalized_path.exists(),
            "is_file": normalized_path.is_file(),
            "is_readable": os.access(normalized_path, os.R_OK) if normalized_path.exists() else False,
            "size": normalized_path.stat().st_size if normalized_path.exists() else 0,
            "modified_time": datetime.fromtimestamp(normalized_path.stat().st_mtime).isoformat() if normalized_path.exists() else None
        }
        
        return jsonify({
            "success": True,
            "message": "Teste de arquivo concluído",
            "file_info": result
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint /test-file: {e}")
        return jsonify({
            "success": False,
            "message": f"Erro interno: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando Git Manager Microservice Melhorado")
    app.run(host='0.0.0.0', port=8080, debug=False)
