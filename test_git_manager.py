#!/usr/bin/env python3
"""
Teste do Git Manager Microservice
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL do microserviço (ajustar conforme necessário)
# BASE_URL = "http://localhost:8080"  # Para teste local
BASE_URL = "https://git-manager-609095880025.us-central1.run.app"  # Para teste em produção

def test_health():
    """Teste 1: Health Check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Health check passou")
            return True
        else:
            logger.error(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        return False

def test_status():
    """Teste 2: Status do Git Manager"""
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Status obtido: {data}")
            return True
        else:
            logger.error(f"❌ Status falhou: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no status: {e}")
        return False

def test_process():
    """Teste 3: Processar arquivos"""
    try:
        response = requests.post(f"{BASE_URL}/process", timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Processamento concluído: {data}")
            return True
        else:
            logger.error(f"❌ Processamento falhou: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}")
        return False

def test_force_commit():
    """Teste 4: Forçar commit"""
    try:
        response = requests.post(f"{BASE_URL}/force-commit", 
                               json={"pattern": "dash_*.html"}, 
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Force commit concluído: {data}")
            return True
        else:
            logger.error(f"❌ Force commit falhou: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no force commit: {e}")
        return False

def run_all_tests():
    """Executar todos os testes"""
    logger.info("🧪 Iniciando testes do Git Manager Microservice")
    logger.info(f"🌐 URL Base: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Status", test_status),
        ("Process Files", test_process),
        ("Force Commit", test_force_commit),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"🧪 Executando: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logger.info(f"✅ {test_name} passou")
            else:
                logger.error(f"❌ {test_name} falhou")
        except Exception as e:
            logger.error(f"❌ {test_name} erro: {e}")
            results[test_name] = False
        
        time.sleep(2)  # Pausa entre testes
    
    # Relatório final
    logger.info("\n" + "="*60)
    logger.info("📊 RELATÓRIO FINAL - TESTES GIT MANAGER")
    logger.info("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    logger.info(f"📈 Total de Testes: {total}")
    logger.info(f"✅ Testes Passaram: {passed}")
    logger.info(f"❌ Testes Falharam: {total - passed}")
    logger.info(f"📊 Taxa de Sucesso: {passed / total * 100:.1f}%")
    
    logger.info("\n📋 DETALHES DOS TESTES:")
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        logger.info(f"  {status} {test_name}")
    
    if passed == total:
        logger.info("\n🎉 Todos os testes passaram com sucesso!")
    else:
        logger.info(f"\n⚠️ {total - passed} teste(s) falharam.")
    
    logger.info("="*60)

if __name__ == "__main__":
    run_all_tests()
