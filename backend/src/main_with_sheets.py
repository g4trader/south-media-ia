from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from datetime import datetime, timedelta
import random

app = FastAPI(title="South Media IA Backend", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash.iasouth.tech",
        "https://south-media-ia.vercel.app", 
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_dynamic_mock_data():
    """Gera dados mock dinâmicos baseados na estrutura das planilhas Google Sheets"""
    
    # Dados contratados (CONS)
    cons_data = {
        "Budget Contratado (R$)": 500000,
        "Budget Utilizado (R$)": random.randint(100000, 150000),
        "Impressões": random.randint(20000000, 30000000),
        "Cliques": random.randint(100000, 150000),
        "Visitas (Footfall)": random.randint(7000, 10000)
    }
    
    # Dados por canal (PER)
    channels = ["CTV", "YouTube", "TikTok", "Disney", "Netflix", "Footfall Display"]
    per_data = []
    
    for channel in channels:
        base_budget = {
            "CTV": 120000,
            "YouTube": 100000,
            "TikTok": 80000,
            "Disney": 70000,
            "Netflix": 60000,
            "Footfall Display": 70000
        }
        
        budget_contratado = base_budget[channel]
        budget_utilizado = int(budget_contratado * random.uniform(0.20, 0.30))
        
        channel_data = {
            "Canal": channel,
            "Budget Contratado (R$)": budget_contratado,
            "Budget Utilizado (R$)": budget_utilizado,
            "Impressões": random.randint(3000000, 6000000),
            "Cliques": random.randint(15000, 30000),
            "Visitas (Footfall)": random.randint(2000, 3000)
        }
        
        # Adicionar métricas específicas por canal
        if channel in ["CTV", "YouTube", "Disney", "Netflix"]:
            channel_data["VTR"] = round(random.uniform(0.6, 0.9), 2)
            channel_data["CPV"] = round(random.uniform(0.8, 1.5), 2)
        elif channel == "TikTok":
            channel_data["VTR"] = round(random.uniform(0.6, 0.8), 2)
            channel_data["CPV"] = round(random.uniform(0.8, 1.2), 2)
            channel_data["CPM"] = round(random.uniform(4.0, 6.0), 2)
        elif channel == "Footfall Display":
            channel_data["CPM"] = round(random.uniform(4.0, 6.0), 2)
        
        per_data.append(channel_data)
    
    # Dados diários (DAILY)
    daily_data = []
    for i in range(7):  # Últimos 7 dias
        date = datetime.now() - timedelta(days=i)
        for channel in channels:
            daily_data.append({
                "Data": date.strftime("%Y-%m-%d"),
                "Canal": channel,
                "Impressões": random.randint(100000, 1000000),
                "Cliques": random.randint(500, 5000),
                "Visitas (Footfall)": random.randint(100, 500),
                "Spend": random.randint(1000, 10000)
            })
    
    return {
        "CONS": cons_data,
        "PER": per_data,
        "DAILY": daily_data
    }

@app.get("/")
def read_root():
    return {"message": "South Media IA Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/auth/login")
def login():
    return {"message": "Login endpoint - CORS enabled"}

@app.get("/api/dashboard/data")
def dashboard_data():
    """Endpoint que retorna dados do dashboard com estrutura das planilhas Google Sheets"""
    try:
        # Por enquanto, retorna dados mock dinâmicos
        # TODO: Integrar com Google Sheets quando as credenciais estiverem configuradas
        data = get_dynamic_mock_data()
        
        return {
            "message": "Dashboard data - Google Sheets integration ready",
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source": "mock_data_dynamic"  # Indica que são dados mock dinâmicos
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Error fetching dashboard data",
            "data": get_dynamic_mock_data()  # Fallback para dados mock
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
