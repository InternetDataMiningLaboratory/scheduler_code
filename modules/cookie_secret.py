# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月13日 星期六 15时38分50秒
# 生成cookie加密密钥
#
import base64
import uuid


def _generate():
    '''
        生成密钥
    '''
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

_SECRET = _generate()

def update(force=False):
    '''
        更新密钥
        force参数指定是否强制刷新
    '''
    if not force and _SECRET is not None:
        return
    _SECRET = _generate()

def get():
    return _SECRET
