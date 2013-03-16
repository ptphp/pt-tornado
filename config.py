#!/usr/bin/env python
# -*- coding=utf-8 -*-
'''
Created on 2013-2-3
@author: Joseph
'''
import os
from dhole.lib.alipay import alipay #@UnresolvedImport

settings={
          'site_name':u"",
          'site_title':u"",    
          'port':8000,
          "static_path":os.path.join(os.path.dirname(__file__), "static"),
          "template_path" : os.path.join(os.path.dirname(__file__), "template"),
          "login_url":"/signin",
          "xsrf_cookies": False,
          "autoescape":None,
          "gzip" : True, 
          "debug" : False,
          "cookie_secret":'cookie_secret',
          'key_salt':"key_salt"
}

mysql_config = {
                'dev':{
                    'mysql_host':'127.0.0.1',
                    'mysql_db':'',
                    'mysql_user':'root',
                    'mysql_pass':'root',
                    'mysql_debug':True,
                    'schema_file':os.path.join("data","schema.sql"),
                    },
                
                'deploy':{
                    'mysql_host':'127.0.0.1',
                    'mysql_db':'',
                    'mysql_user':'',
                    'mysql_pass':'',
                    'mysql_debug':False,
                    'schema_file':os.path.join(os.path.dirname(__file__), "data","schema.sql"),
                        }
                }
def getDevSetting(__settings):
    __settings['debug'] = True
    __settings['static_path'] = os.path.join(os.path.dirname(__file__), "static")    
    # __settings['static_path'] = 'D:\Dhole\PtProject\PtWebos\Public\static'
    return __settings

def setDev():
    alipay_setting = alipay.Settings()    
    alipay_setting.ALIPAY_PARTNER = ''    
    alipay_setting.ALIPAY_KEY = ''    
    alipay_setting.ALIPAY_SELLER_EMAIL = ''    
    alipay_setting.ALIPAY_NOTIFY_URL = ''    
    alipay_setting.ALIPAY_RETURN_URL = ''

def setDeploy():
    alipay_setting = alipay.Settings()    
    alipay_setting.ALIPAY_PARTNER = ''    
    alipay_setting.ALIPAY_KEY = ''    
    alipay_setting.ALIPAY_SELLER_EMAIL = ''    
    alipay_setting.ALIPAY_NOTIFY_URL = ''    
    alipay_setting.ALIPAY_RETURN_URL = ''

