# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年06月12日 星期五 19时07分23秒
# 
# 环境变量文件
#
import os

def get_user():
    return os.getenv('DATABASE_USER')

def get_password():
    return os.getenv('DATABASE_PASSWD')
