"""
APIs Dinâmicas para Dashboard Multi-Cliente
South Media Dashboard
"""

from flask import Blueprint, jsonify, request
from google.cloud import bigquery
from datetime import datetime, timedelta
import json
import logging
from ..auth.client_auth import require_client_auth, get_current_client_id, validate_client_access

logger = logging.getLogger(__name__)

# Blueprint para rotas de cliente
client_bp = Blueprint('client', __name__, url_prefix='/api/client')

# Cliente BigQuery (será inicializado no main.py)
bq_client = None

def init_bigquery_client(client):
    """Inicializa o cliente BigQuery"""
    global bq_client
    bq_client = client

@client_bp.route('/<client_id>/dashboard', methods=['GET'])
@require_client_auth
def get_client_dashboard(client_id):
    """
    Retorna dados do dashboard para um cliente específico
    """
    try:
        # Validar acesso
        if not validate_client_access(client_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Período para análise (padrão: últimos 30 dias)
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Query para dados do dashboard
        query = """
        WITH campaign_summary AS (
            SELECT 
                c.client_id,
                c.client_name,
                COUNT(DISTINCT camp.campaign_id) as total_campaigns,
                COUNT(DISTINCT CASE WHEN camp.status = 'active' THEN camp.campaign_id END) as active_campaigns,
                SUM(camp.budget) as total_budget
            FROM `automatizar-452311.south_media_campaigns.clients` c
            LEFT JOIN `automatizar-452311.south_media_campaigns.campaigns` camp ON c.client_id = camp.client_id
            WHERE c.client_id = @client_id
            GROUP BY c.client_id, c.client_name
        ),
        metrics_summary AS (
            SELECT 
                client_id,
                SUM(impressions) as total_impressions,
                SUM(clicks) as total_clicks,
                SUM(cost) as total_cost,
                SUM(conversions) as total_conversions,
                AVG(ctr) as avg_ctr,
                AVG(cpm) as avg_cpm,
                AVG(cpc) as avg_cpc
            FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
            WHERE client_id = @client_id 
            AND date BETWEEN @start_date AND @end_date
            GROUP BY client_id
        ),
        device_breakdown AS (
            SELECT 
                device_type,
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(cost) as cost
            FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
            WHERE client_id = @client_id 
            AND date BETWEEN @start_date AND @end_date
            GROUP BY device_type
        ),
        daily_performance AS (
            SELECT 
                date,
                SUM(cost) as daily_cost,
                SUM(impressions) as daily_impressions,
                SUM(clicks) as daily_clicks,
                AVG(cpc) as daily_cpc
            FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
            WHERE client_id = @client_id 
            AND date BETWEEN @start_date AND @end_date
            GROUP BY date
            ORDER BY date
        )
        SELECT 
            cs.*,
            COALESCE(ms.total_impressions, 0) as total_impressions,
            COALESCE(ms.total_clicks, 0) as total_clicks,
            COALESCE(ms.total_cost, 0) as total_cost,
            COALESCE(ms.total_conversions, 0) as total_conversions,
            COALESCE(ms.avg_ctr, 0) as avg_ctr,
            COALESCE(ms.avg_cpm, 0) as avg_cpm,
            COALESCE(ms.avg_cpc, 0) as avg_cpc
        FROM campaign_summary cs
        LEFT JOIN metrics_summary ms ON cs.client_id = ms.client_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("client_id", "STRING", client_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date)
            ]
        )
        
        # Executar query principal
        results = bq_client.query(query, job_config=job_config)
        dashboard_data = None
        
        for row in results:
            dashboard_data = {
                'client_id': row.client_id,
                'client_name': row.client_name,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_campaigns': row.total_campaigns or 0,
                    'active_campaigns': row.active_campaigns or 0,
                    'total_budget': float(row.total_budget or 0),
                    'total_impressions': int(row.total_impressions or 0),
                    'total_clicks': int(row.total_clicks or 0),
                    'total_cost': float(row.total_cost or 0),
                    'total_conversions': int(row.total_conversions or 0),
                    'avg_ctr': float(row.avg_ctr or 0),
                    'avg_cpm': float(row.avg_cpm or 0),
                    'avg_cpc': float(row.avg_cpc or 0)
                }
            }
            break
        
        if not dashboard_data:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        # Buscar breakdown por dispositivo
        device_query = """
        SELECT 
            device_type,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(cost) as cost
        FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
        WHERE client_id = @client_id 
        AND date BETWEEN @start_date AND @end_date
        GROUP BY device_type
        ORDER BY cost DESC
        """
        
        device_results = bq_client.query(device_query, job_config=job_config)
        device_breakdown = []
        
        for row in device_results:
            device_breakdown.append({
                'device_type': row.device_type,
                'impressions': int(row.impressions or 0),
                'clicks': int(row.clicks or 0),
                'cost': float(row.cost or 0)
            })
        
        dashboard_data['device_breakdown'] = device_breakdown
        
        # Buscar performance diária
        daily_query = """
        SELECT 
            date,
            SUM(cost) as daily_cost,
            SUM(impressions) as daily_impressions,
            SUM(clicks) as daily_clicks,
            AVG(cpc) as daily_cpc
        FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
        WHERE client_id = @client_id 
        AND date BETWEEN @start_date AND @end_date
        GROUP BY date
        ORDER BY date
        """
        
        daily_results = bq_client.query(daily_query, job_config=job_config)
        daily_performance = []
        
        for row in daily_results:
            daily_performance.append({
                'date': row.date.isoformat(),
                'cost': float(row.daily_cost or 0),
                'impressions': int(row.daily_impressions or 0),
                'clicks': int(row.daily_clicks or 0),
                'cpc': float(row.daily_cpc or 0)
            })
        
        dashboard_data['daily_performance'] = daily_performance
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Erro ao buscar dashboard do cliente {client_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@client_bp.route('/<client_id>/campaigns', methods=['GET'])
@require_client_auth
def get_client_campaigns(client_id):
    """
    Retorna lista de campanhas do cliente
    """
    try:
        if not validate_client_access(client_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de filtro
        status = request.args.get('status', 'all')
        campaign_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 50, type=int)
        
        # Construir query
        where_conditions = ["c.client_id = @client_id"]
        query_params = [bigquery.ScalarQueryParameter("client_id", "STRING", client_id)]
        
        if status != 'all':
            where_conditions.append("c.status = @status")
            query_params.append(bigquery.ScalarQueryParameter("status", "STRING", status))
        
        if campaign_type != 'all':
            where_conditions.append("c.campaign_type = @campaign_type")
            query_params.append(bigquery.ScalarQueryParameter("campaign_type", "STRING", campaign_type))
        
        query = f"""
        SELECT 
            c.campaign_id,
            c.campaign_name,
            c.campaign_type,
            c.platform,
            c.start_date,
            c.end_date,
            c.budget,
            c.daily_budget,
            c.objective,
            c.status,
            
            -- Métricas agregadas dos últimos 30 dias
            COALESCE(SUM(m.impressions), 0) as total_impressions,
            COALESCE(SUM(m.clicks), 0) as total_clicks,
            COALESCE(SUM(m.cost), 0) as total_cost,
            COALESCE(SUM(m.conversions), 0) as total_conversions,
            COALESCE(AVG(m.ctr), 0) as avg_ctr,
            COALESCE(AVG(m.cpm), 0) as avg_cpm,
            COALESCE(AVG(m.cpc), 0) as avg_cpc,
            
            -- Performance score
            CASE 
                WHEN AVG(m.ctr) > 0.02 AND AVG(m.cpc) < 2.0 THEN 'Excelente'
                WHEN AVG(m.ctr) > 0.01 AND AVG(m.cpc) < 3.0 THEN 'Bom'
                WHEN AVG(m.ctr) > 0.005 THEN 'Regular'
                ELSE 'Precisa Melhorar'
            END as performance_status
            
        FROM `automatizar-452311.south_media_campaigns.campaigns` c
        LEFT JOIN `automatizar-452311.south_media_campaigns.campaign_metrics` m 
            ON c.campaign_id = m.campaign_id 
            AND m.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        WHERE {' AND '.join(where_conditions)}
        GROUP BY c.campaign_id, c.campaign_name, c.campaign_type, c.platform, 
                 c.start_date, c.end_date, c.budget, c.daily_budget, c.objective, c.status
        ORDER BY c.created_at DESC
        LIMIT @limit
        """
        
        query_params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        results = bq_client.query(query, job_config=job_config)
        
        campaigns = []
        for row in results:
            campaigns.append({
                'campaign_id': row.campaign_id,
                'campaign_name': row.campaign_name,
                'campaign_type': row.campaign_type,
                'platform': row.platform,
                'start_date': row.start_date.isoformat() if row.start_date else None,
                'end_date': row.end_date.isoformat() if row.end_date else None,
                'budget': float(row.budget or 0),
                'daily_budget': float(row.daily_budget or 0),
                'objective': row.objective,
                'status': row.status,
                'metrics': {
                    'impressions': int(row.total_impressions or 0),
                    'clicks': int(row.total_clicks or 0),
                    'cost': float(row.total_cost or 0),
                    'conversions': int(row.total_conversions or 0),
                    'ctr': float(row.avg_ctr or 0),
                    'cpm': float(row.avg_cpm or 0),
                    'cpc': float(row.avg_cpc or 0)
                },
                'performance_status': row.performance_status
            })
        
        return jsonify({
            'client_id': client_id,
            'campaigns': campaigns,
            'total_campaigns': len(campaigns),
            'filters': {
                'status': status,
                'type': campaign_type,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar campanhas do cliente {client_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@client_bp.route('/<client_id>/campaign/<campaign_id>/metrics', methods=['GET'])
@require_client_auth
def get_campaign_metrics(client_id, campaign_id):
    """
    Retorna métricas detalhadas de uma campanha específica
    """
    try:
        if not validate_client_access(client_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de período
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Query para métricas da campanha
        query = """
        SELECT 
            date,
            impressions,
            clicks,
            cost,
            conversions,
            ctr,
            cpm,
            cpc,
            device_type,
            age_group,
            gender,
            location
        FROM `automatizar-452311.south_media_campaigns.campaign_metrics`
        WHERE client_id = @client_id 
        AND campaign_id = @campaign_id
        AND date BETWEEN @start_date AND @end_date
        ORDER BY date DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("client_id", "STRING", client_id),
                bigquery.ScalarQueryParameter("campaign_id", "STRING", campaign_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date)
            ]
        )
        
        results = bq_client.query(query, job_config=job_config)
        
        metrics = []
        for row in results:
            metrics.append({
                'date': row.date.isoformat(),
                'impressions': int(row.impressions or 0),
                'clicks': int(row.clicks or 0),
                'cost': float(row.cost or 0),
                'conversions': int(row.conversions or 0),
                'ctr': float(row.ctr or 0),
                'cpm': float(row.cpm or 0),
                'cpc': float(row.cpc or 0),
                'device_type': row.device_type,
                'age_group': row.age_group,
                'gender': row.gender,
                'location': row.location
            })
        
        return jsonify({
            'client_id': client_id,
            'campaign_id': campaign_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas da campanha {campaign_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@client_bp.route('/<client_id>/insights', methods=['GET'])
@require_client_auth
def get_client_insights(client_id):
    """
    Retorna insights e recomendações para o cliente
    """
    try:
        if not validate_client_access(client_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar insights ativos
        query = """
        SELECT 
            insight_id,
            campaign_id,
            insight_type,
            title,
            description,
            recommendation,
            impact_level,
            supporting_data,
            created_at
        FROM `automatizar-452311.south_media_campaigns.campaign_insights`
        WHERE client_id = @client_id 
        AND status = 'active'
        AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP())
        ORDER BY 
            CASE impact_level 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            created_at DESC
        LIMIT 20
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
            ]
        )
        
        results = bq_client.query(query, job_config=job_config)
        
        insights = []
        for row in results:
            insights.append({
                'insight_id': row.insight_id,
                'campaign_id': row.campaign_id,
                'insight_type': row.insight_type,
                'title': row.title,
                'description': row.description,
                'recommendation': row.recommendation,
                'impact_level': row.impact_level,
                'supporting_data': json.loads(row.supporting_data) if row.supporting_data else {},
                'created_at': row.created_at.isoformat()
            })
        
        return jsonify({
            'client_id': client_id,
            'insights': insights,
            'total_insights': len(insights)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar insights do cliente {client_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@client_bp.route('/<client_id>/auth/login', methods=['POST'])
def client_login(client_id):
    """
    Endpoint para login de cliente (gera token de acesso)
    """
    try:
        from ..auth.client_auth import create_client_session
        
        # Criar sessão para o cliente
        session_data = create_client_session(client_id)
        
        if not session_data:
            return jsonify({'error': 'Cliente não encontrado ou inativo'}), 404
        
        return jsonify({
            'success': True,
            'token': session_data['token'],
            'client_info': session_data['client_info'],
            'expires_in': session_data['expires_in']
        })
        
    except Exception as e:
        logger.error(f"Erro no login do cliente {client_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoint para validar token
@client_bp.route('/<client_id>/auth/validate', methods=['GET'])
@require_client_auth
def validate_token(client_id):
    """
    Valida se o token atual ainda é válido
    """
    return jsonify({
        'valid': True,
        'client_id': client_id
    })

