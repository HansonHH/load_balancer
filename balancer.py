#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Xin Han
# Email: hxinhan@gmail.com

import json
import ConfigParser
import requests
from threading import Thread, Lock

# Get video servers info from configuration file
config = ConfigParser.ConfigParser()
config.read("balancer.conf")
SERVERS = map(str.strip, config.get('VideoServers', 'servers').split(','))

# A counter for distributing user requests based in a round-robin fashion
POINTER = 0

# Create a lock for Mutual exclusion. Avoid several threads get access to the shared variable POINTER at exactly the same time
lock = Lock()

# Thread class which can return value
class RequestThread(Thread):
        
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self.__init___return = None
                            
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
                                                            
    def join(self):
        Thread.join(self)
        return self._return


# Distribute requests in a round-robin fashion
def round_robin():

    global POINTER
    
    index = POINTER % len(SERVERS)
    video_server_url = SERVERS[index]
    # Increase POINTER by one 
    POINTER = POINTER + 1

    print POINTER

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


def allocateStream(url, headers, post_data):

    # Send POST request to the chosen video server 
    res = requests.post(url, headers = headers, timeout = 1, data = post_data) 
    
    return res


# Load balancer's function for allocating stream
def balancer_allocateStream(env):

    # Generate request headers based on client's request headers
    headers = generate_headers(env['headers_raw']) 
    # Retrive json data from client's request
    post_data = env['wsgi.input'].read()

    # Initiate a for loop with the length of SERVERS list. 
    # The loop will be terminated immediately, if balancer successfully gets a response from any video server
    for i in range(len(SERVERS)):        
        
        # Acquire the lock
        lock.acquire()
        
        # Get video server url based on Round-Robin
        video_server_url = round_robin()

        try:
            # Create a thread
            thread = RequestThread(target = allocateStream, args = (video_server_url, headers, post_data))
            
            # Initiate the thread
            thread.start()
            
            # Wait for the thread to stop
            res = thread.join()

            # Release the lock
            lock.release()
        
            # If video server responds with a 500 error code, try another video server instead
            if res.status_code == 500:
                continue

            # If no error occurs, then send response to client immediately
            else:
                response_body = {}
                # Remove "secret" key-value pairt from video server response
                response_body['url'] = res.json()['url']
            
                return generate_response(str(res.status_code), response_body)

        # If Timeout exception or Connection error is raised, try another video server instead 
        except:
            # Release the lock
            lock.release()
            continue

    # After execution of the loop above, if the balancer can't get any response from all the video servers, 
    # then balancer sends back a 500 error response to client
    response_body = {"Error": {"detail":"Internal servers raise errors", "type":"500 Error"}}
    
    return generate_response('500', response_body)


