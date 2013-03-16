#!user/bin/env python
# -*- coding: utf8 -*- 
from tornado.web import HTTPError
from tornado.web import authenticated
from dhole.db import *
from dhole.db.models import *
from dhole.base import BaseHandler
from dhole.base import unauthenticated
from sqlalchemy.orm.exc import NoResultFound #@UnresolvedImport
from hashlib import md5
import datetime
import time
from dhole.lib.email.main import sendEmail #@UnresolvedImport
from dhole.lib.alipay.alipay import create_direct_pay_by_user,return_verify#@UnresolvedImport
import urllib


class UserForgetPasswordHandler(BaseHandler,UserDBMixin):
	def post(self):
		username = self.get_argument("username", None)
		if username is None:return self.write("error|身份证叼不能为空！")
		
		user = self.get_user_by_idcard(username)
		
		if user is None:return self.write("error|身份证不存在")		
		email = user.email
		password = self.gen_password()
		
		pwd = md5(password).hexdigest()
		pwd = md5(self.settings['key_salt']+pwd).hexdigest()
		print "===================>",password
		self.update_newpassword(user.id,pwd)
		sendEmail([email], '战神网络密码修改',u"尊敬的用户您的密码已修改成功！<br>身份证号：%s<br>密码:%s" % (username,password) )
		self.write(u"您的密码已发送到:%s,请查收" % user.email)

class UserPasswordHandler(BaseHandler,UserDBMixin):
	@authenticated
	def post(self):
		old_password = self.get_argument("old_pass", None)
		new_password = self.get_argument("new_pass", None)
		re_password = self.get_argument("re_pass", None)
		
		if old_password is None or new_password is None or re_password is None :
			return self.write('error|密码不能为空！')
		
		if len(new_password)> 100 or len(new_password)<6:return self.write("error|密码不能少于6位！")
			
		if new_password != re_password :return self.write("error|重复密码不正确！")
		uid = self.get_secure_cookie("uid")		
		password = self.get_password_by_id(uid)
		if password == False : return self.write('error|没有找到用户密码！')
		
		pwd = md5(old_password).hexdigest()
		pwd = md5(self.settings['key_salt']+pwd).hexdigest()
		
		if password != pwd:return self.write("error|原码密不正确")
		
		pwd = md5(new_password).hexdigest()
		pwd = md5(self.settings['key_salt']+pwd).hexdigest()
		
		self.update_newpassword(uid,pwd)
		return self.write("0")
	
class UserProfileHandler(BaseHandler,UserDBMixin):
	@authenticated
	def get(self):
		nav_header = "user"
		title = self._("user")
		userinfo = self.get_user_info_by_id(self.get_secure_cookie("uid"))
		print userinfo
		self.render("user/profile.html", locals())
class UserOrderHandler(BaseHandler,OrderDBMixin):
	@authenticated
	def get(self):
		nav_header = "user"
		title = self._("user")
		orders = self.get_orders_by_uid(self.get_secure_cookie('uid'))
		self.render("user/order.html", locals())
		
class UserHandler(BaseHandler,iProductDBMixin):
	@authenticated
	def get(self):
		nav_header = "user"
		title = self._("user")
		print self.get_secure_cookie('uid')
		baodans = self.get_baodan_by_uid(self.get_secure_cookie('uid'))
		print baodans
		self.render("user/index.html", locals())
#login
class SigninHandler(BaseHandler,UserDBMixin):
	@unauthenticated
	def get(self):
		self.render("user/signin.html", locals())
	
	@unauthenticated
	def post(self):		
		usr = self.get_argument("usr", default = "")
		pwd = self.get_argument("pwd", default = "")
		
		res = self.get_user_by_idcard(usr)		
		if res is None: return self.write("error|身份证号不存在，请重新再试")
		pwd = md5(pwd).hexdigest()
		pwd = md5(self.settings['key_salt']+pwd).hexdigest()
		
		user = self.select_member_by_usr_pwd(usr,pwd)			
		if user is None:return self.write("error|身份证号和密码不匹配，请重新再试")
		
		auth = self.create_auth(user.id)		
		self.set_secure_cookie("auth", auth['secret'])
		self.set_secure_cookie("uid", str(user.id))
		self.write("0")

