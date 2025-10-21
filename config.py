#!/usr/bin/env python3
"""
Configuração de ambiente para o Dashboard Builder
"""

import os
from typing import Dict, Any

class EnvironmentConfig:
    """Configuração baseada no ambiente"""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.config = self._get_config()
    
    def _detect_environment(self) -> str:
        """Detectar ambiente baseado em variáveis ou contexto"""
        # Verificar se está rodando no Cloud Run
        if os.environ.get('K_SERVICE'):
            return 'production'
        
        # Verificar se está rodando localmente
        if os.environ.get('LOCAL_DEV') == 'true':
            return 'development'
        
        # Verificar se está rodando em produção (Cloud Run) - PORT=8080
        if os.environ.get('PORT') == '8080':
            return 'production'
        
        # Padrão: desenvolvimento
        return 'development'
    
    def _get_config(self) -> Dict[str, Any]:
        """Obter configuração baseada no ambiente"""
        
        if self.environment == 'production':
            return {
                'api_endpoint': 'https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app',
                'git_manager_url': None,  # Desativado para evitar instabilidade
                'debug': False,
                'port': int(os.environ.get('PORT', 8080))
            }
        else:  # development
            return {
                'api_endpoint': 'http://localhost:5002',
                'git_manager_url': None,  # Desativado para evitar instabilidade
                'debug': True,
                'port': 5002
            }
    
    def get_api_endpoint(self) -> str:
        """Obter endpoint da API baseado no ambiente"""
        return self.config['api_endpoint']
    
    def get_git_manager_url(self) -> str:
        """Obter URL do Git Manager baseado no ambiente"""
        return self.config['git_manager_url']
    
    def is_production(self) -> bool:
        """Verificar se está em produção"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Verificar se está em desenvolvimento"""
        return self.environment == 'development'
    
    def get_port(self) -> int:
        """Obter porta baseada no ambiente"""
        return self.config['port']
    
    def is_debug(self) -> bool:
        """Verificar se debug está habilitado"""
        return self.config['debug']

# Instância global da configuração
config = EnvironmentConfig()

# Funções de conveniência
def get_api_endpoint() -> str:
    """Obter endpoint da API"""
    return config.get_api_endpoint()

def get_git_manager_url() -> str:
    """Obter URL do Git Manager"""
    return config.get_git_manager_url()

def is_production() -> bool:
    """Verificar se está em produção"""
    return config.is_production()

def is_development() -> bool:
    """Verificar se está em desenvolvimento"""
    return config.is_development()

def get_port() -> int:
    """Obter porta"""
    return config.get_port()

def is_debug() -> bool:
    """Verificar se debug está habilitado"""
    return config.is_debug()

# Log da configuração
if __name__ == "__main__":
    print(f"🌍 Ambiente detectado: {config.environment}")
    print(f"🔗 API Endpoint: {config.get_api_endpoint()}")
    print(f"🔧 Debug: {config.is_debug()}")
    print(f"🚪 Porta: {config.get_port()}")