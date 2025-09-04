"""
Configuração de logging para a aplicação
"""
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger principal
logger = logging.getLogger(__name__)
