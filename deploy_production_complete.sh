#!/bin/bash

echo "🚀 DEPLOY COMPLETO PARA PRODUÇÃO"
echo "========================================"
echo ""
echo "⚠️  ATENÇÃO: Este script irá:"
echo "   1. Fazer backup dos dados atuais de produção"
echo "   2. Limpar dados de produção"
echo "   3. Fazer deploy do código atualizado"
echo "   4. Recriar todos os dashboards a partir do CSV"
echo ""
read -p "Deseja continuar? (sim/não): " confirm

if [ "$confirm" != "sim" ]; then
    echo "❌ Deploy cancelado pelo usuário"
    exit 1
fi

echo ""
echo "📊 PASSO 1: BACKUP DOS DADOS DE PRODUÇÃO"
echo "========================================"
python3 backup_production_data.py
if [ $? -ne 0 ]; then
    echo "❌ Erro ao fazer backup. Deploy cancelado por segurança."
    exit 1
fi

echo ""
echo "🧹 PASSO 2: LIMPANDO DADOS DE PRODUÇÃO"
echo "========================================"
echo "⚠️  Limpando BigQuery e Firestore de PRODUÇÃO..."

# Criar script de limpeza de produção
cat > clean_production_data.py << 'EOF'
#!/usr/bin/env python3

import os
from google.cloud import bigquery
from google.cloud import firestore

# Configurar para produção
os.environ['PROJECT_ID'] = 'automatizar-452311'
os.environ['ENVIRONMENT'] = 'production'

def main():
    try:
        print('🧹 LIMPANDO DADOS DE PRODUÇÃO')
        print('=' * 50)
        
        # Conectar aos serviços
        bq_client = bigquery.Client()
        firestore_client = firestore.Client()
        
        # Configurações de produção
        prod_dataset = 'south_media_dashboards'
        prod_campaigns_collection = 'campaigns'
        prod_dashboards_collection = 'dashboards'
        
        print(f'🎯 Limpando ambiente: PRODUCTION')
        print(f'📊 Dataset BigQuery: {prod_dataset}')
        print(f'📊 Coleções Firestore: {prod_campaigns_collection}, {prod_dashboards_collection}')
        
        # 1. LIMPAR BIGQUERY PRODUÇÃO
        print('\n📊 LIMPANDO BIGQUERY PRODUÇÃO...')
        
        tables_to_clear = ['campaigns', 'dashboards', 'metrics']
        
        for table in tables_to_clear:
            try:
                print(f'  🗑️ Limpando tabela: {table}')
                clear_query = f"DELETE FROM `automatizar-452311.{prod_dataset}.{table}` WHERE TRUE"
                result = bq_client.query(clear_query)
                result.result()  # Aguardar conclusão
                print(f'  ✅ Tabela {table} limpa')
            except Exception as e:
                print(f'  ⚠️ Tabela {table} não existe ou erro: {e}')
        
        # 2. LIMPAR FIRESTORE PRODUÇÃO
        print('\n📊 LIMPANDO FIRESTORE PRODUÇÃO...')
        
        collections_to_clear = [prod_campaigns_collection, prod_dashboards_collection]
        
        for collection_name in collections_to_clear:
            try:
                print(f'  🗑️ Limpando coleção: {collection_name}')
                collection = firestore_client.collection(collection_name)
                docs = collection.stream()
                
                deleted_count = 0
                for doc in docs:
                    doc.reference.delete()
                    deleted_count += 1
                
                print(f'  ✅ Coleção {collection_name} limpa ({deleted_count} documentos removidos)')
                
            except Exception as e:
                print(f'  ❌ Erro ao limpar coleção {collection_name}: {e}')
        
        print('\n🎉 LIMPEZA DE PRODUÇÃO CONCLUÍDA!')
        
    except Exception as e:
        print(f'❌ Erro na limpeza: {e}')
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
EOF

python3 clean_production_data.py
if [ $? -ne 0 ]; then
    echo "❌ Erro ao limpar dados. Deploy cancelado."
    exit 1
fi

echo ""
echo "🏗️  PASSO 3: FAZENDO DEPLOY DO CÓDIGO"
echo "========================================"
./deploy_gen_dashboard_ia.sh
if [ $? -ne 0 ]; then
    echo "❌ Erro no deploy. Verifique os logs."
    exit 1
fi

echo ""
echo "⏳ Aguardando serviço estabilizar (30 segundos)..."
sleep 30

echo ""
echo "📊 PASSO 4: RECRIANDO DASHBOARDS A PARTIR DO CSV"
echo "========================================"

