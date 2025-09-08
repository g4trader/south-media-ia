from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import pandas as pd
import os
from datetime import datetime
import logging
import re

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

def process_tsv_data():
    """Processa os arquivos TSV e retorna dados do dashboard"""
    try:
        # Caminho para os arquivos TSV
        tsv_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/static/tsv"
        
        # Dados contratados (arquivos que começam com "dash -")
        contract_data = {}
        delivery_data = []
        
        # Processar arquivos de contrato
        for filename in os.listdir(tsv_path):
            if filename.startswith("dash -") and filename.endswith(".tsv"):
                channel = filename.replace("dash - ", "").replace(" (1).tsv", "").replace(" (1)", "")
                
                try:
                    df = pd.read_csv(os.path.join(tsv_path, filename), sep='\t', encoding='utf-8')
                    
                    # Extrair dados contratados
                    if not df.empty:
                        row = df.iloc[0]
                        contract_data[channel] = {
                            "Budget Contratado (R$)": safe_float(row.get("Budget Contratado (R$)", 0)),
                            "Budget Utilizado (R$)": safe_float(row.get("Budget Utilizado (R$)", 0)),
                            "Impressões": safe_float(row.get("Impressões", 0)),
                            "Cliques": safe_float(row.get("Cliques", 0)),
                            "CTR": safe_float(row.get("CTR", 0)),
                            "VC (100%)": safe_float(row.get("VC (100%)", 0)),
                            "VTR (100%)": safe_float(row.get("VTR (100%)", 0)),
                            "CPV (R$)": safe_float(row.get("CPV (R$)", 0)),
                            "CPM (R$)": safe_float(row.get("CPM (R$)", 0)),
                            "Pacing (%)": safe_float(row.get("Pacing (%)", 0))
                        }
                except Exception as e:
                    logger.error(f"Erro ao processar {filename}: {e}")
                    continue
        
        # Processar arquivos de entrega diária com lógica específica por canal
        for filename in os.listdir(tsv_path):
            if not filename.startswith("dash -") and filename.endswith(".tsv"):
                # Extrair canal do nome do arquivo
                if "CTV" in filename:
                    channel = "CTV"
                    process_ctv_delivery(os.path.join(tsv_path, filename), delivery_data)
                elif "Disney" in filename:
                    channel = "Disney"
                    process_disney_delivery(os.path.join(tsv_path, filename), delivery_data)
                elif "Footfall" in filename:
                    channel = "Footfall Display"
                    process_footfall_delivery(os.path.join(tsv_path, filename), delivery_data)
                elif "Netflix" in filename:
                    channel = "Netflix"
                    process_netflix_delivery(os.path.join(tsv_path, filename), delivery_data)
                elif "TikTok" in filename:
                    channel = "TikTok"
                    process_tiktok_delivery(os.path.join(tsv_path, filename), delivery_data)
                elif "Youtube" in filename:
                    channel = "YouTube"
                    process_youtube_delivery(os.path.join(tsv_path, filename), delivery_data)
        
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
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar dados TSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados: {str(e)}"
        )

def process_ctv_delivery(filepath, delivery_data):
    """Processa dados de entrega do CTV"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 7:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                starts = safe_float(row.iloc[2])
                q25 = safe_float(row.iloc[3])
                q50 = safe_float(row.iloc[4])
                q75 = safe_float(row.iloc[5])
                q100 = safe_float(row.iloc[6])
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "CTV",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": starts,
                        "q25": q25,
                        "q50": q50,
                        "q75": q75,
                        "q100": q100,
                        "impressions": None,
                        "clicks": None,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar CTV delivery: {e}")

def process_footfall_delivery(filepath, delivery_data):
    """Processa dados de entrega do Footfall Display"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 4:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                impressions = safe_float(row.iloc[2])
                clicks = safe_float(row.iloc[3])
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "Footfall Display",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": None,
                        "q25": None,
                        "q50": None,
                        "q75": None,
                        "q100": None,
                        "impressions": impressions,
                        "clicks": clicks,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar Footfall delivery: {e}")

def process_tiktok_delivery(filepath, delivery_data):
    """Processa dados de entrega do TikTok"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 4:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "TikTok",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": None,
                        "q25": None,
                        "q50": None,
                        "q75": None,
                        "q100": None,
                        "impressions": None,
                        "clicks": None,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar TikTok delivery: {e}")

def process_youtube_delivery(filepath, delivery_data):
    """Processa dados de entrega do YouTube"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 4:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "YouTube",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": None,
                        "q25": None,
                        "q50": None,
                        "q75": None,
                        "q100": None,
                        "impressions": None,
                        "clicks": None,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar YouTube delivery: {e}")

def process_disney_delivery(filepath, delivery_data):
    """Processa dados de entrega do Disney"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 4:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "Disney",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": None,
                        "q25": None,
                        "q50": None,
                        "q75": None,
                        "q100": None,
                        "impressions": None,
                        "clicks": None,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar Disney delivery: {e}")

def process_netflix_delivery(filepath, delivery_data):
    """Processa dados de entrega do Netflix"""
    try:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
        
        for _, row in df.iterrows():
            if len(row) >= 4:
                date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                spend = safe_float(row.iloc[-1])  # Última coluna
                
                if date and spend and spend > 0:
                    delivery_data.append({
                        "date": str(date),
                        "channel": "Netflix",
                        "creative": str(creative) if creative else "",
                        "spend": spend,
                        "starts": None,
                        "q25": None,
                        "q50": None,
                        "q75": None,
                        "q100": None,
                        "impressions": None,
                        "clicks": None,
                        "visits": None
                    })
    except Exception as e:
        logger.error(f"Erro ao processar Netflix delivery: {e}")

@router.get("/data")
async def get_dashboard_data():
    """Endpoint para obter dados atualizados do dashboard"""
    try:
        data = process_tsv_data()
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
