from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.models.campaign import (
    CampaignCreate, CampaignResponse, CampaignUpdate,
    VideoMetrics, DisplayMetrics, CampaignSummary, DashboardData
)
from src.models.user import UserRole
from src.services.auth_service import auth_service, can_read_campaigns, can_write_campaigns
from src.services.bigquery_service import BigQueryService
from src.services.sheets_service import sheets_service
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])
bigquery_service = BigQueryService()

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    current_user: Dict[str, Any] = Depends(can_read_campaigns),
    client_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get campaigns with permission-based filtering"""
    try:
        # Filter campaigns based on user role and permissions
        user_role = current_user.get("role")
        user_agency_id = current_user.get("agency_id")
        user_client_id = current_user.get("client_id")
        
        # Get campaigns from BigQuery
        campaigns = bigquery_service.get_campaigns()
        
        # Filter based on user permissions
        filtered_campaigns = []
        for campaign in campaigns:
            # Admin can see all campaigns
            if user_role == UserRole.ADMIN:
                filtered_campaigns.append(campaign)
            # Agency users can see their clients' campaigns
            elif user_role == UserRole.AGENCY:
                if campaign.get("agency_id") == user_agency_id:
                    filtered_campaigns.append(campaign)
            # Client users can only see their own campaigns
            elif user_role == UserRole.CLIENT:
                if campaign.get("client_id") == user_client_id:
                    filtered_campaigns.append(campaign)
        
        # Apply additional filters
        if client_id:
            filtered_campaigns = [c for c in filtered_campaigns if c.get("client_id") == client_id]
        
        if status:
            filtered_campaigns = [c for c in filtered_campaigns if c.get("status") == status]
        
        return filtered_campaigns
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaigns: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(can_read_campaigns)
):
    """Get a specific campaign"""
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
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: Dict[str, Any] = Depends(can_write_campaigns)
):
    """Create a new campaign"""
    try:
        # Only admin and agency users can create campaigns
        user_role = current_user.get("role")
        if user_role not in [UserRole.ADMIN, UserRole.AGENCY]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin and agency users can create campaigns"
            )
        
        # Create campaign in BigQuery
        campaign_id = str(uuid.uuid4())
        campaign = {
            "id": campaign_id,
            **campaign_data.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # In a real implementation, you would save to BigQuery
        # For now, we'll return the campaign data
        
        return CampaignResponse(**campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: Dict[str, Any] = Depends(can_write_campaigns)
):
    """Update a campaign"""
    try:
        # Check if campaign exists and user has access
        campaign = bigquery_service.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check permissions
        user_role = current_user.get("role")
        user_agency_id = current_user.get("agency_id")
        
        if user_role == UserRole.AGENCY and campaign.get("agency_id") != user_agency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update campaign
        updated_campaign = {**campaign, **campaign_data.dict(exclude_unset=True)}
        updated_campaign["updated_at"] = datetime.utcnow()
        
        # In a real implementation, you would update in BigQuery
        
        return CampaignResponse(**updated_campaign)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.require_role([UserRole.ADMIN]))
):
    """Delete a campaign (admin only)"""
    try:
        # Check if campaign exists
        campaign = bigquery_service.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # In a real implementation, you would delete from BigQuery
        
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )

@router.get("/{campaign_id}/metrics")
async def get_campaign_metrics(
    campaign_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(can_read_campaigns)
):
    """Get campaign metrics"""
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
        
        # Get metrics from BigQuery
        metrics = bigquery_service.get_campaign_metrics(campaign_id, start_date, end_date)
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign metrics: {str(e)}"
        )

@router.post("/{campaign_id}/sync-sheets")
async def sync_campaign_from_sheets(
    campaign_id: str,
    spreadsheet_id: str,
    sheet_name: str,
    current_user: Dict[str, Any] = Depends(can_write_campaigns)
):
    """Sync campaign data from Google Sheets"""
    try:
        # Check if user has access to this campaign
        campaign = bigquery_service.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Read data from Google Sheets
        df = sheets_service.read_sheet_data(spreadsheet_id, sheet_name)
        
        if df is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read data from Google Sheets"
            )
        
        # Process data based on campaign type
        campaign_type = campaign.get("campaign_type")
        
        if campaign_type == "video":
            metrics = sheets_service.process_video_campaign_data(df, campaign_id)
        elif campaign_type == "display":
            metrics = sheets_service.process_display_campaign_data(df, campaign_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported campaign type"
            )
        
        # Save metrics to BigQuery
        # In a real implementation, you would save to BigQuery
        
        return {
            "message": "Campaign data synced successfully",
            "metrics_count": len(metrics)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync campaign data: {str(e)}"
        )
