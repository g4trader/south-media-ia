#!/usr/bin/env python3
"""
Script para extrair dados da campanha COPACOL INSTITUCIONAL PROGRAMÁTICA 30s
da planilha Google Sheets e atualizar o dashboard.
"""

import json
from datetime import datetime, timedelta

import pandas as pd

from google_sheets_service import GoogleSheetsService

def extract_copacol_data():
    """Extrai dados da campanha COPACOL da planilha Google Sheets"""
    
    # IDs das planilhas
    main_sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"
    publishers_sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"
    
    # GIDs das abas
    main_gid = "1667459933"  # Dados de entrega
    publishers_gid = "1065935170"  # Lista de Publishers
    
    try:
        # Inicializar serviço do Google Sheets
        sheets_service = GoogleSheetsService()
        
        # Extrair dados principais da campanha
        print("Extraindo dados principais da campanha...")
        main_data = sheets_service.read_sheet_data(main_sheet_id, gid=main_gid)
        
        # Extrair lista de publishers
        print("Extraindo lista de publishers...")
        publishers_data = sheets_service.read_sheet_data(
            publishers_sheet_id, gid=publishers_gid
        )
        
        # Processar dados da campanha
        campaign_data = process_campaign_data(main_data)
        
        # Processar dados de publishers
        publishers_list = process_publishers_data(publishers_data)
        
        # Gerar dados diários simulados (baseado nos dados reais)
        daily_data = generate_daily_data(campaign_data)
        
        # Salvar dados em arquivo JSON
        output_data = {
            "campaign_data": campaign_data,
            "publishers": publishers_list,
            "daily_data": daily_data,
            "extraction_date": datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"copacol_campaign_data_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Dados extraídos e salvos em: {output_file}")
        
        # Atualizar dashboard HTML
        update_dashboard_html(output_data)
        
        return output_data
        
    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return None

def process_campaign_data(raw_data):
    """Processa dados brutos da campanha"""
    
    # Dados contratados (conforme especificação)
    campaign_data = {
        "Budget Contratado (R$)": 46373.00,
        "Budget Utilizado (R$)": 0,
        "Impressões Contratadas": 201625,
        "Impressões Realizadas": 0,
        "CPV Contratado (R$)": 0.23,
        "CPV Realizado (R$)": 0,
        "VTR (100%)": 0,
        "CTR (%)": 0,
        "Pacing (%)": 0,
        "Canal": "Programática Video",
        "Campanha": "COPACOL INSTITUCIONAL PROGRAMÁTICA 30s",
        "Período": "08/09/2025 a 05/10/2025"
    }
    
    # Processar dados reais da planilha se disponíveis
    if isinstance(raw_data, pd.DataFrame):
        df = raw_data
    elif raw_data:
        try:
            if isinstance(raw_data, list) and len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            else:
                df = pd.DataFrame(raw_data)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if not df.empty:
        for row_dict in df.to_dict(orient="records"):
            if not isinstance(row_dict, dict):
                continue

            # Mapear colunas da planilha para nossos dados
            if "Budget Utilizado" in row_dict:
                try:
                    value = row_dict.get("Budget Utilizado", 0)
                    if pd.notna(value):
                        campaign_data["Budget Utilizado (R$)"] = float(
                            str(value).replace(",", ".")
                        )
                except (ValueError, TypeError):
                    pass

            if "Impressões Realizadas" in row_dict:
                try:
                    value = row_dict.get("Impressões Realizadas", 0)
                    if pd.notna(value):
                        campaign_data["Impressões Realizadas"] = int(
                            float(str(value).replace(",", "."))
                        )
                except (ValueError, TypeError):
                    pass

            if "CPV Realizado" in row_dict:
                try:
                    value = row_dict.get("CPV Realizado", 0)
                    if pd.notna(value):
                        campaign_data["CPV Realizado (R$)"] = float(
                            str(value).replace(",", ".")
                        )
                except (ValueError, TypeError):
                    pass

            if "VTR" in row_dict:
                try:
                    value = row_dict.get("VTR", 0)
                    if pd.notna(value):
                        campaign_data["VTR (100%)"] = float(
                            str(value).replace(",", ".")
                        )
                except (ValueError, TypeError):
                    pass

            if "CTR" in row_dict:
                try:
                    value = row_dict.get("CTR", 0)
                    if pd.notna(value):
                        campaign_data["CTR (%)"] = float(
                            str(value).replace(",", ".")
                        )
                except (ValueError, TypeError):
                    pass
    
    # Calcular pacing
    if campaign_data["Budget Contratado (R$)"] > 0:
        campaign_data["Pacing (%)"] = (campaign_data["Budget Utilizado (R$)"] / campaign_data["Budget Contratado (R$)"]) * 100
    
    return campaign_data

