# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年05月11日 星期一 21时46分03秒
# 
import cluster, logging
from call import Call

LISTEN_DIRECTORY = 'listen/'

class Event(object):
    __slots__ = [
        'crawl_finished',
        'patch_finished',
        'search_finished',
        'calculate_finished',
    ]
    crawl_finished = 'crawler.crawl_finished'
    patch_finished = 'searchEngine.patch_finished'
    search_finished = 'searchEngine.search_finished'
    calculate_finished = 'model.calculate_finished'

class Binding(object):
    __slots__ = [
        'bind_event',
        'listen_event',
        'key',
    ]
    
    def __init__(self, bind_event, listen_event):
        self.bind_event =\
            '{listen_directory}{bind_event}'.format(
                listen_directory = LISTEN_DIRECTORY,
                bind_event=bind_event,
            )
        
        self.listen_event =\
            '{listen_event}'.format(
                listen_event=listen_event,
            )

        self.key = self.bind_event + '/' + self.listen_event

    def bind(self):
        cluster.CONSUL_CLIENT.kv.put(self.key, self.listen_event)
        logging.info('Binding service: ' + self.bind_event + ':' + self.listen_event)

    def unbind(self):
        cluster.CONSUL_CLIENT.kv.delete(self.key)
        logging.info('Unbinding service: ' + self.bind_event + ':' + self.listen_event)

    @staticmethod
    def query(bind_event):
        bind_dir = LISTEN_DIRECTORY + bind_event
        keys = cluster.CONSUL_CLIENT.kv.get(bind_dir, keys=True)[1]
        if keys is None:
            return None
        filtered_keys = []
        for key in keys:
            key = key.split('/')[-1]
            if key == bind_event:
                continue
            filtered_keys.append(key)
        logging.info('Query binding: ' + bind_event + '\n' + '\n'.join(filtered_keys))
        return filtered_keys

    @staticmethod
    def register(bind_event):
        if Binding.query(bind_event) is None:
            bind_event = LISTEN_DIRECTORY + bind_event
            cluster.CONSUL_CLIENT.kv.put(bind_event, None)
        logging.info('Register event: ' + bind_event)

    @staticmethod
    def register_dict(bind_events):
        map(Binding.register, bind_events)
        logging.info('Register events: \n' + '\n'.join(bind_event))

    @staticmethod
    def notify(bind_event, arguments):
        listen_events = Binding.query(bind_event)
        if listen_events is None:
            logging.info('Notifying events by ' + bind_event + ': no listen events')
            return
        logging.info('Notifying events by ' + bind_event + ':\n' + '\n'.join(listen_events))
        def get_event(e, arguments=arguments):
            if not e:
                return
            event = {}
            e = e.split('.')
            event['service_name'] = e[0]
            event['service_action'] = e[1]
            event['arguments'] = arguments
            Call(**event)
        map(get_event, listen_events)
