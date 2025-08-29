from src.models.user import db
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CampaignType(str, Enum):
    VIDEO = "video"
    DISPLAY = "display"
    HYBRID = "hybrid"

class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"

class CampaignBase(BaseModel):
    name: str
    client_id: str
    campaign_type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    
    # Contract details
    contract_scope: str  # "completions" for video, "impressions" for display
    unit_cost: str       # "CPV" for video, "CPM" for display
    total_budget: float
    start_date: datetime
    end_date: datetime
    
    # Channels
    channels: List[str] = []
    
    # Additional metadata
    description: Optional[str] = None
    objectives: Optional[List[str]] = None
    target_audience: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[CampaignStatus] = None
    total_budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    channels: Optional[List[str]] = None
    description: Optional[str] = None
    objectives: Optional[List[str]] = None
    target_audience: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Video Campaign Metrics
class VideoMetrics(BaseModel):
    date: datetime
    completion_rate: float
    skip_rate: float
    start_rate: float
    completions_25: int
    completions_50: int
    completions_75: int
    completions_100: int
    video_starts: int
    investment: float
    creative: Optional[str] = None

class VideoMetricsCreate(VideoMetrics):
    campaign_id: str

class VideoMetricsResponse(VideoMetrics):
    id: str
    campaign_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Display Campaign Metrics
class DisplayMetrics(BaseModel):
    date: datetime
    creative: str
    impressions: int
    clicks: int
    ctr: float
    cpm: float
    cpc: float
    investment: float

class DisplayMetricsCreate(DisplayMetrics):
    campaign_id: str

class DisplayMetricsResponse(DisplayMetrics):
    id: str
    campaign_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Campaign Summary
class CampaignSummary(BaseModel):
    campaign_id: str
    total_impressions: int
    total_clicks: int
    total_investment: float
    avg_ctr: float
    avg_cpm: float
    avg_cpc: float
    completion_rate: Optional[float] = None  # For video campaigns
    total_completions: Optional[int] = None  # For video campaigns

# Dashboard Data
class DashboardData(BaseModel):
    campaign_id: str
    campaign_name: str
    client_name: str
    campaign_type: CampaignType
    summary: CampaignSummary
    daily_metrics: List[Dict[str, Any]]
    creatives: List[str] = []

# Google Sheets Integration
class SheetsConfig(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    campaign_id: str
    update_frequency: str = "daily"  # daily, weekly, monthly
    last_updated: Optional[datetime] = None

class SheetsConfigCreate(SheetsConfig):
    pass

class SheetsConfigResponse(SheetsConfig):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

