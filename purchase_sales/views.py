# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
import json
import time

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest

from auto_account import models as auto_account_models
from base import models as base_models
from purchase_sales import models, forms
from stock import models as stock_models


# 创建进货/销售订单，直接进入审核状态
# 一个总单的应收/付合计是详细单的实际应收/付的和，总单的实收/付由用户填入，详细单的实际收/付也是由用户填
# 以上数据由前端发到后端
# 新建进货/销售单时提供选择商品查询所有商品条目就好，前端拼接或者后端拼接
def add_order(request):
    form = forms.FormAddOrder(request.POST)
    if form.is_valid():
        json_data = json.loads(form.cleaned_data['json_data_str'])
        order_obj = models.Order()
        if json_data['type'] != u'进货订单' and json_data['type'] != u'销售订单':
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '未指明是进货订单还是销售订单', 'data': []}),
                                          content_type='application/json')
        if json_data['type'] == '进货订单':
            order_obj.identifier = 'jinhuo' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
            order_obj.type = 0
        else:
            order_obj.identifier = 'xiaoshou' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
            order_obj.type = 1
        client_id = json_data['client']
        if not base_models.Client.objects.filter(id=client_id, status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '客户无效', 'data': []}),
                                          content_type='application/json')
        order_obj.client = base_models.Client.objects.get(id=client_id)
        warehouse_id = json_data['warehouse']
        if not base_models.Warehouse.objects.filter(id=warehouse_id, status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '仓库无效', 'data': []}),
                                          content_type='application/json')
        order_obj.warehouse = base_models.Warehouse.objects.get(id=warehouse_id)
        # order_obj.cabinets = json_data['cabinets']
        order_obj.send_way = json_data['send_way']
        count_type_list = ['现结结账', '现结未结账', '月结结账', '月结未结账', '批结结账', '批结未结账']  # 也可以去form校验。
        if not json_data['count_type'] in count_type_list:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '结算方式不规范', 'data': []}),
                                          content_type='application/json')
        count_type_dict = {'现结结账': 0, '现结未结账': 1, '月结结账': 2, '月结未结账': 3, '批结结账': 4,
                           '批结未结账': 5}
        order_obj.count_type = count_type_dict[json_data['count_type']]
        order_obj.real_price = json_data['real_price']  # 已收/付金额
        order_obj.need_price = json_data['need_price']  # 实收/付金额
        # for i in json_data['orders']:
        #     if not base_models.Goods.objects.filter(id=i["goods"]).exists():
        #         return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '详细订单中商品不存在', 'data': []})
        #                                       content_type='application/json')
        #     order_obj.need_price += base_models.Goods.objects.get(id=i["goods"]).sale_price * i["num"]
        # 总订单计算总应收/付金额，改为前端发来实际总应收/付金额
        order_obj.save()
        for i in json_data['orders']:
            detail_order_obj = models.DetailOrder()
            detail_order_obj.num = i["num"]
            if not base_models.Goods.objects.filter(id=i["goods"], status=1).exists():
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '列表中商品无效', 'data': []}),
                                              content_type='application/json')
            detail_order_obj.price = base_models.Goods.objects.get(id=i["goods"]).sale_price
            # detail_order_obj.need_price = base_models.Goods.objects.get(id=i["goods"]).sale_price * i["num"]
            # 批发价*数量，详细单总应收/付由前端算并发送给后端，详细单实际总应收/付也是
            detail_order_obj.need_price = i['need_price']
            detail_order_obj.new_need_price = i['new_need_price']
            detail_order_obj.batch = i["batch"]  # 批次在这里
            detail_order_obj.order = order_obj
            detail_order_obj.goods = base_models.Goods.objects.get(id=i["goods"])
            detail_order_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '创建{}成功'.format(json_data['type']), 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


def search_order(order_type):
    queryset = models.Order.objects.select_related('client', 'warehouse').filter(type=order_type, order_status=1)
    order_list = list()
    json_dic = dict()
    for i in queryset:
        order_dict = dict()
        order_dict['id'] = i.id
        order_dict['identifier'] = i.identifier
        order_dict['client'] = i.client.name
        order_dict['warehouse'] = i.warehouse.name
        order_dict['count_type'] = i.get_count_type_display()
        order_dict['approval_status'] = i.get_approval_status_display()
        order_dict['create_time'] = i.create_time.strftime('%Y-%m-%d')
        if i.kucun_order:
            order_dict['order_kucun'] = '已{}库'.format({0: '进', 1: '出'}[order_type])
        else:
            order_dict['order_kucun'] = '未{}库'.format({0: '进', 1: '出'}[order_type])
        order_list.append(order_dict)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询{}成功'.format({0: '进货', 1: '销售'}[order_type])
    json_dic['data'] = order_list
    return json_dic


