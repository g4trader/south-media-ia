from google.cloud import bigquery
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, bigquery_client: bigquery.Client, project_id: str, dataset_id: str):
        self.client = bigquery_client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.video_kpis_table = f"{project_id}.{dataset_id}.video_kpis"
        self.campaigns_table = f"{project_id}.{dataset_id}.campaigns"
    
    def get_video_campaigns(self) -> List[Dict]:
        """Retorna lista de campanhas com dados de vídeo."""
        query = f"""
        SELECT DISTINCT
            c.campaign_id,
            c.campaign_name,
            c.date_start,
            c.date_end,
            c.objective,
            c.budget_contracted,
            COUNT(vk.campaign_id) as video_creatives_count
        FROM
            `{self.campaigns_table}` AS c
        INNER JOIN
            `{self.video_kpis_table}` AS vk
        ON
            c.campaign_id = vk.campaign_id
        GROUP BY
            c.campaign_id, c.campaign_name, c.date_start, c.date_end, c.objective, c.budget_contracted
        ORDER BY
            c.date_start DESC
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            campaigns = []
            for row in results:
                campaigns.append({
                    'campaign_id': row.campaign_id,
                    'campaign_name': row.campaign_name,
                    'date_start': row.date_start.isoformat() if row.date_start else None,
                    'date_end': row.date_end.isoformat() if row.date_end else None,
                    'objective': row.objective,
                    'budget_contracted': float(row.budget_contracted) if row.budget_contracted else 0,
                    'video_creatives_count': row.video_creatives_count
                })
            
            return campaigns
        
        except Exception as e:
            logger.error(f"Error fetching video campaigns: {str(e)}")
            raise
    
    def get_campaign_video_kpis(self, campaign_id: str) -> Dict:
        """Retorna KPIs de vídeo para uma campanha específica."""
        query = f"""
        SELECT
            SUM(video_starts) as total_video_starts,
            AVG(video_completion_rate) as avg_completion_rate,
            AVG(video_skip_rate) as avg_skip_rate,
            AVG(video_start_rate) as avg_start_rate,
            SUM(video_25_percent_complete) as total_25_percent,
            SUM(video_50_percent_complete) as total_50_percent,
            SUM(video_75_percent_complete) as total_75_percent,
            SUM(video_100_percent_complete) as total_100_percent,
            SUM(invested_value) as total_video_investment,
            SUM(impressions) as total_video_impressions,
            SUM(clicks) as total_video_clicks,
            AVG(ctr) as avg_video_ctr
        FROM
            `{self.video_kpis_table}`
        WHERE
            campaign_id = @campaign_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return {}
            
            row = results[0]
            return {
                'total_video_starts': row.total_video_starts or 0,
                'avg_completion_rate': float(row.avg_completion_rate) if row.avg_completion_rate else 0,
                'avg_skip_rate': float(row.avg_skip_rate) if row.avg_skip_rate else 0,
                'avg_start_rate': float(row.avg_start_rate) if row.avg_start_rate else 0,
                'total_25_percent': row.total_25_percent or 0,
                'total_50_percent': row.total_50_percent or 0,
                'total_75_percent': row.total_75_percent or 0,
                'total_100_percent': row.total_100_percent or 0,
                'total_video_investment': float(row.total_video_investment) if row.total_video_investment else 0,
                'total_video_impressions': row.total_video_impressions or 0,
                'total_video_clicks': row.total_video_clicks or 0,
                'avg_video_ctr': float(row.avg_video_ctr) if row.avg_video_ctr else 0
            }
        
        except Exception as e:
            logger.error(f"Error fetching video KPIs for campaign {campaign_id}: {str(e)}")
            raise
    
    def get_format_breakdown(self, campaign_id: str) -> List[Dict]:
        """Retorna breakdown de performance por formato de vídeo."""
        query = f"""
        SELECT
            video_format,
            SUM(video_starts) as video_starts,
            AVG(video_completion_rate) as completion_rate,
            AVG(video_skip_rate) as skip_rate,
            SUM(invested_value) as investment,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks
        FROM
            `{self.video_kpis_table}`
        WHERE
            campaign_id = @campaign_id
        GROUP BY
            video_format
        ORDER BY
            video_starts DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            formats = []
            for row in results:
                formats.append({
                    'video_format': row.video_format,
                    'video_starts': row.video_starts or 0,
                    'completion_rate': float(row.completion_rate) if row.completion_rate else 0,
                    'skip_rate': float(row.skip_rate) if row.skip_rate else 0,
                    'investment': float(row.investment) if row.investment else 0,
                    'impressions': row.impressions or 0,
                    'clicks': row.clicks or 0
                })
            
            return formats
        
        except Exception as e:
            logger.error(f"Error fetching format breakdown for campaign {campaign_id}: {str(e)}")
            raise

    def get_daily_performance(self, campaign_id: str) -> List[Dict]:
        """Retorna histórico de performance diária para uma campanha específica."""
        query = f"""
        SELECT
            date,
            SUM(video_starts) as daily_video_starts,
            AVG(video_completion_rate) as daily_completion_rate,
            AVG(video_skip_rate) as daily_skip_rate,
            SUM(invested_value) as daily_investment
        FROM
            `{self.video_kpis_table}`
        WHERE
            campaign_id = @campaign_id
        GROUP BY
            date
        ORDER BY
            date
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            daily_performance = []
            for row in results:
                daily_performance.append({
                    'date': row.date.isoformat() if row.date else None,
                    'daily_video_starts': row.daily_video_starts or 0,
                    'daily_completion_rate': float(row.daily_completion_rate) if row.daily_completion_rate else 0,
                    'daily_skip_rate': float(row.daily_skip_rate) if row.daily_skip_rate else 0,
                    'daily_investment': float(row.daily_investment) if row.daily_investment else 0
                })
            
            return daily_performance
        
        except Exception as e:
            logger.error(f"Error fetching daily performance for campaign {campaign_id}: {str(e)}")
            raise

    def get_top_creatives(self, campaign_id: str) -> List[Dict]:
        """Retorna os top criativos por video starts para uma campanha específica."""
        query = f"""
        SELECT
            creative_name,
            video_format,
            SUM(video_starts) as video_starts,
            AVG(video_completion_rate) as completion_rate,
            SUM(video_100_percent_complete) as complete_views,
            SUM(invested_value) as investment
        FROM
            `{self.video_kpis_table}`
        WHERE
            campaign_id = @campaign_id
        GROUP BY
            creative_name, video_format
        ORDER BY
            video_starts DESC
        LIMIT 10
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            top_creatives = []
            for row in results:
                top_creatives.append({
                    'creative_name': row.creative_name,
                    'video_format': row.video_format,
                    'video_starts': row.video_starts or 0,
                    'completion_rate': float(row.completion_rate) if row.completion_rate else 0,
                    'complete_views': row.complete_views or 0,
                    'investment': float(row.investment) if row.investment else 0
                })
            
            return top_creatives
        
        except Exception as e:
            logger.error(f"Error fetching top creatives for campaign {campaign_id}: {str(e)}")
            raise

    def get_video_formats_comparison(self) -> List[Dict]:
        """Retorna uma comparação de performance entre diferentes formatos de vídeo."""
        query = f"""
        SELECT
            video_format,
            COUNT(DISTINCT campaign_id) as campaigns_count,
            SUM(video_starts) as total_starts,
            AVG(video_completion_rate) as avg_completion_rate,
            AVG(video_skip_rate) as avg_skip_rate,
            SUM(video_100_percent_complete) as total_complete_views,
            SUM(invested_value) as total_investment,
            AVG(ctr) as avg_ctr
        FROM
            `{self.video_kpis_table}`
        WHERE
            video_format IS NOT NULL
        GROUP BY
            video_format
        ORDER BY
            total_starts DESC
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            formats = []
            for row in results:
                formats.append({
                    'video_format': row.video_format,
                    'campaigns_count': row.campaigns_count,
                    'total_starts': row.total_starts or 0,
                    'avg_completion_rate': float(row.avg_completion_rate) if row.avg_completion_rate else 0,
                    'avg_skip_rate': float(row.avg_skip_rate) if row.avg_skip_rate else 0,
                    'total_complete_views': row.total_complete_views or 0,
                    'total_investment': float(row.total_investment) if row.total_investment else 0,
                    'avg_ctr': float(row.avg_ctr) if row.avg_ctr else 0
                })
            
            return formats
        
        except Exception as e:
            logger.error(f"Error fetching video formats comparison: {str(e)}")
            raise


