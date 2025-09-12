#!/usr/bin/env python3
"""
Script de teste para validar a configuração da automação
"""

import os
import sys
import json
from datetime import datetime

def test_dependencies():
    """Testa se as dependências estão instaladas"""
    print("🔍 Testando dependências...")
    
    required_packages = [
        'google-api-python-client',
        'google-auth-httplib2', 
        'google-auth-oauthlib',
        'pandas',
        'schedule',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def test_directories():
    """Testa se os diretórios necessários existem"""
    print("\n🔍 Testando diretórios...")
    
    required_dirs = [
        'logs',
        'backups',
        'credentials'
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n❌ Diretórios faltando: {', '.join(missing_dirs)}")
        print("Execute: python setup_automation.py")
        return False
    
    print("✅ Todos os diretórios existem")
    return True

def test_config_files():
    """Testa se os arquivos de configuração existem"""
    print("\n🔍 Testando arquivos de configuração...")
    
    config_files = [
        'config.py',
        'credentials.json',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file in config_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Arquivos faltando: {', '.join(missing_files)}")
        if 'credentials.json' in missing_files:
            print("Configure as credenciais do Google Sheets")
        if 'config.py' in missing_files:
            print("Execute: python setup_automation.py")
        return False
    
    print("✅ Todos os arquivos de configuração existem")
    return True

def test_config_content():
    """Testa o conteúdo dos arquivos de configuração"""
    print("\n🔍 Testando conteúdo da configuração...")
    
    try:
        from config import GOOGLE_SHEETS_CONFIG
        
        # Verificar se os IDs das planilhas foram configurados
        placeholder_count = 0
        configured_count = 0
        
        for channel, config in GOOGLE_SHEETS_CONFIG.items():
            sheet_id = config['sheet_id']
            if 'YOUR_' in sheet_id:
                print(f"  ⚠️ {channel}: ID não configurado")
                placeholder_count += 1
            else:
                print(f"  ✅ {channel}: ID configurado")
                configured_count += 1
        
        if placeholder_count > 0:
            print(f"\n⚠️ {placeholder_count} canais sem ID configurado")
            print("Execute: python setup_automation.py")
            return False
        
        print(f"✅ {configured_count} canais configurados")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar config.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def test_google_credentials():
    """Testa as credenciais do Google"""
    print("\n🔍 Testando credenciais do Google...")
    
    try:
        credentials_file = 'credentials.json'
        
        if not os.path.exists(credentials_file):
            print("  ❌ Arquivo credentials.json não encontrado")
            return False
        
        # Verificar se é um JSON válido
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds or 'web' in creds:
            print("  ✅ Credenciais válidas")
            return True
        else:
            print("  ❌ Formato de credenciais inválido")
            return False
            
    except json.JSONDecodeError:
        print("  ❌ Arquivo credentials.json inválido")
        return False
    except Exception as e:
        print(f"  ❌ Erro ao verificar credenciais: {e}")
        return False

def test_google_sheets_connection():
    """Testa conexão com Google Sheets"""
    print("\n🔍 Testando conexão com Google Sheets...")
    
    try:
        from google_sheets_processor import GoogleSheetsProcessor
        
        processor = GoogleSheetsProcessor()
        
        # Testar com um canal
        from config import GOOGLE_SHEETS_CONFIG
        test_channel = list(GOOGLE_SHEETS_CONFIG.keys())[0]
        test_config = GOOGLE_SHEETS_CONFIG[test_channel]
        
        print(f"  🧪 Testando canal: {test_channel}")
        
        df = processor.read_sheet_data(
            test_config['sheet_id'],
            sheet_name=test_config.get('sheet_name'),
            gid=test_config.get('gid')
        )
        
        if not df.empty:
            print(f"  ✅ Conexão bem-sucedida! {len(df)} linhas encontradas")
            return True
        else:
            print("  ⚠️ Conexão OK, mas nenhum dado encontrado")
            return True
            
    except Exception as e:
        print(f"  ❌ Erro na conexão: {e}")
        return False

def test_dashboard_file():
    """Testa se o arquivo do dashboard existe"""
    print("\n🔍 Testando arquivo do dashboard...")
    
    dashboard_file = 'static/dash_sonho.html'
    
    if not os.path.exists(dashboard_file):
        print(f"  ❌ {dashboard_file} não encontrado")
        return False
    
    # Verificar se contém as variáveis necessárias
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = ['const CONS =', 'const PER =', 'const DAILY =']
    missing_vars = []
    
    for var in required_vars:
        if var in content:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Variáveis faltando no dashboard: {', '.join(missing_vars)}")
        return False
    
    print("✅ Arquivo do dashboard está correto")
    return True

def run_full_test():
    """Executa todos os testes"""
    print("🧪 TESTE COMPLETO DA CONFIGURAÇÃO DA AUTOMAÇÃO")
    print("=" * 60)
    
    tests = [
        ("Dependências", test_dependencies),
        ("Diretórios", test_directories),
        ("Arquivos de Configuração", test_config_files),
        ("Conteúdo da Configuração", test_config_content),
        ("Credenciais Google", test_google_credentials),
        ("Arquivo do Dashboard", test_dashboard_file),
        ("Conexão Google Sheets", test_google_sheets_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Resultado: {passed}/{len(results)} testes passaram")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A automação está pronta para ser executada")
        print("\n🚀 Para iniciar a automação:")
        print("   python dashboard_automation.py")
        print("\n🔍 Para monitoramento:")
        print("   python monitoring.py")
    else:
        print(f"\n⚠️ {failed} teste(s) falharam")
        print("❌ Corrija os problemas antes de executar a automação")
        print("\n📋 Próximos passos:")
        print("   1. Execute: pip install -r requirements.txt")
        print("   2. Execute: python setup_automation.py")
        print("   3. Configure as credenciais do Google Sheets")
        print("   4. Execute este teste novamente")
    
    return failed == 0

def main():
    """Função principal"""
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal durante os testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
