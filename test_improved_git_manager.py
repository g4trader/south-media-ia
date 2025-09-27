#!/usr/bin/env python3
"""
Teste do Git Manager Melhorado
Script para testar a versão melhorada em desenvolvimento
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

def test_improved_git_manager():
    """Testar o Git Manager Melhorado"""
    
    # URL do Git Manager (local)
    git_manager_url = "http://localhost:8080"
    
    print("🧪 Testando Git Manager Melhorado")
    print("=" * 50)
    
    # 1. Testar health check
    print("\n1️⃣ Testando Health Check...")
    try:
        response = requests.get(f"{git_manager_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check OK: {data}")
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False
    
    # 2. Criar arquivo de teste
    print("\n2️⃣ Criando arquivo de teste...")
    test_file_path = Path("static/test_dashboard.html")
    test_file_path.parent.mkdir(exist_ok=True)
    
    test_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard de Teste</title>
</head>
<body>
    <h1>Dashboard de Teste</h1>
    <p>Criado em: {}</p>
    <p>Teste do Git Manager Melhorado</p>
</body>
</html>
""".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Arquivo de teste criado: {test_file_path}")
    
    # 3. Testar acesso ao arquivo
    print("\n3️⃣ Testando acesso ao arquivo...")
    try:
        test_data = {
            "file_path": str(test_file_path)
        }
        
        response = requests.post(
            f"{git_manager_url}/test-file",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Teste de arquivo OK:")
            print(f"   - Path original: {data['file_info']['original_path']}")
            print(f"   - Path normalizado: {data['file_info']['normalized_path']}")
            print(f"   - Existe: {data['file_info']['exists']}")
            print(f"   - É arquivo: {data['file_info']['is_file']}")
            print(f"   - É legível: {data['file_info']['is_readable']}")
            print(f"   - Tamanho: {data['file_info']['size']} bytes")
        else:
            print(f"❌ Teste de arquivo falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro no teste de arquivo: {e}")
    
    # 4. Testar notificação de dashboard
    print("\n4️⃣ Testando notificação de dashboard...")
    try:
        notification_data = {
            "action": "dashboard_created",
            "file_path": str(test_file_path),
            "campaign_key": "test_campaign",
            "client": "Cliente Teste",
            "campaign_name": "Campanha de Teste"
        }
        
        response = requests.post(
            f"{git_manager_url}/notify",
            json=notification_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notificação processada:")
            print(f"   - Sucesso: {data['success']}")
            print(f"   - Mensagem: {data['message']}")
            if 'file_committed' in data:
                print(f"   - Arquivo commitado: {data['file_committed']}")
        else:
            print(f"❌ Notificação falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro na notificação: {e}")
    
    # 5. Verificar status do Git
    print("\n5️⃣ Verificando status do Git...")
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print(f"📝 Mudanças no Git:")
                for line in changes.split('\n'):
                    print(f"   {line}")
            else:
                print("✅ Nenhuma mudança pendente no Git")
        else:
            print(f"⚠️ Erro ao verificar status do Git: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao verificar Git: {e}")
    
    # 6. Limpeza
    print("\n6️⃣ Limpando arquivo de teste...")
    try:
        if test_file_path.exists():
            test_file_path.unlink()
            print(f"✅ Arquivo de teste removido: {test_file_path}")
    except Exception as e:
        print(f"❌ Erro ao remover arquivo de teste: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")
    
    return True

if __name__ == '__main__':
    test_improved_git_manager()
