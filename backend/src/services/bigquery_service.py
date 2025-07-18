from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
from typing import List, Dict, Any, Optional

class BigQueryService:
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'your-project-id')
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
    
    def get_campaign_data(self, client_id: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Get campaign data from BigQuery"""
        if not self.client:
            return self._get_mock_campaign_data()
        
        query = f"""
        SELECT 
            campaign_id,
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
            date_end
        FROM `{self.project_id}.{self.dataset_id}.campaigns`
        WHERE client_id = @client_id
        """
        
        if campaign_id:
            query += " AND campaign_id = @campaign_id"
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("client_id", "STRING", client_id),
            ]
        )
        
        if campaign_id:
            job_config.query_parameters.append(
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)
            )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            campaigns = []
            for row in results:
                campaigns.append(dict(row))
            
            return {"campaigns": campaigns}
        except Exception as e:
            print(f"Error querying BigQuery: {e}")
            return self._get_mock_campaign_data()
    
    def get_strategies_data(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get strategies data from BigQuery"""
        if not self.client:
            return self._get_mock_strategies_data()
        
        query = f"""
        SELECT 
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
    
    def _get_mock_campaign_data(self) -> Dict[str, Any]:
        """Mock data for development"""
        return {
            "campaigns": [{
                "campaign_id": "demo_campaign_001",
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
            }]
        }
    
    def _get_mock_strategies_data(self) -> List[Dict[str, Any]]:
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
            },
            {
                "strategy_name": "DCS - Conteúdo Semântico - Educação",
                "budget_used": 10000.00,
                "impressions": 4000000,
                "clicks": 4800,
                "ctr": 0.12,
                "cpm": 2.50,
                "cpc": 2.08
            },
            {
                "strategy_name": "D3P - Interesse em Educação",
                "budget_used": 10000.00,
                "impressions": 4000000,
                "clicks": 4800,
                "ctr": 0.12,
                "cpm": 6.00,
                "cpc": 2.08
            },
            {
                "strategy_name": "D3P - Estilo de Vida - Estudante",
                "budget_used": 10000.00,
                "impressions": 2500000,
                "clicks": 3500,
                "ctr": 0.14,
                "cpm": 4.00,
                "cpc": 2.86
            },
            {
                "strategy_name": "D3P - Microsegmento - Jovem Adulto",
                "budget_used": 10000.00,
                "impressions": 2500000,
                "clicks": 4000,
                "ctr": 0.16,
                "cpm": 4.00,
                "cpc": 2.50
            },
            {
                "strategy_name": "DRG - Retargeting de todo o site",
                "budget_used": 10000.00,
                "impressions": 2000000,
                "clicks": 5000,
                "ctr": 0.25,
                "cpm": 5.00,
                "cpc": 2.00
            },
            {
                "strategy_name": "D2P - Lookalike de Alunos",
                "budget_used": 10000.00,
                "impressions": 2500000,
                "clicks": 5000,
                "ctr": 0.20,
                "cpm": 4.00,
                "cpc": 2.00
            }
        ]
    
    def _get_mock_device_breakdown(self) -> List[Dict[str, Any]]:
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