#reg
class SignupHandler(BaseHandler,UserDBMixin):
	@unauthenticated
	def get(self):
		self.render("user/signup.html", locals())
	@unauthenticated
	def post(self):
		self.require_setting('key_salt', 'key for Password')
		usr = self.get_argument("usr", default = "")
		pwd = self.get_argument("pwd", default = "")
		error = []
		error.extend(self.check_username(usr.lower(), queryDB = True))
		error.extend(self.check_password(pwd))
		if error:
			self.render("user/signup.html", locals())
			return
		member = User()
		member.username = usr
		pwd = md5(pwd).hexdigest()
		member.password = md5(self.settings['key_salt']+pwd).hexdigest()
		member.addtime = datetime.datetime.now()
		self.db.add(member)
		self.db.commit()
		auth = self.create_auth(member.id)
		self.set_secure_cookie('auth', auth.secret)
		self.set_secure_cookie('uid', str(auth.user_id))
		self.redirect('/')

class JoinHandler(BaseHandler,UserDBMixin):
	#@authenticated
	def get(self):
		self.render("user/join.html", locals())

class JoinPayHandler(BaseHandler,OrderDBMixin):
	def get(self):
		id =self.get_argument('id', None)		
		orderno = self.get_secure_cookie('otoken',None)
		if id is None or orderno is None : raise tornado.web.HTTPError(404)
		
		order = self.get_order_by_id_orderno(id,orderno)
		
		if order is None or order.status != 0:return self.write("订单状态不正确")
		
		money = order.price
		orderno = order.orderno
		name = order.name		
		sex = order.sex
		payurl = create_direct_pay_by_user(orderno, u'战神网站充值', u'充值 %d 元' % money, money)	
		self.render('game/pay.html',locals())

class JoinAlipayHandler(BaseHandler,OrderDBMixin,UserDBMixin,iProductDBMixin):
	def get(self):
		param = {}
		param['body'] = self.get_argument('body','')
		param['buyer_email'] = self.get_argument('buyer_email','')
		param['buyer_id'] = self.get_argument('buyer_id','')
		param['exterface'] = self.get_argument('exterface','')
		param['is_success'] = self.get_argument('is_success','')
		param['notify_id'] = self.get_argument('notify_id','')
		param['notify_time'] = self.get_argument('notify_time','')
		param['notify_type'] = self.get_argument('notify_type','')
		param['out_trade_no'] = self.get_argument('out_trade_no','')
		param['payment_type'] = self.get_argument('payment_type','')
		param['seller_email'] = self.get_argument('seller_email','')
		param['seller_id'] = self.get_argument('seller_id','')
		param['subject'] = self.get_argument('subject','')
		param['total_fee'] = self.get_argument('total_fee','')
		param['trade_no'] = self.get_argument('trade_no','')
		param['trade_status'] = self.get_argument('trade_status','')
		param['sign'] = self.get_argument('sign','')
		param['sign_type'] = self.get_argument('sign_type','')
		verify = return_verify(param)
		if verify:
			print "trade_no:"+param['trade_no']
			print "total_fee:"+param['total_fee']
			print "out_trade_no:"+param['out_trade_no']			
			orderno = param['out_trade_no']
			order = self.get_order_by_orderno(orderno)
			if order.status > 0: return self.write('订单已更新')
			
			self.update_order_by_orderno(orderno)
			
			u = self.get_user_by_idcard(order.idcard)
			
			if u is None:
				password = self.gen_password()
				pwd = md5(password).hexdigest()
				pwd = md5(self.settings['key_salt']+pwd).hexdigest()	
				user_id = self.create_user(order.idcard,order.email,order.name,pwd)
				#userinfo
				print user_id, order.birth, order.sex, order.mobile, order.address, order.phone, order.zip
				self.update_user_info(user_id, order.birth, order.sex, order.mobile, order.address, order.phone, order.zip)				
				email = order.email
			else:
				password = None
				user_id = u['id']
				email = u['email']
				
			ipro = self.get_ipro_by_uid_pid(user_id, order.pro_id,order.account)
			print ipro
			if ipro is None:
				#pass
				ipro_id = self.saveIPro(order.id,user_id)
			else:
				#if ipro.isActive:return self.write("error|您已激活您的理赔，请重新检查")
				return self.write("您已激活您的理赔，请重新检查")
			
			sendEmail([email], '战神网络用户信息',self.getEmailBody(order,password) )
			return self.render('game/success.html',locals())
		else:
			self.write("无效订单！")
	def getEmailBody(self,order,pwd):
		product = self.get_cname_gname_pinfo_by_pid(order.pro_id)	
		print product	
		htmlText = self.render_string('game/order_email.html',order=order,product=product,pwd=pwd)
		return htmlText
		
