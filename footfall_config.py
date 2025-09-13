"""
Configurações específicas para processamento de Footfall
"""

# Configuração da planilha de footfall (quando disponível)
FOOTFALL_SHEETS_CONFIG = {
    "Footfall Data": {
        "sheet_id": "SEU_SHEET_ID_FOOTFALL",  # Substituir pelo ID real
        "gid": "SEU_GID_FOOTFALL",  # Substituir pelo GID real
        "columns": {
            "name": "Nome da Loja",
            "lat": "Latitude",
            "lon": "Longitude", 
            "users": "Usuários Detectados",
            "rate": "Taxa de Conversão (%)"
        }
    }
}

# Configurações de validação
FOOTFALL_VALIDATION = {
    "lat_range": (-90, 90),
    "lon_range": (-180, 180),
    "users_min": 0,
    "rate_min": 0,
    "rate_max": 100,
    "required_fields": ["lat", "lon", "name", "users", "rate"]
}

# Configurações de backup
FOOTFALL_BACKUP_CONFIG = {
    "enabled": True,
    "backup_dir": "footfall_backups",
    "max_backups": 10
}

# Configurações de atualização
FOOTFALL_UPDATE_CONFIG = {
    "auto_update_enabled": True,
    "update_interval_hours": 6,  # Footfall pode ser atualizado com menos frequência
    "dashboard_file": "static/dash_sonho.html",
    "commit_and_push": True
}
