# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import time

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest

from base import models as base_models
from stock import models, forms


# Create your views here.
# 查询所有有进出库记录且存量大于0的物品(商品条目可能无效)
def goods_kucun(request):
    kucun_dict = models.KucunOrderDetail.objects.values('goods', 'goods__name', 'goods__spec__name', 'goods__spec__id',
                                                        'goods__purchase_price', 'goods__sale_price',
                                                        'order__warehouse__name', 'order__warehouse__id',
                                                        'batch').distinct().order_by('goods', 'batch')
    kucungt_list = list()  # 用来存库存大于0的物品
    for i in kucun_dict:
        now_num_dict = models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch']).aggregate(
            now_num=Sum('num'))
        if now_num_dict['now_num'] > 0:
            i['now_num'] = now_num_dict['now_num']
            kucungt_list.append(i)
        else:
            continue
    return HttpResponse(json.dumps({'code': 'ok', 'msg': '仓库商品查询成功', 'data': kucungt_list}),
                        content_type='application/json')


# 盘点时根据库，查询有进出库记录的物品
def check_goods(request):
    form = forms.FormGoods(request.POST)
    if form.is_valid():
        warehouse = form.cleaned_data['warehouse']
        kucun_dict = models.KucunOrderDetail.objects.filter(order__warehouse=warehouse) \
            .values('goods', 'goods__sale_price', 'goods__purchase_price', 'goods__name', 'batch').distinct().order_by(
            'goods', 'batch')
        kucun_list = list()  # 用来存有库存记录的物品
        for i in kucun_dict:
            now_num_dict = models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch']).aggregate(
                now_num=Sum('num'))
            i['now_num'] = now_num_dict['now_num']
            kucun_list.append(i)
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '查询库物品成功', 'data': kucun_list}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 盘点商品单，一旦生成即改变库存,若需要临时保存功能另外补充接口
# 盘点，1创建库存记录总单，2创建库存记录详细单（外键总单），3创建盘点单（外键库存记录总单）
def check_kucun(request):
    form = forms.FormCheck(request.POST)
    if form.is_valid():
        json_goods_dic = json.loads(form.cleaned_data['json_goods_str'])  # 从form获取json
        kucunorder_obj = models.KucunOrder()  # 创建库存记录总单
        kucunorder_obj.identifier = 'ku' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        kucunorder_obj.how = 3  # 库存改变方式，3代表盘点
        if not base_models.Warehouse.objects.filter(id=json_goods_dic["warehouse"], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '盘点的仓库不存在', 'data': []}),
                                          content_type='application/json')
        kucunorder_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic["warehouse"])
        kucunorder_obj.save()
        for i in json_goods_dic['goods']:  # 创建库存详细单
            if i['num'] < 0:
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '各种物品数值设置不可以小于0', 'data': []}),
                                              content_type='application/json')
            else:
                kucunorderdetail_obj = models.KucunOrderDetail()
                if not base_models.Goods.objects.filter(id=i['goods'], status=1).exists():
                    return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '有商品无效', 'data': []}),
                                                  content_type='application/json')
                kucunorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
                kucunorderdetail_obj.batch = i['batch']
                kucunorderdetail_obj.order = kucunorder_obj
                # kucunorderdetail_obj.num = i['num'] - models.KucunOrderDetail.objects.select_related('order').filter(
                #     goods=i['good'], batch=i['batch'], order__warehouse=i['warehouse']).aggregate(
                #     good_sum=Sum('num'))['good_sum']
                before_sum = models.KucunOrderDetail.objects.filter(
                    goods=i['goods'], batch=i['batch'], order__warehouse=json_goods_dic['warehouse']).aggregate(
                    goods_sum=Sum('num'))['goods_sum']
                if not before_sum and before_sum != 0:  # 排除该商品在历史库存记录不存在情况
                    return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '有商品在进出库记录不存在', 'data': []}),
                                                  content_type='application/json')
                kucunorderdetail_obj.num = i['num'] - before_sum
                kucunorderdetail_obj.save()
        checkorder_obj = models.CheckOrder()  # 创建盘点单
        checkorder_obj.identifier = 'check' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        checkorder_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse'])
        checkorder_obj.check_time = json_goods_dic['check_time']
        checkorder_obj.kucun_order = kucunorder_obj
        checkorder_obj.save()
        for i in json_goods_dic['goods']:  # 创建盘点详细单
            checkorderdetail_obj = models.CheckOrderDetail()
            checkorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
            checkorderdetail_obj.num = i['num']
            checkorderdetail_obj.batch = i['batch']
            checkorderdetail_obj.order = checkorder_obj
            checkorderdetail_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '创建库存记录单和盘点单成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 调拨商品（考虑批次）,一旦生成即改变库存
