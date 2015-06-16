# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月15日 星期一 15时31分04秒
#
# 模型层调用文件 
#
import logging
import cluster
from bind import Binding, Event
import tornado.gen
import environment
import database
import json

Binding(Event.patch_finished, 'model.calculate').bind() #绑定索引更新完成事件
Binding.register(Event.calculate_finished) #注册索引更新完成事件

def calculate(arguments):
    '''
        搜索引擎更新索引
        参数:
            model_id: 模型id
    '''
    model_id = arguments.get('model_id', None)

    #检查参数
    if model_id is None:
        return 'Error: no model id'
    
    model = database.Model.select(model_id)
    
    if model is None:
        return 'Error: model not found'
    
    model_args = {}
    for argument in json.loads(model.model_arguments):
        model_args[argument] = arguments.get(argument, None)
        if model_args[argument] is None:
            return 'Error: {argument} not found !'.format(argument=argument)

    #生成命令
    command = "".join(model_args.values())

    #创建并开启容器
    try:
        container = cluster.SWARM_CLIENT.create_container(
            image=model.model_image,
            command=command,
            environment={
                "DATABASE_USER" : environment.get_user(),
                "DATABASE_PASSWD" : environment.get_password(),
            },
        )
    except Exception, e:
        return 'Error:'+str(e)
    
    cluster.SWARM_CLIENT.start(
        container,
    )
    
    @tornado.gen.engine
    def gen_wait(container=container):
        yield tornado.gen.Task(cluster.async_action, container, 'wait')
        cluster.SWARM_CLIENT.remove_container(container)
        Binding.notify(Event.calculate_finished, 'okay')

    try:
        gen_wait()
    except StopIteration:
        return 'Error'

    return 'Success'
