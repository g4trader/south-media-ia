from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class BigQueryService:
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'automatizar-452311')
        self.dataset_id = os.environ.get('BIGQUERY_DATASET', 'south_media_dashboard')
        
        # Initialize BigQuery client
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(credentials=credentials, project=self.project_id)
        else:
            # For development, use default credentials or mock data
            self.client = None
            print("Warning: BigQuery credentials not found. Using mock data for development.")
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients from BigQuery"""
        if not self.client:
            return self._get_mock_clients()
        
        query = f"""
        SELECT 
            client_id,
            client_name,
            company,
            contact_email,
            status,
            created_at
        FROM `{self.project_id}.{self.dataset_id}.clients`
        WHERE status = 'active'
        ORDER BY client_name
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            clients = []
            for row in results:
                client_data = dict(row)
                # Convert timestamp to string for JSON serialization
                if 'created_at' in client_data and client_data['created_at']:
                    client_data['created_at'] = client_data['created_at'].isoformat()
                clients.append(client_data)
            
            return clients
        except Exception as e:
            print(f"Error querying clients: {e}")
            return self._get_mock_clients()
    
    def get_client_campaigns(self, client_id: str) -> List[Dict[str, Any]]:
        """Get campaigns for a specific client"""
        if not self.client:
            return self._get_mock_campaigns(client_id)
        
        query = f"""
        SELECT 
            campaign_id,
            client_id,
            campaign_name,
            budget_contracted,
            budget_used,
            impressions_contracted,
            impressions_delivered,
            clicks,
            cpm,
            cpc,
            ctr,
            objective,
            date_start,
            date_end,
            status
        FROM `{self.project_id}.{self.dataset_id}.campaigns`
        WHERE client_id = @client_id
        ORDER BY date_start DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("client_id", "STRING", client_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            campaigns = []
            for row in results:
                campaign_data = dict(row)
                # Convert dates to strings for JSON serialization
                if 'date_start' in campaign_data and campaign_data['date_start']:
                    campaign_data['date_start'] = campaign_data['date_start'].isoformat()
                if 'date_end' in campaign_data and campaign_data['date_end']:
                    campaign_data['date_end'] = campaign_data['date_end'].isoformat()
                campaigns.append(campaign_data)
            
            return campaigns
        except Exception as e:
            print(f"Error querying campaigns for client {client_id}: {e}")
            return self._get_mock_campaigns(client_id)
    
    def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed campaign data from BigQuery"""
        if not self.client:
            return self._get_mock_campaign_data(campaign_id)
        
        query = f"""
        SELECT 
            campaign_id,
            client_id,
            campaign_name,
            budget_contracted,
            budget_used,
            impressions_contracted,
            impressions_delivered,
            clicks,
            cpm,
            cpc,
            ctr,
            objective,
            date_start,
            date_end,
            status
        FROM `{self.project_id}.{self.dataset_id}.campaigns`
        WHERE campaign_id = @campaign_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                campaign_data = dict(row)
                # Convert dates to strings for JSON serialization
                if 'date_start' in campaign_data and campaign_data['date_start']:
                    campaign_data['date_start'] = campaign_data['date_start'].isoformat()
                if 'date_end' in campaign_data and campaign_data['date_end']:
                    campaign_data['date_end'] = campaign_data['date_end'].isoformat()
                return campaign_data
            
            return None
        except Exception as e:
            print(f"Error querying campaign {campaign_id}: {e}")
            return self._get_mock_campaign_data(campaign_id)
    
    def get_strategies_data(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get strategies data from BigQuery"""
        if not self.client:
            return self._get_mock_strategies_data()
        
        query = f"""
        SELECT 
            strategy_id,
            campaign_id,
            strategy_name,
            budget_used,
            impressions,
            clicks,
            ctr,
            cpm,
            cpc
        FROM `{self.project_id}.{self.dataset_id}.strategies`
        WHERE campaign_id = @campaign_id
        ORDER BY budget_used DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            strategies = []
            for row in results:
                strategies.append(dict(row))
            
            return strategies
        except Exception as e:
            print(f"Error querying strategies: {e}")
            return self._get_mock_strategies_data()
    
    def get_device_breakdown(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get device breakdown data from BigQuery"""
        if not self.client:
            return self._get_mock_device_breakdown()
        
        query = f"""
        SELECT 
            device_type,
            impressions,
            percentage
        FROM `{self.project_id}.{self.dataset_id}.device_breakdown`
        WHERE campaign_id = @campaign_id
        ORDER BY percentage DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            breakdown = []
            for row in results:
                breakdown.append(dict(row))
            
            return breakdown
        except Exception as e:
            print(f"Error querying device breakdown: {e}")
            return self._get_mock_device_breakdown()
    
    def get_performance_history(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get performance history for charts"""
        if not self.client:
            return self._get_mock_performance_history()
        
        query = f"""
        SELECT 
            date,
            cpc,
            cpm,
            ctr,
            impressions,
            clicks
        FROM `{self.project_id}.{self.dataset_id}.performance_history`
        WHERE campaign_id = @campaign_id
        ORDER BY date ASC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            history = []
            for row in results:
                row_data = dict(row)
                # Convert date to string for JSON serialization
                if 'date' in row_data and row_data['date']:
                    row_data['date'] = row_data['date'].isoformat()
                history.append(row_data)
            
            return history
        except Exception as e:
            print(f"Error querying performance history: {e}")
            return self._get_mock_performance_history()
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        if not self.client:
            return self._get_mock_admin_stats()
        
        try:
            # Get total clients
            clients_query = f"""
            SELECT COUNT(*) as total_clients
            FROM `{self.project_id}.{self.dataset_id}.clients`
            WHERE status = 'active'
            """
            
            # Get active campaigns
            campaigns_query = f"""
            SELECT COUNT(*) as active_campaigns
            FROM `{self.project_id}.{self.dataset_id}.campaigns`
            WHERE status = 'active'
            """
            
            # Get total budget
            budget_query = f"""
            SELECT SUM(budget_contracted) as total_budget
            FROM `{self.project_id}.{self.dataset_id}.campaigns`
            WHERE status = 'active'
            """
            
            # Get total impressions
            impressions_query = f"""
            SELECT SUM(impressions_delivered) as total_impressions
            FROM `{self.project_id}.{self.dataset_id}.campaigns`
            WHERE status = 'active'
            """
            
            # Execute queries
            clients_result = list(self.client.query(clients_query).result())[0]
            campaigns_result = list(self.client.query(campaigns_query).result())[0]
            budget_result = list(self.client.query(budget_query).result())[0]
            impressions_result = list(self.client.query(impressions_query).result())[0]
            
            return {
                'total_clients': clients_result['total_clients'] or 0,
                'active_campaigns': campaigns_result['active_campaigns'] or 0,
                'total_budget': float(budget_result['total_budget'] or 0),
                'total_impressions': int(impressions_result['total_impressions'] or 0)
            }
            
        except Exception as e:
            print(f"Error querying admin stats: {e}")
            return self._get_mock_admin_stats()
    
    # Mock data methods for development
    def _get_mock_clients(self):
        """Mock clients data for development"""
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
            }
        ]
    
    def _get_mock_campaigns(self, client_id):
        """Mock campaigns data for development"""
        if client_id == 'client_001':
            return [
                {
                    'campaign_id': 'client_001_camp_001',
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
                }
            ]
        return []
    
    def _get_mock_campaign_data(self, campaign_id):
        """Mock campaign data for development"""
        return {
            "campaign_id": campaign_id,
            "campaign_name": "Campanha de Demonstração",
            "budget_contracted": 100000.00,
            "budget_used": 100000.00,
            "impressions_contracted": 25000000,
            "impressions_delivered": 26500000,
            "clicks": 40500,
            "cpm": 3.77,
            "cpc": 2.47,
            "ctr": 0.15,
            "objective": "Tráfego para o site",
            "date_start": "2023-07-01",
            "date_end": "2023-07-31"
        }
    
    def _get_mock_strategies_data(self):
        """Mock strategies data for development"""
        return [
            {
                "strategy_name": "DWN - Portais de Notícias",
                "budget_used": 20000.00,
                "impressions": 5000000,
                "clicks": 7000,
                "ctr": 0.14,
                "cpm": 4.00,
                "cpc": 2.86
            },
            {
                "strategy_name": "DWL - Sites do Segmento",
                "budget_used": 20000.00,
                "impressions": 4000000,
                "clicks": 353,
                "ctr": 0.14,
                "cpm": 5.00,
                "cpc": 3.13
            }
        ]
    
    def _get_mock_device_breakdown(self):
        """Mock device breakdown data for development"""
        return [
            {
                "device_type": "Mobile",
                "impressions": 21374300,
                "percentage": 80.62
            },
            {
                "device_type": "Desktop",
                "impressions": 4910450,
                "percentage": 18.53
            },
            {
                "device_type": "Tablets",
                "impressions": 222600,
                "percentage": 0.84
            }
        ]
    
    def _get_mock_performance_history(self):
        """Mock performance history data for development"""
        return [
            {"date": "2023-07-01", "cpc": 3.6, "cpm": 4.2, "ctr": 0.14, "impressions": 1200000, "clicks": 1680},
            {"date": "2023-07-02", "cpc": 3.4, "cpm": 4.0, "ctr": 0.15, "impressions": 1250000, "clicks": 1875},
            {"date": "2023-07-03", "cpc": 3.2, "cpm": 3.8, "ctr": 0.16, "impressions": 1300000, "clicks": 2080}
        ]
    
    def _get_mock_admin_stats(self):
        """Mock admin stats for development"""
        return {
            'total_clients': 3,
            'active_campaigns': 5,
            'total_budget': 450000.0,
            'total_impressions': 95000000
        }

