#!user/bin/env python
# -*- coding: utf8 -*- 

from dhole.db import *
from dhole.base import BaseHandler
from tornado.web import authenticated
from dhole.db import *
from dhole.lib.imagelib.imagelib import Recaptcha #@UnresolvedImport
import logging
import random

def generate_random(length=8):
    """Generate random number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


class HomeHandler(BaseHandler,CompnayDBMixin,ContentDBMixin):
	def get(self):
		nav_header = "index"
		title = self._("Home")
		breadcrumb = []
		#print self.settings		
		#news = self.getIndexNews9()
		#picNews = self.getIndexPicNews()
		picNews = []
		companys = self.getIndexCompany()
		self.render('index.html',locals())


class CheckCaptchaHandler(BaseHandler):
	def get(self):
		cap = self.get_argument('c', None)
		if not cap:
			return self.write("1")	
		if cap == self.get_secure_cookie("captcha"):			
			return self.write("0")
		else:
			return self.write("1")
class CaptchaHandler(BaseHandler):
	def get(self):
		text = generate_random(4)
		self.set_secure_cookie("captcha", text)		
		strIO = Recaptcha(text)		
		#,mimetype='image/png'
		self.set_header("Content-Type", "image/png")
		return self.write(strIO.read())
		
__all__ = ["HomeHandler"]