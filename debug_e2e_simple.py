#!/usr/bin/env python3
"""
Teste simples para debugar o problema E2E
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://mvp-dashboard-builder-609095880025.us-central1.run.app"

def test_generate_dashboard():
    """Teste simples de geração de dashboard"""
    try:
        # Dados para o teste
        client_name = "Cliente Debug"
        campaign_name = "Campanha Debug"
        sheet_id = "1hutJ0nUM3hNYeRBSlgpowbknWnI5qu-etrHWtEoaKD8"
        
        # Fazer requisição para gerar dashboard
        payload = {
            "client": client_name,
            "campaign_name": campaign_name,
            "sheet_id": sheet_id
        }
        
        logger.info(f"🚀 Gerando dashboard com dados: {payload}")
        
        response = requests.post(
            f"{BASE_URL}/api/generate-dashboard",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                dashboard_url = result.get("dashboard_url")
                campaign_key = result.get("campaign_key")
                logger.info(f"✅ Dashboard gerado: {dashboard_url}")
                logger.info(f"✅ Campaign Key: {campaign_key}")
                
                # Testar API de dados
                api_url = f"{BASE_URL}/api/{campaign_key}/data"
                logger.info(f"🧪 Testando API: {api_url}")
                
                time.sleep(2)  # Aguardar um pouco
                
                api_response = requests.get(api_url, timeout=30)
                logger.info(f"📊 API Response Status: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    if api_data.get("success"):
                        logger.info("✅ API funcionando perfeitamente!")
                        logger.info(f"📈 Dados: {api_data.get('data', {}).get('campaign_summary', {})}")
                    else:
                        logger.error(f"❌ API retornou erro: {api_data.get('message')}")
                else:
                    logger.error(f"❌ API falhou com status: {api_response.status_code}")
                    logger.error(f"❌ Response: {api_response.text}")
                
                return True
            else:
                logger.error(f"❌ Geração falhou: {result.get('message')}")
                return False
        else:
            logger.error(f"❌ HTTP Error: {response.status_code}")
            logger.error(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando teste de debug E2E")
    success = test_generate_dashboard()
    
    if success:
        logger.info("🎉 Teste passou!")
    else:
        logger.info("💥 Teste falhou!")

