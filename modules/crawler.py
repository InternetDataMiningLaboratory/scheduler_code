# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月27日 星期一 17时48分32秒
# 
import dClient
from database import Crawler
from bind import Binding, Event
import logging

CRAWLER_IMAGE = 'companyservice/crawler'
Binding.register(Event.crawl_finished)

def crawl(arguments):
    if 'crawler_id' not in arguments:
        return 'Error: crawler_id is neccessary'
    crawler_id = arguments.get('crawler_id').pop()
    if isinstance(crawler_id, list):
        crawler_id = crawler_id.pop()
    patch_id = arguments.get('patch_id')
    if isinstance(patch_id, list):
        patch_id = patch_id.pop()
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
    for times in xrange(5):
        try:
            container = dClient.client.create_container(
                image=CRAWLER_IMAGE,
                command=command,
            )
            break
        except Exception, e:
            Crawler.status(crawler_id, 'error', str(e))
            return 'Error:'+e
    else:
        Crawler.status(crawler_id, 'error', 'pulling error')
        return 'Error'
    Crawler.register(crawler_id, container)
    Crawler.status(crawler_id, 'pending')
    dClient.client.start(container)
    Crawler.status(crawler_id, 'crawling')
    
    def callback(response, container=container, crawler_id=crawler_id, patch_id=patch_id):
        dClient.client.remove_container(container)
        Crawler.status(crawler_id, 'finished')
        Binding.notify(Event.crawl_finished, arguments={'patch_id':patch_id})

    try:
        dClient.async_action(container, 'wait', callback=callback).next()
    except StopIteration:
        Crawler.status(crawler_id, 'error', 'async method wrong!')
        return 'Error'   
    return 'Success'
