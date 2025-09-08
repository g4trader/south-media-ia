from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import pandas as pd
import os
from datetime import datetime
import logging
import re
from src.services.sheets_service import SheetsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def safe_float(value):
    """Converte valor para float de forma segura"""
    if pd.isna(value) or value == "" or value is None:
        return None
    
    # Se já é numérico
    if isinstance(value, (int, float)):
        return float(value)
    
    # Converter string para float
    try:
        # Remover caracteres não numéricos exceto ponto e vírgula
        clean_value = str(value).replace(',', '.').replace('R$', '').replace(' ', '')
        # Remover caracteres não numéricos
        clean_value = re.sub(r'[^\d.-]', '', clean_value)
        
        if clean_value == '' or clean_value == '-':
            return None
            
        return float(clean_value)
    except (ValueError, TypeError):
        return None

def process_dashboard_data():
    """Processa dados do dashboard a partir do Google Sheets"""
    try:
        # Inicializar serviço do Google Sheets
        sheets_service = SheetsService()
        
        if not sheets_service.is_available():
            logger.warning("Google Sheets não disponível, usando dados mock")
            return get_mock_data()
        
        # Obter dados contratados
        contract_data = sheets_service.get_contract_data()
        
        # Obter dados de entrega diária
        delivery_data = sheets_service.get_all_channels_data()
        
        # Calcular dados consolidados
        total_budget = sum(data.get("Budget Contratado (R$)", 0) or 0 for data in contract_data.values())
        total_used = sum(data.get("Budget Utilizado (R$)", 0) or 0 for data in contract_data.values())
        total_impressions = sum(data.get("Impressões", 0) or 0 for data in contract_data.values())
        total_clicks = sum(data.get("Cliques", 0) or 0 for data in contract_data.values())
        total_vc = sum(data.get("VC (100%)", 0) or 0 for data in contract_data.values())
        
        consolidated = {
            "Budget Contratado (R$)": total_budget,
            "Budget Utilizado (R$)": total_used,
            "Impressões": total_impressions,
            "Cliques": total_clicks,
            "CTR (cons.)": total_clicks / total_impressions if total_impressions > 0 else 0,
            "VC (100%)": total_vc,
            "VTR (cons.)": sum(data.get("VTR (100%)", 0) or 0 for data in contract_data.values()) / len(contract_data) if contract_data else 0,
            "CPM (R$) cons.": (total_used / total_impressions * 1000) if total_impressions > 0 else 0,
            "CPV (R$) cons.": (total_used / total_vc) if total_vc > 0 else 0
        }
        
        return {
            "consolidated": consolidated,
            "channels": contract_data,
            "daily": delivery_data,
            "last_updated": datetime.now().isoformat(),
            "data_source": "google_sheets"
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar dados do dashboard: {e}")
        # Em caso de erro, retornar dados mock
        return get_mock_data()

def get_mock_data():
    """Retorna dados mock quando Google Sheets não está disponível"""
    contract_data = {
        "CTV": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": None,
            "Cliques": None,
            "CTR": None,
            "VC (100%)": 14718.0,
            "VTR (100%)": 0.8329,
            "CPV (R$)": 0.2,
            "CPM (R$)": None,
            "Pacing (%)": 0.247
        },
        "Disney": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": None,
            "Cliques": None,
            "CTR": None,
            "VC (100%)": 14718.0,
            "VTR (100%)": 0.8329,
            "CPV (R$)": 0.2,
            "CPM (R$)": None,
            "Pacing (%)": 0.247
        },
        "Footfall Display": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": 14718.0,
            "Cliques": 147.0,
            "CTR": 0.01,
            "VC (100%)": None,
            "VTR (100%)": None,
            "CPV (R$)": None,
            "CPM (R$)": 0.2,
            "Pacing (%)": 0.247
        },
        "Netflix": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": None,
            "Cliques": None,
            "CTR": None,
            "VC (100%)": 14718.0,
            "VTR (100%)": 0.8329,
            "CPV (R$)": 0.2,
            "CPM (R$)": None,
            "Pacing (%)": 0.247
        },
        "TikTok": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": 14718.0,
            "Cliques": 147.0,
            "CTR": 0.01,
            "VC (100%)": 14718.0,
            "VTR (100%)": 0.8329,
            "CPV (R$)": 0.2,
            "CPM (R$)": 0.2,
            "Pacing (%)": 0.247
        },
        "YouTube": {
            "Budget Contratado (R$)": 11895.55,
            "Budget Utilizado (R$)": 2943.6,
            "Impressões": None,
            "Cliques": None,
            "CTR": None,
            "VC (100%)": 14718.0,
            "VTR (100%)": 0.8329,
            "CPV (R$)": 0.2,
            "CPM (R$)": None,
            "Pacing (%)": 0.247
        }
    }
    
    # Dados mock de entrega diária
    delivery_data = [
        {
            "date": "01/09/2025",
            "channel": "CTV",
            "creative": "Sonho 15s",
            "spend": 171.8,
            "starts": 891.0,
            "q25": 889.0,
            "q50": 871.0,
            "q75": 864.0,
            "q100": 859.0,
            "impressions": None,
            "clicks": None,
            "visits": None
        }
    ]
    
    # Calcular consolidado
    total_budget = sum(data.get("Budget Contratado (R$)", 0) or 0 for data in contract_data.values())
    total_used = sum(data.get("Budget Utilizado (R$)", 0) or 0 for data in contract_data.values())
    total_impressions = sum(data.get("Impressões", 0) or 0 for data in contract_data.values())
    total_clicks = sum(data.get("Cliques", 0) or 0 for data in contract_data.values())
    total_vc = sum(data.get("VC (100%)", 0) or 0 for data in contract_data.values())
    
    consolidated = {
        "Budget Contratado (R$)": total_budget,
        "Budget Utilizado (R$)": total_used,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (cons.)": total_clicks / total_impressions if total_impressions > 0 else 0,
        "VC (100%)": total_vc,
        "VTR (cons.)": sum(data.get("VTR (100%)", 0) or 0 for data in contract_data.values()) / len(contract_data) if contract_data else 0,
        "CPM (R$) cons.": (total_used / total_impressions * 1000) if total_impressions > 0 else 0,
        "CPV (R$) cons.": (total_used / total_vc) if total_vc > 0 else 0
    }
    
    return {
        "consolidated": consolidated,
        "channels": contract_data,
        "daily": delivery_data,
        "last_updated": datetime.now().isoformat(),
        "data_source": "mock"
    }


@router.get("/data")
async def get_dashboard_data():
    """Endpoint para obter dados atualizados do dashboard"""
    try:
        data = process_dashboard_data()
        return data
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados: {str(e)}"
        )

@router.get("/health")
async def dashboard_health():
    """Health check do dashboard"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/test-sheets")
async def test_google_sheets():
    """Testa a conexão com Google Sheets"""
    try:
        sheets_service = SheetsService()
        result = sheets_service.test_connection()
        return result
    except Exception as e:
        logger.error(f"Erro ao testar Google Sheets: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
