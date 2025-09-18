#!/usr/bin/env python3
"""
Ler lista de sites diretamente da API do Google Sheets
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def read_sites_direct():
    """Ler lista de sites diretamente da API"""
    
    print("📋 LENDO LISTA DE SITES DIRETAMENTE DA API")
    print("=" * 70)
    
    # Configurar credenciais
    credentials_file = 'service-account-key.json'
    
    if not os.path.exists(credentials_file):
        print(f"❌ Arquivo de credenciais não encontrado: {credentials_file}")
        return None
    
    try:
        # Autenticar
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Construir serviço
        service = build('sheets', 'v4', credentials=credentials)
        
        # ID da planilha e GID
        sheet_id = "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o"
        gid = "490289068"
        
        print(f"📊 Lendo planilha: {sheet_id}")
        print(f"📋 GID: {gid}")
        
        # Ler dados da planilha (coluna A)
        range_name = f"Lista de portais!A:A"
        
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        print(f"📄 Dados lidos: {len(values)} linhas")
        
        # Extrair lista de sites
        sites = []
        for i, row in enumerate(values):
            if row and len(row) > 0:
                site = row[0].strip()
                print(f"   Linha {i+1}: '{site}'")
                
                # Filtrar apenas sites válidos (não vazios, não cabeçalho)
                if site and site.lower() != 'site domain' and len(site) > 3:
                    sites.append(site)
                    print(f"   ✅ Adicionado: '{site}'")
        
        print(f"\n🌐 Sites encontrados: {len(sites)}")
        
        # Mostrar primeiros 10 sites
        print(f"\n📋 PRIMEIROS 10 SITES:")
        for i, site in enumerate(sites[:10], 1):
            print(f"   {i:2d}. {site}")
        
        if len(sites) > 10:
            print(f"   ... e mais {len(sites) - 10} sites")
        
        # Salvar lista de sites
        sites_data = {
            "sites_list": sites,
            "total_sites": len(sites),
            "source": "Programática Video - Semana do Pescado",
            "sheet_id": sheet_id,
            "gid": gid
        }
        
        timestamp = "20250916_122500"
        filename = f"sites_list_direct_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sites_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Lista de sites salva: {filename}")
        
        return sites_data
        
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return None

if __name__ == "__main__":
    read_sites_direct()