# 1创两个库存记录总单，2创两个库存记录总单各自详细单，3创一个调拨商品单
def change_kucun(request):
    form = forms.FormChange(request.POST)
    if form.is_valid():
        json_goods_dic = json.loads(form.cleaned_data['json_goods_str'])
        kucunorder_out_obj = models.KucunOrder()  # 创建out库存记录总单
        kucunorder_out_obj.identifier = 'changeout' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        kucunorder_out_obj.how = 4  # 库存改变方式，4代表调拨
        if not base_models.Warehouse.objects.filter(id=json_goods_dic['warehouse_out'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '调拨出库的仓库无效', 'data': []}),
                                          content_type='application/json')
        kucunorder_out_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_out'])
        kucunorder_out_obj.save()

        kucunorder_in_obj = models.KucunOrder()  # 创建in库存记录总单
        kucunorder_in_obj.identifier = 'changein' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        kucunorder_in_obj.how = 4  # 库存改变方式，4代表调拨
        if not base_models.Warehouse.objects.filter(id=json_goods_dic['warehouse_in'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '调拨入库的仓库无效', 'data': []}),
                                          content_type='application/json')
        kucunorder_in_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_in'])
        kucunorder_in_obj.save()
        # 创建调拨的库存详细单
        for i in json_goods_dic['goods']:
            if i['num'] < 0:
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '各种物品数值设置不可以小于0', 'data': []}),
                                              content_type='application/json')
            else:
                # goods_kuncun = models.KucunOrderDetail.objects.select_related('order').filter(
                #     goods=i['good'], batch=i['batch'], order__warehouse=i['warehouse']).aggregate(
                #     good_sum=Sum('num'))['good_sum']
                goods_kuncun = models.KucunOrderDetail.objects.filter(
                    goods=i['goods'], batch=i['batch'], order__warehouse=json_goods_dic['warehouse_out']).aggregate(
                    goods_sum=Sum('num'))['goods_sum']
                if i['num'] > goods_kuncun:
                    return HttpResponseBadRequest(
                        json.dumps({'code': 'false', 'msg': '调出数量{}大于出货仓库剩余库存'.format(i['num']), 'data': []}),
                        content_type='application/json')
                else:
                    kucunorderdetail_obj = models.KucunOrderDetail()  # 库存out详细记录单
                    if not base_models.Goods.objects.filter(id=i['goods'], status=1).exists():
                        return HttpResponseBadRequest(
                            json.dumps({'code': 'false', 'msg': '出库商品存在无效', 'data': []}),
                            content_type='application/json')
                    kucunorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
                    kucunorderdetail_obj.batch = i['batch']
                    kucunorderdetail_obj.order = kucunorder_out_obj
                    kucunorderdetail_obj.num = -i['num']  # 出库为负数
                    kucunorderdetail_obj.save()

                    kucunorderdetail_obj = models.KucunOrderDetail()  # 库存in详细记录单
                    kucunorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
                    kucunorderdetail_obj.batch = i['batch']
                    kucunorderdetail_obj.order = kucunorder_in_obj
                    kucunorderdetail_obj.num = i['num']
                    kucunorderdetail_obj.save()

        changeorder_obj = models.ChangeOrder()  # 创建调拨总单
        changeorder_obj.identifier = 'change' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        changeorder_obj.warehouse_out = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_out'])
        changeorder_obj.warehouse_in = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_in'])
        changeorder_obj.change_time = json_goods_dic['change_time']
        changeorder_obj.kucun_out_order = kucunorder_out_obj
        changeorder_obj.kucun_in_order = kucunorder_in_obj
        changeorder_obj.save()
        for i in json_goods_dic['goods']:  # 创建调拨详细单
            changeorderdetail_obj = models.ChangeOrderDetail()
            changeorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
            changeorderdetail_obj.num = i['num']
            changeorderdetail_obj.batch = i['batch']
            changeorderdetail_obj.order = changeorder_obj
            changeorderdetail_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '创建库存记录单和调拨单成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 加工商品,一旦生成即改变库存，多种(A仓库）变多种（B仓库),如果出现原料不都在一个仓库，需要先调拨，产物也是，只能产到一个仓库
