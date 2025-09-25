#!/usr/bin/env python3
"""
Script para fazer commit manual de dashboards gerados no Cloud Run
Uso: python commit_dashboard.py <nome_do_arquivo>
Exemplo: python commit_dashboard.py dash_nike_air_max.html
"""

import sys
import os
import subprocess
import requests
from pathlib import Path

def download_dashboard_from_cloud_run(filename):
    """Baixa dashboard do Cloud Run para local"""
    cloud_run_url = f"https://south-media-ia-609095880025.us-central1.run.app/static/{filename}"
    
    print(f"📥 Baixando {filename} do Cloud Run...")
    try:
        response = requests.get(cloud_run_url, timeout=30)
        response.raise_for_status()
        
        # Salvar arquivo localmente
        file_path = Path("static") / filename
        file_path.parent.mkdir(exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Arquivo salvo em: {file_path}")
        return str(file_path)
        
    except Exception as e:
        print(f"❌ Erro ao baixar arquivo: {e}")
        return None

def commit_dashboard(filename):
    """Faz commit do dashboard no Git"""
    if not filename.endswith('.html'):
        filename += '.html'
    
    print(f"🚀 Iniciando processo de commit para {filename}")
    
    # 1. Baixar arquivo do Cloud Run
    file_path = download_dashboard_from_cloud_run(filename)
    if not file_path:
        return False
    
    # 2. Verificar se arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # 3. Git add
        print("📝 Adicionando arquivo ao Git...")
        subprocess.run(['git', 'add', file_path], check=True, capture_output=True)
        
        # 4. Git commit
        commit_message = f"add: Dashboard {filename} (auto-generated)"
        print(f"💾 Fazendo commit: {commit_message}")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
        
        # 5. Git push
        print("⬆️ Fazendo push para GitHub...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
        
        print("🎉 Commit realizado com sucesso!")
        print(f"📊 Dashboard disponível em: https://dash.iasouth.tech/static/{filename}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.decode()}")
        if e.stderr:
            print(f"stderr: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python commit_dashboard.py <nome_do_arquivo>")
        print("📝 Exemplo: python commit_dashboard.py dash_nike_air_max.html")
        sys.exit(1)
    
    filename = sys.argv[1]
    success = commit_dashboard(filename)
    
    if success:
        print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("🎯 O dashboard agora está disponível no Vercel")
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("🔧 Verifique os erros acima e tente novamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
