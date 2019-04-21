# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
from io import BytesIO

import xlwt
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest

from base import models as base_models
from purchase_sales import models as purchase_sales_models
from report import forms
from stock import models as stock_models


# 当下我方总应付/总应发
def remain_money(request):
    form = forms.FormOrderMoney(request.POST)
    if form.is_valid():
        need_type = form.cleaned_data['need_type']  # 0进货，1销售
        # 取出有效的、进货或销售、未付清的、已进出库的订单
        order_query = purchase_sales_models.Order.objects.filter(type=need_type, approval_status=1, order_status=1)
        if order_query.exists():
            total_realy_price = order_query.aggregate(a=Sum('real_price'))['a']  # 所有订单实付/收
            total_need_price = order_query.aggregate(b=Sum('need_price'))['b']  # 所有订单应付/收，大于等于上面
            need_money = total_need_price - total_realy_price
        else:
            return HttpResponseBadRequest(
                json.dumps({'code': 'false', 'msg': '不存在{}订单'.format({0: '应付', 1: '应收'}[need_type]),
                            'data': []}),
                content_type='application/json')
        return HttpResponse(json.dumps({'code': 'ok', 'msg': '查询{}成功'.format({0: '应付', 1: '应收'}[need_type]),
                                        'data': [{'need_money': need_money}]}),
                            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 计算某供应商/客户总应付/收
def client_remain_money(request):
    form = forms.FormClientMoney(request.POST)
    if form.is_valid():
        client_id = form.cleaned_data['id']
        client_obj = base_models.Client.objects.get(id=client_id)
        order_query = purchase_sales_models.Order.objects.filter(client=client_obj, approval_status=1, order_status=1)
        total_realy_price = order_query.aggregate(a=Sum('real_price'))['a']  # 该客户所有订单实付/收
        total_need_price = order_query.aggregate(b=Sum('need_price'))['b']  # 该客户所有订单应付/收，大于等于上面
        if not total_realy_price:
            total_realy_price = 0
        if not total_need_price:
            total_need_price = 0
        need_money = total_need_price - total_realy_price
        return HttpResponse(
            json.dumps({'code': 'ok', 'msg': '查询成功', 'data': {'client_id': client_id, 'need_money': need_money}}),
            content_type='application/json')
    else:
        e = ','.join([form.errors[i][0] for i in form.errors]) if len(form.errors) > 0 else u'未知错误'
        return HttpResponseBadRequest(json.dumps({'code': 'false', 'msg': e, 'data': []}),
                                      content_type='application/json')


# 导出报表 商品库存
def export_1(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'商品库存', cell_overwrite_ok=True)

    style = xlwt.easyxf("""
                    font: 
                        height 220, 
                        name SimSun, 
                        colour_index black, 
                        bold off; 
                    align: 
                        wrap on, 
                        vert centre, 
                        horiz center;
                    borders:
                        left thin, 
                        right thin, 
                        top thin, 
                        bottom thin
                     """)
    sheet.write_merge(0, 0, 0, 21, '{}月库存表'.format(datetime.datetime.now().strftime('%Y.%m')), style)
    sheet.write_merge(1, 2, 0, 0, '序号', style)
    sheet.write_merge(1, 2, 1, 1, '商品全名', style)
    sheet.write_merge(1, 2, 2, 2, '批次', style)
    sheet.write_merge(1, 2, 3, 3, '单位', style)
    sheet.write_merge(1, 1, 4, 6, '本月期初库存（上月期末库存）', style)
    sheet.write_merge(1, 1, 7, 9, '本期购入（从月初到当前）', style)
    sheet.write_merge(1, 1, 10, 12, '本期加工入库（消耗）', style)
    sheet.write_merge(1, 1, 13, 15, '本期加工出库（产出）', style)
    sheet.write_merge(1, 1, 16, 18, '本期发出', style)
    sheet.write_merge(1, 1, 19, 21, '期末结存', style)
    sheet.row(2).set_style(xlwt.easyxf('font:height 440;'))
    for i in range(6):
        sheet.write(2, 4 + 3 * i, '数量', style)
        sheet.write(2, 5 + 3 * i, '单价', style)
        sheet.write(2, 6 + 3 * i, '金额', style)
    xuhao = 0
    row = 2
    for i in stock_models.KucunOrderDetail.objects.values('goods', 'batch').distinct().order_by('goods', 'batch'):
        xuhao += 1
        row += 1
        goods_obj = base_models.Goods.objects.select_related('spec').filter(id=i['goods']).first()
        good_name = goods_obj.name
        good_batch = i['batch']
        good_spec = goods_obj.spec.name
        sheet.write(row, 0, xuhao, style)
        sheet.write(row, 1, good_name, style)
        sheet.write(row, 2, good_batch, style)
        sheet.write(row, 3, good_spec, style)
        # 本月期初库存
        qichu = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # 本月第一天
        lastmonth_sum = stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'],
                                                                     order__create_time__lt=qichu).aggregate(
            a=Sum('num'))[
            'a']  # 本月开始前该商品总数
        if not lastmonth_sum:
            lastmonth_sum = 0  # 初始化上月剩余库存，上月不一定有库存，需要初始化
        sheet.write(row, 4, lastmonth_sum, style)
        sheet.write(row, 5, goods_obj.purchase_price, style)  # 这种商品的进货价/采购价
        sheet.write(row, 6, lastmonth_sum * goods_obj.purchase_price, style)
        # 本期购入
        now_datetime = datetime.datetime.now()  # 当前时间
        benqi_sum = stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'], order__how=0,
                                                                 order__create_time__range=(
                                                                     qichu, now_datetime)).aggregate(
            a=Sum('num'))['a']  # 月初到目前采购/进货商品总数
        if not benqi_sum:
            benqi_sum = 0  # 可能本期没进货，none改0
        sheet.write(row, 7, benqi_sum, style)
        sheet.write(row, 8, goods_obj.purchase_price, style)  # 这种商品的进货价/采购价
        sheet.write(row, 9, benqi_sum * goods_obj.purchase_price, style)
        # 本期加工消耗
        xiaohao_sum = \
            stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'], order__how=2, num__lt=0,
                                                         order__create_time__range=(qichu, now_datetime)).aggregate(
                a=Sum('num'))['a']  # 月初到目前采购/进货商品总数
        if not xiaohao_sum:
            xiaohao_sum = 0
        else:
            xiaohao_sum = abs(xiaohao_sum)
        sheet.write(row, 10, xiaohao_sum, style)
        sheet.write(row, 11, goods_obj.purchase_price, style)  # 这种商品的进货价/采购价
        sheet.write(row, 12, xiaohao_sum * goods_obj.purchase_price, style)
        # 本期加工产出
        chanchu_sum = \
            stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'], order__how=2, num__gt=0,
                                                         order__create_time__range=(
                                                             qichu, now_datetime)).aggregate(
                a=Sum('num'))['a']  # 月初到目前采购/进货商品总数
        if not chanchu_sum:  # 没加工情况
            chanchu_sum = 0
        sheet.write(row, 13, chanchu_sum, style)
        sheet.write(row, 14, goods_obj.purchase_price, style)  # 全是这种商品的进货价/采购价
        sheet.write(row, 15, chanchu_sum * goods_obj.purchase_price, style)
        # 本期发出
        xiaoshou_sum = stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'], order__how=1,
                                                                    order__create_time__range=(
                                                                        qichu, now_datetime)).aggregate(
            a=Sum('num'))['a']  # 月初到目前销售商品总数
        if not xiaoshou_sum:  # 没售出
            xiaoshou_sum = 0
        else:
            xiaoshou_sum = abs(xiaoshou_sum)
        sheet.write(row, 16, xiaoshou_sum, style)
        sheet.write(row, 17, goods_obj.sale_price, style)  # 这种商品的批发价
        sheet.write(row, 18, xiaoshou_sum * goods_obj.sale_price, style)
        # 期末结存
        qimo_sum = stock_models.KucunOrderDetail.objects.filter(goods=i['goods'], batch=i['batch'],
                                                                order__create_time__range=[qichu,
                                                                                           now_datetime]).aggregate(
            a=Sum('num'))['a']  # 到目前商品总数

        if not qimo_sum:  # 没售出
            qimo_sum = 0
        else:
            qimo_sum = abs(qimo_sum)
        sheet.write(row, 19, qimo_sum, style)
        sheet.write(row, 20, goods_obj.purchase_price, style)  # 这种商品的进货价/采购价
        sheet.write(row, 21, qimo_sum * goods_obj.purchase_price, style)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出报表 销售明细表