# 创建两张库存记录总单（两个库），创建总单的详细单（外键总单)，创建加工总单（外键库存总单），创建加工详细单（外键加工总单）
def work_goods(request):
    form = forms.FormWork(request.POST)
    if form.is_valid():
        json_goods_dic = json.loads(form.cleaned_data['json_goods_str'])
        kucunorder_out_obj = models.KucunOrder()  # 创建out库存记录总单
        kucunorder_out_obj.identifier = 'workout' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        kucunorder_out_obj.how = 2  # 库存改变方式，2代表加工
        # if not base_models.Warehouse.objects.filter(id=json_goods_dic['warehouse_out'], status=1).exists():
        if not base_models.Warehouse.objects.filter(name=json_goods_dic['warehouse_out'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '加工出货仓库无效', 'data': []}),
                                          content_type='application/json')
        # kucunorder_out_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_out'])
        kucunorder_out_obj.warehouse = base_models.Warehouse.objects.get(name=json_goods_dic['warehouse_out'])
        kucunorder_out_obj.save()

        kucunorder_in_obj = models.KucunOrder()  # 创建in库存记录总单
        kucunorder_in_obj.identifier = 'workin' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        kucunorder_in_obj.how = 2  # 库存改变方式，2代表加工
        if not base_models.Warehouse.objects.filter(id=json_goods_dic['warehouse_in'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '加工入货仓库无效', 'data': []}),
                                          content_type='application/json')
        kucunorder_in_obj.warehouse = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_in'])
        kucunorder_in_obj.save()

        for i in json_goods_dic['goods_out']:  # out记录详细单
            i['num'] = float(i['num'])
            if i['num'] < 0:
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '物品数值设置不可以小于0', 'data': []}),
                                              content_type='application/json')
            else:
                goods_kuncun = models.KucunOrderDetail.objects.filter(
                    # goods=i['goods'], batch=i['batch'], order__warehouse=json_goods_dic['warehouse_out']).aggregate(
                    goods=i['goods'], batch=i['batch'],
                    order__warehouse__name=json_goods_dic['warehouse_out']).aggregate(
                    goods_sum=Sum('num'))['goods_sum']
                if i['num'] > goods_kuncun:
                    return HttpResponseBadRequest(
                        json.dumps({'code': 'false', 'msg': '加工消耗数量{}大于当前库存'.format(i['num']), 'data': []}),
                        content_type='application/json')
                else:
                    kucunorderdetail_obj = models.KucunOrderDetail()  # 库存out详细记录单
                    if not base_models.Goods.objects.filter(id=i['goods'], status=1).exists():
                        return HttpResponseBadRequest(
                            json.dumps({'code': 'false', 'msg': '加工消耗物品无效', 'data': []}),
                            content_type='application/json')
                    kucunorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])  # 这里货物只要存在过就行
                    kucunorderdetail_obj.batch = i['batch']
                    kucunorderdetail_obj.order = kucunorder_out_obj
                    kucunorderdetail_obj.num = -i['num']  # 加工出库，负数
                    kucunorderdetail_obj.save()

        for i in json_goods_dic['goods_in']:  # in记录详细单
            i['num'] = float(i['num'])
            if i['num'] < 0:
                return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '各种物品数值设置不可以小于0', 'data': []}),
                                              content_type='application/json')
            else:
                kucunorderdetail_obj = models.KucunOrderDetail()  # 库存in详细记录单
                if not base_models.Goods.objects.filter(id=i['goods'], status=1).exists():
                    return HttpResponseBadRequest(
                        json.dumps({'code': 'false', 'msg': '加工生成物品无效', 'data': []}),
                        content_type='application/json')
                kucunorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
                kucunorderdetail_obj.batch = i['batch']
                kucunorderdetail_obj.order = kucunorder_in_obj
                kucunorderdetail_obj.num = i['num']
                kucunorderdetail_obj.save()

        workgoodsorder_obj = models.WorkGoodsOrder()  # 创建加工总单
        workgoodsorder_obj.identifier = 'work' + time.strftime(str("%Y-%m-%d-%H-%M-%S"), time.localtime())
        # workgoodsorder_obj.batch = json_goods['batch']    # 批次写在详细单
        # workgoodsorder_obj.warehouse_out = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_out'])
        workgoodsorder_obj.warehouse_out = base_models.Warehouse.objects.get(name=json_goods_dic['warehouse_out'])
        workgoodsorder_obj.warehouse_in = base_models.Warehouse.objects.get(id=json_goods_dic['warehouse_in'])
        workgoodsorder_obj.change_time = json_goods_dic['work_time']
        workgoodsorder_obj.kucun_out_order = kucunorder_out_obj
        workgoodsorder_obj.kucun_in_order = kucunorder_in_obj
        workgoodsorder_obj.save()
        for i in json_goods_dic['goods_out']:  # 创建加工消耗详细单
            workgoodorderdetail_obj = models.WorkGoodsOrderDetail()
            workgoodorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
            workgoodorderdetail_obj.num = -i['num']  # 负数
            workgoodorderdetail_obj.batch = i['batch']
            workgoodorderdetail_obj.order = workgoodsorder_obj
            workgoodorderdetail_obj.save()
        for i in json_goods_dic['goods_in']:  # 创建加工生成详细单
            workgoodorderdetail_obj = models.WorkGoodsOrderDetail()
            workgoodorderdetail_obj.goods = base_models.Goods.objects.get(id=i['goods'])
            workgoodorderdetail_obj.num = i['num']
            workgoodorderdetail_obj.batch = i['batch']
            workgoodorderdetail_obj.order = workgoodsorder_obj
            workgoodorderdetail_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '创建库存记录单和加工单成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 粗略查询盘点单
