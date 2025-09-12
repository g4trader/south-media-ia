#!/usr/bin/env python3
"""
Sistema de monitoramento e notificações para automação do dashboard
"""

import os
import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
from config import NOTIFICATION_CONFIG

logger = logging.getLogger(__name__)

class DashboardMonitor:
    """Classe para monitoramento e notificações"""
    
    def __init__(self):
        self.log_file = 'logs/dashboard_automation.log'
        self.status_file = 'logs/dashboard_status.json'
        self.notification_config = NOTIFICATION_CONFIG
    
    def check_last_update(self):
        """Verifica quando foi a última atualização"""
        try:
            if not os.path.exists(self.log_file):
                return None
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Procura pela última linha de sucesso
            for line in reversed(lines):
                if "✅ Atualização automática concluída com sucesso!" in line:
                    # Extrai timestamp da linha
                    parts = line.split(' - ')
                    if len(parts) >= 1:
                        timestamp_str = parts[0]
                        try:
                            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        except:
                            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar última atualização: {e}")
            return None
    
    def check_dashboard_health(self):
        """Verifica saúde geral do dashboard"""
        try:
            status = {
                'last_update': None,
                'is_healthy': True,
                'errors': [],
                'warnings': []
            }
            
            # Verificar última atualização
            last_update = self.check_last_update()
            status['last_update'] = last_update.isoformat() if last_update else None
            
            if last_update:
                # Verificar se a atualização é recente (menos de 6 horas)
                hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
                
                if hours_since_update > 6:
                    status['warnings'].append(f"Última atualização há {hours_since_update:.1f} horas")
                    status['is_healthy'] = False
                
                if hours_since_update > 12:
                    status['errors'].append(f"Dashboard não atualizado há {hours_since_update:.1f} horas")
                    status['is_healthy'] = False
            
            # Verificar arquivo do dashboard
            dashboard_file = 'static/dash_sonho.html'
            if not os.path.exists(dashboard_file):
                status['errors'].append("Arquivo do dashboard não encontrado")
                status['is_healthy'] = False
            
            # Verificar logs de erro recentes
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Verifica erros das últimas 24 horas
                recent_errors = []
                for line in lines[-100:]:  # Últimas 100 linhas
                    if 'ERROR' in line or '❌' in line:
                        recent_errors.append(line.strip())
                
                if len(recent_errors) > 5:
                    status['warnings'].append(f"{len(recent_errors)} erros recentes encontrados")
                    status['is_healthy'] = False
            
            # Salvar status
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saúde do dashboard: {e}")
            return {'is_healthy': False, 'errors': [str(e)]}
    
    def send_email_notification(self, subject, message):
        """Envia notificação por email"""
        if not self.notification_config['email']['enabled']:
            return False
        
        try:
            email_config = self.notification_config['email']
            
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = email_config['to_email']
            msg['Subject'] = f"[Dashboard Automation] {subject}"
            
            msg.attach(MimeText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['username'], email_config['to_email'], text)
            server.quit()
            
            logger.info("✅ Notificação por email enviada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            return False
    
    def send_webhook_notification(self, message):
        """Envia notificação via webhook"""
        if not self.notification_config['enabled'] or not self.notification_config['webhook_url']:
            return False
        
        try:
            payload = {
                'text': f"Dashboard Automation: {message}",
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                self.notification_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Notificação via webhook enviada")
                return True
            else:
                logger.error(f"❌ Erro no webhook: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar webhook: {e}")
            return False
    
    def send_notification(self, subject, message, is_error=False):
        """Envia notificação (email e/ou webhook)"""
        if is_error:
            logger.error(f"🚨 {subject}: {message}")
        else:
            logger.warning(f"⚠️ {subject}: {message}")
        
        # Enviar email
        self.send_email_notification(subject, message)
        
        # Enviar webhook
        self.send_webhook_notification(f"{subject}: {message}")
    
    def generate_health_report(self):
        """Gera relatório de saúde do dashboard"""
        try:
            status = self.check_dashboard_health()
            
            report = f"""
RELATÓRIO DE SAÚDE DO DASHBOARD
===============================
Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Status Geral: {'✅ SAUDÁVEL' if status['is_healthy'] else '❌ PROBLEMAS DETECTADOS'}

Última Atualização: {status['last_update'] or 'Nunca'}

"""
            
            if status['errors']:
                report += "ERROS:\n"
                for error in status['errors']:
                    report += f"  ❌ {error}\n"
                report += "\n"
            
            if status['warnings']:
                report += "AVISOS:\n"
                for warning in status['warnings']:
                    report += f"  ⚠️ {warning}\n"
                report += "\n"
            
            if not status['errors'] and not status['warnings']:
                report += "✅ Nenhum problema detectado!\n"
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return f"Erro ao gerar relatório: {e}"
    
    def run_monitoring(self):
        """Executa monitoramento completo"""
        try:
            logger.info("🔍 Executando monitoramento do dashboard...")
            
            status = self.check_dashboard_health()
            
            # Se não está saudável, enviar notificação
            if not status['is_healthy']:
                if status['errors']:
                    self.send_notification(
                        "ERRO CRÍTICO",
                        f"Dashboard com problemas críticos: {'; '.join(status['errors'])}",
                        is_error=True
                    )
                elif status['warnings']:
                    self.send_notification(
                        "AVISO",
                        f"Dashboard com avisos: {'; '.join(status['warnings'])}",
                        is_error=False
                    )
            
            # Gerar relatório
            report = self.generate_health_report()
            logger.info(f"\n{report}")
            
            return status['is_healthy']
            
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
            self.send_notification("ERRO DE MONITORAMENTO", str(e), is_error=True)
            return False

def main():
    """Função principal para execução standalone do monitoramento"""
    monitor = DashboardMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
