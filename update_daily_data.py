#!/usr/bin/env python3
"""
Script para atualizar os dados diários no dashboard
"""

import json
import re

def update_daily_data():
    # Ler os novos dados diários
    with open('daily_data_temp.json', 'r') as f:
        daily_data = json.load(f)
    
    # Converter para string JavaScript
    daily_js = json.dumps(daily_data, separators=(',', ':'))
    
    # Ler o arquivo HTML
    with open('static/dash_multicanal_spotify_programatica.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Encontrar e substituir o array DAILY
    pattern = r'const DAILY = \[.*?\];'
    replacement = f'const DAILY = {daily_js};'
    
    # Escapar caracteres especiais na substituição
    replacement = replacement.replace('\\', '\\\\')
    
    new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    # Salvar o arquivo atualizado
    with open('static/dash_multicanal_spotify_programatica.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("✅ Dados diários atualizados com sucesso!")

if __name__ == "__main__":
    update_daily_data()