# 粗略查询有效进货订单
def all_order_simple(request):
    json_dic = search_order(0)
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 粗略查询有效销售订单
def all_sell_simple(request):
    json_dic = search_order(1)
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询某张订单
def unite_order_detail(request):
    form = forms.FormUniteOrder(request.POST)
    if form.is_valid():
        if not models.Order.objects.filter(id=form.cleaned_data['id'], order_status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '详细查询的订单无效', 'data': []}),
                                          content_type='application/json')
        order_obj = models.Order.objects.select_related("client", "warehouse").get(
            id=form.cleaned_data['id'])
        # order_obj = models.Order.objects.get(id=form.cleaned_data['id'])
        json_dic = dict()
        order_dict = dict()
        info_dict = dict()
        info_dict['id'] = order_obj.id
        info_dict['identifier'] = order_obj.identifier
        info_dict['type'] = order_obj.get_type_display()
        info_dict['client'] = order_obj.client.name
        info_dict['warehouse'] = order_obj.warehouse.name
        # info_dict['cabinets'] = order_obj.cabinets
        # order_dict['batch'] = order_obj.batch
        info_dict['send_way'] = order_obj.send_way
        info_dict['count_type'] = order_obj.get_count_type_display()
        info_dict['real_price'] = order_obj.real_price
        info_dict['need_price'] = order_obj.need_price
        info_dict['approval_status'] = order_obj.get_approval_status_display()
        info_dict['create_time'] = str(order_obj.create_time.strftime('%Y-%m-%d'))  # 注意str
        if order_obj.kucun_order:
            info_dict['order_kucun'] = '已{}库'.format({0: '进', 1: '出'}[order_obj.type])
        else:
            info_dict['order_kucun'] = '未{}库'.format({0: '进', 1: '出'}[order_obj.type])
        detail_list = list()  # 列表存放以字典存储的详细订单
        for i in order_obj.detailorder_set.select_related('goods','goods__spec').all():
            detail_dict = dict()
            detail_dict['num'] = i.num
            detail_dict['price'] = i.price
            detail_dict['need_price'] = i.need_price
            detail_dict['new_need_price'] = i.new_need_price
            detail_dict['batch'] = i.batch
            detail_dict['goods'] = i.goods.name
            # detail_dict['spec'] = i.goods.spec.name
            detail_dict['goods_id'] = i.goods.id
            detail_dict['spec'] = i.goods.spec.name
            detail_list.append(detail_dict)
        order_dict['info'] = info_dict
        order_dict['orders'] = detail_list
        json_dic['code'] = 'ok'
        json_dic['msg'] = '查询成功'
        json_dic['data'] = order_dict
        return HttpResponse(json.dumps(json_dic), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 修改订单，只能修改审核失败订单，且只能修改基本信息
def edit_order(request):
    form = forms.FormEditOrder(request.POST)
    if form.is_valid():
        order_id = int(form.cleaned_data['id'])
        order_obj = models.Order.objects.get(id=order_id)
        if not order_obj.approval_status != 2:  # 只能修改审核失败订单
            # order_obj.identifier = 'sh_psi' + time.strftime(str("-%Y-%m-%d-"), time.localtime()) + str(order_obj.id)
            # order_obj.type = json_data['type']
            client_id = form.cleaned_data['client']
            if not base_models.Client.objects.filter(id=client_id, status=1).exists():
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '客户无效', 'data': []}),
                                              content_type='application/json')
            order_obj.client = base_models.Client.objects.get(id=client_id)
            warehouse_id = form.cleaned_data['warehouse']
            if not base_models.Warehouse.objects.filter(id=warehouse_id, status=1).exists():
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '仓库无效', 'data': []}),
                                              content_type='application/json')
            order_obj.warehouse_id = base_models.Warehouse.objects.get(id=warehouse_id)
            order_obj.cabinets = form.cleaned_data['cabinets']
            order_obj.send_way = form.cleaned_data['send_way']
            count_type_list = ['现结付清', '现结未付清', '月结付清', '月结未付清', '批结付清', '批结未付清']
            if not form.cleaned_data['count_type'] in count_type_list:
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '结算方式不规范', 'data': []}),
                                              content_type='application/json')
            count_type_dict = {'现结付清': 0, '现结未付清': 1, '月结付清': 2, '月结未付清': 3, '批结付清': 4, '批结未付清': 5}
            order_obj.count_type = count_type_dict[form.cleaned_data['count_type']]
            order_obj.real_price = form.cleaned_data['real_price']
            order_obj.need_price = form.cleaned_data['need_price']
            order_obj.save()
            return HttpResponse(json.dumps({'code': 'ok', 'msg': '修改订单成功', 'data': []}),
                                content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'code': 'false', 'msg': '只能修改审核失败的订单',
                            'data': []}), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除订单
