# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月18日 星期六 15时07分45秒
# 
from docker import Client
import cClient
import logging
import urllib
import database
import tornado.gen
import tornado.httpclient

local_client = Client('tcp://127.0.0.1:2375')
(index, swarm_list) = cClient.client.catalog.service('swarm')
if not swarm_list:
    logging.info("swarm manage service not found, try to start one")
    for retry in xrange(5):
        try:
            local_client.start('swarm_manager')
            logging.info("swarm manage service start")
            break
        except:
            local_client.create_container(
                image='swarm', 
                detach=True, 
                ports=[2375],
                name='swarm_manager',
                command=[
                    'manage',
                    'consul://consul:8500',
                ],
            )
            logging.error("Not found swarm manage service container, create a new service container")
_swarm = swarm_list.pop()
_base_url =\
    '{address}:{port}'.format(
        address=_swarm.get('Address'),
        port=str(_swarm.get('ServicePort'))
    )

client = Client(
    base_url=_base_url,
    version='1.17',
)

logging.info('swarm client start')

def _do_nothing(response):
    pass

def async_action(
    container, 
    action, 
    method='POST',
    args={}, 
    callback=_do_nothing,
    connect_timeout=float('inf'),
    request_timeout=float('inf')
):
    _actions =\
        ['wait', 'stop']
    container_id = container['Id']
    body = urllib.urlencode(args)
    url =\
        'http://{base_url}/containers/{container_id}/{action}'.format(
            base_url=_base_url,
            container_id=container_id,
            action=action,
        )
    _async_client = tornado.httpclient.AsyncHTTPClient()

    request =\
        tornado.httpclient.HTTPRequest(
            url=url, 
            method=method,
            body=body,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
        )
    logging.info('async container action:' + url)
    yield _async_client.fetch(request, callback=callback)

def async(func):
    def wrapper(*arg, **kwarg):
        logging.info('wrapper')
        yield func(*arg, **kwarg)
    return wrapper