def check_kucun_simple(request):
    query_set = models.CheckOrder.objects.select_related('warehouse').all()
    json_dic = dict()
    data_list = list()
    for i in query_set:
        data_dic = dict()
        data_dic['id'] = i.id
        data_dic['identifier'] = i.identifier
        data_dic['warehouse'] = i.warehouse.name
        data_dic['check_time'] = i.check_time
        data_list.append(data_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '粗略查询盘点单成功'
    json_dic['data'] = data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询盘点单
def check_kucun_detail(request):
    form = forms.OrderDetail(request.POST)
    if not form.is_valid():
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
    else:
        check_order_id = form.cleaned_data['id']
        if not models.CheckOrder.objects.filter(id=check_order_id):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '查询的盘点单不存在', 'data': []}),
                                          content_type='application/json')
        check_order_obj = models.CheckOrder.objects.select_related('warehouse').get(id=check_order_id)
        detail_list = list()
        for i in check_order_obj.checkorderdetail_set.all().select_related('goods'):
            detail_dic = dict()
            detail_dic['goods'] = i.goods.name
            detail_dic['goods_id'] = i.goods.id
            detail_dic['num'] = i.num
            detail_dic['batch'] = i.batch
            detail_list.append(detail_dic)
        data_dic = dict()
        data_dic['identifier'] = check_order_obj.identifier
        data_dic['warehouse'] = check_order_obj.warehouse.name
        data_dic['check_time'] = check_order_obj.check_time
        data_dic['detail_list'] = detail_list
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '详细查询盘点单成功', 'data': data_dic}),
                            content_type='application/json')


# 粗略查询调拨单
def change_kucun_simple(request):
    query_set = models.ChangeOrder.objects.select_related('warehouse_out', 'warehouse_in').all()
    json_dic = dict()
    data_list = list()
    for i in query_set:
        data_dic = dict()
        data_dic['id'] = i.id
        data_dic['identifier'] = i.identifier
        data_dic['warehouse_out'] = i.warehouse_out.name
        data_dic['warehouse_in'] = i.warehouse_in.name
        data_dic['change_time'] = i.change_time
        data_list.append(data_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '粗略查询调拨单成功'
    json_dic['data'] = data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询调拨单
def change_kucun_detail(request):
    form = forms.OrderDetail(request.POST)
    if not form.is_valid():
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
    else:
        change_order_id = form.cleaned_data['id']
        if not models.ChangeOrder.objects.filter(id=change_order_id):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '查询的调拨单不存在', 'data': []}),
                                          content_type='application/json')
        change_order_obj = models.ChangeOrder.objects.select_related('warehouse_out', 'warehouse_in').get(
            id=change_order_id)
        detail_list = list()
        for i in change_order_obj.changeorderdetail_set.all().select_related('goods'):
            detail_dic = dict()
            detail_dic['goods'] = i.goods.name
            detail_dic['goods_id'] = i.goods.id
            detail_dic['num'] = i.num
            detail_dic['batch'] = i.batch
            detail_list.append(detail_dic)
        data_dic = dict()
        data_dic['identifier'] = change_order_obj.identifier
        data_dic['warehouse_out'] = change_order_obj.warehouse_out.name
        data_dic['warehouse_in'] = change_order_obj.warehouse_in.name
        data_dic['change_time'] = change_order_obj.change_time
        data_dic['detail_list'] = detail_list
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '详细查询调拨单成功', 'data': data_dic}),
                            content_type='application/json')


