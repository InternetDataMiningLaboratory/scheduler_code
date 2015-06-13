# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年05月11日 星期一 17时07分31秒
# 
import logging
import cluster
from bind import Binding, Event
import tornado.gen

SEARCH_ENGINE_IMAGE = 'companyservice/searchengine'

Binding(Event.crawl_finished, 'searchEngine.patch').bind() #绑定爬虫爬取完成事件
Binding.register(Event.patch_finished) #注册索引更新完成事件
Binding.register(Event.search_finished) #注册搜索完成事件

def patch(arguments):
    '''
        搜索引擎更新索引
        参数:
            patch_id: 更新数据批次id
    '''
    patch_id = arguments.get('patch_id', None)

    #检查参数
    if patch_id is None:
        return 'Error: no patch id'

    #生成命令
    command = 'patch {patch_id}'.format(patch_id=patch_id)

    #创建并开启容器
    try:
        container = cluster.SWARM_CLIENT.create_container(
            image=SEARCH_ENGINE_IMAGE,
            command=command,
            environment=["affinity:container==luceneIndex"],
        )
    except Exception, e:
        return 'Error:'+str(e)
    
    cluster.SWARM_CLIENT.start(
        container,
        volumes_from='luceneIndex',
    )
    
    #容器结束后回调命令
    def callback(response, container=container, patch_id=patch_id):
        cluster.CONSUL_CLIENT.remove_container(container)
        Binding.notify(Event.patch_finished, arguments={'patch_id':patch_id})

    try:
        cluster.async_action(container, 'wait', callback=callback).next()
    except StopIteration:
        Crawler.status(crawler_id, 'error', 'async method wrong!')
        return 'Error'   

    return 'Success'

def search(arguments):
    '''
        搜索引擎搜索命令
        参数:
            search_id 搜索项id
    '''
    
    #检查参数
    search_id = arguments.get('search_id', None)
    
    if search_id is None:
        return 'Error: no search id'

    #创建并开启容器
    
    command = 'search {search_id}'.format(search_id=search_id)

    try:
        container = cluster.SWARM_CLIENT.create_container(
            image=SEARCH_ENGINE_IMAGE,
            command=command,
            environment=["affinity:container==luceneIndex"],
        )
    except Exception, e:
        return 'Error:'+str(e)

    cluster.SWARM_CLIENT.start(
        container,
        volumes_from='luceneIndex',
    )
    
    @cluster.async
    def wait(container, search_id=search_id):
        cluster.SWARM_CLIENT.wait(container)
        cluster.SWARM_CLIENT.remove_container(container)
        Binding.notify(Event.search_finished, arguments={'search_id':search_id})

    try:
       wait(container).next() 
    except StopIteration:
        return 'Error'   

    return 'Success'
