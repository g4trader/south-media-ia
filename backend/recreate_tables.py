#!/usr/bin/env python3
"""
Script para recriar tabelas com schema correto e inserir dados únicos
"""

import os
from google.cloud import bigquery
from datetime import datetime, timedelta
import random

# Configurar credenciais
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ubuntu/upload/automatizar-452311-b122eb2aa628.json'

def recreate_tables_with_unique_data():
    """Recria tabelas e insere dados únicos"""
    
    client = bigquery.Client(project='automatizar-452311')
    dataset_id = 'south_media_dashboard'
    
    print("🔄 Recriando tabelas com dados únicos...")
    
    # Deletar tabelas existentes
    tables_to_delete = ['campaigns', 'strategies', 'daily_performance', 'device_breakdown']
    for table_name in tables_to_delete:
        try:
            table_ref = client.dataset(dataset_id).table(table_name)
            client.delete_table(table_ref)
            print(f"✅ Tabela {table_name} deletada")
        except:
            print(f"⚠️ Tabela {table_name} não existia")
    
    # Criar tabela campaigns
    campaigns_schema = [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("client_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("start_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("end_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("budget", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("contracted_impressions", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("objective", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED")
    ]
    
    campaigns_table = bigquery.Table(client.dataset(dataset_id).table('campaigns'), schema=campaigns_schema)
    client.create_table(campaigns_table)
    print("✅ Tabela campaigns criada")
    
    # Criar tabela strategies
    strategies_schema = [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("budget", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("ctr", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("cpm", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED")
    ]
    
    strategies_table = bigquery.Table(client.dataset(dataset_id).table('strategies'), schema=strategies_schema)
    client.create_table(strategies_table)
    print("✅ Tabela strategies criada")
    
    # Criar tabela daily_performance
    daily_schema = [
        bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED")
    ]
    
    daily_table = bigquery.Table(client.dataset(dataset_id).table('daily_performance'), schema=daily_schema)
    client.create_table(daily_table)
    print("✅ Tabela daily_performance criada")
    
    # Criar tabela device_breakdown
    device_schema = [
        bigquery.SchemaField("campaign_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("device", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("percentage", "FLOAT", mode="REQUIRED")
    ]
    
    device_table = bigquery.Table(client.dataset(dataset_id).table('device_breakdown'), schema=device_schema)
    client.create_table(device_table)
    print("✅ Tabela device_breakdown criada")
    
    # Inserir dados únicos das campanhas
    campaigns_data = [
        {
            'id': 1,
            'client_id': 1,  # TechCorp Brasil
            'name': 'Black Friday Tech 2024',
            'start_date': '2024-11-01',
            'end_date': '2024-11-30',
            'budget': 150000.00,
            'contracted_impressions': 35000000,
            'objective': 'Conversões e Vendas',
            'status': 'Ativa'
        },
        {
            'id': 2,
            'client_id': 1,  # TechCorp Brasil
            'name': 'Natal Tech 2024',
            'start_date': '2024-12-01',
            'end_date': '2024-12-31',
            'budget': 200000.00,
            'contracted_impressions': 50000000,
            'objective': 'Awareness e Alcance',
            'status': 'Ativa'
        },
        {
            'id': 3,
            'client_id': 2,  # EduSmart
            'name': 'Volta às Aulas 2025',
            'start_date': '2025-01-15',
            'end_date': '2025-02-28',
            'budget': 80000.00,
            'contracted_impressions': 20000000,
            'objective': 'Captação de Leads',
            'status': 'Ativa'
        },
        {
            'id': 4,
            'client_id': 2,  # EduSmart
            'name': 'Cursos Online Premium',
            'start_date': '2025-03-01',
            'end_date': '2025-04-30',
            'budget': 120000.00,
            'contracted_impressions': 30000000,
            'objective': 'Tráfego Qualificado',
            'status': 'Ativa'
        },
        {
            'id': 5,
            'client_id': 3,  # HealthPlus
            'name': 'Vida Saudável 2025',
            'start_date': '2025-01-01',
            'end_date': '2025-03-31',
            'budget': 180000.00,
            'contracted_impressions': 40000000,
            'objective': 'Engajamento e Interação',
            'status': 'Ativa'
        }
    ]
    
    # Inserir campanhas
    errors = client.insert_rows_json(campaigns_table, campaigns_data)
    if errors:
        print(f"❌ Erro ao inserir campanhas: {errors}")
    else:
        print("✅ Campanhas inseridas com dados únicos")
    
    # Estratégias únicas para cada campanha
    strategies_data = [
        # TechCorp - Black Friday Tech 2024 (Campanha 1) - R$ 150.000
        {'id': 1, 'campaign_id': 1, 'name': 'Display - E-commerce Tech', 'budget': 30000, 'impressions': 8500000, 'clicks': 25500, 'ctr': 0.30, 'cpm': 3.53, 'cpc': 1.18},
        {'id': 2, 'campaign_id': 1, 'name': 'Video - YouTube Tech', 'budget': 25000, 'impressions': 6200000, 'clicks': 18600, 'ctr': 0.30, 'cpm': 4.03, 'cpc': 1.34},
        {'id': 3, 'campaign_id': 1, 'name': 'Social - Facebook Tech', 'budget': 20000, 'impressions': 5800000, 'clicks': 23200, 'ctr': 0.40, 'cpm': 3.45, 'cpc': 0.86},
        {'id': 4, 'campaign_id': 1, 'name': 'Search - Google Ads Tech', 'budget': 35000, 'impressions': 4200000, 'clicks': 42000, 'ctr': 1.00, 'cpm': 8.33, 'cpc': 0.83},
        {'id': 5, 'campaign_id': 1, 'name': 'Retargeting - Tech Visitors', 'budget': 15000, 'impressions': 3100000, 'clicks': 24800, 'ctr': 0.80, 'cpm': 4.84, 'cpc': 0.60},
        {'id': 6, 'campaign_id': 1, 'name': 'Programmatic - Tech Audience', 'budget': 25000, 'impressions': 7200000, 'clicks': 14400, 'ctr': 0.20, 'cpm': 3.47, 'cpc': 1.74},
        
        # TechCorp - Natal Tech 2024 (Campanha 2) - R$ 200.000
        {'id': 7, 'campaign_id': 2, 'name': 'Display - Portais Natal', 'budget': 40000, 'impressions': 12000000, 'clicks': 36000, 'ctr': 0.30, 'cpm': 3.33, 'cpc': 1.11},
        {'id': 8, 'campaign_id': 2, 'name': 'Video - Christmas Campaign', 'budget': 35000, 'impressions': 8500000, 'clicks': 25500, 'ctr': 0.30, 'cpm': 4.12, 'cpc': 1.37},
        {'id': 9, 'campaign_id': 2, 'name': 'Social - Instagram Natal', 'budget': 30000, 'impressions': 9200000, 'clicks': 46000, 'ctr': 0.50, 'cpm': 3.26, 'cpc': 0.65},
        {'id': 10, 'campaign_id': 2, 'name': 'Search - Presentes Tech', 'budget': 45000, 'impressions': 6800000, 'clicks': 68000, 'ctr': 1.00, 'cpm': 6.62, 'cpc': 0.66},
        {'id': 11, 'campaign_id': 2, 'name': 'Retargeting - Christmas', 'budget': 25000, 'impressions': 5200000, 'clicks': 41600, 'ctr': 0.80, 'cpm': 4.81, 'cpc': 0.60},
        {'id': 12, 'campaign_id': 2, 'name': 'Programmatic - Holiday', 'budget': 25000, 'impressions': 8300000, 'clicks': 16600, 'ctr': 0.20, 'cpm': 3.01, 'cpc': 1.51},
        
        # EduSmart - Volta às Aulas 2025 (Campanha 3) - R$ 80.000
        {'id': 13, 'campaign_id': 3, 'name': 'Display - Portais Educação', 'budget': 15000, 'impressions': 4800000, 'clicks': 9600, 'ctr': 0.20, 'cpm': 3.13, 'cpc': 1.56},
        {'id': 14, 'campaign_id': 3, 'name': 'Video - Educacional', 'budget': 12000, 'impressions': 3200000, 'clicks': 6400, 'ctr': 0.20, 'cpm': 3.75, 'cpc': 1.88},
        {'id': 15, 'campaign_id': 3, 'name': 'Social - Facebook Edu', 'budget': 10000, 'impressions': 2800000, 'clicks': 8400, 'ctr': 0.30, 'cpm': 3.57, 'cpc': 1.19},
        {'id': 16, 'campaign_id': 3, 'name': 'Search - Cursos Online', 'budget': 18000, 'impressions': 2400000, 'clicks': 24000, 'ctr': 1.00, 'cpm': 7.50, 'cpc': 0.75},
        {'id': 17, 'campaign_id': 3, 'name': 'Retargeting - Estudantes', 'budget': 8000, 'impressions': 1600000, 'clicks': 12800, 'ctr': 0.80, 'cpm': 5.00, 'cpc': 0.63},
        {'id': 18, 'campaign_id': 3, 'name': 'Programmatic - Education', 'budget': 17000, 'impressions': 5200000, 'clicks': 10400, 'ctr': 0.20, 'cpm': 3.27, 'cpc': 1.63},
        
        # EduSmart - Cursos Online Premium (Campanha 4) - R$ 120.000
        {'id': 19, 'campaign_id': 4, 'name': 'Display - Premium Education', 'budget': 25000, 'impressions': 7500000, 'clicks': 15000, 'ctr': 0.20, 'cpm': 3.33, 'cpc': 1.67},
        {'id': 20, 'campaign_id': 4, 'name': 'Video - Premium Courses', 'budget': 20000, 'impressions': 5200000, 'clicks': 10400, 'ctr': 0.20, 'cpm': 3.85, 'cpc': 1.92},
        {'id': 21, 'campaign_id': 4, 'name': 'Social - LinkedIn Premium', 'budget': 18000, 'impressions': 4600000, 'clicks': 13800, 'ctr': 0.30, 'cpm': 3.91, 'cpc': 1.30},
        {'id': 22, 'campaign_id': 4, 'name': 'Search - Premium Learning', 'budget': 30000, 'impressions': 3800000, 'clicks': 38000, 'ctr': 1.00, 'cpm': 7.89, 'cpc': 0.79},
        {'id': 23, 'campaign_id': 4, 'name': 'Retargeting - Premium Users', 'budget': 12000, 'impressions': 2400000, 'clicks': 19200, 'ctr': 0.80, 'cpm': 5.00, 'cpc': 0.63},
        {'id': 24, 'campaign_id': 4, 'name': 'Programmatic - High Value', 'budget': 15000, 'impressions': 6500000, 'clicks': 13000, 'ctr': 0.20, 'cpm': 2.31, 'cpc': 1.15},
        
        # HealthPlus - Vida Saudável 2025 (Campanha 5) - R$ 180.000
        {'id': 25, 'campaign_id': 5, 'name': 'Display - Saúde e Bem-estar', 'budget': 35000, 'impressions': 10500000, 'clicks': 21000, 'ctr': 0.20, 'cpm': 3.33, 'cpc': 1.67},
        {'id': 26, 'campaign_id': 5, 'name': 'Video - Vida Saudável', 'budget': 30000, 'impressions': 7800000, 'clicks': 15600, 'ctr': 0.20, 'cpm': 3.85, 'cpc': 1.92},
        {'id': 27, 'campaign_id': 5, 'name': 'Social - Instagram Health', 'budget': 25000, 'impressions': 6200000, 'clicks': 18600, 'ctr': 0.30, 'cpm': 4.03, 'cpc': 1.34},
        {'id': 28, 'campaign_id': 5, 'name': 'Search - Saúde Online', 'budget': 40000, 'impressions': 5200000, 'clicks': 52000, 'ctr': 1.00, 'cpm': 7.69, 'cpc': 0.77},
        {'id': 29, 'campaign_id': 5, 'name': 'Retargeting - Health Visitors', 'budget': 20000, 'impressions': 3800000, 'clicks': 30400, 'ctr': 0.80, 'cpm': 5.26, 'cpc': 0.66},
        {'id': 30, 'campaign_id': 5, 'name': 'Programmatic - Wellness', 'budget': 30000, 'impressions': 6500000, 'clicks': 13000, 'ctr': 0.20, 'cpm': 4.62, 'cpc': 2.31}
    ]
    
    # Inserir estratégias
    errors = client.insert_rows_json(strategies_table, strategies_data)
    if errors:
        print(f"❌ Erro ao inserir estratégias: {errors}")
    else:
        print("✅ Estratégias inseridas com dados únicos")
    
    print("\n🎉 DADOS ÚNICOS CRIADOS COM SUCESSO!")
    print("\n📊 RESUMO DAS CAMPANHAS:")
    print("1. TechCorp - Black Friday Tech 2024: R$ 150.000, 35M impressões")
    print("2. TechCorp - Natal Tech 2024: R$ 200.000, 50M impressões")
    print("3. EduSmart - Volta às Aulas 2025: R$ 80.000, 20M impressões")
    print("4. EduSmart - Cursos Online Premium: R$ 120.000, 30M impressões")
    print("5. HealthPlus - Vida Saudável 2025: R$ 180.000, 40M impressões")
    print("\n✅ Cada campanha agora tem números completamente únicos!")

if __name__ == "__main__":
    recreate_tables_with_unique_data()

