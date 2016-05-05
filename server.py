#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xin Han
# Email: hxinhan@gmail.com

import eventlet

# Monkeypatch the standard library to green this program
eventlet.monkey_patch()

from eventlet import wsgi
#from application import application
from application import *

# Get port info from configuration file
LISTEN_PORT = int(config.get('Balancer', 'port'))

# The non-blocking load balancer listens on port 3000 by default
listener = eventlet.listen(('', LISTEN_PORT))

# Allocate a pool of 1000 green threads
pool = eventlet.GreenPool(1000)

# Initiate load balancer
wsgi.server(listener, application, custom_pool = pool)


