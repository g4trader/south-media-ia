from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
    return {
        "message": "Dashboard data endpoint - CORS enabled",
        "data": {
            "CONS": {
                "Budget Contratado (R$)": 500000,
                "Budget Utilizado (R$)": 125000,
                "Impressões": 25000000,
                "Cliques": 125000,
                "Visitas (Footfall)": 8500
            },
            "PER": [
                {
                    "Canal": "CTV",
                    "Budget Contratado (R$)": 150000,
                    "Budget Utilizado (R$)": 37500,
                    "Impressões": 7500000,
                    "Cliques": 37500,
                    "Visitas (Footfall)": 2500,
                    "VTR": 0.5,
                    "CPV": 15.0
                }
            ],
            "DAILY": [
                {
                    "Data": "2024-09-08",
                    "Canal": "CTV",
                    "Impressões": 1000000,
                    "Cliques": 5000,
                    "Visitas (Footfall)": 300,
                    "Spend": 5000
                }
            ]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
