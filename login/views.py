# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.models import User, auth
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.http import urlquote
from django.views.decorators.http import require_http_methods

from sh_psi.settings import WORK_WEIXIN_CONFIG
# from libs import WorkWeixin  # 实例化微信操作类
import WorkWeixin
# from login import forms


# Create your views here.
@require_http_methods(['GET'])  # js操作前端用GET方式get后端
def confirm_login(request):
    form = WorkWeixin.comfirm_login_form(request.GET)
    if form.is_valid():
        code = form.cleaned_data['code']
        state = form.cleaned_data['state']
        ww = WorkWeixin.WorkWeixin()
        status, msg = ww.get_user_id(code)
        if status:
            userid = msg
            if not User.objects.filter(username=userid).exists():
                status, user_info = ww.get_user_info(userid)
                if status:
                    u = User(username=userid, first_name=user_info['name'])
                    u.save()
                    auth.login(request, u)
                    # if state == 'mobile':
                    #     return HttpResponseRedirect('/mobile/#/')
                    r = HttpResponseRedirect('/#/')
                    r.set_cookie('userid', urlquote(u.username), max_age=7200)
                    r.set_cookie('chinese_name', urlquote(u.first_name), max_age=7200)
                    return r
                else:
                    return HttpResponseBadRequest(
                        json.dumps({'status': False, 'msg': '获取微信服务失败，请稍后重试:' + str(user_info)}))
            else:
                u = User.objects.get(username=userid)
                auth.login(request, u)
                r = HttpResponseRedirect('/#/')
                r.set_cookie('userid', urlquote(u.username), max_age=7200)
                r.set_cookie('chinese_name', urlquote(u.first_name), max_age=7200)
                return r
        else:
            return HttpResponseBadRequest(json.dumps({'msg': '获取微信服务失败，请稍后重试:' + msg}))
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'status': False, 'msg': e, 'data': ''}))


# 前端ajax访问，获取后端关于配置信息，用来获取二维码，用户扫了二维码并确认登陆，微信服务器回复相关信息（成功或失败）给前端后带着相关信息跳转到指定地址
@require_http_methods(['POST'])
def get_login_meta(request):
    referrer = request.META['HTTP_REFERER']  # 请求本url前的url，当前访问某个保存界面，没登陆，登陆后自动跳回
    return HttpResponse(json.dumps({'msg': '', 'data': {
        'appid': WORK_WEIXIN_CONFIG['corpid'],
        'agentid': WORK_WEIXIN_CONFIG['agentid'],
        # 'redirect_uri': referrer + 'psi/login/confirm_login',  # 跳转网址
        'redirect_uri': referrer + WORK_WEIXIN_CONFIG['redirect_uri'],
        'state': WORK_WEIXIN_CONFIG['corpid'],
    }}))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/#/login")
