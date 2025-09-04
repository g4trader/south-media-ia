from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.models.campaign import CampaignSummary
from src.models.user import UserRole
from src.services.auth_service import auth_service, require_permissions
from src.services.bigquery_service import BigQueryService
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])
bigquery_service = BigQueryService()

@router.get("/campaign/{campaign_id}")
async def get_campaign_dashboard(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(require_permissions(["dashboard:read"]))
):
    """Get dashboard data for a specific campaign"""
    try:
        # Check if user has access to this campaign
        campaign = bigquery_service.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check permissions
        user_role = current_user.get("role")
        user_agency_id = current_user.get("agency_id")
        user_client_id = current_user.get("client_id")
        
        if user_role == UserRole.AGENCY and campaign.get("agency_id") != user_agency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if user_role == UserRole.CLIENT and campaign.get("client_id") != user_client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get campaign metrics
        metrics = bigquery_service.get_campaign_metrics(campaign_id)
        
        # Get client information
        client = bigquery_service.get_client(campaign.get("client_id"))
        
        # Calculate summary
        summary = calculate_campaign_summary(metrics, campaign)
        
        # Prepare dashboard data
        dashboard_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("name", ""),
            "client_name": client.get("name", "") if client else "",
            "campaign_type": campaign.get("campaign_type", ""),
            "summary": summary,
            "daily_metrics": metrics,
            "creatives": get_unique_creatives(metrics)
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}"
        )

@router.get("/client/{client_id}")
async def get_client_dashboards(
    client_id: str,
    current_user: Dict[str, Any] = Depends(require_permissions(["dashboard:read"]))
):
    """Get all dashboards for a specific client"""
    try:
        # Check if user has access to this client
        user_role = current_user.get("role")
        user_agency_id = current_user.get("agency_id")
        user_client_id = current_user.get("client_id")
        
        if user_role == UserRole.CLIENT and user_client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get client campaigns
        campaigns = bigquery_service.get_client_campaigns(client_id)
        
        # Filter campaigns based on user permissions
        if user_role == UserRole.AGENCY:
            campaigns = [c for c in campaigns if c.get("agency_id") == user_agency_id]
        
        # Get dashboard data for each campaign
        dashboards = []
        for campaign in campaigns:
            try:
                metrics = bigquery_service.get_campaign_metrics(campaign.get("id"))
                summary = calculate_campaign_summary(metrics, campaign)
                
                dashboard = {
                    "campaign_id": campaign.get("id"),
                    "campaign_name": campaign.get("name"),
                    "campaign_type": campaign.get("campaign_type"),
                    "status": campaign.get("status"),
                    "summary": summary,
                    "last_updated": campaign.get("updated_at")
                }
                dashboards.append(dashboard)
            except Exception as e:
                # Skip campaigns with errors
                continue
        
        return {
            "client_id": client_id,
            "dashboards": dashboards,
            "total_campaigns": len(dashboards)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get client dashboards: {str(e)}"
        )

@router.get("/agency/{agency_id}")
async def get_agency_dashboards(
    agency_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.require_role([UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]))
):
    """Get all dashboards for an agency (admin and agency users only)"""
    try:
        # Check if user has access to this agency
        user_role = current_user.get("role")
        user_agency_id = current_user.get("agency_id")
        
        if user_role == UserRole.AGENCY and user_agency_id != agency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get agency clients
        clients = bigquery_service.get_agency_clients(agency_id)
        
        # Get dashboards for all clients
        all_dashboards = []
        for client in clients:
            try:
                client_dashboards = await get_client_dashboards(
                    client.get("id"), 
                    current_user
                )
                all_dashboards.extend(client_dashboards.get("dashboards", []))
            except Exception as e:
                # Skip clients with errors
                continue
        
        return {
            "agency_id": agency_id,
            "dashboards": all_dashboards,
            "total_campaigns": len(all_dashboards),
            "total_clients": len(clients)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agency dashboards: {str(e)}"
        )

@router.get("/admin/overview")
async def get_admin_overview(
    current_user: Dict[str, Any] = Depends(auth_service.require_role([UserRole.SUPER_ADMIN]))
):
    """Get admin overview dashboard"""
    try:
        # Get all campaigns
        campaigns = bigquery_service.get_campaigns()
        
        # Calculate overall statistics
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.get("status") == "active"])
        total_investment = sum([c.get("total_budget", 0) for c in campaigns])
        
        # Get recent activity
        recent_campaigns = sorted(
            campaigns, 
            key=lambda x: x.get("updated_at", ""), 
            reverse=True
        )[:10]
        
        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_investment": total_investment,
            "recent_campaigns": recent_campaigns,
            "campaigns_by_type": {
                "video": len([c for c in campaigns if c.get("campaign_type") == "video"]),
                "display": len([c for c in campaigns if c.get("campaign_type") == "display"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin overview: {str(e)}"
        )

def calculate_campaign_summary(metrics: List[Dict], campaign: Dict) -> CampaignSummary:
    """Calculate campaign summary from metrics"""
    if not metrics:
        return CampaignSummary(
            campaign_id=campaign.get("id", ""),
            total_impressions=0,
            total_clicks=0,
            total_investment=0,
            avg_ctr=0,
            avg_cpm=0,
            avg_cpc=0
        )
    
    # Calculate totals
    total_impressions = sum([m.get("impressions", 0) for m in metrics])
    total_clicks = sum([m.get("clicks", 0) for m in metrics])
    total_investment = sum([m.get("investment", 0) for m in metrics])
    
    # Calculate averages
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpm = (total_investment / total_impressions * 1000) if total_impressions > 0 else 0
    avg_cpc = (total_investment / total_clicks) if total_clicks > 0 else 0
    
    # For video campaigns, calculate completion metrics
    completion_rate = None
    total_completions = None
    
    if campaign.get("campaign_type") == "video":
        total_completions = sum([m.get("completions_100", 0) for m in metrics])
        video_starts = sum([m.get("video_starts", 0) for m in metrics])
        completion_rate = (total_completions / video_starts * 100) if video_starts > 0 else 0
    
    return CampaignSummary(
        campaign_id=campaign.get("id", ""),
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        total_investment=total_investment,
        avg_ctr=avg_ctr,
        avg_cpm=avg_cpm,
        avg_cpc=avg_cpc,
        completion_rate=completion_rate,
        total_completions=total_completions
    )

def get_unique_creatives(metrics: List[Dict]) -> List[str]:
    """Extract unique creatives from metrics"""
    creatives = set()
    for metric in metrics:
        creative = metric.get("creative")
        if creative:
            creatives.add(creative)
    return list(creatives)
