#!/usr/bin/env python3
"""
Exemplo de como atualizar os dados do dashboard dinamicamente
Este script demonstra como o sistema de atualização funciona
"""

import requests
import json
import time
from datetime import datetime

# URL da API do dashboard
API_URL = "http://localhost:8000/api/dashboard"

def test_dashboard_api():
    """Testa a API do dashboard"""
    print("🧪 Testando API do Dashboard...")
    
    try:
        # Testar health check
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
        
        # Testar endpoint de dados
        response = requests.get(f"{API_URL}/data")
        if response.status_code == 200:
            data = response.json()
            print("✅ Dados do dashboard: OK")
            print(f"   Última atualização: {data.get('last_updated', 'N/A')}")
            print(f"   Canais encontrados: {len(data.get('channels', {}))}")
            print(f"   Registros diários: {len(data.get('daily', []))}")
            
            # Mostrar resumo dos dados consolidados
            consolidated = data.get('consolidated', {})
            print(f"   Orçamento contratado: R$ {consolidated.get('Budget Contratado (R$)', 0):,.2f}")
            print(f"   Orçamento utilizado: R$ {consolidated.get('Budget Utilizado (R$)', 0):,.2f}")
            
            return True
        else:
            print(f"❌ Dados do dashboard falharam: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Verifique se o backend está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def monitor_dashboard_updates():
    """Monitora atualizações do dashboard em tempo real"""
    print("\n🔄 Monitorando atualizações do dashboard...")
    print("   (Pressione Ctrl+C para parar)")
    
    last_update = None
    
    try:
        while True:
            response = requests.get(f"{API_URL}/data")
            if response.status_code == 200:
                data = response.json()
                current_update = data.get('last_updated')
                
                if current_update != last_update:
                    print(f"🆕 Nova atualização detectada: {current_update}")
                    last_update = current_update
                    
                    # Mostrar estatísticas
                    consolidated = data.get('consolidated', {})
                    print(f"   💰 Orçamento: R$ {consolidated.get('Budget Utilizado (R$)', 0):,.2f} / R$ {consolidated.get('Budget Contratado (R$)', 0):,.2f}")
                    print(f"   📊 Impressões: {consolidated.get('Impressões', 0):,}")
                    print(f"   👆 Cliques: {consolidated.get('Cliques', 0):,}")
                else:
                    print(".", end="", flush=True)
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
            
            time.sleep(10)  # Verificar a cada 10 segundos
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoramento interrompido pelo usuário")

def simulate_data_update():
    """Simula uma atualização de dados (para teste)"""
    print("\n🔄 Simulando atualização de dados...")
    
    # Aqui você poderia:
    # 1. Atualizar arquivos TSV
    # 2. Fazer upload de novos dados
    # 3. Processar dados de uma fonte externa
    
    print("   📝 Para simular uma atualização:")
    print("   1. Modifique um arquivo TSV em /static/tsv/")
    print("   2. O dashboard detectará automaticamente a mudança")
    print("   3. Os dados serão atualizados na próxima requisição")

def show_usage():
    """Mostra como usar o sistema"""
    print("""
🚀 SISTEMA DE ATUALIZAÇÃO DINÂMICA DO DASHBOARD

📋 COMO FUNCIONA:
1. Backend processa arquivos TSV automaticamente
2. Frontend faz requisições a cada 5 minutos
3. Dados são atualizados em tempo real
4. Indicadores visuais mostram status

🔧 ENDPOINTS DISPONÍVEIS:
- GET /api/dashboard/health - Status da API
- GET /api/dashboard/data - Dados atualizados do dashboard

📁 ESTRUTURA DE DADOS:
- /static/tsv/dash - *.tsv → Dados contratados por canal
- /static/tsv/*.tsv → Dados de entrega diária

🔄 ATUALIZAÇÃO AUTOMÁTICA:
- Intervalo: 5 minutos
- Retry: 3 tentativas em caso de erro
- Notificações visuais no dashboard

💡 COMO ATUALIZAR DADOS:
1. Substitua arquivos TSV na pasta /static/tsv/
2. O sistema detectará automaticamente
3. Dashboard será atualizado na próxima sincronização

🎯 EXEMPLOS DE USO:
- python update-dashboard-example.py test    # Testar API
- python update-dashboard-example.py monitor # Monitorar atualizações
- python update-dashboard-example.py help    # Mostrar ajuda
""")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "test":
        success = test_dashboard_api()
        sys.exit(0 if success else 1)
        
    elif command == "monitor":
        if test_dashboard_api():
            monitor_dashboard_updates()
        else:
            sys.exit(1)
            
    elif command == "simulate":
        simulate_data_update()
        
    elif command == "help":
        show_usage()
        
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("   Use: python update-dashboard-example.py help")
        sys.exit(1)
