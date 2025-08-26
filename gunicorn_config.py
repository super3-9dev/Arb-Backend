# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 2
preload_app = True
reload = False
accesslog = "-"
errorlog = "-"
loglevel = "info"