class JoinFinalHandler(BaseHandler,UserDBMixin,ProductDBMixin,OrderDBMixin,iProductDBMixin):
	def post(self):
		captcha = self.get_argument('captcha', None)
		if not captcha:return self.write('error|验证码不能为空')		
		_captcha = self.get_secure_cookie('captcha')
		if captcha != _captcha: return self.write("error|验证码不正确")		
		
		email = self.get_argument('email', None)
		if not email or len(email) > 50:return self.write('error|Email不能为空且不能超过50位')
		
		idcard = self.get_argument('idcard', None)
		if not idcard or len(idcard) > 20:return self.write('error|身份证号不能为空且不能超过20位')
		
		name = self.get_argument('name', None)
		if not name or len(name) > 5:return self.write('error|姓名不能为空且不能超过5位')
		
		sex = self.get_argument('sex', 0)		
		birth = self.get_argument('birth', '')
		
		mobile = self.get_argument('mobile', '')
		if not mobile or len(mobile) > 20:return self.write('error|手机不能为空且不能超过20位')
		
		address = self.get_argument('address', '')		
		if not address or len(address) > 100:return self.write('error|地址不能为空且不能超过1000位')
		
		account = self.get_argument('account', '')
		if not account or len(account) > 50:return self.write('error|游戏帐号不能为空且不能超过50位')		
			
		phone = self.get_argument('phone', '')
		if len(phone) > 20 :return self.write('error|住家电话不能超过20位')
		
		zip = self.get_argument('zip', '')
		if len(zip) > 6:return self.write('error|邮编不能超过6位')
		
		gameid = self.get_argument('gameid', '')
		
		product = self.get_argument('product', None)
		if not product:return self.write('error|您没有选择理赔等级')	
		print product
		pro = self.table("product").getOne(product)
		if not pro:return self.write('error|理赔产品为空')
		_promo = pro.promo		
		orderno =  int(time.time()*10)	
		self.set_secure_cookie('otoken',str(orderno))
		print orderno
		order = self.get_order_by_pid_idcard(product, idcard,account)
		if order: return self.write('error|您已购买过')
				
		id = self.saveOrder(orderno,pro.id,account,email,idcard,name,sex,birth,mobile,phone,address,zip,0,_promo)
		self.write(str(id))
		

#logout
class SignoutHandler(BaseHandler,UserDBMixin):
	@authenticated
	def get(self):
		auth = self.get_secure_cookie('auth')
		self.delete_auth_by_secret(auth)
		self.clear_cookie('auth')
		self.clear_cookie('uid')
		self.redirect('/')

__all__ = ["SigninHandler","SignupHandler","SignoutHandler"]
