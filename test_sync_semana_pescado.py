#!/usr/bin/env python3
"""
Teste da funcionalidade de sincronização da Semana do Pescado
"""

import requests
import json
import time

def test_sync_endpoint():
    """Testar o endpoint de sincronização"""
    
    print("🧪 TESTANDO ENDPOINT DE SINCRONIZAÇÃO - SEMANA DO PESCADO")
    print("=" * 60)
    
    # URL do endpoint (ajustar conforme necessário)
    url = "http://localhost:5000/api/semana-pescado/sync"
    
    try:
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição POST
        response = requests.post(url, timeout=120)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 207]:  # 200 = OK, 207 = Multi-Status
            result = response.json()
            
            print(f"✅ Sucesso: {result.get('success', False)}")
            print(f"📝 Mensagem: {result.get('message', 'N/A')}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            
            if result.get('dashboard_file'):
                print(f"📄 Dashboard atualizado: {result.get('dashboard_file')}")
            
            # Mostrar resultados dos scripts
            scripts_results = result.get('scripts_results', [])
            if scripts_results:
                print(f"\n📋 RESULTADOS DOS SCRIPTS:")
                for script_result in scripts_results:
                    status = "✅" if script_result['success'] else "❌"
                    print(f"   {status} {script_result['script']}")
                    
                    if not script_result['success'] and script_result.get('error'):
                        print(f"      Erro: {script_result['error']}")
            
            return True
            
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Mensagem de erro: {error_data.get('message', 'N/A')}")
            except:
                print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - A requisição demorou mais de 2 minutos")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão - Verifique se o servidor está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_scripts_individually():
    """Testar scripts individuais"""
    
    print(f"\n🔧 TESTANDO SCRIPTS INDIVIDUALMENTE")
    print("=" * 60)
    
    scripts = [
        'google_sheets_processor.py',
        'process_daily_data.py', 
        'generate_dashboard_final_no_netflix.py'
    ]
    
    import subprocess
    import sys
    from pathlib import Path
    
    base_path = Path(__file__).parent
    
    for script in scripts:
        script_path = base_path / script
        print(f"\n📄 Testando: {script}")
        
        if script_path.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"   ✅ Sucesso")
                    if result.stdout:
                        print(f"   📤 Output: {result.stdout[:200]}...")
                else:
                    print(f"   ❌ Erro (código: {result.returncode})")
                    if result.stderr:
                        print(f"   📤 Erro: {result.stderr[:200]}...")
                        
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Timeout")
            except Exception as e:
                print(f"   ❌ Exceção: {e}")
        else:
            print(f"   ❌ Arquivo não encontrado")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE SINCRONIZAÇÃO")
    print("=" * 60)
    
    # Teste 1: Endpoint de sincronização
    success = test_sync_endpoint()
    
    # Teste 2: Scripts individuais (se o endpoint falhar)
    if not success:
        test_scripts_individually()
    
    print(f"\n🎯 TESTE CONCLUÍDO")
    print("=" * 60)
