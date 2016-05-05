#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xin Han
# Email: hxinhan@gmail.com

from balancer import *


def application(env, start_response):

    PATH_INFO = env['PATH_INFO']
    REQUEST_METHOD = env['REQUEST_METHOD']

    if PATH_INFO == '/allocateStream' and REQUEST_METHOD == 'POST':

        status_code, headers, response_body = balancer_allocateStream(env) 

        start_response(status_code, headers)

        return response_body

    # Handle requests that ends with undefined urls
    else:
                
        response_body = {"Error": {"detail":"Could not find the requested service", "type":"NotFound"}}
        status_code, headers, response_body = generate_response('404', response_body) 

        start_response(status_code, headers)

        return response_body

