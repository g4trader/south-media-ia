#!/usr/bin/env python3

import requests
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ENVIRONMENTS = {
    'PRODUÇÃO': 'https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app',
    'STAGING': 'https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app',
    'HML': 'https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app'
}

def check_environment(name, url):
    """Verificar status de um ambiente"""
    try:
        logger.info(f"\n📊 {name}")
        logger.info("-" * 60)
        
        # Verificar persistência
        response = requests.get(f"{url}/persistence-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('persistence_status', {})
            
            logger.info(f"  ✅ BigQuery: {'Disponível' if status.get('bigquery_available') else 'Indisponível'}")
            logger.info(f"  ✅ Firestore: {'Disponível' if status.get('firestore_available') else 'Indisponível'}")
            logger.info(f"  📋 Campanhas: {status.get('campaigns_count', 0)}")
            logger.info(f"  📊 Dashboards: {status.get('dashboards_count', 0)}")
            logger.info(f"  📦 Tamanho: {status.get('total_size_bytes', 0)} bytes")
            logger.info(f"  🔗 Lista: {url}/dashboards-list")
            
            return True
        else:
            logger.error(f"  ❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Erro: {e}")
        return False

def main():
    logger.info("🔍 VERIFICAÇÃO DE TODOS OS AMBIENTES")
    logger.info("=" * 60)
    
    results = {}
    
    for name, url in ENVIRONMENTS.items():
        results[name] = check_environment(name, url)
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO GERAL")
    logger.info("=" * 60)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        logger.info(f"{icon} {name}: {'OK' if status else 'ERRO'}")
    
    logger.info("\n🎉 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == '__main__':
    main()
