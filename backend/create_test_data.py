#!/usr/bin/env python3
"""
Script para criar dados de teste no BigQuery para múltiplos clientes e campanhas
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
from datetime import datetime, timedelta
import random

class TestDataCreator:
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'automatizar-452311')
        self.dataset_id = 'south_media_dashboard'
        
        # Initialize BigQuery client
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(credentials=credentials, project=self.project_id)
        else:
            print("Error: BigQuery credentials not found!")
            return
    
    def create_dataset_and_tables(self):
        """Create dataset and tables if they don't exist"""
        try:
            # Create dataset
            dataset_id = f"{self.project_id}.{self.dataset_id}"
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            
            try:
                dataset = self.client.create_dataset(dataset, timeout=30)
                print(f"Created dataset {dataset.dataset_id}")
            except Exception as e:
                if "Already Exists" in str(e):
                    print(f"Dataset {dataset.dataset_id} already exists")
                else:
                    raise e
            
            # Create tables
            self._create_clients_table()
            self._create_campaigns_table()
            self._create_strategies_table()
            self._create_device_breakdown_table()
            self._create_performance_history_table()
            
        except Exception as e:
            print(f"Error creating dataset and tables: {e}")
    
    def _create_clients_table(self):
        """Create clients table"""
        table_id = f"{self.project_id}.{self.dataset_id}.clients"
        
        schema = [
            bigquery.SchemaField("client_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("client_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("contact_email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.table_id}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table clients already exists")
            else:
                raise e
    
    def _create_campaigns_table(self):
        """Create campaigns table"""
        table_id = f"{self.project_id}.{self.dataset_id}.campaigns"
        
        schema = [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("client_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("campaign_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("budget_contracted", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("budget_used", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("impressions_contracted", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("impressions_delivered", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("cpm", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("ctr", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("objective", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date_start", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("date_end", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.table_id}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table campaigns already exists")
            else:
                raise e
    
    def _create_strategies_table(self):
        """Create strategies table"""
        table_id = f"{self.project_id}.{self.dataset_id}.strategies"
        
        schema = [
            bigquery.SchemaField("strategy_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("strategy_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("budget_used", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("ctr", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpm", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.table_id}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table strategies already exists")
            else:
                raise e
    
    def _create_device_breakdown_table(self):
        """Create device breakdown table"""
        table_id = f"{self.project_id}.{self.dataset_id}.device_breakdown"
        
        schema = [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("device_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("percentage", "FLOAT", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.table_id}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table device_breakdown already exists")
            else:
                raise e
    
    def _create_performance_history_table(self):
        """Create performance history table for charts"""
        table_id = f"{self.project_id}.{self.dataset_id}.performance_history"
        
        schema = [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("cpc", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("cpm", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("ctr", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("impressions", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("clicks", "INTEGER", mode="REQUIRED"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.table_id}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table performance_history already exists")
            else:
                raise e
    
    def insert_test_data(self):
        """Insert test data for multiple clients and campaigns"""
        try:
            # Clear existing data
            self._clear_existing_data()
            
            # Insert clients
            clients_data = self._generate_clients_data()
            self._insert_clients(clients_data)
            
            # Insert campaigns for each client
            for client in clients_data:
                campaigns_data = self._generate_campaigns_data(client['client_id'])
                self._insert_campaigns(campaigns_data)
                
                # Insert strategies and device breakdown for each campaign
                for campaign in campaigns_data:
                    strategies_data = self._generate_strategies_data(campaign['campaign_id'])
                    self._insert_strategies(strategies_data)
                    
                    device_data = self._generate_device_breakdown_data(campaign['campaign_id'])
                    self._insert_device_breakdown(device_data)
                    
                    performance_data = self._generate_performance_history_data(campaign['campaign_id'], campaign['date_start'], campaign['date_end'])
                    self._insert_performance_history(performance_data)
            
            print("✅ Test data inserted successfully!")
            
        except Exception as e:
            print(f"Error inserting test data: {e}")
    
    def _clear_existing_data(self):
        """Clear existing test data"""
        tables = ['performance_history', 'device_breakdown', 'strategies', 'campaigns', 'clients']
        
        for table in tables:
            query = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table}` WHERE TRUE"
            try:
                job = self.client.query(query)
                job.result()
                print(f"Cleared table {table}")
            except Exception as e:
                print(f"Error clearing table {table}: {e}")
    
    def _generate_clients_data(self):
        """Generate test clients data"""
        return [
            {
                'client_id': 'client_001',
                'client_name': 'TechCorp Brasil',
                'company': 'TechCorp Ltda',
                'contact_email': 'contato@techcorp.com.br',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            },
            {
                'client_id': 'client_002',
                'client_name': 'EduSmart',
                'company': 'EduSmart Educação',
                'contact_email': 'marketing@edusmart.com.br',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            },
            {
                'client_id': 'client_003',
                'client_name': 'HealthPlus',
                'company': 'HealthPlus Saúde',
                'contact_email': 'digital@healthplus.com.br',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
        ]
    
    def _generate_campaigns_data(self, client_id):
        """Generate campaigns data for a client"""
        campaigns = []
        
        if client_id == 'client_001':  # TechCorp
            campaigns = [
                {
                    'campaign_id': f'{client_id}_camp_001',
                    'client_id': client_id,
                    'campaign_name': 'Campanha Black Friday 2024',
                    'budget_contracted': 150000.00,
                    'budget_used': 148500.00,
                    'impressions_contracted': 30000000,
                    'impressions_delivered': 31200000,
                    'clicks': 52000,
                    'cpm': 4.76,
                    'cpc': 2.86,
                    'ctr': 0.167,
                    'objective': 'Conversões no e-commerce',
                    'date_start': '2024-11-01',
                    'date_end': '2024-11-30',
                    'status': 'active'
                },
                {
                    'campaign_id': f'{client_id}_camp_002',
                    'client_id': client_id,
                    'campaign_name': 'Campanha Natal 2024',
                    'budget_contracted': 200000.00,
                    'budget_used': 185000.00,
                    'impressions_contracted': 40000000,
                    'impressions_delivered': 38500000,
                    'clicks': 68000,
                    'cpm': 4.81,
                    'cpc': 2.72,
                    'ctr': 0.177,
                    'objective': 'Awareness e Conversões',
                    'date_start': '2024-12-01',
                    'date_end': '2024-12-25',
                    'status': 'active'
                }
            ]
        elif client_id == 'client_002':  # EduSmart
            campaigns = [
                {
                    'campaign_id': f'{client_id}_camp_001',
                    'client_id': client_id,
                    'campaign_name': 'Campanha Volta às Aulas 2025',
                    'budget_contracted': 100000.00,
                    'budget_used': 100000.00,
                    'impressions_contracted': 25000000,
                    'impressions_delivered': 26500000,
                    'clicks': 40500,
                    'cpm': 3.77,
                    'cpc': 2.47,
                    'ctr': 0.153,
                    'objective': 'Tráfego para o site',
                    'date_start': '2025-01-15',
                    'date_end': '2025-02-28',
                    'status': 'active'
                }
            ]
        elif client_id == 'client_003':  # HealthPlus
            campaigns = [
                {
                    'campaign_id': f'{client_id}_camp_001',
                    'client_id': client_id,
                    'campaign_name': 'Campanha Janeiro Branco',
                    'budget_contracted': 80000.00,
                    'budget_used': 75000.00,
                    'impressions_contracted': 20000000,
                    'impressions_delivered': 19800000,
                    'clicks': 28000,
                    'cpm': 3.79,
                    'cpc': 2.68,
                    'ctr': 0.141,
                    'objective': 'Conscientização sobre saúde mental',
                    'date_start': '2025-01-01',
                    'date_end': '2025-01-31',
                    'status': 'active'
                },
                {
                    'campaign_id': f'{client_id}_camp_002',
                    'client_id': client_id,
                    'campaign_name': 'Campanha Prevenção Cardiovascular',
                    'budget_contracted': 120000.00,
                    'budget_used': 95000.00,
                    'impressions_contracted': 28000000,
                    'impressions_delivered': 22400000,
                    'clicks': 35000,
                    'cpm': 4.24,
                    'cpc': 2.71,
                    'ctr': 0.156,
                    'objective': 'Agendamento de consultas',
                    'date_start': '2025-02-01',
                    'date_end': '2025-03-31',
                    'status': 'active'
                }
            ]
        
        return campaigns
    
    def _generate_strategies_data(self, campaign_id):
        """Generate strategies data for a campaign"""
        base_strategies = [
            "DWN - Portais de Notícias",
            "DWL - Sites do Segmento",
            "DCS - Conteúdo Semântico",
            "D3P - Interesse Específico",
            "D3P - Estilo de Vida",
            "D3P - Microsegmento",
            "DRG - Retargeting",
            "D2P - Lookalike"
        ]
        
        strategies = []
        total_budget = random.uniform(80000, 200000)
        
        for i, strategy_name in enumerate(base_strategies):
            budget_portion = total_budget / len(base_strategies) * random.uniform(0.5, 1.5)
            impressions = int(budget_portion * random.uniform(2000, 5000))
            clicks = int(impressions * random.uniform(0.001, 0.003))
            ctr = clicks / impressions if impressions > 0 else 0
            cpm = budget_portion / (impressions / 1000) if impressions > 0 else 0
            cpc = budget_portion / clicks if clicks > 0 else 0
            
            strategies.append({
                'strategy_id': f'{campaign_id}_strat_{i+1:03d}',
                'campaign_id': campaign_id,
                'strategy_name': strategy_name,
                'budget_used': round(budget_portion, 2),
                'impressions': impressions,
                'clicks': clicks,
                'ctr': round(ctr, 4),
                'cpm': round(cpm, 2),
                'cpc': round(cpc, 2)
            })
        
        return strategies
    
    def _generate_device_breakdown_data(self, campaign_id):
        """Generate device breakdown data for a campaign"""
        # Realistic device distribution
        mobile_pct = random.uniform(75, 85)
        desktop_pct = random.uniform(12, 20)
        tablet_pct = 100 - mobile_pct - desktop_pct
        
        total_impressions = random.randint(20000000, 40000000)
        
        return [
            {
                'campaign_id': campaign_id,
                'device_type': 'Mobile',
                'impressions': int(total_impressions * mobile_pct / 100),
                'percentage': round(mobile_pct, 2)
            },
            {
                'campaign_id': campaign_id,
                'device_type': 'Desktop',
                'impressions': int(total_impressions * desktop_pct / 100),
                'percentage': round(desktop_pct, 2)
            },
            {
                'campaign_id': campaign_id,
                'device_type': 'Tablets',
                'impressions': int(total_impressions * tablet_pct / 100),
                'percentage': round(tablet_pct, 2)
            }
        ]
    
    def _generate_performance_history_data(self, campaign_id, start_date, end_date):
        """Generate daily performance history for charts"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        performance_data = []
        current_date = start
        
        # Base values with some variation
        base_cpc = random.uniform(2.0, 3.5)
        base_cpm = random.uniform(3.0, 5.0)
        base_ctr = random.uniform(0.12, 0.20)
        
        while current_date <= end:
            # Add some daily variation
            daily_cpc = base_cpc * random.uniform(0.8, 1.2)
            daily_cpm = base_cpm * random.uniform(0.8, 1.2)
            daily_ctr = base_ctr * random.uniform(0.8, 1.2)
            daily_impressions = random.randint(800000, 1500000)
            daily_clicks = int(daily_impressions * daily_ctr)
            
            performance_data.append({
                'campaign_id': campaign_id,
                'date': current_date.strftime('%Y-%m-%d'),
                'cpc': round(daily_cpc, 2),
                'cpm': round(daily_cpm, 2),
                'ctr': round(daily_ctr, 4),
                'impressions': daily_impressions,
                'clicks': daily_clicks
            })
            
            current_date += timedelta(days=1)
        
        return performance_data
    
    def _insert_clients(self, clients_data):
        """Insert clients data"""
        table_id = f"{self.project_id}.{self.dataset_id}.clients"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, clients_data)
        if errors:
            print(f"Error inserting clients: {errors}")
        else:
            print(f"Inserted {len(clients_data)} clients")
    
    def _insert_campaigns(self, campaigns_data):
        """Insert campaigns data"""
        table_id = f"{self.project_id}.{self.dataset_id}.campaigns"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, campaigns_data)
        if errors:
            print(f"Error inserting campaigns: {errors}")
        else:
            print(f"Inserted {len(campaigns_data)} campaigns")
    
    def _insert_strategies(self, strategies_data):
        """Insert strategies data"""
        table_id = f"{self.project_id}.{self.dataset_id}.strategies"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, strategies_data)
        if errors:
            print(f"Error inserting strategies: {errors}")
        else:
            print(f"Inserted {len(strategies_data)} strategies")
    
    def _insert_device_breakdown(self, device_data):
        """Insert device breakdown data"""
        table_id = f"{self.project_id}.{self.dataset_id}.device_breakdown"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, device_data)
        if errors:
            print(f"Error inserting device breakdown: {errors}")
        else:
            print(f"Inserted {len(device_data)} device breakdown records")
    
    def _insert_performance_history(self, performance_data):
        """Insert performance history data"""
        table_id = f"{self.project_id}.{self.dataset_id}.performance_history"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, performance_data)
        if errors:
            print(f"Error inserting performance history: {errors}")
        else:
            print(f"Inserted {len(performance_data)} performance history records")

def main():
    print("🚀 Creating test data for South Media IA Dashboard...")
    
    creator = TestDataCreator()
    
    if not hasattr(creator, 'client') or creator.client is None:
        print("❌ BigQuery client not initialized. Check credentials.")
        return
    
    print("📊 Creating dataset and tables...")
    creator.create_dataset_and_tables()
    
    print("💾 Inserting test data...")
    creator.insert_test_data()
    
    print("✅ Test data creation completed!")

if __name__ == "__main__":
    main()

