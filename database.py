# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月06日 星期五 16时36分19秒
# 
import torndb
import logging
import json
import os

COMPANY_SERVICE =\
    torndb.Connection(
        'mysql.service.consul',
        'company_service',
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWD'),
    )

def release():
    COMPANY_SERVICE.close()

class Crawler(object):
    __slots__ =\
        (
            "crawler_id",
            "crawler_name",
            "crawler_jobid",
            "crawler_type",
            "crawler_type",
            "crawler_rule",
            "crawler_timing",
            "crawler_status",
        )

    @staticmethod        
    def select(crawler_id):
        sql =\
            (
                'SELECT * '
                'FROM contribute_crawler.crawler '
                'WHERE crawler_id = {crawler_id}'
            ).format(crawler_id=crawler_id)
        return COMPANY_SERVICE.get(sql)
    
    @staticmethod
    def _update(index, value_dict, search_column='crawler_id'):
        value_sql = ''
        if getattr(Crawler, search_column, None) is None:
            logging.error('Search column '+search_column+' not in Crawler!')
            return
        for key, value in value_dict.iteritems():
            if getattr(Crawler, key, None) is None:
                logging.error('Key '+key+' not in Crawler, skip in the update course')
                continue
            if isinstance(value, basestring):
                value = ''.join(('\'', value, '\''))
            value_sql += '{key} = {value} '.format(key=key, value=value)
        sql =\
            (
                'UPDATE contribute_crawler.crawler '
                'SET {value_sql} '
                'WHERE {search_column} = {index}'
            ).format(
                value_sql=value_sql,
                search_column=search_column,
                index=index,
            )
        COMPANY_SERVICE.execute(sql)
        
    @staticmethod
    def status(crawler_id, new_status, text=None, search_column='crawler_id'):
        _status = [
            'error',
            'finished',
            'pending',
            'crawling',
        ]
        if new_status not in _status:
            logging.error('Error: '+new_status+' not defined in Crawler update')
            return
        if text is not None:
            new_status = ''.join((new_status, ':', text))
        value_dict = {'crawler_status': new_status}
        Crawler._update(crawler_id, value_dict, search_column=search_column)

    @staticmethod
    def register(crawler_id, container):
        container_id = container['Id']
        value_dict = {'crawler_jobid': container_id}
        Crawler._update(crawler_id, value_dict)
