from celery import Celery
from src.config import settings
from src.services.sheets_service import sheets_service
from src.services.bigquery_service import BigQueryService
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "south_media_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

@celery_app.task(bind=True)
def sync_campaign_data(self, campaign_id: str, spreadsheet_id: str, sheet_name: str):
    """Sync campaign data from Google Sheets"""
    try:
        logger.info(f"Starting sync for campaign {campaign_id}")
        
        # Read data from Google Sheets
        df = sheets_service.read_sheet_data(spreadsheet_id, sheet_name)
        
        if df is None:
            logger.error(f"Failed to read data from Google Sheets for campaign {campaign_id}")
            return {"status": "error", "message": "Failed to read data from Google Sheets"}
        
        # Get campaign info
        bigquery_service = BigQueryService()
        campaign = bigquery_service.get_campaign(campaign_id)
        
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return {"status": "error", "message": "Campaign not found"}
        
        # Process data based on campaign type
        campaign_type = campaign.get("campaign_type")
        
        if campaign_type == "video":
            metrics = sheets_service.process_video_campaign_data(df, campaign_id)
        elif campaign_type == "display":
            metrics = sheets_service.process_display_campaign_data(df, campaign_id)
        else:
            logger.error(f"Unsupported campaign type: {campaign_type}")
            return {"status": "error", "message": "Unsupported campaign type"}
        
        # Save metrics to BigQuery
        # In a real implementation, you would save to BigQuery
        logger.info(f"Processed {len(metrics)} metrics for campaign {campaign_id}")
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "metrics_count": len(metrics),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error syncing campaign {campaign_id}: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def sync_all_campaigns(self):
    """Sync all active campaigns from their Google Sheets"""
    try:
        logger.info("Starting sync for all campaigns")
        
        bigquery_service = BigQueryService()
        campaigns = bigquery_service.get_campaigns()
        
        # Filter active campaigns with Google Sheets configuration
        active_campaigns = [
            c for c in campaigns 
            if c.get("status") == "active" and c.get("sheets_config")
        ]
        
        results = []
        for campaign in active_campaigns:
            try:
                sheets_config = campaign.get("sheets_config")
                result = sync_campaign_data.delay(
                    campaign.get("id"),
                    sheets_config.get("spreadsheet_id"),
                    sheets_config.get("sheet_name")
                )
                results.append({
                    "campaign_id": campaign.get("id"),
                    "task_id": result.id
                })
            except Exception as e:
                logger.error(f"Error queuing sync for campaign {campaign.get('id')}: {e}")
                results.append({
                    "campaign_id": campaign.get("id"),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "total_campaigns": len(active_campaigns),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sync_all_campaigns: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def cleanup_old_data(self, days_to_keep: int = 90):
    """Clean up old campaign data"""
    try:
        logger.info(f"Starting cleanup of data older than {days_to_keep} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # In a real implementation, you would delete old data from BigQuery
        # For now, we'll just log the action
        
        logger.info(f"Cleanup completed. Cutoff date: {cutoff_date}")
        
        return {
            "status": "success",
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_data: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def generate_daily_report(self):
    """Generate daily report of campaign performance"""
    try:
        logger.info("Starting daily report generation")
        
        bigquery_service = BigQueryService()
        campaigns = bigquery_service.get_campaigns()
        
        # Get yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Generate report data
        report_data = {
            "date": yesterday.date().isoformat(),
            "total_campaigns": len(campaigns),
            "active_campaigns": len([c for c in campaigns if c.get("status") == "active"]),
            "campaigns_by_type": {
                "video": len([c for c in campaigns if c.get("campaign_type") == "video"]),
                "display": len([c for c in campaigns if c.get("campaign_type") == "display"])
            },
            "total_investment": sum([c.get("total_budget", 0) for c in campaigns])
        }
        
        # In a real implementation, you would save the report to BigQuery
        # and potentially send it via email
        
        logger.info("Daily report generated successfully")
        
        return {
            "status": "success",
            "report": report_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return {"status": "error", "message": str(e)}

# Periodic tasks configuration
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""
    # Sync all campaigns daily at 6 AM UTC
    sender.add_periodic_task(
        crontab(hour=6, minute=0),
        sync_all_campaigns.s(),
        name='daily-sync-campaigns'
    )
    
    # Generate daily report at 7 AM UTC
    sender.add_periodic_task(
        crontab(hour=7, minute=0),
        generate_daily_report.s(),
        name='daily-report'
    )
    
    # Cleanup old data weekly on Sunday at 2 AM UTC
    sender.add_periodic_task(
        crontab(day_of_week=0, hour=2, minute=0),
        cleanup_old_data.s(),
        name='weekly-cleanup'
    )

# Import crontab for periodic tasks
from celery.schedules import crontab
