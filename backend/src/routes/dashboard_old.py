from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import pandas as pd
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

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
                            "Budget Contratado (R$)": float(row.get("Budget Contratado (R$)", 0)),
                            "Budget Utilizado (R$)": float(row.get("Budget Utilizado (R$)", 0)),
                            "Impressões": float(row.get("Impressões", 0)) if pd.notna(row.get("Impressões")) else None,
                            "Cliques": float(row.get("Cliques", 0)) if pd.notna(row.get("Cliques")) else None,
                            "CTR": float(row.get("CTR", 0)) if pd.notna(row.get("CTR")) else None,
                            "VC (100%)": float(row.get("VC (100%)", 0)) if pd.notna(row.get("VC (100%)")) else None,
                            "VTR (100%)": float(row.get("VTR (100%)", 0)) if pd.notna(row.get("VTR (100%)")) else None,
                            "CPV (R$)": float(row.get("CPV (R$)", 0)) if pd.notna(row.get("CPV (R$)", 0)) else None,
                            "CPM (R$)": float(row.get("CPM (R$)", 0)) if pd.notna(row.get("CPM (R$)", 0)) else None,
                            "Pacing (%)": float(row.get("Pacing (%)", 0)) if pd.notna(row.get("Pacing (%)")) else None
                        }
                except Exception as e:
                    logger.error(f"Erro ao processar {filename}: {e}")
                    continue
        
        # Processar arquivos de entrega diária
        for filename in os.listdir(tsv_path):
            if not filename.startswith("dash -") and filename.endswith(".tsv"):
                # Extrair canal do nome do arquivo
                if "CTV" in filename:
                    channel = "CTV"
                elif "Disney" in filename:
                    channel = "Disney"
                elif "Footfall" in filename:
                    channel = "Footfall Display"
                elif "Netflix" in filename:
                    channel = "Netflix"
                elif "TikTok" in filename:
                    channel = "TikTok"
                elif "Youtube" in filename:
                    channel = "YouTube"
                else:
                    continue
                
                try:
                    df = pd.read_csv(os.path.join(tsv_path, filename), sep='\t', encoding='utf-8')
                    
                    for _, row in df.iterrows():
                        if len(row) >= 4:
                            date = row.iloc[0] if pd.notna(row.iloc[0]) else None
                            creative = row.iloc[1] if pd.notna(row.iloc[1]) else None
                            spend = float(row.iloc[-1]) if pd.notna(row.iloc[-1]) else 0
                            
                            if date and spend > 0:
                                delivery_record = {
                                    "date": str(date),
                                    "channel": channel,
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
                                }
                                
                                # Para canais de vídeo, tentar extrair starts e quartis
                                if channel in ["CTV", "Disney", "Netflix", "YouTube"] and len(row) >= 6:
                                    delivery_record["starts"] = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                                    delivery_record["q25"] = float(row.iloc[3]) if pd.notna(row.iloc[3]) else None
                                    delivery_record["q50"] = float(row.iloc[4]) if pd.notna(row.iloc[4]) else None
                                    delivery_record["q75"] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else None
                                    delivery_record["q100"] = float(row.iloc[6]) if pd.notna(row.iloc[6]) else None
                                
                                # Para canais de display, tentar extrair impressões e cliques
                                elif channel == "Footfall Display" and len(row) >= 4:
                                    delivery_record["impressions"] = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                                    delivery_record["clicks"] = float(row.iloc[3]) if pd.notna(row.iloc[3]) else None
                                
                                delivery_data.append(delivery_record)
                                
                except Exception as e:
                    logger.error(f"Erro ao processar entrega {filename}: {e}")
                    continue
        
        # Calcular dados consolidados
        total_budget = sum(data.get("Budget Contratado (R$)", 0) for data in contract_data.values())
        total_used = sum(data.get("Budget Utilizado (R$)", 0) for data in contract_data.values())
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