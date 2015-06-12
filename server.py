# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月04日 星期三 15时54分30秒
# 
import tornado.ioloop
import tornado.autoreload
import application
import database
from tornado.options import define, options

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.application.listen(80)
    server_instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.add_reload_hook(database.release)
    server_instance.start()
