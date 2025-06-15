import multiprocessing

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '/opt/bridge-health/logs/gunicorn_access.log'
errorlog = '/opt/bridge-health/logs/gunicorn_error.log'
loglevel = 'info'

# Process naming
proc_name = 'bridge-health'

# Server mechanics
daemon = False
pidfile = '/opt/bridge-health/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'