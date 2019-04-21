# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponse

from auto_account import forms
from auto_account import models
from base import models as base_models


# Create your views here.
# 关于结帐过程，创建了客户/供应商账单模型，每次客户在不是下单时给的钱都会创建客户的入账记录，对应有入账总额，
# 对有效订单，点一次结账，产生该客户的入账记录，金额为负，如果金额不足以结账，就提示余额不足。
# 对销售客户入账功能，另外对客户每次自助结账一张销售总单时，产生一个负的入账，直到余额不足
# 如果对供应商的订单结账，应该多一个对供应商的账单记录
def client_income(request):
    form = forms.FormClientIncome(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['client']
        money = form.cleaned_data['money']
        client_obj = base_models.Client.objects.filter(id=client_id, status=1).first()
        if not client_obj:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '该客户不存在', 'data': []}),
                                          content_type='application/json')
        client_income_obj = models.ClientIncome()
        client_income_obj.client = client_obj
        client_income_obj.money = money
        client_income_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'mag': '入账成功', 'data': []}), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查询某个客户目前入账余额,正数加负数，余额不足不可结账
def client_income_total(request):
    form = forms.FromClientIncomeTotal(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['client']
        client_obj = base_models.Client.objects.filter(id=client_id, status=1).first()
        if not client_obj:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '该客户不存在', 'data': []}),
                                          content_type='application/json')
        money = models.ClientIncome.objects.filter(client=client_obj, status=1).aggregate(a=Sum('money'))['a']
        if not money:
            money = 0
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '查询客户余额成功', 'data': money}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查询所有客户目前余额
def client_income_now(request):
    query_set = base_models.Client.objects.filter(status=1)
    # query_set = models.ClientIncome.objects.select_related('client').values('client', 'client__name').annotate(
    #     now_money=Sum('money'))  # 分组查询
    json_dic = dict()
    json_data_list = list()
    for i in query_set:
        client_dic = dict()
        client_dic['client'] = i.id
        client_dic['client__name'] = i.name
        client_dic['now_money'] = models.ClientIncome.objects.filter(client=i).aggregate(now_money=Sum('money'))[
            'now_money']
        if not client_dic['now_money']:
            client_dic['now_money'] = 0
        json_data_list.append(client_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询所有客户目前余额成功'
    json_dic['data'] = json_data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 查询某个客户历史记账记录
def client_income_history(request):
    form = forms.FormClientIncomeHistory(request.POST)
    if form.is_valid():
        if not base_models.Client.objects.filter(id=form.cleaned_data['client']):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '客户无效', 'data': []}),
                                          content_type='application/json')
        query_set = models.ClientIncome.objects.select_related('client').filter(client_id=form.cleaned_data['client'])
        json_dic = dict()
        json_data_list = list()
        for i in query_set:
            one_client_income_dic = dict()
            one_client_income_dic['client'] = i.client.name
            one_client_income_dic['money'] = i.money
            one_client_income_dic['crater_time'] = i.create_time.strftime('%Y-%m-%d')
            json_data_list.append(one_client_income_dic)
        json_dic['code'] = 'ok'
        json_dic['msg'] = '查询客户的历史记账记录成功'
        json_dic['data'] = json_data_list
        return HttpResponse(json.dumps(json_dic), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
