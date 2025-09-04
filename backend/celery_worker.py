#!/usr/bin/env python3
"""
Worker do Celery para South Media IA
Gerencia importações automáticas de campanhas e agendamento de tarefas
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.services.scheduler_service import celery_app, start_celery_worker, stop_celery_worker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para iniciar o worker do Celery"""
    try:
        logger.info("🚀 Iniciando Worker do Celery para South Media IA...")
        
        # Verificar variáveis de ambiente
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        logger.info(f"📡 Conectando ao Redis: {redis_url}")
        
        # Iniciar worker
        start_celery_worker()
        
        logger.info("✅ Worker do Celery iniciado com sucesso!")
        logger.info("📋 Tarefas agendadas:")
        logger.info("   - Importação diária: 6h da manhã")
        logger.info("   - Importação semanal: Domingo às 2h da manhã")
        logger.info("   - Importação mensal: Primeiro dia do mês às 3h da manhã")
        
        # Manter o worker rodando
        try:
            while True:
                import time
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Recebido sinal de interrupção...")
            stop_celery_worker()
            logger.info("✅ Worker do Celery encerrado com sucesso!")
            
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar worker do Celery: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

