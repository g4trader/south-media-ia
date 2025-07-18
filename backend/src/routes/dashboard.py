from flask import Blueprint, jsonify, request
from src.services.bigquery_service import BigQueryService
from src.services.insights_service import InsightsService
import jwt
import os
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)
bigquery_service = BigQueryService()
insights_service = InsightsService()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'), algorithms=['HS256'])
            current_client_id = data['client_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_client_id, *args, **kwargs)
    
    return decorated

@dashboard_bp.route('/campaign/<campaign_id>', methods=['GET'])
@token_required
def get_campaign_data(current_client_id, campaign_id):
    """Get campaign data for dashboard"""
    try:
        campaign_data = bigquery_service.get_campaign_data(current_client_id, campaign_id)
        strategies_data = bigquery_service.get_strategies_data(campaign_id)
        device_breakdown = bigquery_service.get_device_breakdown(campaign_id)
        
        if not campaign_data['campaigns']:
            return jsonify({'error': 'Campaign not found'}), 404
        
        campaign = campaign_data['campaigns'][0]
        
        # Calculate progress
        budget_progress = (campaign['budget_used'] / campaign['budget_contracted']) * 100 if campaign['budget_contracted'] > 0 else 0
        impressions_progress = (campaign['impressions_delivered'] / campaign['impressions_contracted']) * 100 if campaign['impressions_contracted'] > 0 else 0
        
        response_data = {
            'campaign': campaign,
            'strategies': strategies_data,
            'device_breakdown': device_breakdown,
            'progress': {
                'budget': round(budget_progress, 1),
                'impressions': round(impressions_progress, 1)
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/campaign/<campaign_id>/insights', methods=['GET'])
@token_required
def get_campaign_insights(current_client_id, campaign_id):
    """Get campaign insights and analysis"""
    try:
        # Get campaign data
        campaign_data = bigquery_service.get_campaign_data(current_client_id, campaign_id)
        strategies_data = bigquery_service.get_strategies_data(campaign_id)
        device_breakdown = bigquery_service.get_device_breakdown(campaign_id)
        
        if not campaign_data['campaigns']:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Prepare data for insights analysis
        analysis_data = {
            'campaign': campaign_data['campaigns'][0],
            'strategies': strategies_data,
            'device_breakdown': device_breakdown
        }
        
        # Generate insights
        insights = insights_service.analyze_campaign_performance(analysis_data)
        
        return jsonify(insights)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/campaigns', methods=['GET'])
@token_required
def get_campaigns_list(current_client_id):
    """Get list of campaigns for client"""
    try:
        campaigns_data = bigquery_service.get_campaign_data(current_client_id)
        return jsonify(campaigns_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/auth/token', methods=['POST'])
def generate_token():
    """Generate JWT token for client authentication"""
    data = request.get_json()
    
    if not data or not data.get('client_id') or not data.get('password'):
        return jsonify({'error': 'Client ID and password are required'}), 400
    
    client_id = data['client_id']
    password = data['password']
    
    # Simple authentication - in production, use proper password hashing
    # For demo purposes, we'll accept any client_id with password "demo123"
    if password == "demo123":
        token = jwt.encode({
            'client_id': client_id
        }, os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'), algorithm='HS256')
        
        return jsonify({
            'token': token,
            'client_id': client_id
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@dashboard_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'South Media Dashboard API'})

