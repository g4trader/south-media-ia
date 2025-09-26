#!/usr/bin/env python3
"""
Serviço de commit para GitHub baseado no que funciona no dashboard-automation
"""

import os
import base64
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubCommitService:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'g4trader'
        self.repo_name = 'south-media-ia'
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"
        
    def test_token_permissions(self):
        """Testa se o token tem as permissões corretas"""
        try:
            if not self.github_token:
                return {"success": False, "error": "Token não configurado"}
            
            # Testar acesso básico ao repositório
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                repo_info = response.json()
                permissions = response.headers.get('X-OAuth-Scopes', '')
                
                return {
                    "success": True,
                    "repo_name": repo_info["name"],
                    "permissions": permissions,
                    "token_length": len(self.github_token)
                }
            elif response.status_code == 401:
                return {"success": False, "error": "Token inválido ou expirado"}
            elif response.status_code == 403:
                return {"success": False, "error": "Token sem permissões suficientes"}
            else:
                return {"success": False, "error": f"Erro HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erro na conexão: {str(e)}"}
    
    def commit_file(self, file_path, content, commit_message=None):
        """Faz commit de um arquivo para o GitHub"""
        try:
            if not self.github_token:
                logger.error("❌ GITHUB_TOKEN não configurado")
                return False
            
            if not commit_message:
                commit_message = f"🤖 Atualização automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
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
                    if response.status_code == 401:
                        logger.error("❌ Token inválido ou expirado")
                        return False
                    elif response.status_code == 403:
                        logger.error("❌ Token sem permissões suficientes")
                        return False
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
            elif response.status_code == 401:
                logger.error("❌ Token inválido ou expirado")
                return False
            elif response.status_code == 403:
                logger.error("❌ Token sem permissões suficientes para escrever")
                return False
            else:
                logger.error(f"❌ Erro no commit: {response.status_code}")
                logger.error(f"   - Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit via GitHub API: {e}")
            return False

def test_github_commit_service():
    """Função de teste para o GitHubCommitService"""
    service = GitHubCommitService()
    
    print("🧪 Testando GitHubCommitService...")
    
    # Testar permissões do token
    token_test = service.test_token_permissions()
    print(f"🔑 Teste de token: {token_test}")
    
    if token_test["success"]:
        # Testar commit de um arquivo pequeno
        test_content = f"""# Teste de GitHubCommitService

Este é um teste do serviço de commit GitHub.

- Gerado em: {datetime.now().isoformat()}
- Sistema: Cloud Run
- Objetivo: Verificar se o commit automático está funcionando

Se você está vendo este arquivo, o commit automático está funcionando! 🎉
"""
        
        success = service.commit_file(
            "test_github_commit_service.md", 
            test_content, 
            "🧪 Teste de GitHubCommitService"
        )
        print(f"📝 Teste de commit: {'✅ Sucesso' if success else '❌ Falhou'}")
    else:
        print(f"❌ Token não está funcionando: {token_test['error']}")

if __name__ == "__main__":
    test_github_commit_service()

"""
Serviço de commit para GitHub baseado no que funciona no dashboard-automation
"""

import os
import base64
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubCommitService:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'g4trader'
        self.repo_name = 'south-media-ia'
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents"
        
    def test_token_permissions(self):
        """Testa se o token tem as permissões corretas"""
        try:
            if not self.github_token:
                return {"success": False, "error": "Token não configurado"}
            
            # Testar acesso básico ao repositório
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                repo_info = response.json()
                permissions = response.headers.get('X-OAuth-Scopes', '')
                
                return {
                    "success": True,
                    "repo_name": repo_info["name"],
                    "permissions": permissions,
                    "token_length": len(self.github_token)
                }
            elif response.status_code == 401:
                return {"success": False, "error": "Token inválido ou expirado"}
            elif response.status_code == 403:
                return {"success": False, "error": "Token sem permissões suficientes"}
            else:
                return {"success": False, "error": f"Erro HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erro na conexão: {str(e)}"}
    
    def commit_file(self, file_path, content, commit_message=None):
        """Faz commit de um arquivo para o GitHub"""
        try:
            if not self.github_token:
                logger.error("❌ GITHUB_TOKEN não configurado")
                return False
            
            if not commit_message:
                commit_message = f"🤖 Atualização automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
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
                    if response.status_code == 401:
                        logger.error("❌ Token inválido ou expirado")
                        return False
                    elif response.status_code == 403:
                        logger.error("❌ Token sem permissões suficientes")
                        return False
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
            elif response.status_code == 401:
                logger.error("❌ Token inválido ou expirado")
                return False
            elif response.status_code == 403:
                logger.error("❌ Token sem permissões suficientes para escrever")
                return False
            else:
                logger.error(f"❌ Erro no commit: {response.status_code}")
                logger.error(f"   - Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer commit via GitHub API: {e}")
            return False

def test_github_commit_service():
    """Função de teste para o GitHubCommitService"""
    service = GitHubCommitService()
    
    print("🧪 Testando GitHubCommitService...")
    
    # Testar permissões do token
    token_test = service.test_token_permissions()
    print(f"🔑 Teste de token: {token_test}")
    
    if token_test["success"]:
        # Testar commit de um arquivo pequeno
        test_content = f"""# Teste de GitHubCommitService

Este é um teste do serviço de commit GitHub.

- Gerado em: {datetime.now().isoformat()}
- Sistema: Cloud Run
- Objetivo: Verificar se o commit automático está funcionando

Se você está vendo este arquivo, o commit automático está funcionando! 🎉
"""
        
        success = service.commit_file(
            "test_github_commit_service.md", 
            test_content, 
            "🧪 Teste de GitHubCommitService"
        )
        print(f"📝 Teste de commit: {'✅ Sucesso' if success else '❌ Falhou'}")
    else:
        print(f"❌ Token não está funcionando: {token_test['error']}")

if __name__ == "__main__":
    test_github_commit_service()


