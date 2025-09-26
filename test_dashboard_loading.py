#!/usr/bin/env python3
"""
Script para testar o carregamento do dashboard
"""

import requests
import time
import json

def test_dashboard_loading():
    """Testa o carregamento do dashboard"""
    
    dashboard_url = "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html"
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    print("🧪 Testando carregamento do dashboard...")
    
    # 1. Testar se o dashboard está acessível
    print("\n1️⃣ Testando acesso ao dashboard...")
    try:
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard acessível")
            print(f"📊 Tamanho: {len(response.content)} bytes")
        else:
            print(f"❌ Dashboard não acessível - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
        return False
    
    # 2. Testar se a API está funcionando
    print("\n2️⃣ Testando API...")
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ API funcionando")
                print(f"📊 Modo de teste: {data.get('test_mode', False)}")
                print(f"📊 Dados disponíveis: {len(data.get('data', {}).get('daily_data', []))} registros")
            else:
                print(f"❌ API retornou erro: {data.get('message')}")
                return False
        else:
            print(f"❌ API não acessível - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
        return False
    
    # 3. Testar se há problemas de CORS
    print("\n3️⃣ Testando CORS...")
    try:
        headers = {
            'Origin': 'https://south-media-ia-609095880025.us-central1.run.app',
            'User-Agent': 'Mozilla/5.0 (compatible; DashboardTest/1.0)'
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            print("✅ CORS configurado:")
            for key, value in cors_headers.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Problema com CORS - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de CORS: {e}")
        return False
    
    # 4. Simular requisição do dashboard
    print("\n4️⃣ Simulando requisição do dashboard...")
    try:
        # Simular headers que o navegador enviaria
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Origin': 'https://south-media-ia-609095880025.us-central1.run.app',
            'Referer': dashboard_url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Requisição simulada bem-sucedida")
            print(f"📊 Cliente: {data.get('data', {}).get('contract', {}).get('client', 'N/A')}")
            print(f"📊 Campanha: {data.get('data', {}).get('contract', {}).get('campaign', 'N/A')}")
            return True
        else:
            print(f"❌ Requisição simulada falhou - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição simulada: {e}")
        return False

def analyze_dashboard_content():
    """Analisa o conteúdo do dashboard para identificar problemas"""
    
    dashboard_url = "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html"
    
    print("\n🔍 Analisando conteúdo do dashboard...")
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        content = response.text
        
        # Verificar se há problemas no JavaScript
        if "Erro ao carregar dados" in content:
            print("⚠️ Dashboard contém mensagem de erro")
        
        if "loadDashboardData" in content:
            print("✅ Função loadDashboardData encontrada")
        else:
            print("❌ Função loadDashboardData não encontrada")
        
        if "fetch(" in content:
            print("✅ Código fetch encontrado")
        else:
            print("❌ Código fetch não encontrado")
        
        if "sebrae_pr_feira_do_empreendedor" in content:
            print("✅ Campaign key correto encontrado")
        else:
            print("❌ Campaign key não encontrado")
        
        # Verificar se há problemas de sintaxe
        if "SyntaxError" in content or "ReferenceError" in content:
            print("❌ Possíveis erros de JavaScript encontrados")
        else:
            print("✅ Nenhum erro de JavaScript óbvio encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao analisar dashboard: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste de carregamento do dashboard")
    
    if test_dashboard_loading():
        print("\n✅ TESTE BÁSICO PASSOU")
        analyze_dashboard_content()
    else:
        print("\n❌ TESTE BÁSICO FALHOU")
    
    print("\n🎯 Teste concluído!")

"""
Script para testar o carregamento do dashboard
"""

import requests
import time
import json

def test_dashboard_loading():
    """Testa o carregamento do dashboard"""
    
    dashboard_url = "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html"
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    print("🧪 Testando carregamento do dashboard...")
    
    # 1. Testar se o dashboard está acessível
    print("\n1️⃣ Testando acesso ao dashboard...")
    try:
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard acessível")
            print(f"📊 Tamanho: {len(response.content)} bytes")
        else:
            print(f"❌ Dashboard não acessível - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
        return False
    
    # 2. Testar se a API está funcionando
    print("\n2️⃣ Testando API...")
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ API funcionando")
                print(f"📊 Modo de teste: {data.get('test_mode', False)}")
                print(f"📊 Dados disponíveis: {len(data.get('data', {}).get('daily_data', []))} registros")
            else:
                print(f"❌ API retornou erro: {data.get('message')}")
                return False
        else:
            print(f"❌ API não acessível - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
        return False
    
    # 3. Testar se há problemas de CORS
    print("\n3️⃣ Testando CORS...")
    try:
        headers = {
            'Origin': 'https://south-media-ia-609095880025.us-central1.run.app',
            'User-Agent': 'Mozilla/5.0 (compatible; DashboardTest/1.0)'
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            print("✅ CORS configurado:")
            for key, value in cors_headers.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Problema com CORS - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de CORS: {e}")
        return False
    
    # 4. Simular requisição do dashboard
    print("\n4️⃣ Simulando requisição do dashboard...")
    try:
        # Simular headers que o navegador enviaria
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Origin': 'https://south-media-ia-609095880025.us-central1.run.app',
            'Referer': dashboard_url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Requisição simulada bem-sucedida")
            print(f"📊 Cliente: {data.get('data', {}).get('contract', {}).get('client', 'N/A')}")
            print(f"📊 Campanha: {data.get('data', {}).get('contract', {}).get('campaign', 'N/A')}")
            return True
        else:
            print(f"❌ Requisição simulada falhou - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição simulada: {e}")
        return False

def analyze_dashboard_content():
    """Analisa o conteúdo do dashboard para identificar problemas"""
    
    dashboard_url = "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html"
    
    print("\n🔍 Analisando conteúdo do dashboard...")
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        content = response.text
        
        # Verificar se há problemas no JavaScript
        if "Erro ao carregar dados" in content:
            print("⚠️ Dashboard contém mensagem de erro")
        
        if "loadDashboardData" in content:
            print("✅ Função loadDashboardData encontrada")
        else:
            print("❌ Função loadDashboardData não encontrada")
        
        if "fetch(" in content:
            print("✅ Código fetch encontrado")
        else:
            print("❌ Código fetch não encontrado")
        
        if "sebrae_pr_feira_do_empreendedor" in content:
            print("✅ Campaign key correto encontrado")
        else:
            print("❌ Campaign key não encontrado")
        
        # Verificar se há problemas de sintaxe
        if "SyntaxError" in content or "ReferenceError" in content:
            print("❌ Possíveis erros de JavaScript encontrados")
        else:
            print("✅ Nenhum erro de JavaScript óbvio encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao analisar dashboard: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste de carregamento do dashboard")
    
    if test_dashboard_loading():
        print("\n✅ TESTE BÁSICO PASSOU")
        analyze_dashboard_content()
    else:
        print("\n❌ TESTE BÁSICO FALHOU")
    
    print("\n🎯 Teste concluído!")