def del_order(request):
    form = forms.FormUniteOrder(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data['id']
        order_obj = models.Order.objects.get(id=order_id)
        order_obj.order_status = 0
        order_obj.save()
        return HttpResponse(json.dumps({'code': 'false', 'msg': '删除订单成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 将订单进出库
def kucun_order(request):
    form = forms.FormUniteOrder(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data['id']
        order_obj = models.Order.objects.get(id=order_id)
        if order_obj.order_status == 0:
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '该订单无效', 'data': []}),
                content_type='application/json')
        elif order_obj.approval_status != 1:  # 最高级通过的值
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '订单未通过最高审批', 'data': []}),
                content_type='application/json')
        elif order_obj.kucun_order:
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '订单已{}库'.format({0: '进', 1: '出'}[order_obj.type]), 'data': []}),
                content_type='application/json')
        else:
            kucunorder_obj = stock_models.KucunOrder()
            kucunorder_obj.identifier = 'ku' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
            kucunorder_obj.how = order_obj.type  # 进货单=进货方式
            # goodkucun_obj.batch = order_obj.batch     # 总单去掉了批次，放详细单
            kucunorder_obj.warehouse = order_obj.warehouse  # model的对象
            kucunorder_obj.save()  # 保存库存总单
            for i in order_obj.detailorder_set.all():  # 遍历商品详细表,生成进出库单
                kucunorderdetail_obj = stock_models.KucunOrderDetail()
                if order_obj.type == 0:
                    kucunorderdetail_obj.num = i.num
                else:
                    kucunorderdetail_obj.num = -i.num
                kucunorderdetail_obj.price = i.price
                kucunorderdetail_obj.need_price = i.price * i.num
                kucunorderdetail_obj.batch = i.batch
                kucunorderdetail_obj.order = kucunorder_obj
                kucunorderdetail_obj.goods = i.goods  # 对象赋值到对象
                kucunorderdetail_obj.save()  # 保存库存详细单
            order_obj.kucun_order = kucunorder_obj  # 写入外键库存单保存采购销售订单
            order_obj.save()  # 保存采购销售订单
            return HttpResponse(
                json.dumps({'code': 'ok ', 'msg': '{}库订单成功'.format({0: '进', 1: '出'}[order_obj.type]), 'data': []}),
                content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 自助收款/付款订单，对销售客户和供应商都有对应账单记录，收够钱自动结案
def bill_order(request):
    form = forms.FormBillOrder(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data['id']
        if not models.Order.objects.filter(id=order_id, order_status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '订单无效', 'data': []}),
                                          content_type='application/json')
        order_obj = models.Order.objects.get(id=order_id)  # 订单有效实例化这个订单
        if order_obj.need_price - order_obj.real_price < form.cleaned_data['money']:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '收的钱比未付要多！', 'data': []}),
                                          content_type='application/json')
        if order_obj.count_type in [0, 2, 4]:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '订单已结案', 'data': []}),
                                          content_type='application/json')
        order_type = order_obj.type
        client_obj = order_obj.client
        money = auto_account_models.ClientIncome.objects.filter(client=client_obj).aggregate(a=Sum('money'))['a']
        if not money:
            money = 0
        if money < form.cleaned_data['money']:
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '{}余额不够支付'.format({0: '对供应商', 1: '顾客'}[order_type]), 'data': []}),
                content_type='application/json')
        elif not form.cleaned_data['money']>0:
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '对订单收款金额需要大于0', 'data': []}),
                content_type='application/json')
        else:
            client_income_obj = auto_account_models.ClientIncome()  # 对销售客户/供应商创建一条账单记录
            client_income_obj.client = client_obj
            client_income_obj.money = -forms.FormBillOrder['money']  # 消费了钱所以是负数
            client_income_obj.save()
            order_obj.real_price += forms.FormBillOrder['money']  # 已收/付变动
            # 收够款了自动结案
            if order_obj.need_price == order_obj.real_price and order_obj.count_type == 1:
                order_obj.count_type = 0
                order_obj.save()
            elif order_obj.need_price == order_obj.real_price and order_obj.count_type == 3:
                order_obj.count_type = 2
                order_obj.save()
            elif order_obj.need_price == order_obj.real_price and order_obj.count_type == 5:
                order_obj.count_type = 4
                order_obj.save()
            return HttpResponse(json.dumps({'code': 'ok', 'msg': '订单结案成功', 'data': []}),
                                content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 强行结案订单
def finish_order(request):
    form = forms.FormFinishOrder(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data['id']
        if not models.Order.objects.filter(id=order_id, order_status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '订单无效', 'data': []}),
                                          content_type='application/json')
        order_obj = models.Order.objects.get(id=order_id)
        if order_obj.count_type in [0, 2, 4]:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '订单已结案', 'data': []}),
                                          content_type='application/json')
        # 直接结案订单
        if order_obj.count_type == 1:
            order_obj.count_type = 0
            order_obj.save()
        elif order_obj.count_type == 3:
            order_obj.count_type = 2
            order_obj.save()
        elif order_obj.count_type == 5:
            order_obj.count_type = 4
            order_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '订单结案成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 粗略查询所有审核中订单
