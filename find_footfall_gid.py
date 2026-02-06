#!/usr/bin/env python3
"""
Script para encontrar o GID da aba Footfall na planilha
"""

import sys
from pathlib import Path
import requests
import re

SPREADSHEET_ID = "1L9rzKij4eFNhRxFVTQbcaT_73WfD3nTaBkHOQXSWvxE"

# Tentar acessar a planilha via URL pública para ver as abas
print("🔍 Procurando GID da aba Footfall...")
print(f"📊 Planilha: {SPREADSHEET_ID}")

# Tentar acessar a página HTML da planilha para extrair os GIDs
try:
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit"
    resp = requests.get(url, timeout=30, verify=False)
    
    # Procurar por padrões de GID na resposta HTML
    # Os GIDs geralmente aparecem em atributos como data-sheet-id ou em URLs
    gid_pattern = r'gid=(\d+)'
    gids_found = set(re.findall(gid_pattern, resp.text))
    
    print(f"\n✅ GIDs encontrados na planilha:")
    for gid in sorted(gids_found):
        print(f"   GID: {gid}")
    
    # Tentar acessar cada GID para ver qual é a aba Footfall
    print("\n🔍 Tentando identificar a aba Footfall...")
    for gid in sorted(gids_found):
        try:
            csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={gid}"
            csv_resp = requests.get(csv_url, timeout=10, verify=False)
            if csv_resp.status_code == 200:
                from io import StringIO
                import pandas as pd
                df = pd.read_csv(StringIO(csv_resp.text), nrows=1)
                if not df.empty:
                    # Verificar se tem colunas que indicam ser a aba Footfall
                    cols = [str(c).lower() for c in df.columns]
                    if any('lat' in c or 'lon' in c or 'long' in c or 'name' in c or 'footfall' in c for c in cols):
                        print(f"\n✅ ABA FOOTFALL ENCONTRADA!")
                        print(f"   GID: {gid}")
                        print(f"   Colunas: {list(df.columns)}")
                        break
        except:
            continue
    
    print("\n💡 Dica: Se não encontrou, verifique manualmente a URL quando clicar na aba Footfall")
    print("   O GID aparecerá na URL como: ...?gid=XXXXXXXX#gid=XXXXXXXX")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n💡 Alternativa: Abra a planilha no navegador, clique na aba Footfall")
    print("   e copie o GID da URL (aparece como ?gid=XXXXXXXX)")
