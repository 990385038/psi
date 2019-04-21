# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse, HttpResponseBadRequest

from base import models, forms


# Create your views here.


# 查询所有商品条目列表
def all_goods(request):
    queryset = models.Goods.objects.filter(status__in=[0, 1]).select_related('spec', 'goods_class').all()
    goods_list = list()
    json_dic = dict()
    for i in queryset:
        goods_dic = dict()
        goods_dic['id'] = i.id
        goods_dic['name'] = i.name
        goods_dic['spec'] = i.spec.name + '-' + i.spec.sub_spec
        goods_dic['goods_class'] = i.goods_class.name
        # goods_dic['supplier'] = i.goods_class
        goods_dic['rec_price'] = i.rec_price
        goods_dic['purchase_price'] = i.purchase_price
        goods_dic['sale_price'] = i.sale_price
        goods_dic['status'] = i.get_status_display()
        goods_list.append(goods_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询成功'
    json_dic['data'] = goods_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 查询所有商品条目列表
def all_goods_valid(request):
    queryset = models.Goods.objects.filter(status=1).select_related('spec', 'goods_class').all()
    goods_list = list()
    json_dic = dict()
    for i in queryset:
        goods_dic = dict()
        goods_dic['id'] = i.id
        goods_dic['name'] = i.name
        goods_dic['spec'] = i.spec.name + '-' + i.spec.sub_spec
        goods_dic['goods_class'] = i.goods_class.name
        # goods_dic['supplier'] = i.goods_class
        goods_dic['rec_price'] = i.rec_price
        goods_dic['purchase_price'] = i.purchase_price
        goods_dic['sale_price'] = i.sale_price
        goods_dic['status'] = i.get_status_display()
        goods_list.append(goods_dic)
    json_dic['code'] = 'ok'
    json_dic['msg'] = '查询成功'
    json_dic['data'] = goods_list
    return HttpResponse(json.dumps(json_dic), content_type='application/json')


# 增加商品
def add_goods(request):
    form = forms.FormGoods(request.POST)
    if form.is_valid():
        goods_obj = models.Goods()
        goods_obj.name = form.cleaned_data['name']

        if not models.Spec.objects.filter(id=form.cleaned_data['spec'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '规格无效', 'data': []}),
                                          content_type='application/json')
        goods_obj.spec = models.Spec.objects.get(id=form.cleaned_data['spec'])

        if not models.Goods_Class.objects.filter(id=form.cleaned_data['goods_class'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '分类无效', 'data': []}),
                                          content_type='application/json')
        goods_obj.goods_class = models.Goods_Class.objects.get(id=form.cleaned_data['goods_class'])

        goods_obj.rec_price = form.cleaned_data['rec_price']
        goods_obj.purchase_price = form.cleaned_data['purchase_price']
        goods_obj.sale_price = form.cleaned_data['sale_price']
        goods_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        goods_obj.save()
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '添加商品成功', 'data': []}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑前根据id先返回该条商品具体信息
def edit_goods_before(request):
    form = forms.FormEditGoodsBefore(request.POST)
    if form.is_valid():
        query_obj = models.Goods.objects.filter(id=form.cleaned_data['id'],
                                                status__in=[0, 1], ).select_related('spec', 'goods_class').first()
        if not query_obj:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '编辑的商品无效', 'data': []}),
                                          content_type='application/json')
        goods_list = list()
        json_dic = dict()
        goods_dic = dict()
        goods_dic['name'] = query_obj.name
        goods_dic['spec'] = query_obj.spec.id  # 规格的id
        goods_dic['spec_ch'] = query_obj.spec.name  # 规格的中文名
        goods_dic['spec_status'] = query_obj.spec.get_status_display()  # 规格的状态
        goods_dic['goods_class'] = query_obj.goods_class.id  # 类别的id
        goods_dic['goods_class_ch'] = query_obj.goods_class.name  # 类别的中文名
        goods_dic['goods_class_status'] = query_obj.goods_class.get_status_display()  # 类别的状态
        goods_dic['rec_price'] = query_obj.rec_price
        goods_dic['purchase_price'] = query_obj.purchase_price
        goods_dic['sale_price'] = query_obj.sale_price
        goods_dic['status'] = query_obj.get_status_display()
        goods_list.append(goods_dic)
        json_dic['code'] = 'ok'
        json_dic['msg'] = '进入{}成功'.format(query_obj.name)
        json_dic['data'] = goods_list
        return HttpResponse(json.dumps(json_dic), content_type='application/json')

    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑商品
