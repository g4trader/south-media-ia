#!/usr/bin/env python3
"""
Configuração real das planilhas Google Sheets por canal
Extraído das URLs fornecidas pelo usuário
"""

# IDs das planilhas extraídos das URLs
SHEETS_CONFIG = {
    "Footfall Display": {
        "spreadsheet_id": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA",
        "sheet_name": "Entrega Diária",
        "gid": "1743413064",
        "url": "https://docs.google.com/spreadsheets/d/10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA/edit?gid=1743413064#gid=1743413064"
    },
    "Disney": {
        "spreadsheet_id": "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o",
        "sheet_name": "Entrega Diária",
        "gid": None,
        "url": "https://docs.google.com/spreadsheets/d/1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o/edit"
    },
    "CTV": {
        "spreadsheet_id": "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U",
        "sheet_name": "Entrega Diária",
        "gid": None,
        "url": "https://docs.google.com/spreadsheets/d/1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U/edit"
    },
    "Netflix": {
        "spreadsheet_id": "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo",
        "sheet_name": "Entrega Diária",
        "gid": None,
        "url": "https://docs.google.com/spreadsheets/d/1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo/edit"
    },
    "TikTok": {
        "spreadsheet_id": "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM",
        "sheet_name": "Entrega Diária",
        "gid": None,
        "url": "https://docs.google.com/spreadsheets/d/1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM/edit?rtpof=true"
    },
    "YouTube": {
        "spreadsheet_id": "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo",
        "sheet_name": "Entrega Diária",
        "gid": "1863167182",
        "url": "https://docs.google.com/spreadsheets/d/1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo/edit?gid=1863167182#gid=1863167182"
    }
}

def generate_env_config():
    """Gera configuração para arquivo .env"""
    print("# Google Sheets Configuration - IDs Reais")
    print("# Configuração extraída das URLs fornecidas")
    print()
    
    for channel, config in SHEETS_CONFIG.items():
        env_key = channel.upper().replace(" ", "_").replace("_DISPLAY", "_DISPLAY")
        print(f"{env_key}_SPREADSHEET_ID={config['spreadsheet_id']}")
    
    print()
    print("# Google Sheets Credentials")
    print("GOOGLE_CREDENTIALS_PATH=credentials.json")

def generate_sheets_service_config():
    """Gera configuração para o SheetsService"""
    print("sheets_config = {")
    for channel, config in SHEETS_CONFIG.items():
        print(f'    "{channel}": {{')
        print(f'        "spreadsheet_id": "{config["spreadsheet_id"]}",')
        print(f'        "sheet_name": "{config["sheet_name"]}",')
        if config.get("gid"):
            print(f'        "gid": "{config["gid"]}",')
        print(f'        "url": "{config["url"]}"')
        print("    },")
    print("}")

def show_summary():
    """Mostra resumo das configurações"""
    print("📊 RESUMO DAS PLANILHAS CONFIGURADAS")
    print("=" * 50)
    
    for channel, config in SHEETS_CONFIG.items():
        print(f"\n📺 {channel}")
        print(f"   🆔 ID: {config['spreadsheet_id']}")
        print(f"   📋 Sheet: {config['sheet_name']}")
        if config.get("gid"):
            print(f"   🔗 GID: {config['gid']}")
        print(f"   🌐 URL: {config['url']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "env":
            generate_env_config()
        elif sys.argv[1] == "config":
            generate_sheets_service_config()
        elif sys.argv[1] == "summary":
            show_summary()
        else:
            print("Uso: python3 sheets_config_real.py [env|config|summary]")
    else:
        show_summary()
        print("\n" + "="*50)
        print("Para gerar configuração .env: python3 sheets_config_real.py env")
        print("Para gerar configuração service: python3 sheets_config_real.py config")
