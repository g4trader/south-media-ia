#!/usr/bin/env python3
"""
Script para debugar o problema específico do dashboard
"""

import requests
import time
import json

def test_dashboard_environments():
    """Testa o dashboard em diferentes ambientes"""
    
    print("🔍 Testando dashboard em diferentes ambientes...")
    
    # URLs para testar
    environments = {
        "Cloud Run": "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html",
        "Vercel": "https://dash.iasouth.tech/static/dash_sebrae_pr_feira_do_empreendedor.html"
    }
    
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    for env_name, dashboard_url in environments.items():
        print(f"\n📊 Testando {env_name}...")
        
        try:
            # Testar acesso ao dashboard
            response = requests.get(dashboard_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Dashboard {env_name} acessível")
                
                # Verificar se contém mensagem de erro
                if "Erro ao carregar dados" in response.text:
                    print("⚠️ Contém mensagem de erro")
                else:
                    print("✅ Sem mensagem de erro")
                
                # Verificar se contém dados de teste
                if "test_mode" in response.text or "Dados de demonstração" in response.text:
                    print("⚠️ Contém referências a dados de teste")
                else:
                    print("✅ Sem referências a dados de teste")
                    
            else:
                print(f"❌ Dashboard {env_name} não acessível - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao testar {env_name}: {e}")

def test_api_with_different_origins():
    """Testa a API com diferentes origens"""
    
    print("\n🌐 Testando API com diferentes origens...")
    
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    origins = [
        "https://south-media-ia-609095880025.us-central1.run.app",
        "https://dash.iasouth.tech",
        "http://localhost:3000",
        "https://localhost:3000"
    ]
    
    for origin in origins:
        print(f"\n🔗 Testando origem: {origin}")
        
        try:
            headers = {
                'Origin': origin,
                'Referer': f"{origin}/static/dash_sebrae_pr_feira_do_empreendedor.html",
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API acessível de {origin}")
                print(f"📊 CORS Origin: {response.headers.get('access-control-allow-origin', 'N/A')}")
                print(f"📊 Success: {data.get('success', False)}")
            else:
                print(f"❌ API não acessível de {origin} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao testar origem {origin}: {e}")

def check_dashboard_javascript():
    """Verifica o JavaScript do dashboard"""
    
    print("\n🔍 Verificando JavaScript do dashboard...")
    
    dashboard_url = "https://dash.iasouth.tech/static/dash_sebrae_pr_feira_do_empreendedor.html"
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        content = response.text
        
        # Verificar problemas comuns
        issues = []
        
        if "loadDashboardData" in content:
            print("✅ Função loadDashboardData encontrada")
        else:
            issues.append("Função loadDashboardData não encontrada")
        
        if "fetch(" in content:
            print("✅ Código fetch encontrado")
        else:
            issues.append("Código fetch não encontrado")
        
        if "sebrae_pr_feira_do_empreendedor" in content:
            print("✅ Campaign key correto")
        else:
            issues.append("Campaign key incorreto")
        
        if "DOMContentLoaded" in content:
            print("✅ Event listener DOMContentLoaded encontrado")
        else:
            issues.append("Event listener DOMContentLoaded não encontrado")
        
        if "await fetch" in content:
            print("✅ Async/await fetch encontrado")
        else:
            issues.append("Async/await fetch não encontrado")
        
        # Verificar se há problemas de sintaxe
        if "SyntaxError" in content or "ReferenceError" in content:
            issues.append("Possíveis erros de JavaScript")
        
        if issues:
            print(f"\n⚠️ Problemas encontrados:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Nenhum problema óbvio encontrado no JavaScript")
            
    except Exception as e:
        print(f"❌ Erro ao verificar JavaScript: {e}")

def suggest_solution():
    """Sugere uma solução para o problema"""
    
    print("\n💡 SUGESTÕES PARA RESOLVER O PROBLEMA:")
    print("\n1. 🔄 Recriar o dashboard com dados reais:")
    print("   - Use o gerador para criar uma nova campanha")
    print("   - Certifique-se de que os dados do Google Sheets estão corretos")
    
    print("\n2. 🧪 Testar com dados reais:")
    print("   - Verificar se o Google Sheets está acessível")
    print("   - Confirmar se as credenciais estão corretas")
    
    print("\n3. 🔧 Verificar logs do navegador:")
    print("   - Abrir DevTools (F12)")
    print("   - Verificar Console para erros JavaScript")
    print("   - Verificar Network para requisições falhadas")
    
    print("\n4. 🌐 Testar em diferentes navegadores:")
    print("   - Chrome, Firefox, Safari")
    print("   - Verificar se é problema específico do navegador")

if __name__ == "__main__":
    print("🚀 Iniciando debug do problema do dashboard")
    
    test_dashboard_environments()
    test_api_with_different_origins()
    check_dashboard_javascript()
    suggest_solution()
    
    print("\n🎯 Debug concluído!")

"""
Script para debugar o problema específico do dashboard
"""

import requests
import time
import json

def test_dashboard_environments():
    """Testa o dashboard em diferentes ambientes"""
    
    print("🔍 Testando dashboard em diferentes ambientes...")
    
    # URLs para testar
    environments = {
        "Cloud Run": "https://south-media-ia-609095880025.us-central1.run.app/static/dash_sebrae_pr_feira_do_empreendedor.html",
        "Vercel": "https://dash.iasouth.tech/static/dash_sebrae_pr_feira_do_empreendedor.html"
    }
    
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    for env_name, dashboard_url in environments.items():
        print(f"\n📊 Testando {env_name}...")
        
        try:
            # Testar acesso ao dashboard
            response = requests.get(dashboard_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Dashboard {env_name} acessível")
                
                # Verificar se contém mensagem de erro
                if "Erro ao carregar dados" in response.text:
                    print("⚠️ Contém mensagem de erro")
                else:
                    print("✅ Sem mensagem de erro")
                
                # Verificar se contém dados de teste
                if "test_mode" in response.text or "Dados de demonstração" in response.text:
                    print("⚠️ Contém referências a dados de teste")
                else:
                    print("✅ Sem referências a dados de teste")
                    
            else:
                print(f"❌ Dashboard {env_name} não acessível - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao testar {env_name}: {e}")

def test_api_with_different_origins():
    """Testa a API com diferentes origens"""
    
    print("\n🌐 Testando API com diferentes origens...")
    
    api_url = "https://south-media-ia-609095880025.us-central1.run.app/api/sebrae_pr_feira_do_empreendedor/data"
    
    origins = [
        "https://south-media-ia-609095880025.us-central1.run.app",
        "https://dash.iasouth.tech",
        "http://localhost:3000",
        "https://localhost:3000"
    ]
    
    for origin in origins:
        print(f"\n🔗 Testando origem: {origin}")
        
        try:
            headers = {
                'Origin': origin,
                'Referer': f"{origin}/static/dash_sebrae_pr_feira_do_empreendedor.html",
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API acessível de {origin}")
                print(f"📊 CORS Origin: {response.headers.get('access-control-allow-origin', 'N/A')}")
                print(f"📊 Success: {data.get('success', False)}")
            else:
                print(f"❌ API não acessível de {origin} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao testar origem {origin}: {e}")

def check_dashboard_javascript():
    """Verifica o JavaScript do dashboard"""
    
    print("\n🔍 Verificando JavaScript do dashboard...")
    
    dashboard_url = "https://dash.iasouth.tech/static/dash_sebrae_pr_feira_do_empreendedor.html"
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        content = response.text
        
        # Verificar problemas comuns
        issues = []
        
        if "loadDashboardData" in content:
            print("✅ Função loadDashboardData encontrada")
        else:
            issues.append("Função loadDashboardData não encontrada")
        
        if "fetch(" in content:
            print("✅ Código fetch encontrado")
        else:
            issues.append("Código fetch não encontrado")
        
        if "sebrae_pr_feira_do_empreendedor" in content:
            print("✅ Campaign key correto")
        else:
            issues.append("Campaign key incorreto")
        
        if "DOMContentLoaded" in content:
            print("✅ Event listener DOMContentLoaded encontrado")
        else:
            issues.append("Event listener DOMContentLoaded não encontrado")
        
        if "await fetch" in content:
            print("✅ Async/await fetch encontrado")
        else:
            issues.append("Async/await fetch não encontrado")
        
        # Verificar se há problemas de sintaxe
        if "SyntaxError" in content or "ReferenceError" in content:
            issues.append("Possíveis erros de JavaScript")
        
        if issues:
            print(f"\n⚠️ Problemas encontrados:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Nenhum problema óbvio encontrado no JavaScript")
            
    except Exception as e:
        print(f"❌ Erro ao verificar JavaScript: {e}")

def suggest_solution():
    """Sugere uma solução para o problema"""
    
    print("\n💡 SUGESTÕES PARA RESOLVER O PROBLEMA:")
    print("\n1. 🔄 Recriar o dashboard com dados reais:")
    print("   - Use o gerador para criar uma nova campanha")
    print("   - Certifique-se de que os dados do Google Sheets estão corretos")
    
    print("\n2. 🧪 Testar com dados reais:")
    print("   - Verificar se o Google Sheets está acessível")
    print("   - Confirmar se as credenciais estão corretas")
    
    print("\n3. 🔧 Verificar logs do navegador:")
    print("   - Abrir DevTools (F12)")
    print("   - Verificar Console para erros JavaScript")
    print("   - Verificar Network para requisições falhadas")
    
    print("\n4. 🌐 Testar em diferentes navegadores:")
    print("   - Chrome, Firefox, Safari")
    print("   - Verificar se é problema específico do navegador")

if __name__ == "__main__":
    print("🚀 Iniciando debug do problema do dashboard")
    
    test_dashboard_environments()
    test_api_with_different_origins()
    check_dashboard_javascript()
    suggest_solution()
    
    print("\n🎯 Debug concluído!")