def edit_goods(request):
    form = forms.FormEditGoods(request.POST)
    if form.is_valid():
        if not models.Goods.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要编辑的商品无效', 'data': []}),
                                          content_type='application/json')
        goods_obj = models.Goods.objects.get(id=form.cleaned_data['id'])
        if not models.Spec.objects.filter(id=form.cleaned_data['spec'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '规格无效', 'data': []}),
                                          content_type='application/json')
        edit_spec_obj = models.Spec.objects.get(id=form.cleaned_data['spec'])
        if not models.Goods_Class.objects.filter(id=form.cleaned_data['goods_class'], status=1).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '分类无效', 'data': []}),
                                          content_type='application/json')
        edit_goods_class_obj = models.Goods_Class.objects.get(id=form.cleaned_data['goods_class'])
        if edit_spec_obj.status == 2 and edit_spec_obj != goods_obj.spec:
            return HttpResponse(
                json.dumps({'code': 'false', 'msg': '选中的规格必须是原来的或者有效的', 'data': []}),
                content_type='application/json')
        elif edit_goods_class_obj.status == 2 and edit_goods_class_obj != goods_obj.goods_class:
            return HttpResponse(
                json.dumps({'code': 'false', 'msg': '选中的分类必须是原来的或者有效的', 'data': []}),
                content_type='application/json')
        else:
            goods_obj.name = form.cleaned_data['name']
            goods_obj.spec = edit_spec_obj
            goods_obj.goods_class = edit_goods_class_obj
            goods_obj.rec_price = form.cleaned_data['rec_price']
            goods_obj.purchase_price = form.cleaned_data['purchase_price']
            goods_obj.sale_price = form.cleaned_data['sale_price']
            goods_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
            goods_obj.save()
            return HttpResponse(
                json.dumps({'code': 'ok', 'msg': '编辑商品成功', 'data': []}),
                content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除商品
def del_goods(request):
    form = forms.FormDelGoods(request.POST)
    if form.is_valid():
        goods_id = form.cleaned_data['id']
        if not models.Goods.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要删除的商品不存在', 'data': []}),
                                          content_type='application/json')
        goods_obj = models.Goods.objects.get(id=goods_id)
        goods_obj.status = 2
        goods_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '删除商品成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查商品分类
def all_class(request):
    class_queryset = models.Goods_Class.objects.filter(status__in=[0, 1])
    json_data = list()
    for i in class_queryset:
        dic_data = dict()
        dic_data['id'] = i.id
        dic_data['status'] = i.get_status_display()
        dic_data['name'] = i.name
        json_data.append(dic_data)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询分类成功', 'data': json_data}),
        content_type='application/json')


# 查商品分类（有效）
def all_class_valid(request):
    class_queryset = models.Goods_Class.objects.filter(status=1)
    json_data = list()
    for i in class_queryset:
        dic_data = dict()
        dic_data['id'] = i.id
        dic_data['status'] = i.get_status_display()
        dic_data['name'] = i.name
        json_data.append(dic_data)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询分类成功', 'data': json_data}),
        content_type='application/json')


# 编辑分类前
def edit_class_before(request):
    form = forms.FormEditClassBefore(request.POST)
    if form.is_valid():
        if not models.Goods_Class.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '选定的分类无效', 'data': []}),
                                          content_type='application/json')
        class_obj = models.Goods_Class.objects.get(id=form.cleaned_data['id'])
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '查询指定分类成功',
                                        'data': {'name': class_obj.name, 'status': class_obj.get_status_display()}}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑分类
