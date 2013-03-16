# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect #@UnresolvedImport

import alipay #@UnresolvedImport

if __name__ == "__main__":
    moneys = 100
    payurl = alipay.create_direct_pay_by_user('12345', u'充值测试', u'充值 %d 元' % moneys, moneys)
    # return HttpResponseRedirect(payurl)
    print payurl # 直接跳转到此 url 用户即可充值  用户充值成功后 alipay 将回调 alipay_notify





