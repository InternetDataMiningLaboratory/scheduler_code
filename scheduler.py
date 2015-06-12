# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月18日 星期六 13时58分52秒
# 
from docker import Client
client = Client(base_url='tcp://172.16.153.32:8888')
print client.containers()
