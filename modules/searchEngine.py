# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年05月11日 星期一 17时07分31秒
# 
import logging
import dClient
from bind import Binding, Event
import tornado.gen

SEARCH_ENGINE_IMAGE = 'companyservice/searchengine'

Binding(Event.crawl_finished, 'searchEngine.patch').bind()
Binding.register(Event.patch_finished)
Binding.register(Event.search_finished)

def patch(arguments):
    patch_id = arguments.get('patch_id', None)

    if patch_id is None:
        return 'Error: no patch id'

    if isinstance(patch_id, list):
        patch_id = patch_id.pop()

    command = 'patch {patch_id}'.format(patch_id=patch_id)

    for times in xrange(5):
        try:
            container = dClient.client.create_container(
                image=SEARCH_ENGINE_IMAGE,
                command=command,
                environment=["affinity:container==luceneIndex"],
            )
            break
        except Exception, e:
            return 'Error:'+str(e)
    else:
        return 'Error: image pull error' 
    
    dClient.client.start(
        container,
        volumes_from='luceneIndex',
    )
    
    def callback(response, container=container, patch_id=patch_id):
        dClient.client.remove_container(container)
        Binding.notify(Event.patch_finished, arguments={'patch_id':patch_id})

    try:
        dClient.async_action(container, 'wait', callback=callback).next()
    except StopIteration:
        Crawler.status(crawler_id, 'error', 'async method wrong!')
        return 'Error'   

    return 'Success'

def search(arguments):
    search_id = arguments.get('search_id', None)
    
    if search_id is None:
        return 'Error: no search id'
    
    if isinstance(search_id, list):
        search_id = search_id.pop()

    command = 'search {search_id}'.format(search_id=search_id)

    for times in xrange(5):
        try:
            container = dClient.client.create_container(
                image=SEARCH_ENGINE_IMAGE,
                command=command,
                environment=["affinity:container==luceneIndex"],
            )
            break
        except Exception, e:
            return 'Error:'+str(e)
    else:
        return 'Error: image pull error' 
    
    dClient.client.start(
        container,
        volumes_from='luceneIndex',
    )
    
    @dClient.async
    def wait(container, search_id=search_id):
        dClient.client.wait(container)
        dClient.client.remove_container(container)
        Binding.notify(Event.search_finished, arguments={'search_id':search_id})

    try:
       wait(container).next() 
    except StopIteration:
        return 'Error'   

    return 'Success'
