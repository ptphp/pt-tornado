# -*- coding: utf-8 -*- 
import re
import time
import urllib
import hashlib
import httplib
import datetime
import functools
import traceback
import simplejson as json
from operator import itemgetter
import tornado.web
import tornado.escape
from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient

from sqlalchemy.exc import StatementError #@UnresolvedImport
from sqlalchemy.orm.exc import NoResultFound #@UnresolvedImport

from dhole.utils import _len
from dhole.db.models import *
import binascii
import uuid
import math

def admined(method):
    """Decorate methods with this to require that user be NOT logged in"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.adminAuth() is None:
            if self.request.method in ("GET", "HEAD"):
                self.redirect("/admin/girl/auth/login")
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

def unauthenticated(method):
    """Decorate methods with this to require that user be NOT logged in"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.request.method in ("GET", "HEAD"):
                self.redirect("/")
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):   
    _ = lambda self, text: self.locale.translate(text) # i18n func    
    @property
    def mail_connection(self):
        return self.application.mail_connection
    
    def getPager(self,curPage,total,size = 10):
        total = int(total)
        curPage = int(curPage)
        pager = {}
        pager['curPage'] = curPage
        pager['total'] = total
        pager['size'] = size
        pager['totalPages'] = int(math.ceil(total/size)+1)
        pager['start'] = (curPage -1)*size
            
        #print "curPage:{0},total:{1},size:{2},math.ceil(total/size){3}".format(curPage,total,size,pager['totalPages'])
        print pager
        return pager
    def get_current_user(self):
        '''Check user is logined'''
        auth = self.get_secure_cookie("auth")
        member_id = self.get_secure_cookie("uid")
        member = None
        if auth and member_id:
            auth = self.dba.get("select * from auth where secret = %s and user_id = %s limit 1",auth,member_id)
            if auth is None:
                self.clear_cookie("auth")
                self.clear_cookie("uid")
            else:
                member = self.dba.get("select * from user where id = %s" ,int(auth.user_id))
        return member
    
    def render(self, tplname, args = {}):
        '''Rewrite render func for use jinja2'''
        if "self" in args.keys():
            args.pop("self")
        tpl = self.jinja2.get_template(tplname)
        ren = tpl.render(page = self, _ = self._, user = self.current_user, **args)
        self.write(ren)
        #self.db.close()
        self.finish()
    def check_text_value(self, value, valName, required = False, max = 65535, min = 0, regex = None, regex_msg = None, is_num = False, vaild = []):
        ''' Common Check Text Value Function '''
        error = []
        if not value:
            if required:
                error.append(self._("%s is required") % valName)
            return error
        if is_num:
            try:
                tmp = int(value)
            except ValueError:
                return [self._("%s must be a number.") % valName]
            else:
                if vaild and tmp not in vaild:
                    return [self._("%s is invalid.") % valName]
                return []
        if _len(value) > max:
            error.append(self._("%s is too long.") % valName)
        elif _len(value) < min:
            error.append(self._("%s is too short.") % valName)
        if regex:
            if not regex.match(value):
                if regex_msg:
                    error.append(regex_msg)
                else:
                    error.append(self._("%s is invalid.") % valName)
        elif vaild and value not in vaild:
            error.append(self._("%s is invalid.") % valName)
        return error
    def check_username(self, usr, queryDB = False):
        return self.check_text_value(usr, self._("身份证"), required = True, max = 20, min = 3, \
                                           regex = re.compile(r'^([\w\d]*)$'), \
                                           regex_msg = self._("身份证不合法"))
    def check_password(self, pwd):
        return self.check_text_value(pwd, self._("Password"), required = True, max = 32, min = 6)
    def check_email(self, email, queryDB = False):
        error = []
        error.extend(self.check_text_value(email, self._("E-mail"), required = True, max = 100, min = 3, \
                                           regex = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE), \
                                           regex_msg = self._("Your Email address is invalid.")))
        if not error and queryDB:
            try:
                query = self.select_member_by_email(email)
            except NoResultFound:
                pass
            else:
                error.append(self._("That Email is taken. Please choose another."))
        return error
    
    @property
    def db(self):
        #return self.application.db
        return None
    
    @property
    def dba(self):
        return self.application.dba
    
    @property
    def jinja2(self):
        return self.application.jinja2
