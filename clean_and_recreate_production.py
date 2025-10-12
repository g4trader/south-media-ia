#!/usr/bin/env python3

import os
import csv
import time
import requests
from google.cloud import bigquery, firestore
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar para produção
os.environ['PROJECT_ID'] = 'automatizar-452311'
os.environ['ENVIRONMENT'] = 'production'

PRODUCTION_URL = "https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app"

def clean_production():
    """Limpar todos os dados de produção"""
    try:
        logger.info("🧹 LIMPANDO DADOS DE PRODUÇÃO")
        logger.info("=" * 60)
        
        bq_client = bigquery.Client()
        firestore_client = firestore.Client()
        
        # Configurações de produção
        prod_dataset = 'south_media_dashboards'
        prod_campaigns_collection = 'campaigns'
        prod_dashboards_collection = 'dashboards'
        
        # 1. LIMPAR BIGQUERY
        logger.info('\n📊 LIMPANDO BIGQUERY...')
        tables = ['campaigns', 'dashboards', 'metrics']
        
        for table in tables:
            try:
                logger.info(f'  🗑️ Limpando: {table}')
                query = f"DELETE FROM `automatizar-452311.{prod_dataset}.{table}` WHERE TRUE"
                bq_client.query(query).result()
                logger.info(f'  ✅ Tabela {table} limpa')
            except Exception as e:
                logger.warning(f'  ⚠️ Erro em {table}: {e}')
        
        # 2. LIMPAR FIRESTORE
        logger.info('\n📊 LIMPANDO FIRESTORE...')
        
        for collection_name in [prod_campaigns_collection, prod_dashboards_collection]:
            try:
                logger.info(f'  🗑️ Limpando: {collection_name}')
                collection = firestore_client.collection(collection_name)
                docs = list(collection.stream())
                
                deleted_count = 0
                for doc in docs:
                    doc.reference.delete()
                    deleted_count += 1
                
                logger.info(f'  ✅ Coleção {collection_name} limpa ({deleted_count} documentos)')
                
            except Exception as e:
                logger.error(f'  ❌ Erro em {collection_name}: {e}')
        
        logger.info('\n✅ LIMPEZA CONCLUÍDA!')
        return True
        
    except Exception as e:
        logger.error(f'❌ Erro na limpeza: {e}')
        return False

def read_csv_data():
    """Ler dados do CSV"""
    try:
        dashboards = []
        with open('dashboards.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sheet_url = row['planilha']
                sheet_id = sheet_url.split('/d/')[1].split('/')[0] if '/d/' in sheet_url else sheet_url
                
                campaign_key = f"{row['cliente'].lower().replace(' ', '_')}_{row['campanha'].lower().replace(' ', '_')}"
                campaign_key = ''.join(c for c in campaign_key if c.isalnum() or c in ['_', '-'])[:100]
                
                dashboards.append({
                    'campaign_key': campaign_key,
                    'client': row['cliente'].strip(),
                    'campaign_name': row['campanha'].strip(),
                    'sheet_id': sheet_id,
                    'channel': row['canal'].strip(),
                    'kpi': row['kpi'].strip().upper()
                })
        
        logger.info(f"📊 {len(dashboards)} dashboards carregados do CSV")
        return dashboards
        
    except Exception as e:
        logger.error(f"❌ Erro ao ler CSV: {e}")
        return []

def generate_dashboard(dashboard_data):
    """Gerar dashboard via API"""
    try:
        response = requests.post(
            f"{PRODUCTION_URL}/api/generate-dashboard",
            json=dashboard_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True
        return False
                
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def main():
    logger.info("🔄 LIMPEZA E RECRIAÇÃO COMPLETA DE PRODUÇÃO")
    logger.info("=" * 60)
    
    # 1. LIMPAR DADOS
    if not clean_production():
        logger.error("❌ Erro na limpeza. Abortando.")
        return
    
    logger.info("\n⏳ Aguardando 5 segundos...")
    time.sleep(5)
    
    # 2. LER CSV
    logger.info("\n📋 LENDO CSV...")
    dashboards = read_csv_data()
    
    if not dashboards:
        logger.error("❌ CSV vazio. Abortando.")
        return
    
    # 3. RECRIAR DASHBOARDS
    logger.info(f"\n🚀 RECRIANDO {len(dashboards)} DASHBOARDS...")
    logger.info("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, dashboard in enumerate(dashboards, 1):
        logger.info(f"\n🔄 [{i}/{len(dashboards)}] {dashboard['client']} - {dashboard['campaign_name']}")
        
        if generate_dashboard(dashboard):
            logger.info(f"  ✅ Criado: {dashboard['campaign_key']}")
            success_count += 1
        else:
            logger.error(f"  ❌ Falhou: {dashboard['campaign_key']}")
            failed_count += 1
        
        if i < len(dashboards):
            time.sleep(2)
    
    # 4. RELATÓRIO
    logger.info("\n" + "=" * 60)
    logger.info("📊 RELATÓRIO FINAL")
    logger.info("=" * 60)
    logger.info(f"✅ Dashboards criados: {success_count}")
    logger.info(f"❌ Falhas: {failed_count}")
    logger.info(f"📊 Taxa de sucesso: {(success_count/len(dashboards))*100:.1f}%")
    
    logger.info("\n🔗 Acesse: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list")

if __name__ == '__main__':
    main()