# 粗略查询加工单
def change_work_goods_simple(request):
    query_set = models.WorkGoodsOrder.objects.select_related('warehouse_out', 'warehouse_in').all()
    json_dic = dict()
    data_list = list()
    for i in query_set:
        data_dic = dict()
        data_dic['id'] = i.id
        data_dic['identifier'] = i.identifier
        data_dic['warehouse_out'] = i.warehouse_out.name
        data_dic['warehouse_in'] = i.warehouse_in.name
        data_dic['work_time'] = i.work_time
        data_list.append(data_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '粗略查询加工单成功'
    json_dic['data'] = data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询加工单
def change_work_goods_detail(request):
    form = forms.OrderDetail(request.POST)
    if not form.is_valid():
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
    else:
        work_order_id = form.cleaned_data['id']
        if not models.WorkGoodsOrder.objects.filter(id=work_order_id):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '查询的调拨单不存在', 'data': []}),
                                          content_type='application/json')
        work_order_obj = models.WorkGoodsOrder.objects.select_related('warehouse_out', 'warehouse_in').get(
            id=work_order_id)
        goods_out = list()
        goods_in = list()
        for i in work_order_obj.workgoodsorderdetail_set.all().select_related('goods'):
            detail_dic = dict()
            detail_dic['goods'] = i.goods.name
            detail_dic['goods_id'] = i.goods.id
            detail_dic['num'] = i.num
            detail_dic['batch'] = i.batch
            if i.num > 0:
                goods_in.append(detail_dic)
            else:
                goods_out.append(detail_dic)
        data_dic = dict()
        data_dic['identifier'] = work_order_obj.identifier
        data_dic['warehouse_out'] = work_order_obj.warehouse_out.name
        data_dic['warehouse_in'] = work_order_obj.warehouse_in.name
        data_dic['work_time'] = work_order_obj.work_time
        data_dic['goods_out'] = goods_out
        data_dic['goods_in'] = goods_in
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '详细查询加工单成功', 'data': data_dic}),
                            content_type='application/json')


# 粗略查询库存记录单
def kucun_order_simple(request):
    query_set = models.KucunOrder.objects.select_related('warehouse').all()
    json_dic = dict()
    data_list = list()
    for i in query_set:
        data_dic = dict()
        data_dic['id'] = i.id
        data_dic['identifier'] = i.identifier
        data_dic['how'] = i.get_how_display()
        data_dic['warehouse'] = i.warehouse.name
        data_dic['create_time'] = i.create_time.strftime('%Y-%m-%d')
        data_list.append(data_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '粗略查询库存记录单成功'
    json_dic['data'] = data_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 详细查询库存记录单
def kucun_order_detail(request):
    form = forms.OrderDetail(request.POST)
    if not form.is_valid():
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
    else:
        kucun_order_id = form.cleaned_data['id']
        if not models.KucunOrder.objects.filter(id=kucun_order_id):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '查询的库存记录单不存在', 'data': []}),
                                          content_type='application/json')
        kucun_order_obj = models.KucunOrder.objects.select_related('warehouse').get(id=kucun_order_id)
        detail_list = list()
        for i in kucun_order_obj.kucunorderdetail_set.all().select_related('goods'):
            detail_dic = dict()
            detail_dic['goods_id'] = i.goods.id
            detail_dic['goods'] = i.goods.name
            detail_dic['num'] = i.num
            detail_dic['batch'] = i.batch
            detail_list.append(detail_dic)
        data_dic = dict()
        data_dic['identifier'] = kucun_order_obj.identifier
        data_dic['how'] = kucun_order_obj.get_how_display()
        data_dic['warehouse'] = kucun_order_obj.warehouse.name
        data_dic['create_time'] = kucun_order_obj.create_time.strftime('%Y-%m-%d')
        data_dic['detail_list'] = detail_list
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '详细查询加工单成功', 'data': data_dic}),
                            content_type='application/json')
