# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月05日 星期四 09时51分22秒
# 
import os 
import modules
all_module = {
}
settings = {
    'debug' : True,
    'login_url' : '/login',
    'static_path' : os.path.join(os.path.dirname(__file__), 'static'),
    'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
    #'log_file_prefix': '8888.log',
    'ui_modules':all_module,
}

