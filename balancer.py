#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xin Han
# Email: hxinhan@gmail.com

import json
import ConfigParser
import requests

# Get video servers info from configuration file
config = ConfigParser.ConfigParser()
config.read("balancer.conf")
SERVERS = map(str.strip, config.get('Video_Servers', 'servers').split(','))

# A counter for distributing user requests based in a round-robin fashion
POINTER = 0

# Distribute requests in a round-robin fashion
def round_robin():

    global POINTER
    
    index = POINTER % len(SERVERS)
    video_server_url = SERVERS[index]
    
    POINTER = POINTER + 1

    return video_server_url

# Generate request headers based on client's request headers
def generate_headers(headers_raw):
    dic = {}
    for item in headers_raw:
        dic[item[0]] = item[1]
    return dic

# Generate response which needs to be sent back to client
def generate_response(status_code, response_body):
    
    headers = [('Content-Type', 'application/json')]
    
    return status_code, headers, json.dumps(response_body)

# Load balancer's function for allocating stream
def balancer_allocateStream(env):

    # Generate request headers based on client's request headers
    headers = generate_headers(env['headers_raw']) 
    # Retrive json data from client's request
    post_data = env['wsgi.input'].read()

    # Initiate a for-loop with the length of SERVERS list
    for i in range(len(SERVERS)):        

        # Get video server url based on Round-Robin
        video_server_url = round_robin()

        # Delivery client request to selected video server based on round robin
        try:
            # Send POST request to the chosen video server with maximum waiting time of 1 second
            res = requests.post(video_server_url, headers = headers, timeout = 30, data = post_data) 

        # Timeout exception is raised, try another video server instead
        except requests.exceptions.Timeout:
            continue

        # Connection error is raised, try another video server instead
        except requests.exceptions.ConnectionError:
            continue

        # If video server responds with a 500 error code, try another video server instead
        if res.status_code == 500:
            continue

        # If no error occurs, then respond to client immediately
        else:
            
            response_body = {}
            # Remove "secret" key-value pairt from video server response
            response_body['url'] = res.json()['url']
            
            return generate_response(str(res.status_code), response_body)

    # Send back a 500 error to client
    response_body = {"Error": {"detail":"Internal servers raise errors", "type":"500 Error"}}
    return generate_response('500', response_body)


