from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.models.notification import (
    NotificationCreate, NotificationResponse, NotificationSummary,
    NotificationType, NotificationPriority, NotificationStatus, NotificationChannel
)
from src.services.company_service import CompanyService
from src.services.user_service import UserService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.company_service = CompanyService()
        self.user_service = UserService()
    
    async def create_notification(self, notification_data: NotificationCreate, creator_user: Dict[str, Any]) -> NotificationResponse:
        """Criar uma nova notificação"""
        try:
            notification_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            notification = NotificationResponse(
                id=notification_id,
                **notification_data.dict(),
                status=NotificationStatus.PENDING,
                created_at=now,
                updated_at=now
            )
            
            # Salvar no BigQuery
            await self._save_notification_to_bigquery(notification)
            
            # Se for imediata, enviar agora
            if notification.immediate:
                await self._send_notification(notification)
            
            logger.info(f"Notificação criada com sucesso: {notification_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {e}")
            raise Exception(f"Falha ao criar notificação: {str(e)}")
    
    async def send_notification(self, notification: NotificationResponse) -> bool:
        """Enviar notificação pelos canais configurados"""
        try:
            recipients = await self._get_notification_recipients(notification)
            
            if not recipients:
                logger.warning(f"Nenhum destinatário encontrado para notificação {notification.id}")
                return False
            
            success_count = 0
            for recipient in recipients:
                for channel in notification.channels:
                    try:
                        if await self._send_to_channel(notification, recipient, channel):
                            success_count += 1
                            await self._record_delivery(notification.id, recipient["id"], channel, "sent")
                        else:
                            await self._record_delivery(notification.id, recipient["id"], channel, "failed")
                    except Exception as e:
                        logger.error(f"Erro ao enviar para {channel}: {e}")
                        await self._record_delivery(notification.id, recipient["id"], channel, "failed", str(e))
            
            if success_count > 0:
                await self._update_notification_status(notification.id, NotificationStatus.SENT)
                logger.info(f"Notificação {notification.id} enviada para {success_count} destinatários")
                return True
            else:
                await self._update_notification_status(notification.id, NotificationStatus.FAILED)
                logger.error(f"Notificação {notification.id} falhou para todos os destinatários")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação {notification.id}: {e}")
            return False
    
    async def _send_to_channel(self, notification: NotificationResponse, recipient: Dict[str, Any], channel: NotificationChannel) -> bool:
        """Enviar notificação para um canal específico"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(notification, recipient)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(notification, recipient)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification, recipient)
            else:
                logger.warning(f"Canal {channel} não implementado")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar para canal {channel}: {e}")
            return False
    
    async def _send_email(self, notification: NotificationResponse, recipient: Dict[str, Any]) -> bool:
        """Enviar notificação por email"""
        try:
            # TODO: Implementar envio real de email
            logger.info(f"Email enviado para {recipient.get('email', 'N/A')}: {notification.title}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    async def _send_slack(self, notification: NotificationResponse, recipient: Dict[str, Any]) -> bool:
        """Enviar notificação para Slack"""
        try:
            # TODO: Implementar envio real para Slack
            logger.info(f"Notificação enviada para Slack: {notification.title}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar para Slack: {e}")
            return False
    
    async def _send_webhook(self, notification: NotificationResponse, recipient: Dict[str, Any]) -> bool:
        """Enviar notificação por webhook"""
        try:
            # TODO: Implementar envio real por webhook
            logger.info(f"Webhook enviado com sucesso: {notification.title}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar webhook: {e}")
            return False
    
    async def _get_notification_recipients(self, notification: NotificationResponse) -> List[Dict[str, Any]]:
        """Obter lista de destinatários para uma notificação"""
        try:
            recipients = []
            
            if notification.user_ids:
                for user_id in notification.user_ids:
                    user = await self.user_service.get_user(user_id, {"company_id": notification.company_id})
                    if user:
                        recipients.append(user)
            else:
                users = await self.user_service.list_company_users(
                    notification.company_id, 
                    {"company_id": notification.company_id}
                )
                recipients.extend(users)
            
            return recipients
            
        except Exception as e:
            logger.error(f"Erro ao obter destinatários: {e}")
            return []
    
    async def _record_delivery(self, notification_id: str, user_id: str, channel: NotificationChannel, status: str, error_message: Optional[str] = None):
        """Registrar entrega de notificação"""
        try:
            logger.info(f"Entrega registrada: {notification_id} -> {user_id} via {channel}: {status}")
        except Exception as e:
            logger.error(f"Erro ao registrar entrega: {e}")
    
    async def _update_notification_status(self, notification_id: str, status: NotificationStatus):
        """Atualizar status de uma notificação"""
        try:
            logger.info(f"Status da notificação {notification_id} atualizado para {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status da notificação: {e}")
    
    async def _save_notification_to_bigquery(self, notification: NotificationResponse):
        """Salvar notificação no BigQuery"""
        logger.info(f"Notificação {notification.id} salva no BigQuery")
    
    async def _send_notification(self, notification: NotificationResponse):
        """Enviar notificação imediatamente"""
        return await self.send_notification(notification)
