#!/usr/bin/env python3
"""
Script para verificar e corrigir os dados de outubro
"""

import json
import os
import re
import requests
from urllib.parse import urlparse, parse_qs
import csv
import io

def extract_sheet_id_and_gid(url):
    """Extrair sheet ID e gid da URL do Google Sheets"""
    parsed = urlparse(url)
    if 'docs.google.com' in parsed.netloc and '/spreadsheets/d/' in parsed.path:
        # Extrair sheet ID
        path_parts = parsed.path.split('/')
        sheet_id = None
        for i, part in enumerate(path_parts):
            if part == 'd' and i + 1 < len(path_parts):
                sheet_id = path_parts[i + 1]
                break
        
        # Extrair gid dos parâmetros
        query_params = parse_qs(parsed.query)
        gid = query_params.get('gid', ['0'])[0]
        
        return sheet_id, gid
    return None, None

def fetch_google_sheets_data(sheet_id, gid):
    """Buscar dados do Google Sheets"""
    try:
        # URL para exportar como CSV
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        print(f"Buscando dados de: {csv_url}")
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Usar csv.reader para processar corretamente
        csv_reader = csv.reader(io.StringIO(response.text))
        rows = list(csv_reader)
        
        if len(rows) < 2:
            print("❌ Dados insuficientes na planilha")
            return []
        
        print(f"✅ {len(rows)-1} linhas de dados encontradas")
        return rows[1:]  # Pular cabeçalho
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return []

def process_footfall_data(data_rows):
    """Processar dados de footfall"""
    footfall_points = []
    
    for row in data_rows:
        try:
            # Verificar se tem dados suficientes
            if len(row) < 6:
                continue
                
            # Extrair dados (assumindo formato: lat, long, proximidade, name, users, rate)
            lat_str = row[0].strip()
            lon_str = row[1].strip()
            name = row[3].strip()
            users_str = row[4].strip()
            rate_str = row[5].strip()
            
            # Pular linhas vazias
            if not lat_str or not lon_str or not name or not users_str or not rate_str:
                continue
            
            # Converter latitude (remover pontos extras e aspas)
            lat_str = lat_str.replace('"', '').replace('.', '', 1).replace('.', '')
            lat = float(lat_str)
            
            # Converter longitude (remover pontos extras e aspas)
            lon_str = lon_str.replace('"', '').replace('.', '', 1).replace('.', '')
            lon = float(lon_str)
            
            # Converter usuários (remover aspas e vírgulas)
            users_str = users_str.replace('"', '').replace(',', '').replace('.', '')
            users = int(users_str)
            
            # Converter taxa (remover aspas, substituir vírgula por ponto)
            rate_str = rate_str.replace('"', '').replace(',', '.')
            rate = float(rate_str)
            
            # Pular se usuários for 0
            if users == 0:
                continue
            
            footfall_points.append({
                "lat": lat,
                "lon": lon,
                "name": name,
                "users": users,
                "rate": rate
            })
            
        except (ValueError, IndexError) as e:
            print(f"⚠️ Pulando linha com erro: {row} - {e}")
            continue
    
    return footfall_points

def update_october_data():
    """Atualizar apenas os dados de outubro"""
    
    # URL da planilha de outubro
    october_url = "https://docs.google.com/spreadsheets/d/1etGnblqr5YZIqXIweKj5qTMGqmWlxL9OLbN_Ss5tzlQ/edit?gid=120680471#gid=120680471"
    
    print("🔄 Buscando dados corretos de outubro...")
    
    # Buscar dados da planilha de outubro
    sheet_id, gid = extract_sheet_id_and_gid(october_url)
    if not sheet_id:
        print("❌ Erro ao extrair ID da planilha de outubro")
        return False
    
    october_raw = fetch_google_sheets_data(sheet_id, gid)
    october_data = process_footfall_data(october_raw)
    
    print(f"✅ Dados de outubro: {len(october_data)} lojas processadas")
    if october_data:
        total_users = sum(store['users'] for store in october_data)
        print(f"   Total de usuários: {total_users:,}")
        print(f"   Primeira loja: {october_data[0]['name']} ({october_data[0]['users']} usuários)")
        
        # Mostrar todos os dados para verificação
        print("\n📊 Dados de outubro extraídos:")
        for i, store in enumerate(october_data, 1):
            print(f"   {i}. {store['name']}: {store['users']} usuários ({store['rate']}%)")
    
    # Atualizar HTML
    html_file = "static/dash_sonho_v2.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Arquivo {html_file} não encontrado!")
        return False
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar FOOTFALL_OUT_POINTS para outubro
    footfall_out_points = "const FOOTFALL_OUT_POINTS = [\n"
    for store in october_data:
        footfall_out_points += f'  {{\n    "lat": {store["lat"]},\n    "lon": {store["lon"]},\n    "name": "{store["name"]}",\n    "users": {store["users"]},\n    "rate": {store["rate"]}\n  }},\n'
    footfall_out_points += "];"
    
    # Substituir FOOTFALL_OUT_POINTS
    pattern = r'const FOOTFALL_OUT_POINTS = \[.*?\];'
    content = re.sub(pattern, footfall_out_points, content, flags=re.DOTALL)
    
    # Salvar arquivo atualizado
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {html_file} atualizado com dados corretos de outubro!")
    return True

if __name__ == "__main__":
    print("🔧 Verificando e corrigindo dados de outubro...")
    
    if update_october_data():
        print("\n🎉 Dados de outubro atualizados!")
        print("💡 Agora teste no navegador para verificar!")
    else:
        print("❌ Erro ao atualizar os dados de outubro")

