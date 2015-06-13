# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月18日 星期六 15时07分45秒
# 
import docker
import consul
import logging
import urllib
import database
import tornado.gen
import tornado.httpclient

#consul客户端
CONSUL_CLIENT = consul.Consul('consul')

class ServiceNotFoundException(Exception):
    '''
        在consul中查找不到指定名字的服务时抛出
    '''
    
    def __init__(self, name):
        super(ServiceNotFoundException, self).__init__()
        self.name = name

class Service(object):
    _service = None

    def __init__(self, service_name):
        service_list = \
            CONSUL_CLIENT.catalog.service(service_name)
        logging.error(service_list)
        if not service_list[1]:
            raise ServiceNotFoundException(service_name)
        self._service = service_list[1].pop()
        
    @property
    def address(self):
        return self._service.get("Address")

    @property
    def port(self):
        return self._service.get("ServicePort")

    @property
    def url(self):
        return '{address}:{port}'.format(
            address=self.address,
            port=str(self.port),
        )

    def __str__(self):
        return self.url

#本地docker客户端
_consul_url = '{consul}:8500'.format(consul=Service("consul").address)
_LOCAL_CLIENT = docker.Client("tcp://{server}:2375".format(server=Service("consul").address), version='1.17')

def create_swarm_service():
    '''
        创建swarm manager容器并启动
    '''
    
    command = "manage consul://{consul}/swarm".format(consul=_consul_url)

    _LOCAL_CLIENT.create_container(
        image='swarm', 
        detach=True, 
        ports=[2375],
        name='swarm_manager',
        command=command,
        host_config=docker.utils.create_host_config(
            publish_all_ports=True
        ),
    )
    _LOCAL_CLIENT.start('swarm_manager')

#检查swarm服务是否存在并启动

try:
    _swarm_service = Service("swarm")
except ServiceNotFoundException:
    logging.info("swarm服务尚未启动")
    try:
        _LOCAL_CLIENT.start('swarm_manager')
        logging.info("启动原有服务")
    except:
        logging.info("原有服务不存在，创建新服务")
        create_swarm_service()

        #重新创建swarm服务
        logging.error("新的swarm服务创建完成")

CONSUL_CLIENT = consul.Consul('consul')
_swarm_service = Service("swarm")

SWARM_CLIENT = docker.Client(
    base_url='tcp://{swarm}'.format(swarm=_swarm_service.url),
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
            base_url=_swarm_service.url,
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

def create_host_config(**kwargs):
    return docker.utils.create_host_config(**kwargs)
