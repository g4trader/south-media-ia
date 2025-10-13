#!/usr/bin/env python3
"""
Script para corrigir completamente o problema da Semana do Pescado
Força limpeza de cache e regeneração de dados
"""

import requests
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SemanaPescadoFixer:
    """Corretor para o problema da Semana do Pescado"""
    
    def __init__(self):
        self.api_endpoint = "https://mvp-dashboard-builder-609095880025.us-central1.run.app"
        self.campaign_key = "copacol_semana_do_pescado_youtube"
        
    def clear_cache_and_regenerate(self):
        """Limpar cache e regenerar dados"""
        logger.info("🔄 Limpando cache e regenerando dados...")
        
        try:
            # 1. Verificar dados atuais
            logger.info("📊 Verificando dados atuais...")
            current_data = self.get_current_data()
            
            if current_data:
                daily_data = current_data.get('daily_data', [])
                logger.info(f"📊 Dados atuais: {len(daily_data)} dias")
                
                if len(daily_data) < 26:
                    logger.warning(f"⚠️ PROBLEMA CONFIRMADO: Apenas {len(daily_data)} dias, esperado 26")
                    
                    # 2. Forçar limpeza de cache (se houver endpoint)
                    logger.info("🧹 Tentando limpar cache...")
                    self.clear_cache()
                    
                    # 3. Aguardar um pouco para o cache ser limpo
                    import time
                    time.sleep(5)
                    
                    # 4. Verificar dados após limpeza
                    logger.info("📊 Verificando dados após limpeza...")
                    new_data = self.get_current_data()
                    
                    if new_data:
                        new_daily_data = new_data.get('daily_data', [])
                        logger.info(f"📊 Dados após limpeza: {len(new_daily_data)} dias")
                        
                        if len(new_daily_data) > len(daily_data):
                            logger.info("✅ Dados atualizados com sucesso!")
                        else:
                            logger.warning("⚠️ Dados ainda incompletos - pode ser problema na lógica de processamento")
                            
                        return new_data
                else:
                    logger.info("✅ Dados já estão completos!")
                    return current_data
            else:
                logger.error("❌ Não foi possível obter dados atuais")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na correção: {e}")
            return None
    
    def get_current_data(self):
        """Obter dados atuais da API"""
        try:
            url = f"{self.api_endpoint}/api/{self.campaign_key}/data"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data')
                else:
                    logger.error(f"❌ API retornou erro: {data.get('message')}")
                    return None
            else:
                logger.error(f"❌ Erro HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados: {e}")
            return None
    
    def clear_cache(self):
        """Tentar limpar cache (se houver endpoint disponível)"""
        try:
            # Tentar diferentes endpoints de limpeza de cache
            cache_endpoints = [
                f"{self.api_endpoint}/api/{self.campaign_key}/clear-cache",
                f"{self.api_endpoint}/api/{self.campaign_key}/refresh",
                f"{self.api_endpoint}/api/clear-cache",
                f"{self.api_endpoint}/api/refresh-data"
            ]
            
            for endpoint in cache_endpoints:
                try:
                    response = requests.post(endpoint, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ Cache limpo via: {endpoint}")
                        return True
                except:
                    continue
            
            logger.warning("⚠️ Nenhum endpoint de limpeza de cache encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def analyze_data_completeness(self, data):
        """Analisar completude dos dados"""
        if not data:
            return
        
        daily_data = data.get('daily_data', [])
        logger.info(f"📊 Análise de completude dos dados:")
        logger.info(f"   Total de dias: {len(daily_data)}")
        
        if daily_data:
            # Verificar período
            dates = [day.get('date') for day in daily_data if day.get('date')]
            if dates:
                first_date = min(dates)
                last_date = max(dates)
                logger.info(f"   Período: {first_date} a {last_date}")
                
                # Verificar se há dados até 28/09
                has_28_sep = any('2025-09-28' in date for date in dates)
                if has_28_sep:
                    logger.info("   ✅ Dados até 28/09: PRESENTES")
                else:
                    logger.warning("   ❌ Dados até 28/09: AUSENTES")
            
            # Verificar impressões
            total_impressions = sum(day.get('impressions', 0) for day in daily_data)
            logger.info(f"   Total de impressões: {total_impressions:,}")
            
            # Verificar se há dados suficientes
            if len(daily_data) >= 26:
                logger.info("   ✅ Dados completos!")
            elif len(daily_data) >= 20:
                logger.warning(f"   ⚠️ Dados parciais: {len(daily_data)}/26 dias")
            else:
                logger.error(f"   ❌ Dados insuficientes: {len(daily_data)}/26 dias")
    
    def generate_report(self, before_data, after_data):
        """Gerar relatório da correção"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "campaign_key": self.campaign_key,
            "before": {
                "days": len(before_data.get('daily_data', [])) if before_data else 0,
                "total_impressions": sum(day.get('impressions', 0) for day in before_data.get('daily_data', [])) if before_data else 0
            },
            "after": {
                "days": len(after_data.get('daily_data', [])) if after_data else 0,
                "total_impressions": sum(day.get('impressions', 0) for day in after_data.get('daily_data', [])) if after_data else 0
            },
            "improvement": {
                "days_added": 0,
                "impressions_added": 0
            }
        }
        
        if before_data and after_data:
            report["improvement"]["days_added"] = report["after"]["days"] - report["before"]["days"]
            report["improvement"]["impressions_added"] = report["after"]["total_impressions"] - report["before"]["total_impressions"]
        
        # Salvar relatório
        with open('semana_pescado_fix_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: semana_pescado_fix_report.json")
        return report

def main():
    """Função principal"""
    logger.info("🚀 Iniciando correção completa da Semana do Pescado...")
    
    fixer = SemanaPescadoFixer()
    
    # Obter dados antes da correção
    before_data = fixer.get_current_data()
    fixer.analyze_data_completeness(before_data)
    
    # Executar correção
    after_data = fixer.clear_cache_and_regenerate()
    
    if after_data:
        fixer.analyze_data_completeness(after_data)
        
        # Gerar relatório
        report = fixer.generate_report(before_data, after_data)
        
        logger.info("✅ Correção concluída!")
        logger.info(f"📊 Resultado: {report['after']['days']} dias, {report['after']['total_impressions']:,} impressões")
        
        if report['improvement']['days_added'] > 0:
            logger.info(f"🎉 Melhoria: +{report['improvement']['days_added']} dias, +{report['improvement']['impressions_added']:,} impressões")
    else:
        logger.error("❌ Falha na correção!")

if __name__ == "__main__":
    main()

