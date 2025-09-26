#!/usr/bin/env python3
"""
Teste do token do GitHub
"""

import os
import requests

def test_github_token():
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ GITHUB_TOKEN não configurado")
        return False
    
    print(f"🔑 Token configurado: {len(token)} caracteres")
    print(f"🔑 Token (primeiros 8): {token[:8]}...")
    
    # Testar acesso ao repositório
    url = "https://api.github.com/repos/g4trader/south-media-ia"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"✅ Repositório acessado: {repo_info['name']}")
            print(f"🔗 URL: {repo_info['html_url']}")
            return True
        elif response.status_code == 401:
            print("❌ Token inválido ou sem permissão")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    test_github_token()

"""
Teste do token do GitHub
"""

import os
import requests

def test_github_token():
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ GITHUB_TOKEN não configurado")
        return False
    
    print(f"🔑 Token configurado: {len(token)} caracteres")
    print(f"🔑 Token (primeiros 8): {token[:8]}...")
    
    # Testar acesso ao repositório
    url = "https://api.github.com/repos/g4trader/south-media-ia"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"✅ Repositório acessado: {repo_info['name']}")
            print(f"🔗 URL: {repo_info['html_url']}")
            return True
        elif response.status_code == 401:
            print("❌ Token inválido ou sem permissão")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    test_github_token()


