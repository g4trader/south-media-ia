from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import LocalOutlierFactor
import json

from src.models.alert import (
    AlertCreate, AlertUpdate, AlertResponse, AlertSummary, AlertInstance,
    AlertType, AlertSeverity, AlertStatus, AlertTrigger, AlertCondition,
    AlertFrequency, MLModelConfig, TrendAnalysis, CompetitorAnalysis
)
from src.models.campaign import CampaignResponse, CampaignPerformance
from src.services.campaign_service import CampaignService
from src.services.company_service import CompanyService
from src.services.notification_service import NotificationService
from src.models.notification import NotificationCreate, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.campaign_service = CampaignService()
        self.company_service = CompanyService()
        self.notification_service = NotificationService()
        
        # Configurações de ML
        self.ml_models = {}
        self.scalers = {}
        self.model_configs = {}
    
    async def create_alert(self, alert_data: AlertCreate, creator_user: Dict[str, Any]) -> AlertResponse:
        """Criar um novo alerta inteligente"""
        try:
            # Gerar ID único para o alerta
            alert_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Calcular próxima verificação
            next_check = self._calculate_next_check(alert_data.frequency)
            
            # Criar alerta
            alert = AlertResponse(
                id=alert_id,
                **alert_data.dict(),
                status=AlertStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                last_triggered=None,
                trigger_count=0,
                last_checked=None,
                next_check=next_check
            )
            
            # Se ML estiver habilitado, configurar modelo
            if alert.machine_learning_enabled:
                await self._setup_ml_model(alert)
            
            # Salvar no BigQuery
            await self._save_alert_to_bigquery(alert)
            
            logger.info(f"Alerta criado com sucesso: {alert_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
            raise Exception(f"Falha ao criar alerta: {str(e)}")
    
    async def check_alerts(self, company_id: str) -> List[AlertInstance]:
        """Verificar todos os alertas ativos de uma empresa"""
        try:
            # Obter alertas ativos
            active_alerts = await self._get_active_alerts(company_id)
            
            triggered_instances = []
            
            for alert in active_alerts:
                # Verificar se é hora de verificar o alerta
                if not self._should_check_alert(alert):
                    continue
                
                # Verificar condições do alerta
                alert_instance = await self._evaluate_alert(alert)
                
                if alert_instance:
                    triggered_instances.append(alert_instance)
                    
                    # Atualizar alerta
                    await self._update_alert_trigger(alert.id, alert_instance)
                    
                    # Enviar notificação
                    await self._send_alert_notification(alert, alert_instance)
            
            logger.info(f"Verificação de alertas concluída: {len(triggered_instances)} alertas acionados")
            return triggered_instances
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
            return []
    
    async def _evaluate_alert(self, alert: AlertResponse) -> Optional[AlertInstance]:
        """Avaliar se um alerta deve ser acionado"""
        try:
            # Obter dados da métrica
            metric_data = await self._get_metric_data(alert)
            
            if not metric_data:
                return None
            
            # Verificar condição básica
            if not self._check_basic_condition(alert, metric_data):
                return None
            
            # Se ML estiver habilitado, verificar anomalia
            if alert.machine_learning_enabled:
                ml_result = await self._check_ml_anomaly(alert, metric_data)
                if not ml_result["is_anomaly"]:
                    return None
                ml_confidence = ml_result["confidence"]
            else:
                ml_confidence = None
            
            # Se análise de tendência estiver habilitada, verificar
            if alert.trend_analysis_enabled:
                trend_analysis = await self._analyze_trend(alert, metric_data)
            else:
                trend_analysis = None
            
            # Se análise de concorrente estiver habilitada, verificar
            if alert.competitor_analysis_enabled:
                competitor_analysis = await self._analyze_competitor(alert, metric_data)
            else:
                competitor_analysis = None
            
            # Criar instância do alerta
            alert_instance = AlertInstance(
                alert_id=alert.id,
                company_id=alert.company_id,
                campaign_id=alert.campaign_id,
                triggered_at=datetime.utcnow(),
                metric_value=metric_data["current_value"],
                threshold_value=alert.threshold_value,
                deviation_percentage=self._calculate_deviation(alert, metric_data),
                context_data={
                    "trend_analysis": trend_analysis.dict() if trend_analysis else None,
                    "competitor_analysis": competitor_analysis.dict() if competitor_analysis else None,
                    "historical_data": metric_data.get("historical_data", [])
                },
                historical_data=metric_data.get("historical_data", []),
                ml_confidence=ml_confidence,
                status=AlertStatus.ACTIVE,
                notifications_sent=[],
                notification_channels=alert.notification_channels
            )
            
            # Salvar instância
            await self._save_alert_instance(alert_instance)
            
            return alert_instance
            
        except Exception as e:
            logger.error(f"Erro ao avaliar alerta {alert.id}: {e}")
            return None
    
    async def _check_ml_anomaly(self, alert: AlertResponse, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar anomalia usando machine learning"""
        try:
            model_key = f"{alert.company_id}_{alert.metric_name}"
            
            if model_key not in self.ml_models:
                # Treinar modelo se não existir
                await self._train_ml_model(alert, metric_data)
            
            # Preparar dados para predição
            current_data = np.array(metric_data["current_value"]).reshape(1, -1)
            
            # Normalizar dados
            if model_key in self.scalers:
                current_data = self.scalers[model_key].transform(current_data)
            
            # Fazer predição
            model = self.ml_models[model_key]
            prediction = model.predict(current_data)
            
            # Isolation Forest retorna -1 para anomalias, 1 para normal
            is_anomaly = prediction[0] == -1
            
            # Calcular score de anomalia (quanto mais negativo, mais anômalo)
            if hasattr(model, 'score_samples'):
                anomaly_score = model.score_samples(current_data)[0]
                # Converter para confiança (0-1)
                confidence = max(0, min(1, 1 - (anomaly_score + 0.5)))
            else:
                confidence = 0.8 if is_anomaly else 0.2
            
            return {
                "is_anomaly": is_anomaly,
                "confidence": confidence,
                "anomaly_score": anomaly_score if hasattr(model, 'score_samples') else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar anomalia ML: {e}")
            return {"is_anomaly": False, "confidence": 0.0}
    
    async def _analyze_trend(self, alert: AlertResponse, metric_data: Dict[str, Any]) -> Optional[TrendAnalysis]:
        """Analisar tendência da métrica"""
        try:
            historical_data = metric_data.get("historical_data", [])
            
            if len(historical_data) < 7:  # Mínimo de 7 pontos para análise
                return None
            
            # Converter para DataFrame
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calcular estatísticas básicas
            current_value = df['value'].iloc[-1]
            average_value = df['value'].mean()
            std_value = df['value'].std()
            min_value = df['value'].min()
            max_value = df['value'].max()
            
            # Análise de tendência simples (regressão linear)
            x = np.arange(len(df))
            y = df['value'].values
            
            if len(x) > 1:
                slope = np.polyfit(x, y, 1)[0]
                
                if slope > 0.01:
                    trend_direction = "up"
                    trend_strength = min(1.0, abs(slope) / std_value if std_value > 0 else 0.5)
                elif slope < -0.01:
                    trend_direction = "down"
                    trend_strength = min(1.0, abs(slope) / std_value if std_value > 0 else 0.5)
                else:
                    trend_direction = "stable"
                    trend_strength = 0.1
            else:
                trend_direction = "stable"
                trend_strength = 0.1
            
            # Calcular confiança baseada na variância
            trend_confidence = max(0.1, min(1.0, 1 - (std_value / average_value if average_value > 0 else 0.5)))
            
            # Análise sazonal simples (comparar com período anterior)
            if len(df) >= 14:  # Pelo menos 2 semanas
                current_week = df.tail(7)['value'].mean()
                previous_week = df.iloc[-14:-7]['value'].mean()
                
                if previous_week > 0:
                    week_over_week_change = (current_week - previous_week) / previous_week
                    seasonal_pattern = "weekly" if abs(week_over_week_change) > 0.1 else None
                    seasonal_strength = min(1.0, abs(week_over_week_change))
                else:
                    seasonal_pattern = None
                    seasonal_strength = 0.0
            else:
                seasonal_pattern = None
                seasonal_strength = 0.0
            
            return TrendAnalysis(
                metric_name=alert.metric_name,
                analysis_period=f"{len(historical_data)}d",
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                trend_confidence=trend_confidence,
                current_value=current_value,
                average_value=average_value,
                standard_deviation=std_value,
                min_value=min_value,
                max_value=max_value,
                seasonal_pattern=seasonal_pattern,
                seasonal_strength=seasonal_strength,
                previous_period_comparison={
                    "current_period_avg": current_value,
                    "previous_period_avg": average_value,
                    "change_percentage": ((current_value - average_value) / average_value * 100) if average_value > 0 else 0
                },
                year_over_year_change=None  # TODO: Implementar comparação YoY
            )
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendência: {e}")
            return None
    
    async def _analyze_competitor(self, alert: AlertResponse, metric_data: Dict[str, Any]) -> Optional[CompetitorAnalysis]:
        """Analisar atividade de concorrentes"""
        try:
            # TODO: Implementar análise real de concorrentes
            # Por enquanto, usando dados mock
            
            competitor_data = {
                "competitor_name": "Concorrente Principal",
                "analysis_date": datetime.utcnow(),
                "competitor_metrics": {
                    "impressions": 50000,
                    "clicks": 2500,
                    "ctr": 5.0,
                    "cpc": 0.85
                },
                "market_share": 0.35,
                "comparison_metrics": {
                    "impressions": {
                        "competitor": 50000,
                        "our_company": metric_data.get("current_value", 0),
                        "difference": 50000 - metric_data.get("current_value", 0)
                    },
                    "ctr": {
                        "competitor": 5.0,
                        "our_company": 4.2,
                        "difference": 5.0 - 4.2
                    }
                },
                "competitive_advantage": "Maior alcance e CTR",
                "threat_level": "medium",
                "active_campaigns": [
                    {"name": "Campanha Q1 2024", "budget": 15000, "status": "active"}
                ],
                "estimated_budget": 15000,
                "target_audience": "Jovens 18-35, interessados em tecnologia"
            }
            
            return CompetitorAnalysis(**competitor_data)
            
        except Exception as e:
            logger.error(f"Erro ao analisar concorrente: {e}")
            return None
    
    async def _setup_ml_model(self, alert: AlertResponse):
        """Configurar modelo de machine learning para o alerta"""
        try:
            model_key = f"{alert.company_id}_{alert.metric_name}"
            
            # Configuração padrão do modelo
            model_config = MLModelConfig(
                model_type="isolation_forest",
                algorithm="isolation_forest",
                parameters={
                    "n_estimators": 100,
                    "contamination": 0.1,
                    "random_state": 42
                },
                training_window_days=alert.ml_training_data_days or 30,
                retrain_frequency_days=7,
                min_data_points=100,
                confidence_threshold=alert.ml_confidence_threshold or 0.8,
                false_positive_rate=0.05
            )
            
            # Criar modelo
            model = IsolationForest(
                n_estimators=model_config.parameters["n_estimators"],
                contamination=model_config.parameters["contamination"],
                random_state=model_config.parameters["random_state"]
            )
            
            # Criar scaler
            scaler = StandardScaler()
            
            # Armazenar modelo e configuração
            self.ml_models[model_key] = model
            self.scalers[model_key] = scaler
            self.model_configs[model_key] = model_config
            
            logger.info(f"Modelo ML configurado para {model_key}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar modelo ML: {e}")
    
    async def _train_ml_model(self, alert: AlertResponse, metric_data: Dict[str, Any]):
        """Treinar modelo de machine learning"""
        try:
            model_key = f"{alert.company_id}_{alert.metric_name}"
            
            if model_key not in self.ml_models:
                await self._setup_ml_model(alert)
            
            historical_data = metric_data.get("historical_data", [])
            
            if len(historical_data) < 50:  # Mínimo de dados para treinamento
                logger.warning(f"Dados insuficientes para treinar modelo ML: {len(historical_data)} pontos")
                return
            
            # Preparar dados de treinamento
            training_data = []
            for data_point in historical_data:
                training_data.append([
                    data_point.get("value", 0),
                    data_point.get("timestamp_hour", 0),
                    data_point.get("timestamp_day_of_week", 0)
                ])
            
            training_data = np.array(training_data)
            
            # Normalizar dados
            scaler = self.scalers[model_key]
            training_data_normalized = scaler.fit_transform(training_data)
            
            # Treinar modelo
            model = self.ml_models[model_key]
            model.fit(training_data_normalized)
            
            # Atualizar configuração
            self.model_configs[model_key].is_trained = True
            self.model_configs[model_key].last_trained = datetime.utcnow()
            
            logger.info(f"Modelo ML treinado para {model_key} com {len(training_data)} pontos")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo ML: {e}")
    
    # Métodos auxiliares
    
    def _calculate_next_check(self, frequency: AlertFrequency) -> datetime:
        """Calcular próxima verificação baseado na frequência"""
        now = datetime.utcnow()
        
        if frequency == AlertFrequency.REAL_TIME:
            return now + timedelta(minutes=1)
        elif frequency == AlertFrequency.EVERY_5_MINUTES:
            return now + timedelta(minutes=5)
        elif frequency == AlertFrequency.EVERY_15_MINUTES:
            return now + timedelta(minutes=15)
        elif frequency == AlertFrequency.EVERY_HOUR:
            return now + timedelta(hours=1)
        elif frequency == AlertFrequency.EVERY_4_HOURS:
            return now + timedelta(hours=4)
        elif frequency == AlertFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == AlertFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(hours=1)
    
    def _should_check_alert(self, alert: AlertResponse) -> bool:
        """Verificar se é hora de verificar o alerta"""
        now = datetime.utcnow()
        
        # Verificar se é hora da próxima verificação
        if alert.next_check and now < alert.next_check:
            return False
        
        # Verificar período de resfriamento
        if alert.last_triggered:
            cooldown_seconds = self._parse_time_period(alert.cooldown_period)
            if now < alert.last_triggered + timedelta(seconds=cooldown_seconds):
                return False
        
        return True
    
    def _parse_time_period(self, period: str) -> int:
        """Converter período de tempo para segundos"""
        try:
            if period.endswith('h'):
                return int(period[:-1]) * 3600
            elif period.endswith('d'):
                return int(period[:-1]) * 86400
            elif period.endswith('m'):
                return int(period[:-1]) * 60
            else:
                return int(period)
        except:
            return 3600  # Padrão: 1 hora
    
    def _check_basic_condition(self, alert: AlertResponse, metric_data: Dict[str, Any]) -> bool:
        """Verificar condição básica do alerta"""
        try:
            current_value = metric_data["current_value"]
            threshold = alert.threshold_value
            
            if alert.condition == AlertCondition.GREATER_THAN:
                return current_value > threshold
            elif alert.condition == AlertCondition.LESS_THAN:
                return current_value < threshold
            elif alert.condition == AlertCondition.EQUAL_TO:
                return current_value == threshold
            elif alert.condition == AlertCondition.NOT_EQUAL_TO:
                return current_value != threshold
            elif alert.condition == AlertCondition.GREATER_THAN_OR_EQUAL:
                return current_value >= threshold
            elif alert.condition == AlertCondition.LESS_THAN_OR_EQUAL:
                return current_value <= threshold
            elif alert.condition == AlertCondition.BETWEEN:
                if alert.threshold_value_secondary:
                    return threshold <= current_value <= alert.threshold_value_secondary
                return False
            elif alert.condition == AlertCondition.OUTSIDE:
                if alert.threshold_value_secondary:
                    return current_value < threshold or current_value > alert.threshold_value_secondary
                return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar condição básica: {e}")
            return False
    
    def _calculate_deviation(self, alert: AlertResponse, metric_data: Dict[str, Any]) -> float:
        """Calcular percentual de desvio"""
        try:
            current_value = metric_data["current_value"]
            threshold = alert.threshold_value
            
            if threshold == 0:
                return 0.0
            
            deviation = ((current_value - threshold) / threshold) * 100
            return round(deviation, 2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular desvio: {e}")
            return 0.0
    
    async def _get_metric_data(self, alert: AlertResponse) -> Optional[Dict[str, Any]]:
        """Obter dados da métrica para análise"""
        try:
            # TODO: Implementar busca real de métricas
            # Por enquanto, usando dados mock
            
            if alert.campaign_id:
                # Métricas de campanha específica
                campaign = await self.campaign_service.get_campaign(alert.campaign_id, {"company_id": alert.company_id})
                if not campaign:
                    return None
                
                performance = await self.campaign_service.get_campaign_performance(alert.campaign_id, {"company_id": alert.company_id})
                
                if alert.metric_name == "ctr":
                    current_value = performance.avg_ctr if performance else 0.0
                elif alert.metric_name == "cpm":
                    current_value = performance.avg_cpm if performance else 0.0
                elif alert.metric_name == "cpc":
                    current_value = performance.avg_cpc if performance else 0.0
                elif alert.metric_name == "budget_utilization":
                    current_value = performance.budget_utilization if performance else 0.0
                else:
                    current_value = 0.0
                
                # Dados históricos mock
                historical_data = [
                    {"timestamp": datetime.utcnow() - timedelta(days=i), "value": current_value + np.random.normal(0, 0.1)}
                    for i in range(30, 0, -1)
                ]
                
            else:
                # Métricas consolidadas da empresa
                if alert.metric_name == "total_impressions":
                    current_value = 125000
                elif alert.metric_name == "total_clicks":
                    current_value = 6250
                elif alert.metric_name == "avg_ctr":
                    current_value = 5.0
                else:
                    current_value = 0.0
                
                historical_data = [
                    {"timestamp": datetime.utcnow() - timedelta(days=i), "value": current_value + np.random.normal(0, current_value * 0.1)}
                    for i in range(30, 0, -1)
                ]
            
            return {
                "current_value": current_value,
                "historical_data": historical_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados da métrica: {e}")
            return None
    
    async def _send_alert_notification(self, alert: AlertResponse, alert_instance: AlertInstance):
        """Enviar notificação do alerta"""
        try:
            # Criar notificação
            notification_data = NotificationCreate(
                title=f"Alerta: {alert.name}",
                message=f"O alerta '{alert.name}' foi acionado. {alert_instance.metric_name}: {alert_instance.metric_value} (Desvio: {alert_instance.deviation_percentage}%)",
                notification_type=NotificationType.CAMPAIGN_ALERT,
                priority=alert.severity.value.upper(),
                company_id=alert.company_id,
                user_ids=alert.recipients,
                role_filter=alert.role_filter,
                campaign_id=alert.campaign_id,
                data={
                    "alert_id": alert.id,
                    "alert_instance_id": alert_instance.id,
                    "metric_name": alert_instance.metric_name,
                    "metric_value": alert_instance.metric_value,
                    "threshold_value": alert_instance.threshold_value,
                    "deviation_percentage": alert_instance.deviation_percentage,
                    "ml_confidence": alert_instance.ml_confidence
                },
                channels=alert.notification_channels,
                immediate=True
            )
            
            # Enviar notificação
            await self.notification_service.create_notification(notification_data, {"company_id": alert.company_id})
            
            logger.info(f"Notificação de alerta enviada: {alert.name}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de alerta: {e}")
    
    # Métodos para BigQuery (TODO)
    
    async def _save_alert_to_bigquery(self, alert: AlertResponse):
        """Salvar alerta no BigQuery"""
        logger.info(f"Alerta {alert.id} salvo no BigQuery")
    
    async def _get_active_alerts(self, company_id: str) -> List[AlertResponse]:
        """Obter alertas ativos de uma empresa"""
        # TODO: Implementar busca real no BigQuery
        # Por enquanto, usando dados mock
        return []
    
    async def _update_alert_trigger(self, alert_id: str, alert_instance: AlertInstance):
        """Atualizar alerta após acionamento"""
        logger.info(f"Alerta {alert_id} atualizado após acionamento")
    
    async def _save_alert_instance(self, alert_instance: AlertInstance):
        """Salvar instância do alerta"""
        logger.info(f"Instância de alerta {alert_instance.id} salva")