def export_2(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'销售明细表', cell_overwrite_ok=True)

    style = xlwt.easyxf("""
                       font: 
                           height 220, 
                           name SimSun, 
                           colour_index black, 
                           bold off; 
                       align: 
                           wrap on, 
                           vert centre, 
                           horiz center;
                       borders:
                           left thin, 
                           right thin, 
                           top thin, 
                           bottom thin
                        """)
    sheet.write_merge(0, 1, 0, 0, '销售日期', style)
    sheet.write_merge(0, 1, 1, 1, '单据类型', style)
    sheet.write_merge(0, 1, 2, 2, '单据编号', style)
    sheet.write_merge(0, 1, 3, 3, '商品名称', style)
    sheet.write_merge(0, 1, 4, 4, '单位', style)
    sheet.write_merge(0, 1, 5, 5, '规格', style)
    sheet.write_merge(0, 0, 6, 8, '期初数', style)
    sheet.write_merge(0, 0, 9, 11, '本期销售', style)
    sheet.write_merge(0, 0, 12, 14, '本期收款', style)
    sheet.write_merge(0, 0, 15, 17, '期末结余', style)
    sheet.write(1, 6, '数量', style)
    sheet.write(1, 7, '单价', style)
    sheet.write(1, 8, '金额', style)
    sheet.write(1, 9, '数量', style)
    sheet.write(1, 10, '单价', style)
    sheet.write(1, 11, '金额', style)
    sheet.write(1, 12, '金额', style)
    sheet.write(1, 13, '付款日期', style)
    sheet.write(1, 14, '付款方式', style)
    sheet.write(1, 15, '数量', style)
    sheet.write(1, 16, '单价', style)
    sheet.write(1, 17, '金额', style)
    # 基于库存变动总表,一个销售单融合在一起写，内部商品分多行
    # row = 2  # 起始行数下标
    # qichu = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # 本月第一天
    # now_datetime = datetime.datetime.now()  # 当前时间
    # for i in models.KucunOrder.objects.annotate(detail_num=Count('kucunorderdetail')).
    # filter(how=1, create_time__range=(
    #         qichu, now_datetime)):
    #     each_order_rows = i.detail_num  # 每条销售库存总单占的行数
    #     # 反复重复融合写，或者一行行重复写，最后显示效果不一样而已
    #     sheet.write_merge(row, row + each_order_rows - 1, 0, 0, i.create_time.strftime('%Y年%m月%d日'), style)
    #     sheet.write_merge(row, row + each_order_rows - 1, 1, 1, '销售单', style)
    #     sheet.write_merge(row, row + each_order_rows - 1, 2, 2, i.identifier, style)
    #     row_goods = row - 1  # 一个销售单可能占多行，但销售单内商品各只占一行
    #     for j in i.kucunorderdetail_set.select_related('good__name', 'good__spec__name',
    #     'good__spec__sub_spec').all():
    #         row_goods += 1
    #         sheet.write(row_goods, 3)放弃这种写法
    #     row = row + each_order_rows  # 下次行数开始地方

    # 基于库存变动详细表，一个销售单可能有多种商品，分多行写，每行销售单信息会重复,但比较简单
    # 先全写完再融合好像也比较方便
    qichu = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # 本月第一天
    now_datetime = datetime.datetime.now()  # 当前时间
    row = 1  # 写excel的前一行
    for i in stock_models.KucunOrderDetail.objects.select_related('order', 'goods').filter(order__how=1,
                                                                                           order__create_time__range=(
                                                                                                   qichu,
                                                                                                   now_datetime)):
        row += 1
        sheet.write(row, 0, i.order__create_time.strftime('%Y年%m月%d日'), style)
        sheet.write(row, 1, '销售单', style)
        sheet.write(row, 2, i.order__identifier, style)
        sheet.write(row, 3, i.good__name, style)
        sheet.write(row, 4, i.batch, style)
        sheet.write(row, 5, i.good__spec__name, style)
        sheet.write(row, 6, i.good__spec__sub_spec, style)
        # 期初数
        qichu_num = \
            stock_models.KucunOrderDetail.objects.filter(goods=i.goods, order__create_time__lt=qichu).aggregate(
                a=Sum('num'))[
                'a']
        sheet.write(row, 7, qichu_num, style)
        sheet.write(row, 8, i.good__purchase_price, style)
        sheet.write(row, 9, qichu_num * i.good__purchase_price, style)
        # 本期销售
        benqi_num = stock_models.KucunOrderDetail.objects.filter(goods=i.goods, order__create_time__range=(
            qichu_num, now_datetime)).aggregate(a=Sum('num'))['a']
        sheet.write(row, 10, benqi_num, style)
        sheet.write(row, 11, i.good__trade_price, style)
        sheet.write(row, 12, benqi_num * i.good__purchase_price, style)
        # 本期收款
        kucunorder_obj = stock_models.KucunOrder.objects.filter(id=i.order.id).first()
        order_obj = purchase_sales_models.Order.objects.filter(kucun_order=kucunorder_obj).first()
        benqi_money = order_obj.real_price  # 同一单会出现多条收款，因为单内商品拆开了
        benqi_date = order_obj.create_time.strftime('%Y年%m月%d日')
        benqi_fukuanfanshi = order_obj.count_type
        sheet.write(row, 13, benqi_money, style)
        sheet.write(row, 14, benqi_date, style)
        sheet.write(row, 15, benqi_fukuanfanshi, style)
        # 期末结余
        qimo_num = stock_models.KucunOrderDetail.objects.filter(goods=i.goods, order__create_time__range=(
            qichu_num, now_datetime)).aggregate(a=Sum('num'))[
            'a']
        sheet.write(row, 16, qimo_num, style)
        sheet.write(row, 17, i.good__purchase_price, style)
        sheet.write(row, 18, qimo_num * i.good__purchase_price, style)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出报表 客户销售汇总表
