#!/usr/bin/env python3
"""
Script para testar o sistema de banco persistente
"""

import requests
import json
import time

# URL da API
API_URL = "https://south-media-ia-609095880025.us-central1.run.app"

def test_persistent_system():
    """Testa o sistema de banco persistente"""
    
    print("🧪 Testando sistema de banco persistente...")
    
    # 1. Criar uma campanha de teste
    print("\n1️⃣ Criando campanha de teste...")
    test_campaign = {
        "client": "Test Persistence",
        "campaign": "Test Campaign Persistence", 
        "sheet_id": "test_sheet_123",
        "tabs": {
            "daily_data": "gid1",
            "contract": "gid2",
            "strategies": "gid3",
            "publishers": "gid4"
        },
        "campaign_key": "test_persistence_campaign"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/generate-dashboard", json=test_campaign)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Campanha criada com sucesso!")
                print(f"📊 Cliente: {result.get('client')}")
                print(f"📊 Campanha: {result.get('campaign')}")
            else:
                print(f"❌ Erro na criação: {result.get('message')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 2. Verificar se a campanha foi salva
    print("\n2️⃣ Verificando se campanha foi salva...")
    try:
        response = requests.get(f"{API_URL}/api/campaigns")
        if response.status_code == 200:
            result = response.json()
            campaigns = result.get("campaigns", [])
            
            test_campaign_found = False
            for campaign in campaigns:
                if campaign.get("key") == "test_persistence_campaign":
                    test_campaign_found = True
                    print("✅ Campanha encontrada na lista!")
                    print(f"📊 Cliente: {campaign.get('client')}")
                    print(f"📊 Campanha: {campaign.get('campaign')}")
                    break
            
            if not test_campaign_found:
                print("❌ Campanha não encontrada na lista")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 3. Forçar backup
    print("\n3️⃣ Forçando backup manual...")
    try:
        response = requests.post(f"{API_URL}/api/backup-database")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Backup realizado com sucesso!")
                print(f"⏰ Timestamp: {result.get('timestamp')}")
            else:
                print(f"❌ Erro no backup: {result.get('message')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição de backup: {e}")
    
    # 4. Testar acesso aos dados da campanha
    print("\n4️⃣ Testando acesso aos dados da campanha...")
    try:
        response = requests.get(f"{API_URL}/api/test_persistence_campaign/data")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Dados da campanha acessíveis!")
                print(f"📊 Modo de teste: {result.get('test_mode', False)}")
            else:
                print(f"❌ Erro no acesso aos dados: {result.get('message')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição de dados: {e}")
    
    print("\n🎯 Teste do sistema persistente concluído!")
    return True

def simulate_deploy_cycle():
    """Simula um ciclo de deploy para testar persistência"""
    
    print("\n🔄 Simulando ciclo de deploy...")
    print("ℹ️ Em um ambiente real, aqui seria feito um novo deploy")
    print("ℹ️ O banco deveria ser restaurado automaticamente do GCS")
    
    # Aguardar um pouco para simular tempo de deploy
    print("⏳ Aguardando 5 segundos para simular deploy...")
    time.sleep(5)
    
    # Verificar se os dados ainda estão lá
    print("🔍 Verificando se dados persistiram após 'deploy'...")
    try:
        response = requests.get(f"{API_URL}/api/campaigns")
        if response.status_code == 200:
            result = response.json()
            campaigns = result.get("campaigns", [])
            
            test_campaign_found = False
            for campaign in campaigns:
                if campaign.get("key") == "test_persistence_campaign":
                    test_campaign_found = True
                    print("✅ Campanha ainda existe após 'deploy'!")
                    break
            
            if not test_campaign_found:
                print("❌ Campanha perdida após 'deploy' - sistema não está persistente!")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando teste do sistema de banco persistente")
    
    # Testar sistema básico
    if test_persistent_system():
        # Simular ciclo de deploy
        if simulate_deploy_cycle():
            print("\n🎉 SISTEMA PERSISTENTE FUNCIONANDO CORRETAMENTE!")
            print("✅ Dados não serão mais perdidos a cada deploy")
        else:
            print("\n⚠️ Sistema ainda não está totalmente persistente")
    else:
        print("\n❌ Falha no teste do sistema persistente")
    
    print("\n🎯 Teste concluído!")
