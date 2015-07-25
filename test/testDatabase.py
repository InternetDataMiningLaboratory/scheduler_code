# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月12日 星期五 19时45分51秒
# 
from database import Connection, ConnectionMissingDatabaseException
import mock
from mock import patch
from nose.tools import *
import torndb
import logging

@patch('logging.error')
def test_database_connection_missing_database_exception(mock_logging_error):
    '''
        test#1 数据库连接函数数据库名未指定异常生成测试
    '''
    try:
        raise ConnectionMissingDatabaseException()
    except ConnectionMissingDatabaseException, e:
        mock_logging_error.assert_called_with(u'异常：数据库连接缺少数据库名！'.encode('utf8'))
        assert_equal(str(e), u'数据库连接未指定数据库名！'.encode('utf8'))

@raises(ConnectionMissingDatabaseException)
def test_throw_database_connection_missing_database_exception():
    '''
        test#1 数据库连接函数数据库名未指定异常抛出测试
    '''
    Connection()

@patch('torndb.Connection')
def test_database_connection(mock_connection):
    '''
        test#2 数据库连接torndb参数传入检测
    '''
    with Connection('mysql') as conn:
        mock_connection.assert_called_with(
            'mysql', 
            'mysql', 
            user=None, 
            password=None,
            connect_timeout=10,
        )

@timed(21)
@patch.object(Connection, '__exit__')
def test_database_connection_operational_exception(mock_exit):
    '''
        test#2 数据库连接OperationalError异常检测
        检查__exit__是否捕获了该异常
        检查是否在超时时限内抛出异常
    '''
    with Connection('mysql') as conn:
        conn.get('test')
    assert_true(mock_exit.called)
    raised_error = mock_exit.call_args_list.pop()[0][1]
    assert_is_instance(raised_error, torndb.OperationalError)

