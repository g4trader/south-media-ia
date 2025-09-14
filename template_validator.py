#!/usr/bin/env python3
"""
Template Validator - Sistema de Validação e Backup de Templates
Garante que apenas templates válidos sejam commitados/pushados
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TemplateValidator:
    """Validador de templates HTML para garantir estabilidade"""
    
    def __init__(self, template_file: str = "static/dash_sonho.html"):
        self.template_file = template_file
        self.backup_dir = "backups"
        self.validation_rules = self._load_validation_rules()
        self.required_sections = [
            "const CONS =",
            "const PER =",
            "const FOOTFALL_POINTS ="
        ]
        
    def _load_validation_rules(self) -> Dict:
        """Carrega regras de validação do arquivo de configuração"""
        return {
            "required_variables": ["CONS", "PER", "FOOTFALL_POINTS"],
            "required_functions": [],  # Funções são opcionais
            "syntax_checks": [
                "const FOOTFALL_POINTS = [",
                "];",  # Verificar se não termina com ]];
                "const PER = [",
                "const CONS = {"
            ],
            "forbidden_patterns": [
                "]];",  # Array duplo
                "Uncaught ReferenceError",
                "PER is not defined",
                "FOOTFALL_POINTS is not defined"
            ]
        }
    
    def validate_template(self, content: str) -> Tuple[bool, List[str]]:
        """
        Valida o template HTML
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # 1. Verificar seções obrigatórias
        for section in self.required_sections:
            if section not in content:
                errors.append(f"❌ Seção obrigatória ausente: {section}")
        
        # 2. Verificar variáveis obrigatórias
        for var in self.validation_rules["required_variables"]:
            if f"const {var}" not in content:
                errors.append(f"❌ Variável obrigatória ausente: {var}")
        
        # 3. Verificar funções obrigatórias
        for func in self.validation_rules["required_functions"]:
            if f"function {func}" not in content:
                errors.append(f"❌ Função obrigatória ausente: {func}")
        
        # 4. Verificar sintaxe específica
        for check in self.validation_rules["syntax_checks"]:
            if check not in content:
                errors.append(f"❌ Sintaxe incorreta: {check}")
        
        # 5. Verificar padrões proibidos
        for pattern in self.validation_rules["forbidden_patterns"]:
            if pattern in content:
                errors.append(f"❌ Padrão proibido encontrado: {pattern}")
        
        # 6. Verificar estrutura do array FOOTFALL_POINTS
        if "const FOOTFALL_POINTS = [[" in content:
            errors.append("❌ FOOTFALL_POINTS com sintaxe incorreta: array duplo")
        
        # 7. Verificar se FOOTFALL_POINTS termina corretamente
        if "]];" in content and "const FOOTFALL_POINTS" in content:
            errors.append("❌ FOOTFALL_POINTS termina com sintaxe incorreta: ]];")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ Template validado com sucesso")
        else:
            logger.error(f"❌ Template inválido com {len(errors)} erros")
            for error in errors:
                logger.error(f"  {error}")
        
        return is_valid, errors
    
    def create_backup(self, content: str) -> str:
        """Cria backup do template atual"""
        try:
            # Criar diretório de backup se não existir
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Gerar hash do conteúdo para nome único
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"dash_sonho_backup_{timestamp}_{content_hash}.html"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Salvar backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"💾 Backup criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None
    
    def get_template_hash(self, content: str) -> str:
        """Gera hash do template para comparação"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def compare_with_backup(self, content: str) -> Dict:
        """Compara template atual com backup mais recente"""
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                           if f.startswith("dash_sonho_backup_") and f.endswith(".html")]
            
            if not backup_files:
                return {"has_backup": False, "is_different": True}
            
            # Pegar backup mais recente
            latest_backup = sorted(backup_files)[-1]
            backup_path = os.path.join(self.backup_dir, latest_backup)
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            current_hash = self.get_template_hash(content)
            backup_hash = self.get_template_hash(backup_content)
            
            return {
                "has_backup": True,
                "is_different": current_hash != backup_hash,
                "latest_backup": latest_backup,
                "current_hash": current_hash,
                "backup_hash": backup_hash
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao comparar com backup: {e}")
            return {"has_backup": False, "is_different": True, "error": str(e)}
    
    def restore_from_backup(self, backup_filename: Optional[str] = None) -> bool:
        """Restaura template a partir de um backup"""
        try:
            if not backup_filename:
                # Usar backup mais recente
                backup_files = [f for f in os.listdir(self.backup_dir) 
                               if f.startswith("dash_sonho_backup_") and f.endswith(".html")]
                if not backup_files:
                    logger.error("❌ Nenhum backup encontrado")
                    return False
                backup_filename = sorted(backup_files)[-1]
            
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            # Validar backup antes de restaurar
            is_valid, errors = self.validate_template(backup_content)
            if not is_valid:
                logger.error(f"❌ Backup inválido: {errors}")
                return False
            
            # Restaurar template
            with open(self.template_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            
            logger.info(f"✅ Template restaurado do backup: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def safe_commit_and_push(self, content: str, commit_message: str) -> Tuple[bool, str]:
        """
        Commit e push seguro com validação
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # 1. Validar template antes de qualquer coisa
            is_valid, errors = self.validate_template(content)
            if not is_valid:
                error_msg = f"❌ Template inválido, commit cancelado. Erros: {errors}"
                logger.error(error_msg)
                return False, error_msg
            
            # 2. Criar backup antes de fazer commit
            backup_path = self.create_backup(content)
            if not backup_path:
                return False, "❌ Falha ao criar backup, commit cancelado"
            
            # 3. Comparar com backup anterior
            comparison = self.compare_with_backup(content)
            if comparison.get("is_different", True):
                logger.info("📝 Template modificado, prosseguindo com commit")
            else:
                logger.info("📄 Template inalterado, commit desnecessário")
                return True, "Template inalterado, commit desnecessário"
            
            # 4. Salvar template validado
            with open(self.template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 5. Fazer commit via GitHub API
            success = self._commit_via_github_api(content, commit_message)
            
            if success:
                logger.info("✅ Commit e push realizados com sucesso")
                return True, "Commit e push realizados com sucesso"
            else:
                # Em caso de erro, restaurar backup
                logger.warning("⚠️ Erro no commit, restaurando backup...")
                self.restore_from_backup()
                return False, "Erro no commit, backup restaurado"
                
        except Exception as e:
            logger.error(f"❌ Erro no commit seguro: {e}")
            # Tentar restaurar backup em caso de erro
            try:
                self.restore_from_backup()
            except:
                pass
            return False, f"Erro no commit seguro: {e}"
    
    def _commit_via_github_api(self, content: str, commit_message: str) -> bool:
        """Faz commit via GitHub API (código reutilizado dos processadores)"""
        try:
            import requests
            import base64
            import os
            
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                logger.warning("⚠️ GITHUB_TOKEN não encontrado")
                return False
            
            # Configurações do GitHub
            repo_owner = "g4trader"
            repo_name = "south-media-ia"
            file_path = "static/dash_sonho.html"
            
            # Obter SHA atual
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"❌ Erro ao obter SHA: {response.status_code}")
                return False
            
            current_sha = response.json()["sha"]
            
            # Preparar dados para commit
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": commit_message,
                "content": content_b64,
                "sha": current_sha
            }
            
            # Fazer commit
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info("✅ Commit realizado via GitHub API")
                return True
            else:
                logger.error(f"❌ Erro no commit: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no commit via GitHub API: {e}")
            return False

def main():
    """Função principal para teste do validador"""
    validator = TemplateValidator()
    
    # Testar com arquivo atual
    if os.path.exists(validator.template_file):
        with open(validator.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Validando template atual...")
        is_valid, errors = validator.validate_template(content)
        
        if is_valid:
            print("✅ Template válido!")
        else:
            print("❌ Template inválido:")
            for error in errors:
                print(f"  {error}")
        
        # Criar backup
        backup_path = validator.create_backup(content)
        if backup_path:
            print(f"💾 Backup criado: {backup_path}")
        
        # Comparar com backup
        comparison = validator.compare_with_backup(content)
        print(f"📊 Comparação com backup: {comparison}")
    
    else:
        print(f"❌ Arquivo não encontrado: {validator.template_file}")

if __name__ == "__main__":
    main()