def export_3(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'客户销售汇总表', cell_overwrite_ok=True)

    style = xlwt.easyxf("""
                       font: 
                           height 220, 
                           name SimSun, 
                           colour_index black, 
                           bold off; 
                       align: 
                           wrap on, 
                           vert centre, 
                           horiz center;
                       borders:
                           left thin, 
                           right thin, 
                           top thin, 
                           bottom thin
                        """)
    sheet.write_merge(0, 0, 0, 7, datetime.datetime.now().strftime('%Y年%m月销售应收款汇总'))
    sheet.write(1, 0, '序号', style)
    sheet.write(1, 1, '客户名称', style)
    sheet.write(1, 2, '期初金额', style)
    sheet.write(1, 3, '本期应收金额', style)
    sheet.write(1, 4, '本期已收金额', style)
    sheet.write(1, 5, '期末应收金额', style)
    sheet.write(1, 6, '备注', style)
    sheet.write(1, 7, '业务员', style)
    xuhao = 0
    for i in base_models.Client.objects.filter(type=0, status=1):
        xuhao += 1
        qichu = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # 本月第一天
        now_datetime = datetime.datetime.now()  # 当前时间
        sheet.write(2, 0, xuhao, style)
        sheet.write(2, 1, i.name, style)
        # 查月初没付清订单已收多少，应收多少
        yuechu_yingshou = \
            purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                       create_time__lt=qichu).aggregate(
                a=Sum('need_price'))['a']
        yuechu_yishou = \
            purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                       create_time__lt=qichu).aggregate(a=Sum('real_price'))[
                'a']
        sheet.write(2, 2, yuechu_yingshou - yuechu_yishou, style)
        benqi_yingshou = purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                                    create_time__range=(qichu, now_datetime)).aggregate(
            a=Sum('need_price'))['a']
        benqi_yishou = purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                                  create_time__range=(qichu, now_datetime)).aggregate(
            a=Sum('real_price'))['a']
        sheet.write(2, 3, benqi_yingshou, style)
        sheet.write(2, 4, benqi_yishou, style)
        qimo_yingshou = yuechu_yingshou - yuechu_yishou + benqi_yingshou - benqi_yishou
        sheet.write(2, 5, qimo_yingshou, style)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出报表 供应商明细表
