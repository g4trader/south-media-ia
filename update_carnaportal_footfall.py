#!/usr/bin/env python3
"""
Script para atualizar o dashboard dash_portal_auto_shopping_jan2026_carnaPortal_footfall.html
com dados do Google Sheet: https://docs.google.com/spreadsheets/d/1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY/edit?gid=1939638014#gid=1939638014
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(__file__))

from real_google_sheets_extractor import RealGoogleSheetsExtractor, CampaignConfig

# Configurações
SPREADSHEET_ID = "1tLz31iH7xVJgIvdGbMlfs8kf0mdeWhZuG8D8x1n3fDY"
DASHBOARD_PATH = "static/dash_portal_auto_shopping_jan2026_carnaPortal_footfall.html"
CLIENT = "Portal Auto Shopping"
CAMPAIGN_NAME = "Campanha Fevereiro (Santander) - CarnaPortal"
CAMPAIGN_KEY = "portal_auto_shopping_jan2026_carnaPortal_footfall"
CHANNEL = "Drive to store"
KPI = "CPM"


def extrair_dados_com_extrator():
    """Extrai dados usando o RealGoogleSheetsExtractor"""
    print("📥 Extraindo dados usando RealGoogleSheetsExtractor...")
    
    config = CampaignConfig(
        client=CLIENT,
        campaign=CAMPAIGN_NAME,
        campaign_key=CAMPAIGN_KEY,
        sheet_id=SPREADSHEET_ID
    )
    # Adicionar channel e kpi se necessário
    config.channel = CHANNEL
    config.kpi = KPI
    
    extractor = RealGoogleSheetsExtractor(config)
    extracted_data = extractor.extract_data()
    
    if not extracted_data:
        print("❌ Não foi possível extrair dados")
        return None, None, None, None
    
    print("✅ Dados extraídos com sucesso!")
    
    # Extrair dados de contrato
    contract_data = extracted_data.get('contract', {})
    
    # Extrair dados diários
    daily_data = extracted_data.get('daily_data', [])
    
    # Converter formato dos dados diários
    daily_formatted = []
    for item in daily_data:
        daily_formatted.append({
            "date": item.get('date', ''),
            "channel": item.get('channel', 'Footfall Display'),
            "creative": item.get('creative', ''),
            "spend": float(item.get('spend', 0)),
            "starts": 0,
            "q25": 0,
            "q50": 0,
            "q75": 0,
            "q100": 0,
            "impressions": int(item.get('impressions', 0)),
            "clicks": int(item.get('clicks', 0)),
            "visits": 0
        })
    
    # Tentar extrair dados de footfall (se houver)
    footfall_points = []
    # O extrator pode não ter dados de footfall, então vamos tentar ler diretamente
    # Por enquanto, retornar lista vazia
    
    return contract_data, daily_formatted, footfall_points, extracted_data


def calcular_metricas_totais(daily_data, contract_data):
    """Calcula métricas totais a partir dos dados diários"""
    total_spend = sum(d.get('spend', 0) for d in daily_data)
    total_impressions = sum(d.get('impressions', 0) for d in daily_data)
    total_clicks = sum(d.get('clicks', 0) for d in daily_data)
    
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    
    budget_contratado = contract_data.get('budget_contracted', contract_data.get('Budget Contratado (R$)', 3750.0))
    pacing = (total_spend / budget_contratado * 100) if budget_contratado > 0 else 0
    
    return {
        "Budget Utilizado (R$)": total_spend,
        "Impressões": total_impressions,
        "Cliques": total_clicks,
        "CTR (%)": ctr / 100,  # Converter para decimal
        "CPM (R$)": cpm,
        "Pacing (%)": pacing / 100  # Converter para decimal
    }


def atualizar_dashboard_html(cons_data, per_data, daily_data, footfall_points):
    """Atualiza o arquivo HTML com os novos dados"""
    dashboard_path = Path(DASHBOARD_PATH)
    
    if not dashboard_path.exists():
        print(f"❌ Arquivo não encontrado: {dashboard_path}")
        return False
    
    print(f"📝 Lendo arquivo HTML...")
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Atualizar CONS
    cons_json = json.dumps(cons_data, ensure_ascii=False, indent=2)
    cons_pattern = r'const CONS = \{[\s\S]*?\};'
    cons_replacement = f'const CONS = {cons_json};'
    html_content = re.sub(cons_pattern, cons_replacement, html_content)
    
    # Atualizar PER
    per_json = json.dumps(per_data, ensure_ascii=False, indent=2)
    per_pattern = r'const PER = \[[\s\S]*?\];'
    per_replacement = f'const PER = {per_json};'
    html_content = re.sub(per_pattern, per_replacement, html_content)
    
    # Atualizar DAILY
    daily_json = json.dumps(daily_data, ensure_ascii=False, indent=2)
    daily_pattern = r'const DAILY = \[[\s\S]*?\];'
    daily_replacement = f'const DAILY = {daily_json};'
    html_content = re.sub(daily_pattern, daily_replacement, html_content)
    
    # Atualizar FOOTFALL_POINTS
    footfall_json = json.dumps(footfall_points, ensure_ascii=False, indent=2)
    footfall_pattern = r'const FOOTFALL_POINTS = \[[\s\S]*?\];'
    footfall_replacement = f'const FOOTFALL_POINTS = {footfall_json};'
    html_content = re.sub(footfall_pattern, footfall_replacement, html_content)
    
    # Salvar arquivo
    print(f"💾 Salvando arquivo atualizado...")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard atualizado com sucesso!")
    return True


def main():
    print("🚀 Iniciando atualização do dashboard CarnaPortal Footfall...")
    print(f"📊 Google Sheet: {SPREADSHEET_ID}")
    print(f"📄 Dashboard: {DASHBOARD_PATH}\n")
    
    # 1. Extrair dados usando o extrator real
    contract_data, daily_data, footfall_points, extracted_data = extrair_dados_com_extrator()
    
    if contract_data is None:
        print("❌ Não foi possível extrair dados")
        return
    
    # 2. Calcular métricas totais
    print("\n📊 Calculando métricas totais...")
    total_metrics = calcular_metricas_totais(daily_data, contract_data)
    
    # 3. Preparar dados CONS
    budget_contratado = contract_data.get('budget_contracted', contract_data.get('Budget Contratado (R$)', 3750.0))
    cpm_contratado = contract_data.get('cpm_contracted', contract_data.get('CPM (R$)', 25.0))
    
    cons_data = {
        "Budget Contratado (R$)": budget_contratado,
        **total_metrics,
        "VC (100%)": 0,
        "VTR (100%)": 0,
        "CPV (R$)": 0
    }
    
    # 4. Preparar dados PER
    per_data = [{
        "Canal": "Footfall Display",
        "Budget Contratado (R$)": cons_data["Budget Contratado (R$)"],
        "Budget Utilizado (R$)": cons_data["Budget Utilizado (R$)"],
        "Impressões": cons_data["Impressões"],
        "Cliques": cons_data["Cliques"],
        "CTR (%)": cons_data["CTR (%)"],
        "VC (100%)": 0,
        "VTR (100%)": 0,
        "CPV (R$)": 0,
        "CPM (R$)": cpm_contratado,
        "Pacing (%)": cons_data["Pacing (%)"],
        "Criativos Únicos": len(set(d.get('creative', '') for d in daily_data if d.get('creative')))
    }]
    
    # 5. Atualizar HTML
    print("\n🔄 Atualizando arquivo HTML...")
    sucesso = atualizar_dashboard_html(cons_data, per_data, daily_data, footfall_points)
    
    if sucesso:
        print("\n✅ Atualização concluída com sucesso!")
        print(f"   - {len(daily_data)} registros diários")
        print(f"   - {len(footfall_points)} pontos de footfall")
        print(f"   - Budget utilizado: R$ {cons_data['Budget Utilizado (R$)']:.2f}")
        print(f"   - Impressões: {cons_data['Impressões']:,}")
    else:
        print("\n❌ Erro ao atualizar dashboard")


if __name__ == "__main__":
    main()
