# -*- coding: utf-8 -*-
# 新的微信包
import logging, time, random, string
from django.conf import settings

WORK_WEIXIN_CONFIG = settings.WORK_WEIXIN_CONFIG
BASE_URL = settings.BASE_URL
import requests
from requests.exceptions import RequestException
from django_redis import get_redis_connection
import hashlib
import requests
from requests.exceptions import RequestException
from django.contrib.auth.models import User, auth
from django_redis import get_redis_connection
import hashlib, json
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest
from django import forms
from django.views.decorators.csrf import csrf_exempt


class comfirm_login_form(forms.Form):
    code = forms.CharField(
        label='企业微信返回码',
        min_length=5,
        max_length=128,
        error_messages={
            'required': u'code不能为空', }
    )
    state = forms.CharField(
        label='csrd_token',
        min_length=5,
        max_length=32,
        error_messages={
            'required': u'state不能为空', }
    )


def parse_wx_ret(rsp):
    """解析微信登录返回的json数据，返回相对应的dict, 错误信息"""
    if 200 != rsp.status_code:
        return None, {'code': rsp.status_code, 'msg': 'http error'}
    try:
        content = rsp.json()
    except Exception as e:
        return None, {'code': 9999, 'msg': e}
    if 'errcode' in content and content['errcode'] != 0:
        return None, {'code': content['errcode'], 'msg': content['errmsg']}
    return content, None


class WorkWeixin():
    def __init__(self):
        self.corpid = WORK_WEIXIN_CONFIG['corpid']
        self.corpsecret = WORK_WEIXIN_CONFIG['corpsecret']
        self.agentid = WORK_WEIXIN_CONFIG['agentid']
        self.access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        self.get_userid_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
        self.get_user_info_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        self.jsapi_ticket_url = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket'
        self.app_jsapi_ticket_url = 'https://qyapi.weixin.qq.com/cgi-bin/ticket/get'
        self.actoken_name = 'work_weixin_at_' + str(self.corpid)
        self.ticket_name = 'work_weixin_jsapi_ticket_' + str(self.corpid)
        self.app_ticket_name = 'work_weixin_app_config_ticket_' + str(self.corpid)

    def get_access_tocken(self):
        redis_conn = get_redis_connection()
        ww_access_token = redis_conn.get(self.actoken_name)
        if ww_access_token:
            return True, ww_access_token
        else:
            try:
                url = self.access_token_url
                r = requests.get(url, params={'corpid': self.corpid, 'corpsecret': self.corpsecret})
                ret = r.json()
                if int(ret['errcode']) == 0:
                    redis_conn.set(self.actoken_name, ret['access_token'], 7100)
                    return True, ret['access_token']
                else:
                    print ret['errmsg']
                    return False, ret['errmsg']
            except  RequestException as e:
                msg = '无法连接微信服务器:错误是:', e.message
                return False, msg

    def get_user_id(self, code):
        status, msg = self.get_access_tocken()
        if status:
            try:
                r = requests.get(self.get_userid_url, params={'access_token': msg, 'code': code})
                ret = r.json()
                if int(ret['errcode']) == 0:
                    print 'ret is ', str(ret)
                    if ret.has_key('OpenId'):
                        return False, '无法获取定位企业'
                    print 'user info is ', ret
                    userid = ret['UserId']
                    return True, userid
                else:
                    print ret['errmsg']
                    return False, ret['errmsg']
            except  RequestException as e:
                msg = '无法连接微信服务器:错误是:', e.message
                return False, msg
        else:
            return False, msg

    def get_user_info(self, user_id):
        ac_status, msg = self.get_access_tocken()
        if ac_status:
            try:
                print 'userid is :', user_id
                r = requests.get(self.get_user_info_url, params={'access_token': msg, 'userid': user_id})
                ret = r.json()
                print 'user info is ', ret
                if ret['errcode'] == 0:
                    user_info = ret
                    return True, user_info
                else:
                    print ret['errmsg']
                    return False, ret['errmsg']
            except  RequestException as e:
                msg = '无法连接微信服务器:错误是:', e.message
                return False, msg
        else:
            return False, msg

    def get_ww_jsapi_ticket(self):
        redis_conn = get_redis_connection()
        ww_jsapi_ticket = redis_conn.get('work_weixin_jsapi_ticket')
        if ww_jsapi_ticket:
            return True, ww_jsapi_ticket
        else:
            ac_status, msg = self.get_access_tocken()
            if ac_status:
                try:
                    r = requests.get(self.jsapi_ticket_url, params={'access_token': msg})
                    ret = r.json()
                    print 'jsapi_ticket msg is ', ret
                    if ret['errcode'] == 0:
                        jsapi_ticket = ret['ticket']
                        redis_conn.set('work_weixin_jsapi_ticket', ret['ticket'], 7100)
                        return True, jsapi_ticket
                    else:
                        print ret['errmsg']
                        return False, ret['errmsg']
                except  RequestException as e:
                    msg = '无法连接微信服务器:错误是:', e.message
                    return False, msg
            else:
                return False, msg

    def get_app_config_ticket(self):
        redis_conn = get_redis_connection()
        work_weixin_app_config_ticket = redis_conn.get('work_weixin_app_config_ticket')
        if work_weixin_app_config_ticket:
            return True, work_weixin_app_config_ticket
        else:
            ac_status, msg = self.get_access_tocken()
            if ac_status:
                try:
                    r = requests.get(self.app_jsapi_ticket_url, params={'access_token': msg, 'type': 'agent_config'})
                    ret = r.json()
                    print 'jsapi_ticket msg is ', ret
                    if ret['errcode'] == 0:
                        jsapi_ticket = ret['ticket']
                        redis_conn.set('work_weixin_app_config_ticket', ret['ticket'], 7100)
                        return True, jsapi_ticket
                    else:
                        print ret['errmsg']
                        return False, ret['errmsg']
                except  RequestException as e:
                    msg = '无法连接微信服务器:错误是:', e.message
                    return False, msg
            else:
                return False, msg

    def gen_signature(self, noncestr, jsapi_ticket, timestamp, url):
        str = 'jsapi_ticket=%s&noncestr=%s&timestamp=%d&url=%s' % (jsapi_ticket, noncestr, timestamp, url)
        s = hashlib.sha1(str).hexdigest()
        print s
        return s

    def get_ww_config(self, url):

        status, app_ticket = self.get_ww_jsapi_ticket()
        if status:
            timestamp = int(time.time())
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            print app_ticket
            sign = self.gen_signature(noncestr=ran_str, jsapi_ticket=app_ticket, timestamp=timestamp, url=url)
            return True, {'timestamp': timestamp,
                          'noncestr': ran_str,
                          'signature': sign,
                          }
        else:
            return False, ''

    def get_app_config(self, url):

        status, app_ticket = self.get_app_config_ticket()
        if status:
            timestamp = int(time.time())
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            print app_ticket
            sign = self.gen_signature(noncestr=ran_str, jsapi_ticket=app_ticket, timestamp=timestamp, url=url)
            return True, {'timestamp': timestamp,
                          'noncestr': ran_str,
                          'signature': sign,
                          }
        else:
            return False, ''


