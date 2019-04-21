# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
# 订单总表、进货/销售详细单
# 总单：应收/付金额(总)，已收/付金额，详细单：应收/付金额，实际应收/付金额
# 之前：详细单有应收/付金额，总单显示总的应收付金额和已收/付金额，如果优惠，则直接将订单状态归为已经结清
# 现在：详细单有应付/付金额，实际应收/付金额，总单显示总的实际应收/付金额和已收/付金额，如果再有优惠，则直接将订单状态归为已经结清
class Order(models.Model):  # 订单总表
    identifier = models.CharField(max_length=32, unique=True)  # 订单编号
    type = models.IntegerField(choices=(
        (0, '进货订单'),
        (1, '销售订单'),
    ))
    client = models.ForeignKey('base.Client')
    warehouse = models.ForeignKey('base.Warehouse')
    cabinets = models.CharField(max_length=32, blank=True)  # 订单运输柜号
    # batch = models.CharField(max_length=32, null=True)  # 设定订单内所有商品为同一批次，放在详细单！
    send_way = models.CharField(max_length=32)  # 发货方式
    count_type = models.IntegerField(choices=(  # 提醒方式月底统一企业微信提醒一次
        (0, '现结结账'),
        (1, '现结未结账'),
        (2, '月结结账'),
        (3, '月结未结账'),
        (4, '批结结账'),
        (5, '批结未结账'),
    ))  # 结算方式
    # price_status = models.IntegerField(choices=(  # 付款状态,改为由count_type体现
    #     (0, '未付清'),
    #     (1, '已付清'),
    # ))
    real_price = models.FloatField()  # 已付/收金额
    need_price = models.FloatField()  # 总应付/收，前端根据详细单合计
    # order_kucun = models.IntegerField(choices=(
    #     (0, '未入/出库'),
    #     (1, '已入/出库'),
    # ), default=0)  # 订单是否已入库,改为通过判断是否有外键库存单知道是否已进出库
    approval_status = models.IntegerField(choices=(  # 各级审批情况
        (0, '审核中'),
        (1, '审核通过'),
        (2, '审核失败'),
    ), default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    order_status = models.IntegerField(choices=(
        (0, '无效/删除'),
        (1, '有效'),
    ), default=1)  # 订单是否有效
    kucun_order = models.ForeignKey('stock.KucunOrder', null=True)  # 连进出库单,允许先为空


class DetailOrder(models.Model):  # 进货/销售详细单
    num = models.FloatField()
    price = models.FloatField()  # 从商品模型快速获取，如果该商品后面修改了价格，这里不受影响
    need_price = models.FloatField()  # 总应付/收，前端用单价和数量计算
    new_need_price = models.FloatField()  # 实际总应付/收，根据总应付/收，用户手改
    batch = models.CharField(max_length=32, null=True)  # 进货时所有商品可以为同一批次，销售时不一定
    order = models.ForeignKey(Order)
    goods = models.ForeignKey('base.Goods')  # 或者不需要外键到Goods
