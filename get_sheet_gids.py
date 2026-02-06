#!/usr/bin/env python3
"""
Script para listar todas as abas e seus GIDs usando a API do Google Sheets
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from google_sheets_service import GoogleSheetsService

SPREADSHEET_ID = "1L9rzKij4eFNhRxFVTQbcaT_73WfD3nTaBkHOQXSWvxE"

print("🔍 Listando abas da planilha...")
print(f"📊 Planilha: {SPREADSHEET_ID}\n")

try:
    service = GoogleSheetsService()
    
    if not service.is_configured():
        print("❌ Google Sheets Service não configurado")
        print("💡 Tentando método alternativo via URL pública...")
        
        # Método alternativo: tentar acessar diretamente algumas URLs comuns
        import requests
        common_gids = [
            "0",  # Primeira aba geralmente tem GID 0
            "1714301106",  # GID usado no dashboard de dezembro
            "304137877",  # GID da aba Report
        ]
        
        print("\n🔍 Testando GIDs comuns...")
        for gid in common_gids:
            try:
                csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={gid}"
                resp = requests.get(csv_url, timeout=10, verify=False)
                if resp.status_code == 200:
                    from io import StringIO
                    import pandas as pd
                    df = pd.read_csv(StringIO(resp.text), nrows=3)
                    if not df.empty:
                        cols = [str(c).lower() for c in df.columns]
                        # Verificar se parece ser a aba Footfall
                        is_footfall = any('lat' in c or 'lon' in c or 'long' in c or 'name' in c or 'footfall' in c or 'users' in c for c in cols)
                        print(f"\n   GID {gid}:")
                        print(f"      Colunas: {list(df.columns)[:5]}...")
                        if is_footfall:
                            print(f"      ✅ PARECE SER A ABA FOOTFALL!")
                        else:
                            print(f"      (Provavelmente não é Footfall)")
            except Exception as e:
                print(f"   GID {gid}: Erro - {e}")
        
        # Tentar também alguns GIDs incrementais próximos ao GID da Report
        print("\n🔍 Testando GIDs próximos ao GID da Report (304137877)...")
        base_gid = 304137877
        for offset in [-1, 1, -2, 2, -3, 3]:
            gid = str(base_gid + offset)
            try:
                csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={gid}"
                resp = requests.get(csv_url, timeout=5, verify=False)
                if resp.status_code == 200:
                    from io import StringIO
                    import pandas as pd
                    df = pd.read_csv(StringIO(resp.text), nrows=2)
                    if not df.empty:
                        cols = [str(c).lower() for c in df.columns]
                        is_footfall = any('lat' in c or 'lon' in c or 'long' in c or 'name' in c or 'footfall' in c or 'users' in c for c in cols)
                        print(f"   GID {gid}: {list(df.columns)[:3]}... {'✅ FOOTFALL!' if is_footfall else ''}")
            except:
                pass
        
    else:
        # Usar a API do Google Sheets
        metadata = service.get_sheet_metadata(SPREADSHEET_ID)
        if metadata:
            sheets = metadata.get('sheets', [])
            print(f"✅ Encontradas {len(sheets)} abas:\n")
            for sheet in sheets:
                props = sheet.get('properties', {})
                sheet_id = props.get('sheetId')
                title = props.get('title', 'Sem nome')
                print(f"   {title}: GID = {sheet_id}")
                if 'footfall' in title.lower():
                    print(f"      ✅ ESTA É A ABA FOOTFALL!")
        else:
            print("❌ Não foi possível obter metadados da planilha")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