def work_weixin_lauth(func):
    # 用于企业自建应用的链接 js-sdk 登陆链接

    def function(request):

        request_url = BASE_URL + '/refund/confirm_login'
        print request_url
        # 获取 openid
        if 'userid' not in request.COOKIES:
            print '-----userid not  in browser!'
            if 'code' not in request.GET:
                print 'code not in request.get'
                url = 'https://open.weixin.qq.com/connect/oauth2/authorize?' \
                      'appid=%s&redirect_uri=%s&response_type=code&state=mobile&scope=snsapi_base#wechat_redirect' % (
                          WORK_WEIXIN_CONFIG['corpid'], request_url)
                # print url
                r = redirect(url)
                r["Access-Control-Allow-Origin"] = "https://open.weixin.qq.com"
                return r
            else:
                # 返回 code页面

                code = request.GET.get('code')
                print 'get CODE'
                # 获取openid
                ww = WorkWeixin()
                status, user_id = ww.get_user_id(code)
                if not status:
                    print 'cannot get user id %s' % user_id
                    return HttpResponseBadRequest(user_id)
        else:
            print 'openid in browser!'
            user_id = request.COOKIES.get('userid')

        if User.objects.filter(username=user_id).exists():
            u = User.objects.get(username=user_id)
            auth.login(request, u)

        else:
            ww = WorkWeixin()
            print 'user_id is %s' % user_id
            status, msg = ww.get_user_info(user_id=user_id)
            if status:
                user_info = msg
                u = User()
                u.username = user_id
                u.first_name = user_info['name']
                u.save()
                auth.login(request, u)
            else:
                return HttpResponseBadRequest('获取用户信息失败:%s,userid is :%s' % (str(msg), user_id))

        resp = func(request, userid=user_id)
        chinese_name = u.first_name
        resp.set_cookie('username', user_id)
        resp.set_cookie('chinese_name', urlquote(chinese_name))
        return resp

    return function


@require_http_methods(['GET'])
def confirm_login(request):
    form = comfirm_login_form(request.GET)
    if form.is_valid():
        code = form.cleaned_data['code']
        state = form.cleaned_data['state']
        ww = WorkWeixin()
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


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/#/login")


@csrf_exempt
@require_http_methods(['POST'])
def get_login_meta(request):
    referrer = request.META['HTTP_REFERER']
    return HttpResponse(json.dumps({'msg': '', 'data': {
        'appid': WORK_WEIXIN_CONFIG['corpid'],
        'agentid': WORK_WEIXIN_CONFIG['agentid'],
        'redirect_uri': referrer + WORK_WEIXIN_CONFIG['redirect_uri'],
        'state': WORK_WEIXIN_CONFIG['corpid'],
    }}))
