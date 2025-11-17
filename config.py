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

# Configuração do Google Sheets (pode ser sobrescrita por variáveis de ambiente)
GOOGLE_SHEETS_CONFIG = {
    "YouTube": {
        "sheet_id": os.environ.get("YOUTUBE_SHEET_ID", "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg"),
        "gid": os.environ.get("YOUTUBE_GID", "304137877"),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "starts": "Video Starts",
            "q25": "25%",
            "q50": "50%",
            "q75": "75%",
            "q100": "100%"
        }
    },
    "Programática Video": {
        "sheet_id": os.environ.get("PROG_VIDEO_SHEET_ID", "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o"),
        "gid": os.environ.get("PROG_VIDEO_GID", "1489416055"),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "starts": "Video Starts",
            "q25": "25%",
            "q50": "50%",
            "q75": "75%",
            "q100": "100%"
        }
    },
    "TikTok": {
        "sheet_id": os.environ.get("TIKTOK_SHEET_ID", ""),
        "gid": os.environ.get("TIKTOK_GID", ""),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "starts": "Video Starts"
        }
    },
    "Netflix": {
        "sheet_id": os.environ.get("NETFLIX_SHEET_ID", "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo"),
        "gid": os.environ.get("NETFLIX_GID", "1743413064"),
        "sheet_name": None,
        "columns": {
            "date": "Day",
            "spend": "Valor investido",
            "impressions": "",  # Netflix não tem coluna de impressões
            "clicks": "",  # Netflix não tem coluna de cliques
            "starts": "Video Starts",
            "q25": "25% Video Complete",
            "q50": "50% Video Complete",
            "q75": "75% Video Complete",
            "q100": "100% Complete",
            "creative": "Criativo"
        }
    },
    "Disney": {
        "sheet_id": os.environ.get("DISNEY_SHEET_ID", ""),
        "gid": os.environ.get("DISNEY_GID", ""),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "starts": "Video Starts",
            "q25": "25%",
            "q50": "50%",
            "q75": "75%",
            "q100": "100%"
        }
    },
    "CTV": {
        "sheet_id": os.environ.get("CTV_SHEET_ID", ""),
        "gid": os.environ.get("CTV_GID", ""),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "starts": "Video Starts",
            "q25": "25%",
            "q50": "50%",
            "q75": "75%",
            "q100": "100%"
        }
    },
    "Footfall Display": {
        "sheet_id": os.environ.get("FOOTFALL_SHEET_ID", ""),
        "gid": os.environ.get("FOOTFALL_GID", ""),
        "sheet_name": None,
        "columns": {
            "date": "Date",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    }
}

# Filtrar canais vazios (sem sheet_id configurado)
GOOGLE_SHEETS_CONFIG = {
    k: v for k, v in GOOGLE_SHEETS_CONFIG.items() 
    if v.get("sheet_id") and v["sheet_id"].strip()
}

# Configuração de automação
AUTOMATION_CONFIG = {
    "dashboard_files": os.environ.get(
        "AUTOMATION_DASHBOARD_FILES",
        "static/dash_sonho.html,static/dash_sonho_v3.html"
    ).split(","),
    "dashboard_file": os.environ.get("AUTOMATION_DASHBOARD_FILE", "static/dash_sonho.html"),
    "backup_enabled": os.environ.get("AUTOMATION_BACKUP_ENABLED", "true").lower() == "true",
    "backup_dir": os.environ.get("AUTOMATION_BACKUP_DIR", "backups"),
    "update_interval_hours": int(os.environ.get("AUTOMATION_UPDATE_INTERVAL_HOURS", "3"))
}

# Log da configuração
if __name__ == "__main__":
    print(f"🌍 Ambiente detectado: {config.environment}")
    print(f"🔗 API Endpoint: {config.get_api_endpoint()}")
    print(f"🔧 Debug: {config.is_debug()}")
    print(f"🚪 Porta: {config.get_port()}")
    print(f"📊 Canais configurados: {len(GOOGLE_SHEETS_CONFIG)}")