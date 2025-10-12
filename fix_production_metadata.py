#!/usr/bin/env python3

import csv
import os
from google.cloud import firestore
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar para produção
os.environ['PROJECT_ID'] = 'automatizar-452311'
os.environ['ENVIRONMENT'] = 'production'

def read_csv_data(csv_file="dashboards.csv"):
    """Ler dados do arquivo CSV"""
    try:
        dashboards = {}
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Gerar campaign_key do mesmo jeito que a automação fez
                campaign_key = f"{row['cliente'].lower().replace(' ', '_')}_{row['campanha'].lower().replace(' ', '_').replace(' ', '_')}"
                campaign_key = ''.join(c for c in campaign_key if c.isalnum() or c in ['_', '-'])[:100]
                
                dashboards[campaign_key] = {
                    'client': row['cliente'].strip(),
                    'campaign_name': row['campanha'].strip(),
                    'channel': row['canal'].strip(),
                    'kpi': row['kpi'].strip().upper()
                }
        
        logger.info(f"📊 {len(dashboards)} dashboards carregados do CSV")
        return dashboards
        
    except Exception as e:
        logger.error(f"❌ Erro ao ler CSV: {e}")
        return {}

def main():
    try:
        logger.info("🔧 CORRIGINDO METADADOS DE PRODUÇÃO")
        logger.info("=" * 60)
        
        # Conectar ao Firestore
        firestore_client = firestore.Client()
        prod_dashboards_collection = 'dashboards'
        
        # Ler dados do CSV
        csv_data = read_csv_data()
        
        if not csv_data:
            logger.error("❌ Nenhum dado encontrado no CSV")
            return
        
        # Buscar todos os dashboards de produção
        docs = firestore_client.collection(prod_dashboards_collection).stream()
        
        updated_count = 0
        not_found_count = 0
        
        for doc in docs:
            data = doc.to_dict()
            campaign_key = doc.id
            created_at = str(data.get('created_at', ''))
            
            # Apenas atualizar dashboards criados hoje
            if '2025-10-11' in created_at:
                # Buscar metadados no CSV
                if campaign_key in csv_data:
                    csv_metadata = csv_data[campaign_key]
                    
                    # Atualizar documento
                    doc.reference.update({
                        'client': csv_metadata['client'],
                        'campaign_name': csv_metadata['campaign_name'],
                        'channel': csv_metadata['channel'],
                        'kpi': csv_metadata['kpi'],
                        'updated_at': datetime.now()
                    })
                    
                    logger.info(f"✅ Atualizado: {campaign_key}")
                    updated_count += 1
                else:
                    logger.warning(f"⚠️ Não encontrado no CSV: {campaign_key}")
                    not_found_count += 1
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 60)
        logger.info(f"✅ Dashboards atualizados: {updated_count}")
        logger.info(f"⚠️ Dashboards não encontrados: {not_found_count}")
        
        if updated_count > 0:
            logger.info("\n🎉 METADADOS DE PRODUÇÃO CORRIGIDOS!")
            logger.info("🔗 Verifique: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
