# Gunicorn configuration for MVP Dashboard Builder
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes - optimized for Cloud Run
workers = int(os.environ.get('GUNICORN_WORKERS', 1))  # Reduced for Cloud Run efficiency
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 5  # Increased for better connection reuse
max_requests = 1000
max_requests_jitter = 50  # Reduced jitter for more predictable recycling

# Restart workers after this many requests, to prevent memory leaks
# (already set above)

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'mvp-dashboard-builder'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (not needed for Cloud Run)
keyfile = None
certfile = None

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Enable worker recycling to prevent memory leaks
max_worker_memory = 200  # MB

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting MVP Dashboard Builder server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading server")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("👋 Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"🔧 Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"✅ Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"🎯 Worker initialized (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info(f"💥 Worker aborted (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 Pre-exec hook")

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"👋 Worker exited (pid: {worker.pid})")

def max_requests_jitter_handler(worker):
    """Called when max_requests is reached."""
    worker.log.info(f"🔄 Worker reached max_requests, recycling (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("👋 Server shutting down")

