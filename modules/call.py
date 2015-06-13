# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年05月11日 星期一 21时15分44秒
# 
import logging

def Call(service_name, service_action, arguments=None):
    info_string =\
        (
            'Calling service {service_name} '
            'in action {service_action} with arguments:\n'
            '{arguments}'
        ).format(
            service_name=service_name,
            service_action=service_action,
            arguments='\n'.join(arguments) if arguments is not None else (),
        )
    logging.info(info_string)
    call_service = None
    try:
        call_service = __import__('modules.'+service_name)
    except ImportError, e:
        logging.exception("call modules import error")
        return 'Error: '+str(e)
    call_service = getattr(call_service, service_name)
    print call_service
    try:
        call_action = getattr(call_service, service_action)
    except AttributeError, e:
        logging.exception("call cattribute error")
        return 'Error: '+str(e)
    return str(call_action(arguments))
