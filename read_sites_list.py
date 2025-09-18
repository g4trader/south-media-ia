#!/usr/bin/env python3
"""
Ler lista de sites da planilha de Programática Video
"""

import json
from google_sheets_processor import GoogleSheetsProcessor

def read_sites_list():
    """Ler lista de sites da planilha"""
    
    print("📋 LENDO LISTA DE SITES DA PLANILHA")
    print("=" * 70)
    
    # Forçar uso de service account
    import os
    os.environ['GOOGLE_CREDENTIALS_FILE'] = 'service-account-key.json'
    
    # Configurar processador de planilhas
    processor = GoogleSheetsProcessor()
    
    # Autenticar
    try:
        processor.authenticate()
        print("✅ Autenticação com Google Sheets realizada com sucesso")
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return
    
    # ID da planilha e GID
    sheet_id = "1VRJrgwKYTxF_QUrJRKeeo6npsTO_AhgrDDBZ4CF4T5o"
    gid = "490289068"
    
    print(f"📊 Lendo planilha: {sheet_id}")
    print(f"📋 GID: {gid}")
    
    try:
        # Ler dados da planilha
        data = processor.read_sheet_data(sheet_id, None, gid, "A:A")
        
        print(f"📄 Dados lidos: {len(data)} linhas")
        
        # Debug: mostrar primeiras linhas
        print(f"\n🔍 DEBUG - Primeiras 10 linhas:")
        for i, row in enumerate(data[:10]):
            print(f"   Linha {i}: {row}")
        
        # Extrair lista de sites (coluna A)
        sites = []
        for row in data:
            # Verificar se row é uma string ou lista
            if isinstance(row, str):
                site = row.strip()
            elif row and len(row) > 0 and row[0]:
                site = row[0].strip()
            else:
                continue
                
            print(f"   Processando: '{site}'")
            # Filtrar apenas sites válidos (não vazios, não cabeçalho)
            if site and site.lower() != 'site domain' and len(site) > 3:
                sites.append(site)
                print(f"   ✅ Adicionado: '{site}'")
        
        print(f"🌐 Sites encontrados: {len(sites)}")
        
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
        
        timestamp = "20250916_122000"
        filename = f"sites_list_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sites_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Lista de sites salva: {filename}")
        
        return sites_data
        
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return None

if __name__ == "__main__":
    read_sites_list()
