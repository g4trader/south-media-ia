#!/usr/bin/env python3

import os
import json
from datetime import datetime
from google.cloud import bigquery
from google.cloud import firestore

# Configurar para produção
os.environ['PROJECT_ID'] = 'automatizar-452311'

def main():
    try:
        print('💾 FAZENDO BACKUP COMPLETO DOS DADOS DE PRODUÇÃO')
        print('=' * 60)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'production_backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)
        
        print(f'📁 Diretório de backup: {backup_dir}')
        
        # Conectar aos serviços
        bq_client = bigquery.Client()
        firestore_client = firestore.Client()
        
        # 1. BACKUP BIGQUERY
        print('\\n📊 BACKUP BIGQUERY...')
        
        # Dataset principal de produção
        datasets_to_backup = [
            'south_media_dashboards',  # Dataset principal
            'south_media_ia',          # Dataset com campaigns_v2 (37 campanhas originais)
            'south_media_dashboards_staging'  # Dataset com 47 dashboards (backup)
        ]
        
        for dataset_id in datasets_to_backup:
            print(f'\\n📁 Backup dataset: {dataset_id}')
            
            try:
                # Listar tabelas
                tables = list(bq_client.list_tables(dataset_id))
                
                for table in tables:
                    table_id = table.table_id
                    print(f'  📋 Backup tabela: {table_id}')
                    
                    # Exportar dados
                    query = f"SELECT * FROM `automatizar-452311.{dataset_id}.{table_id}`"
                    results = list(bq_client.query(query))
                    
                    # Converter para JSON serializable
                    data = []
                    for row in results:
                        row_dict = {}
                        for key, value in row.items():
                            if hasattr(value, 'isoformat'):  # datetime objects
                                row_dict[key] = value.isoformat()
                            else:
                                row_dict[key] = value
                        data.append(row_dict)
                    
                    # Salvar arquivo
                    filename = f'{backup_dir}/bq_{dataset_id}_{table_id}.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f'    ✅ {len(data)} registros salvos em {filename}')
                    
            except Exception as e:
                print(f'    ❌ Erro no dataset {dataset_id}: {e}')
        
        # 2. BACKUP FIRESTORE
        print('\\n📊 BACKUP FIRESTORE...')
        
        # Coleções principais
        collections_to_backup = [
            'campaigns',
            'dashboards',
            'campaigns_staging',
            'dashboards_staging',
            'campaigns_hml',
            'dashboards_hml'
        ]
        
        for collection_name in collections_to_backup:
            print(f'\\n📁 Backup coleção: {collection_name}')
            
            try:
                collection = firestore_client.collection(collection_name)
                docs = collection.stream()
                
                data = []
                doc_count = 0
                
                for doc in docs:
                    doc_count += 1
                    doc_data = doc.to_dict()
                    doc_data['_document_id'] = doc.id
                    
                    # Converter timestamps
                    for key, value in doc_data.items():
                        if hasattr(value, 'timestamp'):  # Firestore timestamp
                            doc_data[key] = value.timestamp()
                        elif hasattr(value, 'isoformat'):  # datetime objects
                            doc_data[key] = value.isoformat()
                    
                    data.append(doc_data)
                
                # Salvar arquivo
                filename = f'{backup_dir}/fs_{collection_name}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f'  ✅ {doc_count} documentos salvos em {filename}')
                
            except Exception as e:
                print(f'  ❌ Erro na coleção {collection_name}: {e}')
        
        # 3. BACKUP METADADOS
        print('\\n📊 BACKUP METADADOS...')
        
        metadata = {
            'backup_timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'project_id': 'automatizar-452311',
            'version': 'production_v23',
            'datasets_backed_up': datasets_to_backup,
            'collections_backed_up': collections_to_backup,
            'summary': {
                'bigquery_datasets': len(datasets_to_backup),
                'firestore_collections': len(collections_to_backup)
            }
        }
        
        # Salvar metadados
        filename = f'{backup_dir}/backup_metadata.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f'✅ Metadados salvos em {filename}')
        
        # 4. RESUMO FINAL
        print('\\n🎉 BACKUP CONCLUÍDO!')
        print('=' * 60)
        print(f'📁 Diretório: {backup_dir}')
        print(f'📊 Datasets BigQuery: {len(datasets_to_backup)}')
        print(f'📊 Coleções Firestore: {len(collections_to_backup)}')
        print(f'⏰ Timestamp: {timestamp}')
        
        # Listar arquivos criados
        files = os.listdir(backup_dir)
        print(f'\\n📋 Arquivos criados ({len(files)}):')
        for file in sorted(files):
            file_path = os.path.join(backup_dir, file)
            size = os.path.getsize(file_path)
            print(f'  📄 {file} ({size:,} bytes)')
        
        print(f'\\n✅ BACKUP SEGURO PARA DEPLOY!')
        
    except Exception as e:
        print(f'❌ Erro no backup: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
