# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月05日 星期四 09时49分35秒
# 

import tornado.web
import handlers
import logging
import json
from modules.call import Call

class BaseHandler(tornado.web.RequestHandler):
    '''
        base handler, the base class of other handlers
        handle the requests which do not be matched by any rules in application
        raise an 404 error
    '''
    def get(self):
        self.write_error(404)
    
    def write_error(self, status_code, **kwargs):
        self.render('404.html', title="404")

class ServiceHandler(BaseHandler):
    '''
        ServiceHandler control the request to service.
        Handler calls some method in the module includes in modules package according to the parameters in request. 
    ''' 
    def post(self, service_name, service_action):
        arguments = self.request.arguments
        self.write(str(Call(service_name, service_action, arguments)))
'''
class PatchHandler(BaseHandler):
    def get(self):
        user_id = self.get_argument('user_id')
        patch = self.get_argument('patch').strip()
        patch = json.dumps(json.loads(patch))
        patch_id = str(database.create_patch(patch))
        model_image = database.model_image(user_id)['model_image']
        dClient.model(model_image, user_id, patch_id)        
    '''   
