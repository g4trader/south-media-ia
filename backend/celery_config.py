"""
Configuração do Celery para South Media IA
"""

import os
from src.config import settings

# Configurações do broker (Redis)
broker_url = settings.redis_url
result_backend = settings.redis_url

# Configurações de tarefas
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'America/Sao_Paulo'
enable_utc = True

# Configurações de performance
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Configurações de tempo
task_time_limit = 30 * 60  # 30 minutos
task_soft_time_limit = 25 * 60  # 25 minutos
task_acks_late = True
worker_prefetch_multiplier = 1

# Configurações de retry
task_default_retry_delay = 300  # 5 minutos
task_max_retries = 3
task_ignore_result = False

# Configurações de logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Configurações de monitoramento
worker_send_task_events = True
task_send_sent_event = True

# Configurações de segurança
worker_disable_rate_limits = False
worker_max_memory_per_child = 200000  # 200MB

# Configurações específicas para importação de campanhas
task_routes = {
    'src.services.scheduler_service.import_campaign_data': {'queue': 'campaign_imports'},
    'src.services.scheduler_service.schedule_daily_imports': {'queue': 'scheduler'},
    'src.services.scheduler_service.schedule_weekly_imports': {'queue': 'scheduler'},
    'src.services.scheduler_service.schedule_monthly_imports': {'queue': 'scheduler'},
}

# Configurações de filas
task_default_queue = 'default'
task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'campaign_imports': {
        'exchange': 'campaign_imports',
        'routing_key': 'campaign_imports',
    },
    'scheduler': {
        'exchange': 'scheduler',
        'routing_key': 'scheduler',
    },
}

# Configurações de beat (agendador)
beat_schedule = {
    'schedule-daily-imports': {
        'task': 'src.services.scheduler_service.schedule_daily_imports',
        'schedule': '0 6 * * *',  # 6h da manhã todos os dias
        'options': {'queue': 'scheduler'}
    },
    'schedule-weekly-imports': {
        'task': 'src.services.scheduler_service.schedule_weekly_imports',
        'schedule': '0 2 * * 0',  # 2h da manhã aos domingos
        'options': {'queue': 'scheduler'}
    },
    'schedule-monthly-imports': {
        'task': 'src.services.scheduler_service.schedule_monthly_imports',
        'schedule': '0 3 1 * *',  # 3h da manhã no primeiro dia do mês
        'options': {'queue': 'scheduler'}
    },
}

# Configurações de monitoramento e métricas
worker_send_task_events = True
task_send_sent_event = True
event_queue_expires = 60
worker_proc_alive_timeout = 60.0

# Configurações de ambiente
if os.getenv('ENVIRONMENT') == 'production':
    # Configurações de produção
    worker_max_memory_per_child = 500000  # 500MB
    task_time_limit = 60 * 60  # 1 hora
    task_soft_time_limit = 50 * 60  # 50 minutos
    worker_prefetch_multiplier = 4
else:
    # Configurações de desenvolvimento
    worker_max_memory_per_child = 200000  # 200MB
    task_time_limit = 30 * 60  # 30 minutos
    task_soft_time_limit = 25 * 60  # 25 minutos
    worker_prefetch_multiplier = 1