def edit_class(request):
    form = forms.FormEditClass(request.POST)
    if form.is_valid():
        class_id = form.cleaned_data['id']
        class_status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        class_name = form.cleaned_data['name']
        if models.Goods_Class.objects.filter(name=class_name).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '该商品名已存在', 'data': []}),
                                          content_type='application/json')
        if not models.Goods_Class.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要编辑的分类无效', 'data': []}),
                                          content_type='application/json')
        class_obj = models.Goods_Class.objects.get(id=class_id)
        class_obj.name = class_name
        class_obj.class_status = class_status
        class_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '分类编辑成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除分类
def del_class(request):
    form = forms.FormDelGoods(request.POST)
    if form.is_valid():
        class_obj = form.cleaned_data['id']
        if not models.Goods_Class.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要删除的分类无效', 'data': []}),
                                          content_type='application/json')
        class_obj = models.Goods_Class.objects.get(id=class_obj)
        class_obj.status = 2
        class_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '删除分类成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 添加分类
def add_class(request):
    form = forms.FormAddClass(request.POST)
    if form.is_valid():
        class_name = form.cleaned_data['name']
        if models.Goods_Class.objects.filter(name=class_name, status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'ok', 'msg': '该分类已存在', 'data': []}),
                                          content_type='application/json')
        elif models.Goods_Class.objects.filter(name=class_name, status=2).exists():
            class_obj = models.Goods_Class.objects.filter(name=class_name, status=2).first()
        else:
            class_obj = models.Goods_Class()
        class_obj.name = class_name
        class_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        class_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '创建分类成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查商品规格
def all_spec(request):
    spec_queryset = models.Spec.objects.exclude(status=2)
    json_data = list()
    for i in spec_queryset:
        dic_data = dict()
        dic_data['id'] = i.id
        dic_data['name'] = i.name
        dic_data['sub_spec'] = i.sub_spec
        dic_data['status'] = i.get_status_display()
        json_data.append(dic_data)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询商品规格成功', 'data': json_data}),
        content_type='application/json')


# 查商品规格（有效）
def all_spec_valid(request):
    spec_queryset = models.Spec.objects.filter(status=1)
    json_data = list()
    for i in spec_queryset:
        dic_data = dict()
        dic_data['id'] = i.id
        dic_data['name'] = i.name
        dic_data['sub_spec'] = i.sub_spec
        dic_data['status'] = i.get_status_display()
        json_data.append(dic_data)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询商品规格成功', 'data': json_data}),
        content_type='application/json')


# 编辑商品规格前
def edit_spec_before(request):
    form = forms.FormEditSpecBefore(request.POST)
    if form.is_valid():
        if not models.Spec.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '选定的规格无效', 'data': []}),
                                          content_type='application/json')
        spec_obj = models.Spec.objects.get(id=form.cleaned_data['id'])
        json_dic = dict()
        json_data_dic = dict()
        json_data_dic['name'] = spec_obj.name
        json_data_dic['sub_spec'] = spec_obj.sub_spec
        json_data_dic['status'] = spec_obj.get_status_display()
        json_dic['code'] = 'ok'
        json_dic['msg'] = '查询指定规格成功'
        json_dic['data'] = json_data_dic
        return HttpResponse(json.dumps(json_dic), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑商品规格
def edit_spec(request):
    form = forms.FormEditSpec(request.POST)
    if form.is_valid():
        spec_id = form.cleaned_data['id']
        if not models.Spec.objects.filter(id=spec_id, status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要编辑的规格无效', 'data': []}),
                                          content_type='application/json')
        spec_obj = models.Spec.objects.get(id=spec_id)
        spec_obj.name = form.cleaned_data['name']
        spec_obj.sub_spec = form.cleaned_data['sub_spec']
        spec_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        spec_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '编辑规格成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除商品规格
def del_spec(request):
    form = forms.FormDelSpec(request.POST)
    if form.is_valid():
        spec_id = form.cleaned_data['id']
        if not models.Spec.objects.filter(id=spec_id).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要删除的规格不存在', 'data': []}),
                                          content_type='application/json')
        spec_obj = models.Spec.objects.get(id=spec_id)
        spec_obj.status = 2
        spec_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '删除规格成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 增加商品规格
