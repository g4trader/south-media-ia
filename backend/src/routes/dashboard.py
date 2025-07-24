from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from ..services.bigquery_service import BigQueryService
import os

dashboard_bp = Blueprint("dashboard", __name__)
bigquery_service = BigQueryService()


@dashboard_bp.route("/admin/stats", methods=["GET"])
@cross_origin()
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        stats = bigquery_service.get_admin_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/admin/clients", methods=["GET"])
@cross_origin()
def get_clients():
    """Get all clients"""
    try:
        clients = bigquery_service.get_clients()
        return jsonify(clients)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/admin/clients/<client_id>/campaigns", methods=["GET"])
@cross_origin()
def get_client_campaigns(client_id):
    """Get campaigns for a specific client"""
    try:
        campaigns = bigquery_service.get_client_campaigns(client_id)
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/campaign/<campaign_id>", methods=["GET"])
@cross_origin()
def get_campaign_dashboard(campaign_id):
    """Get complete campaign dashboard data"""
    try:
        # Get campaign basic data
        campaign_data = bigquery_service.get_campaign_data(campaign_id)
        if not campaign_data:
            return jsonify({"success": False, "error": "Campaign not found"}), 404

        # Get strategies data
        strategies = bigquery_service.get_strategies_data(campaign_id)

        # Get device breakdown
        device_breakdown = bigquery_service.get_device_breakdown(campaign_id)

        # Get performance history for charts
        performance_history = bigquery_service.get_performance_history(campaign_id)

        # Combine all data
        dashboard_data = {
            "campaign": campaign_data,
            "strategies": strategies,
            "device_breakdown": device_breakdown,
            "performance_history": performance_history,
        }

        return jsonify(dashboard_data)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/campaign/<campaign_id>/strategies", methods=["GET"])
@cross_origin()
def get_campaign_strategies(campaign_id):
    """Get strategies for a specific campaign"""
    try:
        strategies = bigquery_service.get_strategies_data(campaign_id)
        return jsonify(strategies)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/campaign/<campaign_id>/device-breakdown", methods=["GET"])
@cross_origin()
def get_campaign_device_breakdown(campaign_id):
    """Get device breakdown for a specific campaign"""
    try:
        device_breakdown = bigquery_service.get_device_breakdown(campaign_id)
        return jsonify(device_breakdown)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dashboard_bp.route("/campaign/<campaign_id>/performance-history", methods=["GET"])
@cross_origin()
def get_campaign_performance_history(campaign_id):
    """Get performance history for charts"""
    try:
        performance_history = bigquery_service.get_performance_history(campaign_id)
        return jsonify(performance_history)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


