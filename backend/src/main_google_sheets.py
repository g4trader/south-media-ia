import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="South Media IA API - Google Sheets Integration",
    version="4.0.0",
    description="API com integração real do Google Sheets para dados do dashboard."
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração das planilhas
SPREADSHEET_IDS = {
    "footfall": "10ttYM3BoqEnEnP0maENnOrE-XrRtC3uvqRTIJr2_pxA",
    "disney": "1-uRCKHOeXsBdGt4qdD2z7fZHR_nLQdNAPLUtMaH5O1o",
    "ctv": "1TGAG1RyOqJRUUYXL52ltayf4MlOYrwvJwolMxToD69U",
    "netflix": "1sU0Y9XZP-wi2ayd_IxYwS0pe8ITmW9oNKDDIKQOv6Fo",
    "tiktok": "1co9l8f7GhhcoWk4HDhUH2kVkUgox73oM",
    "youtube": "1KOh1NpFION9q7434LTEcQ4_s2jAK6tzpghqBVVHKYjo"
}

# Configurar credenciais do Google Sheets
def get_google_sheets_client():
    try:
        # Carregar credenciais do arquivo JSON
        credentials_path = "credentials.json"
        if not os.path.exists(credentials_path):
            raise FileNotFoundError("Arquivo credentials.json não encontrado")
        
        # Definir escopos necessários
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # Carregar credenciais
        credentials = Credentials.from_service_account_file(
            credentials_path, 
            scopes=scopes
        )
        
        # Criar cliente gspread
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"Erro ao configurar Google Sheets: {e}")
        return None

# Função para processar dados de uma planilha
def process_sheet_data(client, spreadsheet_id, channel_name):
    try:
        # Abrir planilha
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Tentar diferentes nomes de abas
        sheet_names = ["Daily", "Entrega Diária", "Dados Diários", "Sheet1"]
        worksheet = None
        
        for sheet_name in sheet_names:
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                break
            except:
                continue
        
        if not worksheet:
            # Se não encontrar nenhuma aba, usar a primeira
            worksheet = spreadsheet.sheet1
        
        # Obter todos os dados
        all_values = worksheet.get_all_values()
        
        if not all_values:
            return {"error": f"Nenhum dado encontrado na planilha {channel_name}"}
        
        # Processar dados (lógica específica por canal)
        processed_data = process_channel_data(all_values, channel_name)
        
        return processed_data
        
    except Exception as e:
        print(f"Erro ao processar planilha {channel_name}: {e}")
        return {"error": f"Erro ao processar {channel_name}: {str(e)}"}

def process_channel_data(data, channel_name):
    """Processa dados específicos de cada canal"""
    if not data or len(data) < 2:
        return {"error": "Dados insuficientes"}
    
    headers = data[0]
    rows = data[1:]
    
    # Lógica específica por canal
    if channel_name == "footfall":
        return process_footfall_data(headers, rows)
    elif channel_name in ["disney", "netflix", "youtube"]:
        return process_video_data(headers, rows)
    elif channel_name == "ctv":
        return process_ctv_data(headers, rows)
    elif channel_name == "tiktok":
        return process_tiktok_data(headers, rows)
    else:
        return process_generic_data(headers, rows)

