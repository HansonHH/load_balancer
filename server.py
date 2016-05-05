#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xin Han
# Email: hxinhan@gmail.com

import eventlet
# Monkeypatch the standard library to green this program
eventlet.monkey_patch()

from eventlet import wsgi
from application import application

# The non-blocking load balancer listens on port 3000
wsgi.server(eventlet.listen(('', 3000)), application)


