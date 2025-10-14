#!/usr/bin/env python3
"""
LIMPEZA E RECRIAÇÃO COMPLETA - PRODUÇÃO
"""

from google.cloud import bigquery
from google.cloud import firestore
import pandas as pd
import requests
import time

PROJECT_ID = "automatizar-452311"
DATASET_ID = "south_media_dashboards"  # PRODUÇÃO (sem sufixo)
PRODUCTION_URL = "https://gen-dashboard-ia-609095880025.us-central1.run.app"

def clean_everything():
    """Limpar TUDO de produção"""
    print("=" * 60)
    print("🧹 LIMPANDO PRODUÇÃO")
    print("=" * 60)
    
    # BigQuery
    bq_client = bigquery.Client(project=PROJECT_ID)
    try:
        bq_client.delete_dataset(f"{PROJECT_ID}.{DATASET_ID}", delete_contents=True, not_found_ok=True)
        print("✅ BigQuery dataset deletado")
    except Exception as e:
        print(f"⚠️  BigQuery: {e}")
    
    # Firestore
    db = firestore.Client(project=PROJECT_ID)
    
    for collection in ["campaigns", "dashboards"]:  # Produção sem sufixo
        batch = db.batch()
        count = 0
        total = 0
        
        for doc in db.collection(collection).stream():
            batch.delete(doc.reference)
            count += 1
            total += 1
            
            if count >= 500:
                batch.commit()
                batch = db.batch()
                count = 0
        
        if count > 0:
            batch.commit()
        
        print(f"✅ Firestore {collection}: {total} documentos deletados")

def create_infrastructure():
    """Criar dataset e tabelas"""
    print("\n📊 CRIANDO INFRAESTRUTURA...")
    
    bq_client = bigquery.Client(project=PROJECT_ID)
    
    # Dataset
    dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset.location = "US"
    bq_client.create_dataset(dataset, exists_ok=True)
    print("✅ Dataset criado")
    
    # Schema campaigns
    campaigns_schema = [
        bigquery.SchemaField("campaign_key", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("client", "STRING"),
        bigquery.SchemaField("campaign_name", "STRING"),
        bigquery.SchemaField("sheet_id", "STRING"),
        bigquery.SchemaField("channel", "STRING"),
        bigquery.SchemaField("kpi", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
    ]
    
    # Schema dashboards (COM file_path!)
    dashboards_schema = [
        bigquery.SchemaField("dashboard_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("campaign_key", "STRING"),
        bigquery.SchemaField("dashboard_name", "STRING"),
        bigquery.SchemaField("dashboard_url", "STRING"),
        bigquery.SchemaField("file_path", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
    ]
    
    # Criar tabelas
    table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.campaigns", schema=campaigns_schema)
    bq_client.create_table(table, exists_ok=True)
    print("✅ Tabela campaigns criada")
    
    table = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.dashboards", schema=dashboards_schema)
    bq_client.create_table(table, exists_ok=True)
    print("✅ Tabela dashboards criada")

def create_dashboards():
    """Criar dashboards do CSV"""
    print("\n📋 CRIANDO DASHBOARDS NA PRODUÇÃO...")
    
    df = pd.read_csv('dashboards.csv')
    print(f"   Total: {len(df)} dashboards\n")
    
    success = 0
    errors = []
    
    for index, row in df.iterrows():
        campaign_key = f"{row['cliente']}_{row['campanha']}".lower().replace(' ', '_').replace('-', '_')
        
        payload = {
            "campaign_key": campaign_key,
            "client": row['cliente'],
            "campaign_name": row['campanha'],
            "sheet_id": row['planilha'].split('/d/')[1].split('/')[0] if '/d/' in row['planilha'] else row['planilha'],
            "channel": row['canal'],
            "kpi": row['kpi'].upper()
        }
        
        try:
            response = requests.post(f"{PRODUCTION_URL}/api/generate-dashboard", json=payload, timeout=120)
            
            if response.status_code == 200 and response.json().get('success'):
                success += 1
                print(f"   [{success}/{len(df)}] ✅ {row['cliente']} - {row['campanha']}")
            else:
                error_msg = f"{row['cliente']} - {row['campanha']}: HTTP {response.status_code}"
                errors.append(error_msg)
                print(f"   [{index+1}/{len(df)}] ❌ {error_msg}")
        except Exception as e:
            error_msg = f"{row['cliente']} - {row['campanha']}: {str(e)[:50]}"
            errors.append(error_msg)
            print(f"   [{index+1}/{len(df)}] ❌ {error_msg}")
        
        time.sleep(1.5)  # Pausa maior para produção
    
    return success, errors

def verify():
    """Verificar resultado"""
    print("\n🔍 VERIFICANDO PRODUÇÃO...")
    
    db = firestore.Client(project=PROJECT_ID)
    bq_client = bigquery.Client(project=PROJECT_ID)
    
    campaigns_fs = len(list(db.collection("campaigns").stream()))
    dashboards_fs = len(list(db.collection("dashboards").stream()))
    
    campaigns_bq = list(bq_client.query(f"SELECT COUNT(*) as total FROM `{PROJECT_ID}.{DATASET_ID}.campaigns`").result())[0].total
    dashboards_bq = list(bq_client.query(f"SELECT COUNT(*) as total FROM `{PROJECT_ID}.{DATASET_ID}.dashboards`").result())[0].total
    
    print(f"\n📊 Firestore:")
    print(f"   • campaigns: {campaigns_fs}/31")
    print(f"   • dashboards: {dashboards_fs}/31")
    print(f"\n📊 BigQuery:")
    print(f"   • campaigns: {campaigns_bq}")
    print(f"   • dashboards: {dashboards_bq}")
    
    return dashboards_fs

def main():
    print("=" * 60)
    print("🚀 RECRIAÇÃO COMPLETA - PRODUÇÃO")
    print("=" * 60)
    print("\n⚠️  ATENÇÃO: Você está prestes a:")
    print("   1. Deletar TODOS os dados de PRODUÇÃO")
    print("   2. Recriar infraestrutura do zero")
    print("   3. Gerar 31 dashboards novamente")
    print("\n" + "=" * 60)
    
    clean_everything()
    create_infrastructure()
    success, errors = create_dashboards()
    total = verify()
    
    print("\n" + "=" * 60)
    if total == 31:
        print("✅ PRODUÇÃO RECRIADA COM SUCESSO!")
    else:
        print(f"⚠️  ATENÇÃO: {total}/31 dashboards criados")
        if errors:
            print(f"\n❌ Erros encontrados ({len(errors)}):")
            for err in errors[:5]:
                print(f"   - {err}")
    print("=" * 60)
    print(f"\n🌐 Verificar em: {PRODUCTION_URL}/dashboards-list")

if __name__ == "__main__":
    main()
