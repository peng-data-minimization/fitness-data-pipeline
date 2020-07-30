import os
port = os.environ.get('PORT', '7777')

worker_class = "eventlet"
workers = 2
bind = "0.0.0.0:" + port