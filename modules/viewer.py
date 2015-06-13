# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月13日 星期六 15时34分46秒
# 
# view前端容器调度代码
#
import cluster
from database import Crawler
from bind import Binding, Event
import logging
import cookie_secret
import environment

VIEWER_IMAGE = 'companyservice/viewer'

def open(arguments):
    '''
        开启viewer容器
        参数:
            number: 开启数量
    '''

    #检查参数
    if 'number' not in arguments:
        return 'Error: number is neccessary'
    
    _cookie_secret = None
    
    if cookie_secret.get() is None:
        cookie_secret.update()
        _cookie_secret = cookie_secret.get()

    number = arguments.get('number')

    #创建并启动容器
    for times in xrange(int(number)):
        try:
            container = cluster.SWARM_CLIENT.create_container(
                image=VIEWER_IMAGE,
                environment={
                    "DATABASE_USER" : environment.get_user(),
                    "DATABASE_PASSWD" : environment.get_password(),
                    "COOKIE_SECRET" : _cookie_secret,
                },
                host_config=cluster.create_host_config(
                    publish_all_ports=True
                ),
            )
        except Exception, e:
            return 'Error:'+str(e)

    cluster.SWARM_CLIENT.start(container)
    return 'Success'
