# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月06日 星期五 16时36分19秒
# 
import torndb
import logging
import json
import environment

COMPANY_SERVICE =\
    torndb.Connection(
        '172.16.153.45',
        'company_service',
        user=environment.get_user(),
        password=environment.get_password(),
    )

def release():
    COMPANY_SERVICE.close()

class Crawler(object):
    '''
        爬虫的持久化对象
    '''

    @staticmethod        
    def select(crawler_id):
        '''
            获取爬虫信息
        '''
        sql =\
            (
                'SELECT * '
                'FROM contribute_crawler.crawler '
                'WHERE crawler_id = {crawler_id}'
            ).format(crawler_id=crawler_id)
        return COMPANY_SERVICE.get(sql)
    
    @staticmethod
    def _update(index, value_dict, search_column='crawler_id'):
        '''
            更新爬虫信息
        '''
        value_sql = ""

        #生成更新语句
        for key, value in value_dict.iteritems():
            #字符串需要用单引号包围
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
        '''
            更新爬虫状态
        '''

        #状态列表
        _status = [
            'error',
            'finished',
            'pending',
            'crawling',
        ]
        
        #检查新状态
        if new_status not in _status:
            logging.error('Error: '+new_status+' not defined in Crawler update')
            return
        
        #状态附带信息的添加
        if text is not None:
            new_status = ''.join((new_status, ':', text))

        value_dict = {'crawler_status': new_status}
        Crawler._update(crawler_id, value_dict, search_column=search_column)

    @staticmethod
    def register(crawler_id, container):
        '''
            生成新的爬虫任务
        '''
        container_id = container['Id']
        value_dict = {'crawler_jobid': container_id}
        Crawler._update(crawler_id, value_dict)
