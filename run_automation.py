#!/usr/bin/env python3
"""
Script principal para executar a automação do dashboard
"""

import os
import sys
import time
import signal
from datetime import datetime
import logging

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomationRunner:
    """Classe para executar a automação"""
    
    def __init__(self):
        self.running = True
        self.automation_process = None
        
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        logger.info(f"🛑 Sinal {signum} recebido. Parando automação...")
        self.running = False
    
    def check_prerequisites(self):
        """Verifica pré-requisitos"""
        logger.info("🔍 Verificando pré-requisitos...")
        
        try:
            # Importar test_automation_setup
            from test_automation_setup import run_full_test
            
            success = run_full_test()
            
            if not success:
                logger.error("❌ Pré-requisitos não atendidos")
                return False
            
            logger.info("✅ Todos os pré-requisitos atendidos")
            return True
            
        except ImportError:
            logger.error("❌ Arquivo test_automation_setup.py não encontrado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar pré-requisitos: {e}")
            return False
    
    def run_single_update(self):
        """Executa uma única atualização"""
        logger.info("🔄 Executando atualização única...")
        
        try:
            from dashboard_automation import DashboardAutomation
            
            automation = DashboardAutomation()
            success = automation.run_update()
            
            if success:
                logger.info("✅ Atualização única concluída com sucesso!")
            else:
                logger.error("❌ Erro na atualização única")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro na atualização única: {e}")
            return False
    
    def run_continuous_automation(self):
        """Executa automação contínua"""
        logger.info("🚀 Iniciando automação contínua...")
        
        try:
            from dashboard_automation import DashboardAutomation
            
            automation = DashboardAutomation()
            automation.start_scheduler()
            
        except Exception as e:
            logger.error(f"❌ Erro na automação contínua: {e}")
    
    def run_monitoring(self):
        """Executa monitoramento"""
        logger.info("🔍 Executando monitoramento...")
        
        try:
            from monitoring import DashboardMonitor
            
            monitor = DashboardMonitor()
            success = monitor.run_monitoring()
            
            if success:
                logger.info("✅ Monitoramento concluído - Sistema saudável")
            else:
                logger.warning("⚠️ Monitoramento concluído - Problemas detectados")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
            return False
    
    def show_menu(self):
        """Mostra menu de opções"""
        print("\n" + "="*50)
        print("🤖 AUTOMAÇÃO DO DASHBOARD")
        print("="*50)
        print("1. Verificar configuração")
        print("2. Executar atualização única")
        print("3. Iniciar automação contínua (a cada 3h)")
        print("4. Executar monitoramento")
        print("5. Sair")
        print("="*50)
    
    def run_interactive(self):
        """Executa modo interativo"""
        while self.running:
            try:
                self.show_menu()
                choice = input("\nEscolha uma opção (1-5): ").strip()
                
                if choice == '1':
                    print("\n🔍 Verificando configuração...")
                    self.check_prerequisites()
                    
                elif choice == '2':
                    print("\n🔄 Executando atualização única...")
                    self.run_single_update()
                    
                elif choice == '3':
                    print("\n🚀 Iniciando automação contínua...")
                    print("Pressione Ctrl+C para parar")
                    self.run_continuous_automation()
                    
                elif choice == '4':
                    print("\n🔍 Executando monitoramento...")
                    self.run_monitoring()
                    
                elif choice == '5':
                    print("\n👋 Saindo...")
                    break
                    
                else:
                    print("\n❌ Opção inválida")
                
                if choice in ['1', '2', '4']:
                    input("\nPressione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no menu interativo: {e}")
                input("\nPressione Enter para continuar...")
    
    def run_command_line(self, args):
        """Executa modo linha de comando"""
        if len(args) < 2:
            print("Uso: python run_automation.py [comando]")
            print("Comandos:")
            print("  check    - Verificar configuração")
            print("  update   - Executar atualização única")
            print("  start    - Iniciar automação contínua")
            print("  monitor  - Executar monitoramento")
            print("  setup    - Executar configuração inicial")
            return
        
        command = args[1].lower()
        
        if command == 'check':
            self.check_prerequisites()
            
        elif command == 'update':
            self.run_single_update()
            
        elif command == 'start':
            self.run_continuous_automation()
            
        elif command == 'monitor':
            self.run_monitoring()
            
        elif command == 'setup':
            try:
                from setup_automation import main as setup_main
                setup_main()
            except Exception as e:
                logger.error(f"❌ Erro no setup: {e}")
                
        else:
            print(f"❌ Comando inválido: {command}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando script de automação...")
    
    try:
        runner = AutomationRunner()
        
        # Se tem argumentos, executa modo linha de comando
        if len(sys.argv) > 1:
            runner.run_command_line(sys.argv)
        else:
            # Senão, executa modo interativo
            runner.run_interactive()
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
    
    logger.info("👋 Script finalizado")

if __name__ == "__main__":
    main()
