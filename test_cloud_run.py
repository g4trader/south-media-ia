#!/usr/bin/env python3
"""
Script para testar a aplicação Cloud Run
"""

import requests
import json
import sys
from datetime import datetime

def test_cloud_run_service(service_url):
    """Testa todos os endpoints do serviço Cloud Run"""
    
    print(f"🧪 TESTANDO SERVIÇO CLOUD RUN")
    print(f"URL: {service_url}")
    print("=" * 50)
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{service_url}/health",
            "method": "GET",
            "expected_status": 200
        },
        {
            "name": "Status",
            "url": f"{service_url}/status", 
            "method": "GET",
            "expected_status": 200
        },
        {
            "name": "Config",
            "url": f"{service_url}/config",
            "method": "GET", 
            "expected_status": 200
        },
        {
            "name": "Logs",
            "url": f"{service_url}/logs",
            "method": "GET",
            "expected_status": 200
        },
        {
            "name": "Index",
            "url": f"{service_url}/",
            "method": "GET",
            "expected_status": 200
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔍 Testando: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=30)
            elif test['method'] == 'POST':
                response = requests.post(test['url'], timeout=30)
            
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == test['expected_status']:
                print(f"   ✅ SUCESSO")
                results.append({"test": test['name'], "status": "success", "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]})
            else:
                print(f"   ❌ FALHA - Esperado: {test['expected_status']}, Recebido: {status}")
                results.append({"test": test['name'], "status": "failed", "error": f"Status {status}"})
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT")
            results.append({"test": test['name'], "status": "timeout", "error": "Timeout"})
        except requests.exceptions.ConnectionError:
            print(f"   🔌 ERRO DE CONEXÃO")
            results.append({"test": test['name'], "status": "connection_error", "error": "Connection error"})
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            results.append({"test": test['name'], "status": "error", "error": str(e)})
    
    # Teste de trigger manual
    print(f"\n🔍 Testando: Trigger Manual")
    print(f"   URL: {service_url}/trigger")
    
    try:
        response = requests.post(f"{service_url}/trigger", timeout=60)
        status = response.status_code
        print(f"   Status: {status}")
        
        if status in [200, 202]:
            print(f"   ✅ SUCESSO - Automação disparada")
            results.append({"test": "Trigger Manual", "status": "success", "response": response.json()})
        else:
            print(f"   ❌ FALHA - Status: {status}")
            results.append({"test": "Trigger Manual", "status": "failed", "error": f"Status {status}"})
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        results.append({"test": "Trigger Manual", "status": "error", "error": str(e)})
    
    # Resumo dos resultados
    print(f"\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    total = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['test']}")
        
        if result['status'] != 'success':
            print(f"    Erro: {result.get('error', 'Desconhecido')}")
    
    print(f"\n📈 Resultado: {successful}/{total} testes passaram")
    
    if successful == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Serviço Cloud Run funcionando perfeitamente")
        return True
    else:
        print(f"\n⚠️ {total - successful} teste(s) falharam")
        print("❌ Verifique os logs e configurações do serviço")
        return False

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python test_cloud_run.py <URL_DO_SERVIÇO>")
        print("Exemplo: python test_cloud_run.py https://dashboard-automation-xxxxx-uc.a.run.app")
        sys.exit(1)
    
    service_url = sys.argv[1].rstrip('/')
    
    try:
        success = test_cloud_run_service(service_url)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