# Criar script de automação para produção
cat > automate_production_dashboards.py << 'EOF'
#!/usr/bin/env python3

import csv
import time
import requests
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PRODUCTION_URL = "https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app"

def read_csv_data(csv_file="dashboards.csv"):
    """Ler dados do arquivo CSV"""
    try:
        dashboards = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Extrair ID da planilha da URL
                sheet_url = row['planilha']
                sheet_id = sheet_url.split('/d/')[1].split('/')[0] if '/d/' in sheet_url else sheet_url
                
                # Gerar campaign_key
                campaign_key = f"{row['cliente'].lower().replace(' ', '_')}_{row['campanha'].lower().replace(' ', '_').replace(' ', '_')}"
                campaign_key = ''.join(c for c in campaign_key if c.isalnum() or c in ['_', '-'])[:100]
                
                dashboard_data = {
                    'campaign_key': campaign_key,
                    'client': row['cliente'].strip(),
                    'campaign_name': row['campanha'].strip(),
                    'sheet_id': sheet_id,
                    'channel': row['canal'].strip(),
                    'kpi': row['kpi'].strip().upper()
                }
                dashboards.append(dashboard_data)
        
        logger.info(f"📊 {len(dashboards)} dashboards carregados do CSV")
        return dashboards
        
    except Exception as e:
        logger.error(f"❌ Erro ao ler CSV: {e}")
        return []

def generate_dashboard_via_api(dashboard_data):
    """Gerar dashboard via API"""
    try:
        logger.info(f"🚀 Gerando: {dashboard_data['client']} - {dashboard_data['campaign_name']}")
        
        response = requests.post(
            f"{PRODUCTION_URL}/api/generate-dashboard",
            json=dashboard_data,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"✅ Dashboard criado: {dashboard_data['campaign_key']}")
                return True, dashboard_data['campaign_key']
            else:
                logger.error(f"❌ Erro na API: {result.get('message', 'Erro desconhecido')}")
                return False, None
        else:
            logger.error(f"❌ Erro HTTP {response.status_code}")
            return False, None
                
    except Exception as e:
        logger.error(f"❌ Erro ao gerar dashboard: {e}")
        return False, None

def main():
    logger.info("🤖 CRIANDO DASHBOARDS EM PRODUÇÃO")
    logger.info("=" * 60)
    
    # Ler dados do CSV
    dashboards = read_csv_data()
    if not dashboards:
        logger.error("❌ Nenhum dashboard encontrado no CSV")
        return False
    
    # Estatísticas
    total = len(dashboards)
    success_count = 0
    failed_count = 0
    failed_dashboards = []
    
    logger.info(f"📊 Total de dashboards para criar: {total}")
    
    # Gerar cada dashboard
    for i, dashboard_data in enumerate(dashboards, 1):
        logger.info(f"\n🔄 [{i}/{total}] Processando...")
        
        success, campaign_key = generate_dashboard_via_api(dashboard_data)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            failed_dashboards.append(dashboard_data)
        
        # Pausa entre requests
        if i < total:
            time.sleep(2)
    
    # Relatório final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RELATÓRIO FINAL")
    logger.info("=" * 60)
    logger.info(f"✅ Dashboards criados com sucesso: {success_count}")
    logger.info(f"❌ Dashboards que falharam: {failed_count}")
    logger.info(f"📊 Taxa de sucesso: {(success_count/total)*100:.1f}%")
    
    if failed_dashboards:
        logger.info("\n❌ DASHBOARDS QUE FALHARAM:")
        for dashboard in failed_dashboards:
            logger.info(f"  - {dashboard['client']} - {dashboard['campaign_name']}")
    
    return success_count == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
EOF

python3 automate_production_dashboards.py
if [ $? -ne 0 ]; then
    echo "⚠️ Alguns dashboards falharam. Verifique os logs."
fi

echo ""
echo "✅ DEPLOY EM PRODUÇÃO CONCLUÍDO!"
echo "========================================"
echo ""
echo "🔗 URLs de Produção:"
echo "  🏠 Home: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/"
echo "  📋 Lista: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list"
echo "  🏥 Health: https://gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/health"
echo ""
echo "📊 Próximos passos:"
echo "  1. Verifique a listagem de dashboards"
echo "  2. Teste alguns dashboards aleatórios"
echo "  3. Confirme que os filtros estão funcionando"
echo ""

# Limpar scripts temporários
rm -f clean_production_data.py automate_production_dashboards.py

echo "🎉 Deploy completo finalizado!"

