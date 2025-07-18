from src.models.user import db
from datetime import datetime

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(100), nullable=False)
    campaign_name = db.Column(db.String(200), nullable=False)
    budget_contracted = db.Column(db.Float, nullable=False)
    budget_used = db.Column(db.Float, default=0.0)
    impressions_contracted = db.Column(db.Integer, nullable=False)
    impressions_delivered = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    cpm = db.Column(db.Float, default=0.0)
    cpc = db.Column(db.Float, default=0.0)
    ctr = db.Column(db.Float, default=0.0)
    objective = db.Column(db.String(100), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'campaign_name': self.campaign_name,
            'budget_contracted': self.budget_contracted,
            'budget_used': self.budget_used,
            'impressions_contracted': self.impressions_contracted,
            'impressions_delivered': self.impressions_delivered,
            'clicks': self.clicks,
            'cpm': self.cpm,
            'cpc': self.cpc,
            'ctr': self.ctr,
            'objective': self.objective,
            'date_start': self.date_start.isoformat() if self.date_start else None,
            'date_end': self.date_end.isoformat() if self.date_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Strategy(db.Model):
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    strategy_name = db.Column(db.String(200), nullable=False)
    budget_used = db.Column(db.Float, nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    ctr = db.Column(db.Float, nullable=False)
    cpm = db.Column(db.Float, nullable=False)
    cpc = db.Column(db.Float, nullable=False)
    
    campaign = db.relationship('Campaign', backref=db.backref('strategies', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'strategy_name': self.strategy_name,
            'budget_used': self.budget_used,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'ctr': self.ctr,
            'cpm': self.cpm,
            'cpc': self.cpc
        }

class DeviceBreakdown(db.Model):
    __tablename__ = 'device_breakdown'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # Mobile, Desktop, Tablets
    impressions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    
    campaign = db.relationship('Campaign', backref=db.backref('device_breakdown', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'device_type': self.device_type,
            'impressions': self.impressions,
            'percentage': self.percentage
        }

