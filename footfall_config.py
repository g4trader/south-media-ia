"""
Configurações específicas para processamento de Footfall
"""

# Configuração da planilha de footfall (dados reais)
FOOTFALL_SHEETS_CONFIG = {
    "Footfall Data": {
        "sheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA",
        "gid": "120680471",
        "columns": {
            "lat": "lat",
            "lon": "long", 
            "proximity": "proximidade metros",
            "name": "name",
            "users": "Footfall Users",
            "rate": "Footfall Rate %"
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
