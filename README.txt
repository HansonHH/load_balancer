# Step1: Please execute the following two commands to install packages before running the load balancer

    sudo apt-get install python-pip python-dev
    sudo pip install eventlet && sudo pip install greenlet && sudo pip install requests

# Step2: Execute the command below to run the load balancer, by default the balancer listens on port 3000
    python server.py

