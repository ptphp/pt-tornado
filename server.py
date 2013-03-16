#!user/bin/env python
# -*- coding: utf8 -*-
import sys,os
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from dhole.lib import torndb #@UnresolvedImport
from jinja2 import Environment, FileSystemLoader #@UnresolvedImport

from sqlalchemy import create_engine #@UnresolvedImport
from sqlalchemy.orm import scoped_session, sessionmaker #@UnresolvedImport

from dhole.db import models
from dhole.filters import filters
from config import settings,mysql_config,getDevSetting,setDev,setDeploy#@UnresolvedImport
from handlers import handlers #@UnresolvedImport

from dhole.lib.alipay import alipay #@UnresolvedImport

define("mode", default='deploy', help="deploy or dev mode") 
define("port", default=settings['port'], help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        ss = alipay.Settings()
        print ss.ALIPAY_RETURN_URL
        if options.mode =='dev':
            setDev()
            global settings
            settings = getDevSetting(settings)   
        else:
            setDeploy()            
        alipay_setting = alipay.Settings()    
        tornado.web.Application.__init__(self, handlers, **settings)     
        # Set Jinja2
        jinja_env = Environment(loader = FileSystemLoader(self.settings['template_path']))
        jinja_env.filters.update(filters)
        self.jinja2 = jinja_env
      
        #engine = create_engine("mysql://{0}:{1}@{2}/{3}?charset=utf8".format(mysql_config[options.mode]['mysql_user'], mysql_config[options.mode]['mysql_pass'], mysql_config[options.mode]['mysql_host'], mysql_config[options.mode]['mysql_db'])
        #                  , pool_size = options.mysql_poolsize
        #                  , pool_recycle = 3600
        #                  , echo=mysql_config[options.mode]['mysql_debug']
        #                  , echo_pool=mysql_config[options.mode]['mysql_debug']
        #                  )
        #self.db = scoped_session(sessionmaker(bind=engine))
        
        # Have one global connection to the blog DB across all handlers
        self.dba = torndb.Connection(
            host=mysql_config[options.mode]['mysql_host'], database=mysql_config[options.mode]['mysql_db'],
            user=mysql_config[options.mode]['mysql_user'], password=mysql_config[options.mode]['mysql_pass'])

def main():   
    import logging 
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
     
    logging.info("server is running at: %d",options.port)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":    
    main()