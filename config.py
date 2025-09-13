"""
Configurações atualizadas para automação do dashboard com GIDs corretos
"""

# IDs das planilhas do Google Sheets para cada canal (com GIDs corretos)
GOOGLE_SHEETS_CONFIG = {
    "YouTube": {
        "sheet_id": "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo",
        "gid": "1863167182",
        "columns": {
            "date": "Date",
            "creative": "criativo", 
            "spend": "Valor investido",
            "starts": "Starts (Video)",
            "q25": "First-Quartile Views (Video)",
            "q50": "Midpoint Views (Video)",
            "q75": "Third-Quartile Views (Video)",
            "q100": "Complete Views (Video)",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    },
    "TikTok": {
        "sheet_id": "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM",
        "gid": "1727929489",
        "columns": {
            "date": "By Day",
            "creative": "Ad name",
            "spend": "Valor Investido", 
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    },
    "Netflix": {
        "sheet_id": "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo",
        "gid": "1743413064",
        "columns": {
            "date": "Day",
            "creative": "Criativo",
            "spend": "Valor investido",
            "starts": "Video Starts",
            "q25": "25% Video Complete",
            "q50": "50% Video Complete", 
            "q75": "75% Video Complete",
            "q100": "100% Complete",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    },
    "Disney": {
        "sheet_id": "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o",
        "gid": "1743413064",
        "columns": {
            "date": "Date",
            "creative": "Creative",
            "spend": "Valor investido",
            "impressions": "Impressions",
            "clicks": "Clicks", 
            "visits": "Visits"
        }
    },
    "CTV": {
        "sheet_id": "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U",
        "gid": "1743413064",
        "columns": {
            "date": "Day",
            "creative": "Creative",
            "spend": "Valor investido",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    },
    "Footfall Display": {
        "sheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA", 
        "gid": "1743413064",
        "columns": {
            "date": "Date",
            "creative": "Creative",
            "spend": "VALOR DO INVESTIMENTO",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "visits": "Visits"
        }
    },
    "Footfall Data": {
        "sheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA", 
        "gid": "120680471",  # Aba Footfall específica
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

# Configurações de automação
AUTOMATION_CONFIG = {
    "update_interval_hours": 3,
    "dashboard_file": "static/dash_sonho.html",
    "log_file": "logs/dashboard_automation.log",
    "backup_enabled": True,
    "backup_dir": "backups"
}

# Configurações de notificação (opcional)
NOTIFICATION_CONFIG = {
    "enabled": False,
    "webhook_url": "",  # URL do webhook para notificações
    "email": {
        "enabled": False,
        "smtp_server": "",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "to_email": ""
    }
}
