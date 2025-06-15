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

# Worker lifecycle hooks
import os

def post_worker_init(worker):
    """Hook called after a worker is initialized."""
    # Only start background updater in one worker using a lock file approach
    lock_file = '/tmp/bridge-health-bg-updater.lock'
    
    if hasattr(worker, 'app') and hasattr(worker.app, 'callable'):
        app = worker.app.callable()
        if hasattr(app, 'background_updater'):
            try:
                # Try to create lock file - if it exists, another worker already has the background updater
                if not os.path.exists(lock_file):
                    with open(lock_file, 'w') as f:
                        f.write(str(worker.pid))
                    
                    with app.app_context():
                        app.background_updater.start()
                        app.background_updater.force_update()
                        print(f"Background updater started in worker {worker.pid}")
                else:
                    print(f"Background updater NOT started in worker {worker.pid} (lock file exists)")
            except Exception as e:
                print(f"Error starting background updater in worker {worker.pid}: {e}")

def worker_exit(server, worker):
    """Hook called when a worker exits."""
    # server parameter required by Gunicorn but not used
    lock_file = '/tmp/bridge-health-bg-updater.lock'
    
    if hasattr(worker, 'app') and hasattr(worker.app, 'callable'):
        app = worker.app.callable()
        if hasattr(app, 'background_updater'):
            try:
                with app.app_context():
                    app.background_updater.stop()
                
                # Remove lock file if this worker created it
                try:
                    with open(lock_file, 'r') as f:
                        lock_pid = f.read().strip()
                    if lock_pid == str(worker.pid):
                        os.remove(lock_file)
                        print(f"Background updater stopped and lock removed for worker {worker.pid}")
                except (FileNotFoundError, ValueError):
                    pass
                    
            except Exception as e:
                print(f"Error stopping background updater in worker {worker.pid}: {e}")