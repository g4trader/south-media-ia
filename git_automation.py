#!/usr/bin/env python3
"""
Sistema de automação Git para o gerador de dashboards
Baseado no sistema que funciona no dashboard_automation.py
"""

import os
import base64
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitAutomation:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'g4trader'
        self.repo_name = 'south-media-ia'
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"
    
    def commit_file_to_github(self, file_path, content, commit_message=None):
        """Faz commit de um arquivo para o GitHub usando API"""
        try:
            if not self.github_token:
                logger.error("❌ GITHUB_TOKEN não configurado")
                return False
            
            if not commit_message:
                commit_message = f"🤖 Dashboard gerado automaticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            logger.info(f"📤 Fazendo commit do arquivo: {file_path}")
            
            # URL do arquivo no GitHub
            url = f"{self.base_url}/{file_path}"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Tentar obter SHA do arquivo atual (se existir)
            current_sha = None
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    current_sha = response.json()["sha"]
                    logger.info(f"✅ Arquivo existente encontrado, SHA: {current_sha[:8]}...")
                elif response.status_code == 404:
                    logger.info("ℹ️ Arquivo não existe, será criado novo")
                else:
                    logger.warning(f"⚠️ Erro ao verificar arquivo existente: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar arquivo existente: {e}")
            
            # Preparar dados do commit
            commit_data = {
                "message": commit_message,
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            
            # Adicionar SHA se arquivo existir (para atualização)
            if current_sha:
                commit_data["sha"] = current_sha
            
            # Fazer commit
            logger.info("🔄 Enviando commit para GitHub...")
            response = requests.put(url, headers=headers, json=commit_data, timeout=30)
            
            if response.status_code in [200, 201]:
                commit_info = response.json()
                logger.info(f"✅ Commit realizado com sucesso!")
                logger.info(f"   - SHA: {commit_info['commit']['sha'][:8]}...")
                logger.info(f"   - URL: {commit_info['content']['html_url']}")
                return True
            else:
                logger.error(f"❌ Erro no commit: {response.status_code}")
                logger.error(f"   - Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit via GitHub API: {e}")
            return False
    
    def test_github_connection(self):
        """Testa a conexão com o GitHub"""
        try:
            if not self.github_token:
                return {"success": False, "error": "GITHUB_TOKEN não configurado"}
            
            # Testar acesso ao repositório
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                repo_info = response.json()
                return {
                    "success": True,
                    "repo_name": repo_info["name"],
                    "repo_url": repo_info["html_url"],
                    "token_length": len(self.github_token)
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao acessar repositório: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na conexão: {str(e)}"
            }

def test_git_automation():
    """Função de teste para o GitAutomation"""
    git = GitAutomation()
    
    print("🧪 Testando GitAutomation...")
    
    # Testar conexão
    connection_test = git.test_github_connection()
    print(f"🔗 Teste de conexão: {connection_test}")
    
    if connection_test["success"]:
        # Testar commit de um arquivo pequeno
        test_content = f"# Teste de automação Git\n\nGerado em: {datetime.now().isoformat()}\n"
        success = git.commit_file_to_github(
            "test_git_automation.md", 
            test_content, 
            "🧪 Teste de automação Git"
        )
        print(f"📝 Teste de commit: {'✅ Sucesso' if success else '❌ Falhou'}")

if __name__ == "__main__":
    test_git_automation()

"""
Sistema de automação Git para o gerador de dashboards
Baseado no sistema que funciona no dashboard_automation.py
"""

import os
import base64
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitAutomation:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'g4trader'
        self.repo_name = 'south-media-ia'
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"
    
    def commit_file_to_github(self, file_path, content, commit_message=None):
        """Faz commit de um arquivo para o GitHub usando API"""
        try:
            if not self.github_token:
                logger.error("❌ GITHUB_TOKEN não configurado")
                return False
            
            if not commit_message:
                commit_message = f"🤖 Dashboard gerado automaticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            logger.info(f"📤 Fazendo commit do arquivo: {file_path}")
            
            # URL do arquivo no GitHub
            url = f"{self.base_url}/{file_path}"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Tentar obter SHA do arquivo atual (se existir)
            current_sha = None
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    current_sha = response.json()["sha"]
                    logger.info(f"✅ Arquivo existente encontrado, SHA: {current_sha[:8]}...")
                elif response.status_code == 404:
                    logger.info("ℹ️ Arquivo não existe, será criado novo")
                else:
                    logger.warning(f"⚠️ Erro ao verificar arquivo existente: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar arquivo existente: {e}")
            
            # Preparar dados do commit
            commit_data = {
                "message": commit_message,
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            
            # Adicionar SHA se arquivo existir (para atualização)
            if current_sha:
                commit_data["sha"] = current_sha
            
            # Fazer commit
            logger.info("🔄 Enviando commit para GitHub...")
            response = requests.put(url, headers=headers, json=commit_data, timeout=30)
            
            if response.status_code in [200, 201]:
                commit_info = response.json()
                logger.info(f"✅ Commit realizado com sucesso!")
                logger.info(f"   - SHA: {commit_info['commit']['sha'][:8]}...")
                logger.info(f"   - URL: {commit_info['content']['html_url']}")
                return True
            else:
                logger.error(f"❌ Erro no commit: {response.status_code}")
                logger.error(f"   - Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit via GitHub API: {e}")
            return False
    
    def test_github_connection(self):
        """Testa a conexão com o GitHub"""
        try:
            if not self.github_token:
                return {"success": False, "error": "GITHUB_TOKEN não configurado"}
            
            # Testar acesso ao repositório
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                repo_info = response.json()
                return {
                    "success": True,
                    "repo_name": repo_info["name"],
                    "repo_url": repo_info["html_url"],
                    "token_length": len(self.github_token)
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao acessar repositório: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na conexão: {str(e)}"
            }

def test_git_automation():
    """Função de teste para o GitAutomation"""
    git = GitAutomation()
    
    print("🧪 Testando GitAutomation...")
    
    # Testar conexão
    connection_test = git.test_github_connection()
    print(f"🔗 Teste de conexão: {connection_test}")
    
    if connection_test["success"]:
        # Testar commit de um arquivo pequeno
        test_content = f"# Teste de automação Git\n\nGerado em: {datetime.now().isoformat()}\n"
        success = git.commit_file_to_github(
            "test_git_automation.md", 
            test_content, 
            "🧪 Teste de automação Git"
        )
        print(f"📝 Teste de commit: {'✅ Sucesso' if success else '❌ Falhou'}")

if __name__ == "__main__":
    test_git_automation()


