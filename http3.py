import eventlet
eventlet.monkey_patch()
from eventlet import wsgi
from eventlet.green import socket
from eventlet.green import threading
from eventlet.green import asyncore
import json



def application(env, start_response):

    PATH_INFO = env['PATH_INFO']
    REQUEST_METHOD = env['REQUEST_METHOD']

    print 'Receive request...'

    status_code, headers, response_body = http_response(env) 

    start_response(status_code, headers)

    return response_body


def http_response(env):
    import time
    time.sleep(50)
    status_code = '200'
    response_body = {"url": "http://video1.neti.systems/svt1?token=12345", "secret":"abcdef"}
    headers = [('Content-Type', 'application/json')]
    return status_code, headers, json.dumps(response_body)



listener = eventlet.listen(('', 8083))
pool = eventlet.GreenPool(1000)
wsgi.server(listener, application, custom_pool = pool)