def all_reviewing_order(request):
    queryset = models.Order.objects.select_related('client', 'warehouse').filter(order_status=1, approval_status=0)
    order_list = list()
    json_dic = dict()
    for i in queryset:
        order_dict = dict()
        order_dict['id'] = i.id
        order_dict['identifier'] = i.identifier
        order_dict['client'] = i.client.name
        order_dict['warehouse'] = i.warehouse.name
        order_dict['count_type'] = i.get_count_type_display()
        order_list.append(order_dict)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询审核中订单成功'
    json_dic['data'] = order_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询某张审核中订单调用上面详细查询某张订单

# 将订单审核通过，权限控制未知
def reviewed_order(request):
    form = forms.ReviewedOrder(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data['id']
        order_is_pass = form.cleaned_data['is_pass']
        order_obj = models.Order.objects.get(id=order_id)
        if order_obj.approval_status != 0:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '订单早已审批', 'data': []}),
                                          content_type='application/json')
        order_obj.approval_status = {0: 2, 1: 1}[order_is_pass]  # 前端传来is_pass，1为审核通过，0为审核失败
        order_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '订单审核成功', 'data': []}), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查询所有已删除/失效订单
def all_del_order(request):
    query_set = models.Order.objects.filter(order_status=0).select_related('client', 'warehouse')
    json_dic = dict()
    data_list = list()
    for i in query_set:
        order_dict = dict()
        order_dict['identifier'] = i.identifier
        order_dict['type'] = i.get_type_display()
        order_dict['client'] = i.get_type_display()
        order_dict['warehouse'] = i.warehouse.name
        order_dict['cabinets'] = i.cabinets
        order_dict['send_way'] = i.send_way
        order_dict['count_type'] = i.get_count_type_display()
        order_dict['real_price'] = i.real_price
        order_dict['need_price'] = i.need_price
        order_dict['approval_status'] = i.get_approval_status_display()
        data_list.append(order_dict)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询所有已删除/失效订单成功'
    json_dic['data'] = data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 查询所有未结案、有效、审核通过的进货或销售订单，被调用
def all_uncount(type):
    query_set = models.Order.objects.select_related('client', 'warehouse').filter(order_status=1,
                                                                                  count_type__in=[1, 3, 5], type=type)
    json_dic = dict()
    json_data = list()
    for i in query_set:
        order_dict = dict()
        order_dict['id'] = i.id
        order_dict['identifier'] = i.identifier
        order_dict['create_time'] = i.create_time.strftime('%Y-%m-%d')
        client_now_money = auto_account_models.ClientIncome.objects.filter(client=i.client).aggregate(a=Sum('money'))[
            'a']
        if not client_now_money:
            client_now_money = 0
        order_dict['client'] = i.client.name
        order_dict['client_now_money'] = client_now_money
        order_dict['warehouse'] = i.warehouse.name
        order_dict['need_price'] = i.need_price
        order_dict['real_price'] = i.real_price
        order_dict['no_price'] = i.need_price - i.real_price
        order_dict['count_type'] = i.get_count_type_display()
        json_data.append(order_dict)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询所有未结案、有效、审核通过的订单成功'
    json_dic['data'] = json_data
    return json_dic


# 查询所有未结案、有效、审核通过的进货订单
def all_uncount_purchase(request):
    ret = all_uncount(0)
    return HttpResponse(json.dumps(ret), content_type='application/json')


# 查询所有未结案、有效、审核通过的销售订单
def all_uncount_sale(request):
    ret = all_uncount(1)
    return HttpResponse(json.dumps(ret), content_type='application/json')