def add_spec(request):
    form = forms.FormAddSpec(request.POST)
    if form.is_valid():
        if models.Spec.objects.filter(name=form.cleaned_data['name'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'ok', 'msg': '商品规格已存在', 'data': []}),
                                          content_type='application/json')
        elif models.Spec.objects.filter(name=form.cleaned_data['name'], status=2).exists():
            spec_obj = models.Spec.objects.filter(name=form.cleaned_data['name']).first()
        else:
            spec_obj = models.Spec()
        spec_obj.name = form.cleaned_data['name']
        spec_obj.sub_spec = form.cleaned_data['sub_spec']
        spec_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        spec_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '创建规格成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查所有供应商或顾客
def all_client(request):
    # form = forms.FormAllClient(request.POST)
    # if form.is_valid():
    # client_type = form.cleaned_data['type']
    # if client_type not in [0, 1]:
    #     return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '请指定供应商还是客户', 'data': []}),
    #                                   content_type='application/json')
    query_set = models.Client.objects.filter(status__in=[0, 1])
    data_list = list()
    for i in query_set:
        client_dic = dict()
        client_dic['id'] = i.id  # 以后涉及查询都要查id
        client_dic['name'] = i.name
        client_dic['tel'] = i.tel
        client_dic['contacts'] = i.contacts
        client_dic['addr'] = i.addr
        client_dic['account'] = i.account
        client_dic['status'] = i.get_status_display()
        client_dic['remarks'] = i.remarks
        client_dic['type'] = i.get_type_display()
        # client_dic['create_time'] = i.create_time.strftime(u'%Y年%m月%d日')  编码处理
        client_dic['create_time'] = i.create_time.strftime('%Y-%m-%d')
        data_list.append(client_dic)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询供应商/顾客成功', 'data': data_list}),
        content_type='application/json')


# else:
#     e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
#     return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
#                                   content_type='application/json')

# 查所有供应商或顾客，有效
def all_client_valid(request):
    query_set = models.Client.objects.filter(status=1)
    data_list = list()
    for i in query_set:
        client_dic = dict()
        client_dic['id'] = i.id  # 以后涉及查询都要查id
        client_dic['name'] = i.name
        client_dic['tel'] = i.tel
        client_dic['contacts'] = i.contacts
        client_dic['addr'] = i.addr
        client_dic['account'] = i.account
        client_dic['status'] = i.get_status_display()
        client_dic['remarks'] = i.remarks
        client_dic['type'] = i.get_type_display()
        # client_dic['create_time'] = i.create_time.strftime(u'%Y年%m月%d日')  编码处理
        client_dic['create_time'] = i.create_time.strftime('%Y-%m-%d')
        data_list.append(client_dic)
    return HttpResponse(
        json.dumps({'code': 'ok', 'msg': '查询供应商/顾客成功', 'data': data_list}),
        content_type='application/json')


