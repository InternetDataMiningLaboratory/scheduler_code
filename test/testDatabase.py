# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月12日 星期五 19时45分51秒
# 
import database
import mock
from mock import patch
from nose.tools import *
import MySQLdb
import MySQLdb.connections
import MySQLdb.cursors
import logging

@patch('logging.error')
def test_database_connection_missing_database_exception(mock_logging_error):
    '''
        数据库名未指定异常生成测试
    '''
    try:
        raise database.ConnectionMissingDatabaseException()
    except database.ConnectionMissingDatabaseException, e:
        mock_logging_error.assert_called_with(u'异常：数据库连接缺少数据库名！'.encode('utf8'))
        assert_equal(str(e), u'数据库连接未指定数据库名！'.encode('utf8'))

@raises(database.ConnectionMissingDatabaseException)
def test_throw_database_connection_missing_database_exception():
    '''
        数据库名未指定异常抛出测试
    '''
    database.Connection()

@patch('MySQLdb.connect')
@patch.multiple('logging', error=mock.Mock(), info=mock.Mock())
def test_database_connection_close(mock_enter):
    '''
        数据库对象exit函数测试
    '''
    #构造具有close属性的mock对象
    mock_connection = mock.Mock()
    mock_connection.mock_add_spec(["close"])
    mock_enter.return_value = mock_connection

    #正常情况下退出数据库连接
    with database.Connection('test') as conn:
        assert_is_not_none(conn)
    logging.error.assert_not_called()
    logging.info.assert_not_called()
    
    assert_true(mock_connection.close.called)

    #抛出异常情况下退出数据库连接
    with database.Connection('test') as conn:
        raise Exception('test')
    logging.error.assert_called_with('test')
    assert_true(logging.info.called)

def test_database_execute():
    '''
        测试数据库操作函数
        正常返回，异常则捕获数据库异常并返回None
    '''
    #构造参数与返回值
    sql = ''
    args = []
    result = None
    
    #构造测试参数
    mock_execute = mock.Mock(return_value=[1,2,3])
    mock_cursor = mock.Mock()
    mock_cursor.attach_mock(mock_execute, 'execute')

    #正常情况
    result = database.Connection('test')._execute(mock_cursor, sql, args)
    assert_list_equal(result, [1,2,3])
    
    #异常情况
    mock_execute.side_effect = Exception('test')
    with patch.object(logging, 'error'):
        result = database.Connection('test')._execute(mock_cursor, sql, args)
        logging.error.assert_called_with('test')
    assert_is(result, None)

@patch('database.Connection._execute')
@patch.object(MySQLdb.connections, 'Connection')
@patch.object(MySQLdb.cursors, 'BaseCursor')
def test_database_query(mock_cursor, mock_connect, mock_execute):
    '''
        测试数据库多条查询函数
        正常返回字典，异常则返回空字典
    '''
    sql = ''
    args = []
    result = None
    
    #构造测试参数
    expect = {
        'test_one' : 1,
        'test_two' : 2,
        'test_three' : 3,
    }
    description = [
        ("test_one", 'test'),
        ("test_two", 'test'),
        ("test_three", 'test'),
    ]
    mock_description = mock.Mock()
    mock_description.description = mock.MagicMock()
    mock_description.description.__iter__.return_value = description
    mock_cursor.return_value = mock_description
    mock_execute.return_value = [1,2,3]
    
    #正常字典返回值
    with database.Connection('test') as conn:
        result = conn.query(sql, args) 
    assert_dict_equal(result, expect)

    #异常返回空字典
    mock_description.description.__iter__.side_effect = Exception('test')
    with database.Connection('test') as conn:
        result = conn.query(sql, args)
    assert_dict_equal(result, {})
   
class TestBasicObject(object):
    '''
        测试持久化数据库对象基类BasicObject
    '''
    def setUp(self):
        '''
            测试准备，创建一个包含两个限定属性的子类
        '''
        class TestObject(database.BasicObject):
            __slots__ = [
                'test_one',
                'test_two',
            ]
        self.test_class = TestObject

    def test_init(self):
        '''
            测试正常创建持久化对象
        '''
        result = self.test_class(test_one='one', test_two='two')
        assert_is_instance(result, self.test_class)
        assert_true(result, 'test_one')
        assert_true(result, 'test_two')
        assert_equal(result.test_one, 'one')
        assert_equal(result.test_two, 'two')
