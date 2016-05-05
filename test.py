import grequests
import json

#urls = ['http://0.0.0.0:3000/allocateStream'] * 1000
urls = ['http://0.0.0.0:3000/allocateStream']

post_data = json.dumps({"channelId":"svt1"})

rs = (grequests.post(u, data=post_data) for u in urls)

grequests.map(rs)

