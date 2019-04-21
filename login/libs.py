# -*- coding: utf-8 -*-
# 旧的微信包
import StringIO
import hashlib
import io
import os
import random
import string
import sys
import time

import qiniu
import requests
import xlwt
from PIL import Image
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlquote
from django_redis import get_redis_connection
from requests.exceptions import RequestException

from sh_psi.settings import WORK_WEIXIN_CONFIG
from sh_psi.settings import qiniu_config, IMAGES_DIR, BASE_URL


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders

    return style


def upload(img, refund_id):
    q = qiniu.Auth(qiniu_config['AK'], qiniu_config['SK'])
    _img = img.read()
    size = len(_img) / (1024 * 1024)  # 上传图片的大小 M单位
    hmd5 = hashlib.md5()
    hmd5.update(_img)
    file_md5 = hmd5.hexdigest()

    image = Image.open(io.BytesIO(_img))
    qiniu_filename = '%s-%s-%s' % (refund_id, file_md5, str(int(time.time())))
    local_filename = 'upfile-{1}.{0}'.format(image.format, refund_id)  # 获取图片后缀（图片格式）
    if size > 1:  # 压缩
        x, y = image.size
        im = image.resize((int(x / 1.73), int(y / 1.73)), Image.ANTIALIAS)  # 等比例压缩 1.73 倍
    else:  # 不压缩
        im = image
    im.save(IMAGES_DIR + local_filename)  # 在根目录有个media文件
    path = IMAGES_DIR + local_filename
    token = q.upload_token(qiniu_config['BUCKET_NAME'], qiniu_filename, 3600, )
    qiniu.put_file(token, qiniu_filename, path)
    return qiniu_filename


def get_qiniu_img_url(key):
    q = qiniu.Auth(qiniu_config['AK'], qiniu_config['SK'])
    #  输入url的方式下载
    base_url = qiniu_config['DOMAIN'] + key
    # 可以设置token过期时间
    return q.private_download_url(base_url, expires=3600)


class WorkWeixin():
    def __init__(self):
        self.corpid = WORK_WEIXIN_CONFIG['corpid']
        self.corpsecret = WORK_WEIXIN_CONFIG['corpsecret']
        self.agentid = WORK_WEIXIN_CONFIG['agentid']
        self.access_token_url = WORK_WEIXIN_CONFIG['access_token_url']
        self.get_userid_url = WORK_WEIXIN_CONFIG['get_userid_url']
        self.corpsecret = WORK_WEIXIN_CONFIG['corpsecret']
        self.get_user_info_url = WORK_WEIXIN_CONFIG['get_user_info_url']
        self.jsapi_ticket_url = WORK_WEIXIN_CONFIG['jsapi_ticket_url']
        self.app_jsapi_ticket_url = WORK_WEIXIN_CONFIG['jsapi_ticket_url']

    def get_access_tocken(self):  # redis操作，从redis快速刷新获取token
        redis_conn = get_redis_connection()
        ww_access_token = redis_conn.get('work_weixin_at')
        if ww_access_token:
            return True, ww_access_token
        else:
            try:
                url = self.access_token_url  # 用企业id和密码去微信的token url获取token到reids
                r = requests.get(url, params={'corpid': self.corpid, 'corpsecret': self.corpsecret})
                ret = r.json()
                if int(ret['errcode']) == 0:
                    redis_conn.set('work_weixin_at', ret['access_token'], 7100)
                    return True, ret['access_token']
                else:
                    print ret['errmsg']
                    return False, ret['errmsg']
            except  RequestException as e:
                msg = '无法连接微信服务器:错误是:', e.message
                return False, msg

    def get_user_id(self, code):  # 消费code
        status, msg = self.get_access_tocken()
        if status:
            try:
                r = requests.get(self.get_userid_url, params={'access_token': msg, 'code': code})
                ret = r.json()  # 用token和消费code去get_userid_url get到了一些东西
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
                ret = r.json()  # 用token和用户id去GET得user_info详细信息
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


def write_excel(sheet_name, header_set, data_list):
    try:
        response = HttpResponse(content_type='application/octet-stream')
        f = xlwt.Workbook(encoding='utf-8')  # 创建工作簿
        sheet1 = f.add_sheet(sheet_name, cell_overwrite_ok=True)  # 创建sheet
        header_dict = {}
        for i in range(0, len(header_set)):
            d = header_set[i]
            header_dict[d] = i
            sheet1.write(0, i, header_set[i], set_style('Times New Roman', 220, True))
        row = 1
        for i in data_list:
            leni = len(i)
            if leni > 0:
                for j in i:
                    if header_dict.has_key(j):
                        sheet1.write(row, header_dict.get(j), i[j])

            else:
                sheet1.write(row, 0, '数据错误2')
            row += 1
        output = StringIO.StringIO()
        f.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        response = HttpResponse(content_type='application/octet-stream')
        f = xlwt.Workbook(encoding='utf-8')  # 创建工作簿
        sheet1 = f.add_sheet(sheet_name, cell_overwrite_ok=True)  # 创建sheet
        sheet1.write(0, 0, '数据异常' + e.message)
        output = StringIO.StringIO()
        f.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response


def sort_refund_list(x, y):
    if x['status'] in [3, 4, 5]:
        return False
    elif x['status'] == 2:
        return True
    else:
        return False


def bank_card_number_formater(s):
    s1 = s[:4] + ' '
    s2 = s[4:]
    # 加空格
    a = len(s2)
    n = 1
    while 4 * n <= a:
        s2 = s2[:5 * n - 1] + ' ' + s2[5 * n - 1:]
        n += 1
    return (s1 + s2)


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
                return redirect(url)
            else:
                # 返回 code页面

                code = request.GET.get('code')
                print 'get CODE'
                # 获取openid
                ww = WorkWeixin()
                status, user_id = ww.get_user_id(code)
                if not status:
                    print 'cannot get user id %s' % user_id
                    return HttpResponse(user_id)
        else:
            print 'openid in browser!'
            user_id = request.COOKIES.get('userid')

        resp = func(request, userid=user_id)
        chinese_name = User.objects.get(username=user_id).first_name
        resp.set_cookie('userid', user_id)
        resp.set_cookie('chinese_name', urlquote(chinese_name))
        return resp

    return function
