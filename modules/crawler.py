# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月27日 星期一 17时48分32秒
# 
import cluster
from database import Crawler
from bind import Binding, Event
import logging

CRAWLER_IMAGE = 'companyservice/crawler'

Binding.register(Event.crawl_finished) #注册事件：爬取结束

def crawl(arguments):
    '''
        开启一个爬虫任务
        参数:
            crawler_id: 开启的爬虫id
            patch_id: 任务爬取数据批次id
    '''

    #检查参数
    if 'crawler_id' not in arguments:
        return 'Error: crawler_id is neccessary'
    
    if 'patch_id' not in arguments:
        return 'Error: patch_id is neccessary'

    crawler_id = arguments.get('crawler_id')
    patch_id = arguments.get('patch_id')

    #生成爬虫容器启动命令
    crawler = Crawler.select(crawler_id)
    command = \
        (
            '{crawler_type} '
            '-a rule_id={crawler_rule} '
            '-a patch_id={patch_id}'
        ).format(
            crawler_type=crawler.get('crawler_type'),
            crawler_rule=crawler.get('crawler_rule'),
            patch_id=patch_id,
        )
    
    #创建并启动容器
    try:
        container = cluster.SWARM_CLIENT.create_container(
            image=CRAWLER_IMAGE,
            environment={
                "DATABASE_USER" : environment.get_user(),
                "DATABASE_PASSWD" : environment.get_password(),
            },
        )
    except Exception, e:
        Crawler.status(crawler_id, 'error', str(e))
        return 'Error:'+e

    Crawler.register(crawler_id, container)
    Crawler.status(crawler_id, 'pending')

    cluster.SWARM_CLIENT.start(container)

    Crawler.status(crawler_id, 'crawling')

    #容器执行完成后的回调函数
    def callback(response, container=container, crawler_id=crawler_id, patch_id=patch_id):
        cluster.SWARM_CLIENT.remove_container(container)
        Crawler.status(crawler_id, 'finished')
        Binding.notify(Event.crawl_finished, arguments={'patch_id':patch_id})

    try:
        cluster.async_action(container, 'wait', callback=callback).next()
    except StopIteration:
        Crawler.status(crawler_id, 'error', 'async method wrong!')
        return 'Error'   
    return 'Success'
