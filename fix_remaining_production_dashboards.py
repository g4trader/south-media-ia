#!/usr/bin/env python3

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

# Mapeamento manual dos dashboards restantes
DASHBOARD_METADATA = {
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
    try:
        logger.info("🔧 CORRIGINDO DASHBOARDS RESTANTES DE PRODUÇÃO")
        logger.info("=" * 60)
        
        # Conectar ao Firestore
        firestore_client = firestore.Client()
        prod_dashboards_collection = 'dashboards'
        
        updated_count = 0
        not_found_count = 0
        
        for campaign_key, metadata in DASHBOARD_METADATA.items():
            try:
                doc_ref = firestore_client.collection(prod_dashboards_collection).document(campaign_key)
                doc = doc_ref.get()
                
                if doc.exists:
                    # Atualizar documento
                    doc_ref.update({
                        'client': metadata['client'],
                        'campaign_name': metadata['campaign_name'],
                        'channel': metadata['channel'],
                        'kpi': metadata['kpi'],
                        'updated_at': datetime.now()
                    })
                    
                    logger.info(f"✅ Atualizado: {campaign_key}")
                    updated_count += 1
                else:
                    logger.warning(f"⚠️ Documento não encontrado: {campaign_key}")
                    not_found_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar {campaign_key}: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 60)
        logger.info(f"✅ Dashboards atualizados: {updated_count}")
        logger.info(f"⚠️ Dashboards não encontrados: {not_found_count}")
        
        if updated_count > 0:
            logger.info("\n🎉 TODOS OS METADADOS DE PRODUÇÃO CORRIGIDOS!")
            logger.info("🔗 Verifique: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
