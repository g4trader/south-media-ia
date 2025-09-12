#!/usr/bin/env python3
"""
Script de inicialização do sistema South Media IA
Inicia API, Redis e Celery Worker
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemManager:
    def __init__(self):
        self.processes = {}
        self.base_path = Path(__file__).parent
        
    def start_redis(self):
        """Iniciar Redis se não estiver rodando"""
        try:
            # Verificar se Redis já está rodando
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                logger.info("✅ Redis já está rodando")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            logger.info("🚀 Iniciando Redis...")
            
            # Tentar iniciar Redis
            redis_process = subprocess.Popen(
                ['redis-server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para ver se iniciou
            time.sleep(3)
            
            if redis_process.poll() is None:
                logger.info("✅ Redis iniciado com sucesso")
                self.processes['redis'] = redis_process
                return True
            else:
                logger.error("❌ Falha ao iniciar Redis")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Redis: {e}")
            return False
    
    def start_celery_worker(self):
        """Iniciar Celery Worker"""
        try:
            logger.info("🚀 Iniciando Celery Worker...")
            
            celery_process = subprocess.Popen(
                [sys.executable, 'celery_worker.py'],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para ver se iniciou
            time.sleep(5)
            
            if celery_process.poll() is None:
                logger.info("✅ Celery Worker iniciado com sucesso")
                self.processes['celery'] = celery_process
                return True
            else:
                logger.error("❌ Falha ao iniciar Celery Worker")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Celery Worker: {e}")
            return False
    
    def start_celery_beat(self):
        """Iniciar Celery Beat (agendador)"""
        try:
            logger.info("🚀 Iniciando Celery Beat...")
            
            beat_process = subprocess.Popen(
                [sys.executable, '-m', 'celery', '-A', 'src.services.scheduler_service.celery_app', 'beat'],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para ver se iniciou
            time.sleep(3)
            
            if beat_process.poll() is None:
                logger.info("✅ Celery Beat iniciado com sucesso")
                self.processes['celery_beat'] = beat_process
                return True
            else:
                logger.error("❌ Falha ao iniciar Celery Beat")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Celery Beat: {e}")
            return False
    
    def start_api(self):
        """Iniciar API FastAPI"""
        try:
            logger.info("🚀 Iniciando API FastAPI...")
            
            api_process = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', 'src.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar um pouco para ver se iniciou
            time.sleep(5)
            
            if api_process.poll() is None:
                logger.info("✅ API FastAPI iniciada com sucesso")
                self.processes['api'] = api_process
                return True
            else:
                logger.error("❌ Falha ao iniciar API FastAPI")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar API FastAPI: {e}")
            return False
    
    def start_system(self):
        """Iniciar todo o sistema"""
        logger.info("🚀 Iniciando Sistema South Media IA...")
        
        # Verificar dependências
        self._check_dependencies()
        
        # Iniciar serviços
        services_started = []
        
        # 1. Redis
        if self.start_redis():
            services_started.append("Redis")
        
        # 2. Celery Worker
        if self.start_celery_worker():
            services_started.append("Celery Worker")
        
        # 3. Celery Beat
        if self.start_celery_beat():
            services_started.append("Celery Beat")
        
        # 4. API
        if self.start_api():
            services_started.append("API FastAPI")
        
        # Resumo
        if len(services_started) == 4:
            logger.info("🎉 Sistema iniciado com sucesso!")
            logger.info(f"✅ Serviços ativos: {', '.join(services_started)}")
            logger.info("🌐 API disponível em: http://localhost:8000")
            logger.info("📚 Documentação: http://localhost:8000/docs")
            logger.info("📊 Status do sistema: http://localhost:8000/api/status")
            return True
        else:
            logger.error(f"❌ Apenas {len(services_started)} de 4 serviços foram iniciados")
            return False
    
    def _check_dependencies(self):
        """Verificar dependências do sistema"""
        logger.info("🔍 Verificando dependências...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error("❌ Python 3.8+ é necessário")
            sys.exit(1)
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verificar arquivos necessários
        required_files = [
            'src/main.py',
            'src/config.py',
            'src/services/scheduler_service.py',
            'celery_worker.py'
        ]
        
        for file_path in required_files:
            if not (self.base_path / file_path).exists():
                logger.error(f"❌ Arquivo não encontrado: {file_path}")
                sys.exit(1)
            logger.info(f"✅ {file_path}")
        
        logger.info("✅ Todas as dependências estão satisfeitas")
    
    def stop_system(self):
        """Parar todo o sistema"""
        logger.info("🛑 Parando sistema...")
        
        for service_name, process in self.processes.items():
            try:
                logger.info(f"🛑 Parando {service_name}...")
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ {service_name} parado")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  {service_name} não parou em 10s, forçando...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Erro ao parar {service_name}: {e}")
        
        self.processes.clear()
        logger.info("✅ Sistema parado")
    
    def monitor_system(self):
        """Monitorar sistema em execução"""
        logger.info("📊 Monitorando sistema...")
        
        try:
            while True:
                # Verificar status dos processos
                for service_name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.error(f"❌ {service_name} parou inesperadamente")
                        return False
                
                # Aguardar
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 Recebido sinal de interrupção...")
            return True

def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger.info(f"🛑 Recebido sinal {signum}")
    if hasattr(system_manager, 'stop_system'):
        system_manager.stop_system()
    sys.exit(0)

if __name__ == "__main__":
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Criar gerenciador do sistema
    system_manager = SystemManager()
    
    try:
        # Iniciar sistema
        if system_manager.start_system():
            # Monitorar sistema
            system_manager.monitor_system()
        else:
            logger.error("❌ Falha ao iniciar sistema")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
    finally:
        # Garantir que o sistema seja parado
        system_manager.stop_system()