# 编辑供应商/顾客前
def edit_client_before(request):
    form = forms.FormEditClientBefore(request.POST)
    if form.is_valid():
        if not models.Client.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '选定的供应商/顾客无效', 'data': []}),
                                          content_type='application/json')
        client_obj = models.Client.objects.get(id=form.cleaned_data['id'])
        json_dic = dict()
        json_data_dic = dict()
        json_data_dic['name'] = client_obj.name
        json_data_dic['tel'] = client_obj.tel
        json_data_dic['contacts'] = client_obj.contacts
        json_data_dic['addr'] = client_obj.addr
        json_data_dic['account'] = client_obj.account
        json_data_dic['status'] = client_obj.get_status_display()
        json_data_dic['remarks'] = client_obj.remarks
        json_data_dic['type'] = client_obj.get_type_display()
        json_dic['code'] = 'ok'
        json_dic['msg'] = '查询指定供应商/顾客成功'
        json_dic['data'] = json_data_dic
        return HttpResponse(json.dumps(json_dic), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑供应商/顾客
def edit_client(request):
    form = forms.FormEditClient(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['id']
        if not models.Client.objects.filter(id=client_id).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要编辑的供应商/顾客不存在', 'data': []}),
                                          content_type='application/json')
        client_obj = models.Client.objects.get(id=client_id)
        client_obj.name = form.cleaned_data['name']
        client_obj.tel = form.cleaned_data['tel']
        client_obj.contacts = form.cleaned_data['contacts']
        client_obj.addr = form.cleaned_data['addr']
        client_obj.account = form.cleaned_data['account']
        client_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        client_obj.remarks = form.cleaned_data['remarks']
        client_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '编辑供应商/顾客成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 添加供应商/顾客
def add_client(request):
    form = forms.FormAddClient(request.POST)
    if form.is_valid():
        if models.Client.objects.filter(name=form.cleaned_data['name'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '供应商/顾客已存在', 'data': []}),
                                          content_type='application/json')
        elif models.Client.objects.filter(name=form.cleaned_data['name'], status=2).exists():
            client_obj = models.Client.objects.filter(name=form.cleaned_data['name']).first()
        else:
            client_obj = models.Client()
        client_obj.name = form.cleaned_data['name']
        client_obj.tel = form.cleaned_data['tel']
        client_obj.contacts = form.cleaned_data['contacts']
        client_obj.addr = form.cleaned_data['addr']
        client_obj.account = form.cleaned_data['account']
        client_obj.remarks = form.cleaned_data['remarks']
        client_obj.type = {'供应商': 0, '顾客': 1}[form.cleaned_data['type']]
        client_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        client_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '添加供应商/顾客成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除供应商/顾客
def del_client(request):
    form = forms.FormDelClient(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['id']
        if not models.Client.objects.filter(id=client_id).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要删除的供应商/顾客不存在', 'data': []}),
                                          content_type='application/json')
        client_obj = models.Client.objects.get(id=client_id)
        if client_obj == 2:
            return HttpResponse(
                json.dumps({'code': 'ok', 'msg': '供应商/顾客已删除', 'data': []}),
                content_type='application/json')
        else:
            client_obj.status = 2
            client_obj.save()
            return HttpResponse(
                json.dumps({'code': 'ok', 'msg': '删除供应商/顾客成功', 'data': []}),
                content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查所有仓库/门店
def all_warehouse(request):
    form = forms.FormAllWarehouse(request.POST)
    if form.is_valid():
        client_type = form.cleaned_data['type']
        query_set = models.Warehouse.objects.filter(type=client_type, status__in=[0, 1])
        data_list = list()
        for i in query_set:
            client_dic = dict()
            client_dic['id'] = i.id
            client_dic['name'] = i.name
            client_dic['addr'] = i.addr
            client_dic['tel'] = i.tel
            client_dic['contacts'] = i.contacts
            client_dic['volume'] = i.volume
            client_dic['type'] = i.get_type_display()
            client_dic['storage_state'] = i.get_storage_state_display()
            client_dic['create_time'] = str(i.create_time)
            client_dic['status'] = i.get_status_display()
            data_list.append(client_dic)
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '查询仓库/门店成功', 'data': data_list}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 查所有仓库/门店，有效
def all_warehouse_valid(request):
    form = forms.FormAllWarehouse(request.POST)
    if form.is_valid():
        client_type = form.cleaned_data['type']
        query_set = models.Warehouse.objects.filter(type=client_type, status=1)
        data_list = list()
        for i in query_set:
            client_dic = dict()
            client_dic['id'] = i.id
            client_dic['name'] = i.name
            client_dic['addr'] = i.addr
            client_dic['tel'] = i.tel
            client_dic['contacts'] = i.contacts
            client_dic['volume'] = i.volume
            client_dic['type'] = i.get_type_display()
            client_dic['storage_state'] = i.get_storage_state_display()
            client_dic['create_time'] = str(i.create_time)
            client_dic['status'] = i.get_status_display()
            data_list.append(client_dic)
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '查询仓库/门店成功', 'data': data_list}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 增加仓库/门店
def add_warehouse(request):
    form = forms.FormAddWarehouse(request.POST)
    if form.is_valid():
        if models.Warehouse.objects.filter(name=form.cleaned_data['name'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '仓库/门店已存在', 'data': []}),
                                          content_type='application/json')
        elif models.Warehouse.objects.filter(name=form.cleaned_data['name'], status=2).exists():  # 添改
            warehouse_obj = models.Warehouse.objects.objects.get(name=form.cleaned_data['name'])
        else:
            warehouse_obj = models.Warehouse()
        warehouse_obj.name = form.cleaned_data['name']
        warehouse_obj.addr = form.cleaned_data['addr']
        warehouse_obj.tel = form.cleaned_data['tel']
        warehouse_obj.contacts = form.cleaned_data['contacts']
        warehouse_obj.volume = form.cleaned_data['volume']
        if not form.cleaned_data['type'] in [1, 2]:
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '注意仓库1，门店2', 'data': []}),
                                          content_type='application/json')
        warehouse_obj.type = form.cleaned_data['type']
        warehouse_obj.remarks = form.cleaned_data['remarks']
        warehouse_obj.storage_state = form.cleaned_data['storage_state']
        warehouse_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        warehouse_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '添加仓库/门店成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 删除仓库/门店