def export_4(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'客户销售汇总表', cell_overwrite_ok=True)
    style = xlwt.easyxf("""
                       font: 
                           height 220, 
                           name SimSun, 
                           colour_index black, 
                           bold off; 
                       align: 
                           wrap on, 
                           vert centre, 
                           horiz center;
                       borders:
                           left thin, 
                           right thin, 
                           top thin, 
                           bottom thin
                        """)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出报表 供应商付款汇总表
def export_5(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'供应商付款汇总表', cell_overwrite_ok=True)

    style = xlwt.easyxf("""
                        font: 
                            height 220, 
                            name SimSun, 
                            colour_index black, 
                            bold off; 
                        align: 
                            wrap on, 
                            vert centre, 
                            horiz center;
                        borders:
                            left thin, 
                            right thin, 
                            top thin, 
                            bottom thin
                         """)
    sheet.write_merge(0, 0, 0, 7, datetime.datetime.now().strftime('%Y年%m月供应商未付款汇总'))
    sheet.write(1, 0, '序号', style)
    sheet.write(1, 1, '供应商名称', style)
    sheet.write(1, 2, '期初金额', style)
    sheet.write(1, 3, '本期应付金额', style)
    sheet.write(1, 4, '本期已付金额', style)
    sheet.write(1, 5, '期末应付金额', style)
    sheet.write(1, 6, '备注', style)
    xuhao = 0
    for i in base_models.Client.objects.filter(type=0, status=1):
        xuhao += 1
        qichu = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # 本月第一天
        now_datetime = datetime.datetime.now()  # 当前时间
        sheet.write(2, 0, xuhao, style)
        sheet.write(2, 1, i.name, style)
        # 查月初没付清订单已付多少，应付多少
        yuechu_yingfu = \
            purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                       create_time__lt=qichu).aggregate(
                a=Sum('need_price'))['a']
        yuechu_yifu = \
            purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                       create_time__lt=qichu).aggregate(a=Sum('real_price'))[
                'a']
        sheet.write(2, 2, yuechu_yingfu - yuechu_yifu, style)
        benqi_yingfu = purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                                  create_time__range=(qichu, now_datetime)).aggregate(
            a=Sum('need_price'))['a']
        benqi_yifu = purchase_sales_models.Order.objects.filter(type=1, client=i, price_status=0, order_status=1,
                                                                create_time__range=(qichu, now_datetime)).aggregate(
            a=Sum('real_price'))['a']
        sheet.write(2, 3, benqi_yingfu, style)
        sheet.write(2, 4, benqi_yifu, style)
        qimo_yingfu = yuechu_yingfu - yuechu_yifu + benqi_yingfu - benqi_yifu
        sheet.write(2, 5, qimo_yingfu, style)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出报表 日报表