def process_footfall_data(headers, rows):
    """Processa dados específicos do Footfall Display"""
    try:
        # Encontrar colunas relevantes
        spend_col = find_column_index(headers, ["spend", "valor", "investimento", "custo"])
        impressions_col = find_column_index(headers, ["impressions", "impressões", "views"])
        clicks_col = find_column_index(headers, ["clicks", "cliques"])
        
        total_spend = 0
        total_impressions = 0
        total_clicks = 0
        
        for row in rows:
            if len(row) > max(spend_col, impressions_col, clicks_col):
                spend = safe_float(row[spend_col]) if spend_col is not None else 0
                impressions = safe_float(row[impressions_col]) if impressions_col is not None else 0
                clicks = safe_float(row[clicks_col]) if clicks_col is not None else 0
                
                total_spend += spend
                total_impressions += impressions
                total_clicks += clicks
        
        return {
            "spend": total_spend,
            "impressions": total_impressions,
            "clicks": total_clicks,
            "cpm": (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        }
    except Exception as e:
        return {"error": f"Erro ao processar dados Footfall: {str(e)}"}

def process_video_data(headers, rows):
    """Processa dados de canais de vídeo (Disney, Netflix, YouTube)"""
    try:
        spend_col = find_column_index(headers, ["spend", "valor", "investimento", "custo"])
        impressions_col = find_column_index(headers, ["impressions", "impressões", "views"])
        views_col = find_column_index(headers, ["views", "visualizações", "vtr"])
        
        total_spend = 0
        total_impressions = 0
        total_views = 0
        
        for row in rows:
            if len(row) > max(spend_col, impressions_col, views_col):
                spend = safe_float(row[spend_col]) if spend_col is not None else 0
                impressions = safe_float(row[impressions_col]) if impressions_col is not None else 0
                views = safe_float(row[views_col]) if views_col is not None else 0
                
                total_spend += spend
                total_impressions += impressions
                total_views += views
        
        vtr = (total_views / total_impressions * 100) if total_impressions > 0 else 0
        cpv = (total_spend / total_views) if total_views > 0 else 0
        
        return {
            "spend": total_spend,
            "impressions": total_impressions,
            "views": total_views,
            "vtr": vtr,
            "cpv": cpv
        }
    except Exception as e:
        return {"error": f"Erro ao processar dados de vídeo: {str(e)}"}

def process_ctv_data(headers, rows):
    """Processa dados específicos do CTV"""
    return process_video_data(headers, rows)  # CTV usa mesma lógica de vídeo

def process_tiktok_data(headers, rows):
    """Processa dados específicos do TikTok (misto: vídeo + display)"""
    try:
        spend_col = find_column_index(headers, ["spend", "valor", "investimento", "custo"])
        impressions_col = find_column_index(headers, ["impressions", "impressões", "views"])
        views_col = find_column_index(headers, ["views", "visualizações", "vtr"])
        
        total_spend = 0
        total_impressions = 0
        total_views = 0
        
        for row in rows:
            if len(row) > max(spend_col, impressions_col, views_col):
                spend = safe_float(row[spend_col]) if spend_col is not None else 0
                impressions = safe_float(row[impressions_col]) if impressions_col is not None else 0
                views = safe_float(row[views_col]) if views_col is not None else 0
                
                total_spend += spend
                total_impressions += impressions
                total_views += views
        
        vtr = (total_views / total_impressions * 100) if total_impressions > 0 else 0
        cpv = (total_spend / total_views) if total_views > 0 else 0
        cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        
        return {
            "spend": total_spend,
            "impressions": total_impressions,
            "views": total_views,
            "vtr": vtr,
            "cpv": cpv,
            "cpm": cpm
        }
    except Exception as e:
        return {"error": f"Erro ao processar dados TikTok: {str(e)}"}

def process_generic_data(headers, rows):
    """Processa dados genéricos quando não há lógica específica"""
    try:
        spend_col = find_column_index(headers, ["spend", "valor", "investimento", "custo"])
        impressions_col = find_column_index(headers, ["impressions", "impressões", "views"])
        
        total_spend = 0
        total_impressions = 0
        
        for row in rows:
            if len(row) > max(spend_col, impressions_col):
                spend = safe_float(row[spend_col]) if spend_col is not None else 0
                impressions = safe_float(row[impressions_col]) if impressions_col is not None else 0
                
                total_spend += spend
                total_impressions += impressions
        
        return {
            "spend": total_spend,
            "impressions": total_impressions
        }
    except Exception as e:
        return {"error": f"Erro ao processar dados genéricos: {str(e)}"}

def find_column_index(headers, possible_names):
    """Encontra o índice de uma coluna baseado em nomes possíveis"""
    for i, header in enumerate(headers):
        header_lower = header.lower().strip()
        for name in possible_names:
            if name.lower() in header_lower:
                return i
    return None

def safe_float(value):
    """Converte valor para float de forma segura"""
    if not value:
        return 0.0
    try:
        # Remove caracteres não numéricos exceto ponto e vírgula
        cleaned = str(value).replace(',', '.').replace('R$', '').replace('%', '').strip()
        return float(cleaned)
    except:
        return 0.0

@app.get("/api/dashboard/data")
async def get_dashboard_data():
    """Endpoint principal para dados do dashboard"""
    try:
        # Tentar conectar ao Google Sheets
        client = get_google_sheets_client()
        
        if not client:
            # Fallback para dados mock se não conseguir conectar
            return get_fallback_data()
        
        # Processar dados de cada canal
        channel_data = {}
        errors = []
        
        for channel, spreadsheet_id in SPREADSHEET_IDS.items():
            try:
                data = process_sheet_data(client, spreadsheet_id, channel)
                if "error" in data:
                    errors.append(f"{channel}: {data['error']}")
                else:
                    channel_data[channel] = data
            except Exception as e:
                errors.append(f"{channel}: {str(e)}")
        
        # Se houver muitos erros, usar fallback
        if len(errors) > len(SPREADSHEET_IDS) / 2:
            print(f"Muitos erros ao acessar planilhas: {errors}")
            return get_fallback_data()
        
        # Montar resposta com dados reais
        response_data = build_dashboard_response(channel_data)
        response_data["source"] = "google_sheets"
        response_data["errors"] = errors if errors else None
        
        return {
            "message": "Dados carregados do Google Sheets",
            "data": response_data,
            "timestamp": datetime.now().isoformat(),
            "source": "google_sheets"
        }
        
    except Exception as e:
        print(f"Erro geral ao carregar dados: {e}")
        return get_fallback_data()

def get_fallback_data():
    """Retorna dados mock como fallback"""
    return {
        "message": "Usando dados simulados (Google Sheets indisponível)",
        "data": get_dynamic_mock_data(),
        "timestamp": datetime.now().isoformat(),
        "source": "mock_data_fallback"
    }

def get_dynamic_mock_data():
    """Gera dados mock dinâmicos"""
    # Dados contratados (CONS)
    cons_data = {
        "Budget Contratado (R$)": 500000,
        "Budget Utilizado (R$)": random.randint(100000, 150000),
        "Impressões": random.randint(20000000, 30000000),
        "Cliques": random.randint(100000, 150000),
        "Visitas (Footfall)": random.randint(7000, 10000)
    }
    
    # Dados por canal (PER)
    per_data = [
        {
            "Canal": "CTV",
            "Budget (R$)": random.randint(80000, 120000),
            "Impressões": random.randint(5000000, 8000000),
            "VTR (%)": round(random.uniform(2.5, 4.5), 2),
            "CPV (R$)": round(random.uniform(0.15, 0.35), 2)
        },
        {
            "Canal": "YouTube",
            "Budget (R$)": random.randint(60000, 90000),
            "Impressões": random.randint(4000000, 6000000),
            "VTR (%)": round(random.uniform(3.0, 5.0), 2),
            "CPV (R$)": round(random.uniform(0.12, 0.28), 2)
        },
        {
            "Canal": "TikTok",
            "Budget (R$)": random.randint(70000, 100000),
            "Impressões": random.randint(3000000, 5000000),
            "VTR (%)": round(random.uniform(4.0, 6.5), 2),
            "CPV (R$)": round(random.uniform(0.08, 0.20), 2),
            "CPM (R$)": round(random.uniform(8.0, 15.0), 2)
        },
        {
            "Canal": "Disney",
            "Budget (R$)": random.randint(50000, 80000),
            "Impressões": random.randint(2000000, 4000000),
            "VTR (%)": round(random.uniform(2.8, 4.2), 2),
            "CPV (R$)": round(random.uniform(0.18, 0.32), 2)
        },
        {
            "Canal": "Netflix",
            "Budget (R$)": random.randint(45000, 75000),
            "Impressões": random.randint(1800000, 3500000),
            "VTR (%)": round(random.uniform(3.2, 4.8), 2),
            "CPV (R$)": round(random.uniform(0.16, 0.30), 2)
        },
        {
            "Canal": "Footfall Display",
            "Budget (R$)": random.randint(40000, 60000),
            "Impressões": random.randint(1500000, 2500000),
            "CPM (R$)": round(random.uniform(12.0, 20.0), 2)
        }
    ]
    
    # Dados diários (DAILY) - últimos 7 dias
    daily_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        daily_data.append({
            "Data": date.strftime("%Y-%m-%d"),
            "Impressões": random.randint(2000000, 4000000),
            "Cliques": random.randint(8000, 15000),
            "Spend (R$)": random.randint(15000, 25000)
        })
    
    return {
        "CONS": cons_data,
        "PER": per_data,
        "DAILY": daily_data
    }

def build_dashboard_response(channel_data):
    """Constrói resposta do dashboard com dados reais das planilhas"""
    # Implementar lógica para construir resposta baseada nos dados reais
    # Por enquanto, retorna estrutura básica
    return {
        "CONS": {
            "Budget Contratado (R$)": 500000,
            "Budget Utilizado (R$)": sum(data.get("spend", 0) for data in channel_data.values()),
            "Impressões": sum(data.get("impressions", 0) for data in channel_data.values()),
            "Cliques": sum(data.get("clicks", 0) for data in channel_data.values()),
            "Visitas (Footfall)": channel_data.get("footfall", {}).get("clicks", 0)
        },
        "PER": [
            {
                "Canal": "CTV",
                "Budget (R$)": channel_data.get("ctv", {}).get("spend", 0),
                "Impressões": channel_data.get("ctv", {}).get("impressions", 0),
                "VTR (%)": channel_data.get("ctv", {}).get("vtr", 0),
                "CPV (R$)": channel_data.get("ctv", {}).get("cpv", 0)
            },
            {
                "Canal": "YouTube",
                "Budget (R$)": channel_data.get("youtube", {}).get("spend", 0),
                "Impressões": channel_data.get("youtube", {}).get("impressions", 0),
                "VTR (%)": channel_data.get("youtube", {}).get("vtr", 0),
                "CPV (R$)": channel_data.get("youtube", {}).get("cpv", 0)
            },
            {
                "Canal": "TikTok",
                "Budget (R$)": channel_data.get("tiktok", {}).get("spend", 0),
                "Impressões": channel_data.get("tiktok", {}).get("impressions", 0),
                "VTR (%)": channel_data.get("tiktok", {}).get("vtr", 0),
                "CPV (R$)": channel_data.get("tiktok", {}).get("cpv", 0),
                "CPM (R$)": channel_data.get("tiktok", {}).get("cpm", 0)
            },
            {
                "Canal": "Disney",
                "Budget (R$)": channel_data.get("disney", {}).get("spend", 0),
                "Impressões": channel_data.get("disney", {}).get("impressions", 0),
                "VTR (%)": channel_data.get("disney", {}).get("vtr", 0),
                "CPV (R$)": channel_data.get("disney", {}).get("cpv", 0)
            },
            {
                "Canal": "Netflix",
                "Budget (R$)": channel_data.get("netflix", {}).get("spend", 0),
                "Impressões": channel_data.get("netflix", {}).get("impressions", 0),
                "VTR (%)": channel_data.get("netflix", {}).get("vtr", 0),
                "CPV (R$)": channel_data.get("netflix", {}).get("cpv", 0)
            },
            {
                "Canal": "Footfall Display",
                "Budget (R$)": channel_data.get("footfall", {}).get("spend", 0),
                "Impressões": channel_data.get("footfall", {}).get("impressions", 0),
                "CPM (R$)": channel_data.get("footfall", {}).get("cpm", 0)
            }
        ],
        "DAILY": []  # Implementar lógica para dados diários se necessário
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "google-sheets-api"}

@app.post("/api/auth/login")
async def login():
    """Mock login endpoint"""
    return {"message": "Login successful (mock)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