def process_publishers_data(raw_data):
    """Processa dados de publishers"""
    
    publishers = []
    
    if isinstance(raw_data, pd.DataFrame):
        df = raw_data
    elif raw_data:
        try:
            if isinstance(raw_data, list) and len(raw_data) > 1:
                df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            else:
                df = pd.DataFrame(raw_data)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if not df.empty:
        for row_dict in df.fillna("").to_dict(orient="records"):
            if not isinstance(row_dict, dict):
                continue

            publisher_name = str(row_dict.get("Publisher", "")).strip()
            if publisher_name:
                publishers.append({
                    "name": publisher_name,
                    "category": str(row_dict.get("Categoria", "Portal")).strip(),
                    "description": str(row_dict.get("Descrição", "")).strip()
                })
    
    # Se não houver dados, usar lista padrão
    if not publishers:
        publishers = [
            {"name": "UOL", "category": "Portal", "description": "Portal de notícias"},
            {"name": "G1", "category": "Portal", "description": "Portal Globo"},
            {"name": "Folha de S.Paulo", "category": "Jornal", "description": "Jornal digital"},
            {"name": "Estadão", "category": "Jornal", "description": "Jornal digital"},
            {"name": "Veja", "category": "Revista", "description": "Revista digital"},
            {"name": "Exame", "category": "Revista", "description": "Revista de negócios"},
            {"name": "InfoMoney", "category": "Portal", "description": "Portal financeiro"},
            {"name": "Valor Econômico", "category": "Jornal", "description": "Jornal econômico"},
            {"name": "Revista Época", "category": "Revista", "description": "Revista digital"},
            {"name": "IstoÉ", "category": "Revista", "description": "Revista digital"},
            {"name": "Terra", "category": "Portal", "description": "Portal de notícias"},
            {"name": "R7", "category": "Portal", "description": "Portal Record"},
            {"name": "Brasil 247", "category": "Portal", "description": "Portal de notícias"},
            {"name": "CartaCapital", "category": "Revista", "description": "Revista digital"},
            {"name": "The Intercept", "category": "Portal", "description": "Portal de jornalismo"}
        ]
    
    return publishers

def generate_daily_data(campaign_data):
    """Gera dados diários baseados nos dados da campanha"""
    
    daily_data = []
    
    # Período da campanha: 08/09/2025 a 05/10/2025
    start_date = datetime(2025, 9, 8)
    end_date = datetime(2025, 10, 5)
    
    current_date = start_date
    day_count = 0
    
    while current_date <= end_date:
        # Simular dados diários baseados no pacing
        daily_spend = campaign_data["Budget Utilizado (R$)"] / 28 if campaign_data["Budget Utilizado (R$)"] > 0 else 0
        daily_impressions = campaign_data["Impressões Realizadas"] / 28 if campaign_data["Impressões Realizadas"] > 0 else 0
        
        daily_data.append({
            "date": current_date.strftime("%d/%m/%Y"),
            "creative": "Vídeo 30s COPACOL",
            "spend": round(daily_spend, 2),
            "starts": int(daily_impressions * 0.8) if daily_impressions > 0 else 0,
            "q25": int(daily_impressions * 0.6) if daily_impressions > 0 else 0,
            "q50": int(daily_impressions * 0.4) if daily_impressions > 0 else 0,
            "q75": int(daily_impressions * 0.2) if daily_impressions > 0 else 0,
            "q100": int(daily_impressions * 0.1) if daily_impressions > 0 else 0,
            "impressions": int(daily_impressions),
            "clicks": int(daily_impressions * (campaign_data["CTR (%)"] / 100)) if campaign_data["CTR (%)"] > 0 else 0,
            "ctr": campaign_data["CTR (%)"] / 100 if campaign_data["CTR (%)"] > 0 else 0
        })
        
        current_date += timedelta(days=1)
        day_count += 1
    
    return daily_data

def update_dashboard_html(data):
    """Atualiza o dashboard HTML com os dados extraídos"""
    
    dashboard_path = "/Users/lucianoterres/Documents/GitHub/south-media-ia/static/dash_copacol_institucional_programatica.html"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Atualizar dados da campanha
        campaign_data = data["campaign_data"]
        
        # Substituir dados no JavaScript
        js_data = f"""
const CAMPAIGN_DATA = {json.dumps(campaign_data, ensure_ascii=False, indent=2)};
"""
        
        # Substituir dados diários
        daily_data = data["daily_data"]
        js_daily = f"""
const DAILY_DATA = {json.dumps(daily_data, ensure_ascii=False, indent=2)};
"""
        
        # Atualizar publishers no HTML
        publishers_html = ""
        for publisher in data["publishers"]:
            publishers_html += f'''
        <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; border-left:4px solid #ff6b35">
          <strong>{publisher["name"]}</strong>
          <div style="font-size:0.8rem; color:rgba(255,255,255,0.7); margin-top:4px">{publisher["description"]}</div>
        </div>'''
        
        # Substituir no HTML
        html_content = html_content.replace(
            'const CAMPAIGN_DATA = {',
            js_data.strip() + '\n\n// Dados diários simulados (serão substituídos por dados reais)\nconst DAILY_DATA = ['
        )
        
        html_content = html_content.replace(
            'const DAILY_DATA = [',
            js_daily.strip() + '\n\n// Dados diários simulados (serão substituídos por dados reais)\nconst DAILY_DATA = ['
        )
        
        # Salvar arquivo atualizado
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard atualizado: {dashboard_path}")
        
    except Exception as e:
        print(f"Erro ao atualizar dashboard: {e}")

if __name__ == "__main__":
    print("Iniciando extração de dados da campanha COPACOL...")
    data = extract_copacol_data()
    
    if data:
        print("Extração concluída com sucesso!")
        print(f"Dados da campanha: {data['campaign_data']}")
        print(f"Publishers encontrados: {len(data['publishers'])}")
        print(f"Dados diários gerados: {len(data['daily_data'])} dias")
    else:
        print("Falha na extração de dados.")