def export_6(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment;filename=sh_psi.xls'
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet(u'日报表', cell_overwrite_ok=True)

    style = xlwt.easyxf("""
                       font: 
                           height 220, 
                           name SimSun, 
                           colour_index black, 
                           bold off; 
                       align: 
                           wrap on, 
                           vert centre, 
                           horiz center;
                       borders:
                           left thin, 
                           right thin, 
                           top thin, 
                           bottom thin
                        """)
    sheet.write_merge(0, 0, 0, 11, '销售·日报表', style)
    sheet.write_merge(1, 1, 0, 11, datetime.datetime.now().strftime('日期：%Y-%m-%d'))
    sheet.write(2, 0, '序号', style)
    sheet.write(2, 1, '配送', style)
    sheet.write(2, 2, '单据编号', style)
    sheet.write(2, 3, '单位', style)
    sheet.write(2, 4, '商品全名', style)
    sheet.write(2, 5, '数量', style)
    sheet.write(2, 6, '单价', style)
    sheet.write(2, 7, '金额', style)
    sheet.write(2, 8, '付款方式', style)
    sheet.write(2, 9, '实收', style)
    sheet.write(2, 10, '欠款', style)
    sheet.write(2, 11, '备注', style)
    xuhao = 0
    row = 2
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for i in purchase_sales_models.DetailOrder.objects.filter(order__create_time__gte=today_start,
                                                              order__order_status=1).select_related('order__identifier',
                                                                                                    'good__name',
                                                                                                    'good__trade_price'):
        xuhao += 1
        row += 1
        sheet.write(row, 0, xuhao, style)
        sheet.write(row, 2, i.order.identifier, style)
        sheet.write(row, 4, i.goods.name)
        sheet.write(row, 5, i.num)
        sheet.write(row, 6, i.goods.trade_price)
        sheet.write(row, 7, i.num * i.goods.trade_price)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response
