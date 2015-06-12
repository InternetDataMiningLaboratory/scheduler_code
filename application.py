#u -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月04日 星期三 20时34分03秒
# 
import tornado.web
import handlers
from settings import settings

'''
    application 
'''
application = tornado.web.Application([
    (r"/service/(\w+)/(\w+)", handlers.ServiceHandler),
    (r"/", handlers.BaseHandler),
], **settings)
