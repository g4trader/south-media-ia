#!/usr/bin/env python3
"""
Script para criar todas as tabelas necessárias no BigQuery
"""

import os
from google.cloud import bigquery

# Configurar credenciais
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ubuntu/upload/automatizar-452311-b122eb2aa628.json'

def setup_bigquery_tables():
    """Cria todas as tabelas necessárias no BigQuery"""
    
    client = bigquery.Client(project='automatizar-452311')
    dataset_id = 'south_media_dashboard'
    
    print("🔄 Configurando tabelas do BigQuery...")
    
    # Criar dataset se não existir
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} já existe")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"✅ Dataset {dataset_id} criado")
    
    # Definir esquemas das tabelas
    tables_schema = {
        'clients': [
            bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
        ],
        'campaigns': [
            bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("client_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("start_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("end_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("budget", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("contracted_impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("objective", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED")
        ],
        'strategies': [
            bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("budget", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("ctr", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpm", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED")
        ],
        'daily_performance': [
            bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED")
        ],
        'device_breakdown': [
            bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("device", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("percentage", "FLOAT", mode="REQUIRED")
        ]
    }
    
    # Criar cada tabela
    for table_name, schema in tables_schema.items():
        table_ref = dataset_ref.table(table_name)
        
        try:
            client.get_table(table_ref)
            print(f"✅ Tabela {table_name} já existe")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            print(f"✅ Tabela {table_name} criada")
    
    print("\n🎉 Todas as tabelas foram configuradas com sucesso!")

if __name__ == "__main__":
    setup_bigquery_tables()

