# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月06日 星期五 16时36分19秒
# 
import MySQLdb as DB
import MySQLdb.cursors as Cursor
import logging
import json
import environment
import traceback


class ConnectionMissingDatabaseException(Exception):
    '''
        异常类，数据库连接未提供数据库名时抛出
        默认处理是中断当前连接操作
    '''
    def __init__(self):
        logging.error(u'异常：数据库连接缺少数据库名！'.encode('utf8'))
    
    def __str__(self):
        return u'数据库连接未指定数据库名！'.encode('utf8')

class Connection(object):
    '''
        数据库连接类
        例子：
            with Connection('mysql') as connection:
                #做一些数据库操作
    '''
    def __init__(self, database_name=None):
        '''
            初始化
            如果参数database_name未给出，则抛出异常
        '''
        if database_name is None:
            raise ConnectionMissingDatabaseException()
        self._database_name = database_name
    
    def __enter__(self):
        '''
            建立数据库连接
        '''
        self._connection = \
            DB.connect(
                host='mysql',
                db=self._database_name,
                user=environment.get_user(),
                passwd=environment.get_password(),
                charset='utf8',
            )
        return self

    def __exit__(self, reason, value, tb):
        '''
            关闭数据库连接，如果有异常则捕获
        '''
        if self._connection is not None:
            self._connection.close()
        if reason is not None:
            logging.error(str(value))
            logging.info(traceback.format_tb(tb))
        return True
    
    def _execute(self, cursor, sql, parameters):
        '''
            数据库执行语句，如果有异常则捕获并打印出错信息
        '''
        try:
            result = cursor.execute(sql, parameters)
        except Exception, e:
            logging.error(str(e))
            result = None
        return result

    def query(self, sql, *args):
        cursor = Cursor.BaseCursor()
        result = self._execute(cursor, sql, args)
        try:
            keys = [key[0] for key in cursor.description]
        except Exception, e:
            logging.error(str(e))
            result = None
        finally:
            cursor.close()
        if result is None:
            return {}
        return dict(zip(keys, result))

class BasicObject(object):
    '''
        数据库持久化对象基类
    '''
    _db = None
    _table = None

    def __init__(self, **kwargs):
        '''
            初始化方法
            读取一系列参数作为字典，将key作为属性，value作为属性的值创建持久化对象
        '''
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

class Crawler(BasicObject):
    '''
        后台爬虫持久化对象类
    '''

    @classmethod        
    def select(cls, crawler_id=None):
        '''
            根据crawler_id获取爬虫信息
        '''
        #如果没有提供crawler_id
        if crawler_id is None:
            return None
        sql =\
            (
                'SELECT * '
                'FROM contribute_crawler.crawler '
                'WHERE crawler_id = %s'
            )
        with Connection('contribute_crawler') as connection:
            cursor = connection.cursor()
            cursor.execute(sql, crawler_id)
            result = cursor.fetchone()
            if result is None:
                return result 
            return cls()
            
            
    
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

class Model(object):
    '''
        模型持久化对象
    '''
    @staticmethod
    def select(model_id):
        '''
            读取模型 
        '''
        sql = (
            'SELECT * '
            'FROM model '
            'WHERE model_id = {model_id}'
        ).format(model_id=model_id)
        
        return COMPANY_SERVICE.get(sql)
