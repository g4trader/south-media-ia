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

# Configurar para HML
os.environ['PROJECT_ID'] = 'automatizar-452311'
os.environ['ENVIRONMENT'] = 'hml'

HML_URL = "https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app"

def clean_hml():
    """Limpar todos os dados de HML"""
    try:
        logger.info("🧹 LIMPANDO DADOS DE HML")
        logger.info("=" * 60)
        
        bq_client = bigquery.Client()
        firestore_client = firestore.Client()
        
        # Configurações de HML
        hml_dataset = 'south_media_dashboards_hml'
        hml_campaigns_collection = 'campaigns_hml'
        hml_dashboards_collection = 'dashboards_hml'
        
        # 1. LIMPAR BIGQUERY
        logger.info('\n📊 LIMPANDO BIGQUERY HML...')
        tables = ['campaigns', 'dashboards', 'metrics']
        
        for table in tables:
            try:
                logger.info(f'  🗑️ Limpando: {table}')
                query = f"DELETE FROM `automatizar-452311.{hml_dataset}.{table}` WHERE TRUE"
                bq_client.query(query).result()
                logger.info(f'  ✅ Tabela {table} limpa')
            except Exception as e:
                logger.warning(f'  ⚠️ Erro em {table}: {e}')
        
        # 2. LIMPAR FIRESTORE
        logger.info('\n📊 LIMPANDO FIRESTORE HML...')
        
        for collection_name in [hml_campaigns_collection, hml_dashboards_collection]:
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
            f"{HML_URL}/api/generate-dashboard",
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

def fix_metadata(campaign_key, metadata):
    """Corrigir metadados de um dashboard"""
    try:
        firestore_client = firestore.Client()
        hml_dashboards_collection = 'dashboards_hml'
        
        doc_ref = firestore_client.collection(hml_dashboards_collection).document(campaign_key)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.update({
                'client': metadata['client'],
                'campaign_name': metadata['campaign_name'],
                'channel': metadata['channel'],
                'kpi': metadata['kpi'],
                'updated_at': datetime.now()
            })
            return True
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar {campaign_key}: {e}")
        return False

# Mapeamento manual dos dashboards com caracteres especiais
MANUAL_FIXES = {
    'senai_linkedin_sponsored_display': {
        'client': 'senai',
        'campaign_name': 'Linkedin Sponsored - display',
        'channel': 'linkedin',
        'kpi': 'CPM'
    },
    'senai_linkedin_sponsored_video': {
        'client': 'senai',
        'campaign_name': 'Linkedin Sponsored - vídeo',
        'channel': 'linkedin',
        'kpi': 'CPM'
    },
    'copacol_campanha_institucional_de_video_de_30s_em_youtube': {
        'client': 'copacol',
        'campaign_name': 'Campanha Institucional de Video de 30s em Youtube',
        'channel': 'youtube',
        'kpi': 'CPV'
    },
    'copacol_campanha_institucional_de_video_de_90s_em_youtube': {
        'client': 'copacol',
        'campaign_name': 'Campanha Institucional de Video de 90s em Youtube',
        'channel': 'youtube',
        'kpi': 'CPM'
    },
    'copacol_institucional_30s_programatica': {
        'client': 'copacol',
        'campaign_name': 'Institucional 30s programática',
        'channel': 'video programatico',
        'kpi': 'CPV'
    },
    'copacol_institucional_remarketing_programatica': {
        'client': 'copacol',
        'campaign_name': 'Institucional REMARKETING Programática',
        'channel': 'video programatico',
        'kpi': 'CPM'
    },
    'copacol_outubro_rosa_programatica': {
        'client': 'copacol',
        'campaign_name': 'Outubro rosa programática',
        'channel': 'Video programática',
        'kpi': 'CPV'
    },
    'copacol_semana_do_pescado_programatica': {
        'client': 'copacol',
        'campaign_name': 'Semana do pescado programática',
        'channel': 'video programático',
        'kpi': 'CPV'
    },
    'sebrae_pr_feira_do_empreendedor_programatica': {
        'client': 'sebrae pr',
        'campaign_name': 'Feira do Empreendedor Programática',
        'channel': 'video programático',
        'kpi': 'CPV'
    },
    'senai_geofence_display': {
        'client': 'Senai',
        'campaign_name': 'Geofence - display',
        'channel': 'Geofence',
        'kpi': 'CPM'
    },
    'unimed_programatica_display': {
        'client': 'unimed',
        'campaign_name': 'Programática display',
        'channel': 'Display programática',
        'kpi': 'CPM'
    },
    'sonho_sabao_em_po': {
        'client': 'sonho',
        'campaign_name': 'Sabão em pó',
        'channel': 'Tiktok',
        'kpi': 'CPM'
    },
    'sonho_sabao_em_po_yt': {
        'client': 'sonho',
        'campaign_name': 'Sabão em pó YT',
        'channel': 'Youtube',
        'kpi': 'CPV'
    },
    'sonho_sabao_em_po_netflix': {
        'client': 'sonho',
        'campaign_name': 'Sabão em pó NetFlix',
        'channel': 'Netflix',
        'kpi': 'CPV'
    },
    'sonho_sabao_em_po_disney': {
        'client': 'sonho',
        'campaign_name': 'Sabão em pó Disney',
        'channel': 'Disney',
        'kpi': 'CPV'
    },
    'sonho_sabao_em_po_ctv': {
        'client': 'sonho',
        'campaign_name': 'Sabão em pó CTV',
        'channel': 'Video programática',
        'kpi': 'CPV'
    }
}

def main():
    logger.info("🔄 LIMPEZA E RECRIAÇÃO COMPLETA DE HML")
    logger.info("=" * 60)
    
    # 1. LIMPAR DADOS
    if not clean_hml():
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
    
    # 4. CORRIGIR METADADOS
    logger.info("\n🔧 CORRIGINDO METADADOS...")
    logger.info("=" * 60)
    
    fixed_count = 0
    for campaign_key, metadata in MANUAL_FIXES.items():
        if fix_metadata(campaign_key, metadata):
            logger.info(f"  ✅ Corrigido: {campaign_key}")
            fixed_count += 1
    
    # 5. RELATÓRIO
    logger.info("\n" + "=" * 60)
    logger.info("📊 RELATÓRIO FINAL")
    logger.info("=" * 60)
    logger.info(f"✅ Dashboards criados: {success_count}")
    logger.info(f"❌ Falhas: {failed_count}")
    logger.info(f"🔧 Metadados corrigidos: {fixed_count}")
    logger.info(f"📊 Taxa de sucesso: {(success_count/len(dashboards))*100:.1f}%")
    
    logger.info("\n🔗 Acesse: https://hml-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list")

if __name__ == '__main__':
    main()
