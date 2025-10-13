#!/usr/bin/env python3
"""
Script para corrigir campanhas na produção
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_production_campaigns():
    """Corrigir campanhas na produção"""
    
    # URL da produção
    prod_url = "https://mvp-dashboard-builder-609095880025.us-central1.run.app"
    
    # Dados da campanha de teste do ambiente de teste
    test_campaign_data = {
        "campaign_key": "copacol_semana_do_pescado_youtube",
        "client": "COPACOL",
        "campaign_name": "Semana do pescado youtube",
        "sheet_id": "1jApuNZO-Y7TF67_yiF3R6yLez6_z9q8_Rt3pDSItOZg",
        "channel": "YouTube"
    }
    
    logger.info("🔧 Iniciando correção de campanhas na produção...")
    
    # 1. Verificar se a campanha existe
    logger.info("🔍 Verificando se a campanha existe...")
    try:
        response = requests.get(f"{prod_url}/api/{test_campaign_data['campaign_key']}/data")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✅ Campanha já existe na produção!")
                return True
            else:
                logger.info("❌ Campanha não existe na produção")
        else:
            logger.info("❌ Erro ao verificar campanha")
    except Exception as e:
        logger.error(f"❌ Erro ao verificar campanha: {e}")
    
    # 2. Tentar criar a campanha usando diferentes endpoints
    logger.info("🔧 Tentando criar campanha...")
    
    # Tentar endpoint de criação
    endpoints_to_try = [
        "/api/campaigns",
        "/api/create-campaign",
        "/api/campaign/create",
        "/campaigns"
    ]
    
    for endpoint in endpoints_to_try:
        try:
            logger.info(f"🔄 Tentando endpoint: {endpoint}")
            response = requests.post(f"{prod_url}{endpoint}", 
                                   json=test_campaign_data,
                                   headers={"Content-Type": "application/json"})
            
            logger.info(f"📊 Status: {response.status_code}")
            logger.info(f"📊 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ Campanha criada com sucesso!")
                    return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no endpoint {endpoint}: {e}")
    
    # 3. Se não conseguir criar, tentar forçar o carregamento dos dados
    logger.info("🔄 Tentando forçar carregamento de dados...")
    
    try:
        # Tentar acessar diretamente os dados da planilha
        response = requests.get(f"{prod_url}/api/{test_campaign_data['campaign_key']}/data")
        logger.info(f"📊 Status da requisição: {response.status_code}")
        logger.info(f"📊 Response: {response.text[:500]}...")
        
    except Exception as e:
        logger.error(f"❌ Erro ao tentar carregar dados: {e}")
    
    logger.info("❌ Não foi possível corrigir as campanhas automaticamente")
    return False

if __name__ == "__main__":
    fix_production_campaigns()