def del_warehouse(request):
    form = forms.FormDelWarehouse(request.POST)
    if form.is_valid():
        warehouse_id = form.cleaned_data['id']
        if not models.Warehouse.objects.filter(id=warehouse_id, status__in=[0, 1]):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要删除的仓库/门店不存在', 'data': []}),
                                          content_type='application/json')
        warehouse_id = models.Warehouse.objects.get(id=warehouse_id)
        warehouse_id.status = 2
        warehouse_id.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '删除仓库/门店成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑仓库/门店前
def edit_warehouse_before(request):
    form = forms.FormEditWarehouseBefore(request.POST)
    if form.is_valid():
        if not models.Warehouse.objects.filter(id=form.cleaned_data['id'], status__in=[0, 1]).exists():
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '选定的供应商/顾客无效', 'data': []}),
                                          content_type='application/json')
        warehouse_obj = models.Warehouse.objects.get(id=form.cleaned_data['id'])
        json_dic = dict()
        json_data_dic = dict()
        json_data_dic['name'] = warehouse_obj.name
        json_data_dic['addr'] = warehouse_obj.addr
        json_data_dic['tel'] = warehouse_obj.tel
        json_data_dic['contacts'] = warehouse_obj.contacts
        json_data_dic['status'] = warehouse_obj.get_status_display()
        json_data_dic['volume'] = warehouse_obj.volume
        json_data_dic['type'] = warehouse_obj.get_type_display()
        json_data_dic['storage_state'] = warehouse_obj.get_storage_state_display()

        json_dic['code'] = 'ok'
        json_dic['msg'] = '查询指定供应商/顾客成功'
        json_dic['data'] = json_data_dic
        return HttpResponse(json.dumps(json_dic), content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 编辑仓库/门店
def edit_warehouse(request):
    form = forms.FormEditWarehouse(request.POST)
    if form.is_valid():
        warehouse_id = form.cleaned_data['id']
        if not models.Warehouse.objects.filter(id=warehouse_id, status__in=[0, 1]):
            return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '要编辑的仓库/门店不存在', 'data': []}),
                                          content_type='application/json')
        warehouse_obj = models.Warehouse.objects.get(id=warehouse_id)
        warehouse_obj.name = form.cleaned_data['name']
        warehouse_obj.addr = form.cleaned_data['addr']
        warehouse_obj.contacts = form.cleaned_data['contacts']
        warehouse_obj.volume = form.cleaned_data['volume']
        type = form.cleaned_data['type']
        if not type in [1, 2]:  # 前端有可能不发数字来
            # return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': '注意仓库1，门店2', 'data': []}),
            #                               content_type='application/json')
            type = {'仓库': 1, '门店': 2}[form.cleaned_data['type']]
        warehouse_obj.type = type
        warehouse_obj.storage_state = {'已满': 0, '未满': 1, '空': 2}[form.cleaned_data['storage_state']]
        warehouse_obj.status = {'停用': 0, '启用': 1, '删除/失效': 2}[form.cleaned_data['status']]
        warehouse_obj.save()
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '编辑仓库/门店成功', 'data': []}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')
