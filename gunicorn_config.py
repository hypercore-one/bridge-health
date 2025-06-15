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

def when_ready(server):
    """Called just after the master process is initialized."""
    # This runs in the master process, not in workers
    pass

def on_starting(server):
    """Called just before the master process is initialized."""
    # Clean up any stale lock files
    lock_file = '/tmp/bridge-health-bg-updater.lock'
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("Removed stale background updater lock file")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    # This is called in the worker process after fork
    # We'll start the background updater here
    lock_file = '/tmp/bridge-health-bg-updater.lock'
    
    try:
        # Try to create lock file atomically
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(worker.pid).encode())
        os.close(fd)
        
        # Import here to avoid import issues
        from app.main import create_app
        app = create_app()
        
        # Start background updater
        with app.app_context():
            app.background_updater.start()
            app.background_updater.force_update()
            print(f"Background updater started in worker {worker.pid}")
            
    except FileExistsError:
        print(f"Background updater NOT started in worker {worker.pid} (lock file exists)")
    except Exception as e:
        print(f"Error starting background updater in worker {worker.pid}: {e}")

def worker_exit(server, worker):
    """Hook called when a worker exits."""
    # server parameter required by Gunicorn but not used
    lock_file = '/tmp/bridge-health-bg-updater.lock'
    
    try:
        # Check if this worker owns the lock file
        if os.path.exists(lock_file):
            with open(lock_file, 'r') as f:
                lock_pid = f.read().strip()
            if lock_pid == str(worker.pid):
                os.remove(lock_file)
                print(f"Background updater lock removed for worker {worker.pid}")
    except Exception as e:
        print(f"Error removing lock file in worker {worker.pid}: {e}")