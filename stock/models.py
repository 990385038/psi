# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
# 库存总单(变更记录)、库存详细单(变更记录)、盘点总单、调拨总单、调拨详细单、加工商品总单、加工商品详细单

# 注意，对一个库
class KucunOrder(models.Model):  # 库存总单(变更记录)
    identifier = models.CharField(max_length=64)  # 进出库单编号
    # type = models.IntegerField(choices=(
    #     (0, '进库'),
    #     (1, '入库'),
    # ))    # 准备修改num为正负体现进出库，改为去掉本属性
    how = models.IntegerField(choices=(
        (0, '进货'),
        (1, '销售'),
        (2, '加工'),
        (3, '盘点'),
        (4, '调拨'),
    ))
    warehouse = models.ForeignKey('base.Warehouse')
    create_time = models.DateTimeField(auto_now_add=True)


class KucunOrderDetail(models.Model):  # 库存详细单(变更记录)
    goods = models.ForeignKey('base.Goods')
    num = models.FloatField()  # 正负值
    batch = models.CharField(max_length=32)  # 注意商品批次号不要放在总单
    order = models.ForeignKey(KucunOrder)


class CheckOrder(models.Model):  # 盘点总单
    identifier = models.CharField(max_length=64)  # 编号
    warehouse = models.ForeignKey('base.Warehouse')
    check_time = models.CharField(max_length=64)  # 盘点日期
    kucun_order = models.ForeignKey('KucunOrder')  # 连进出库单
    create_time = models.DateTimeField(auto_now_add=True)


class CheckOrderDetail(models.Model):  # 盘点详细单
    goods = models.ForeignKey('base.Goods')
    num = models.FloatField()
    batch = models.CharField(max_length=32)  # 注意商品批次号不要放在总单
    order = models.ForeignKey(CheckOrder)  # 连盘点总单
    # create_time = models.DateTimeField(auto_now_add=True)


class ChangeOrder(models.Model):  # 调拨总单
    identifier = models.CharField(max_length=64)  # 编号
    warehouse_out = models.ForeignKey('base.Warehouse', related_name='house_out')
    warehouse_in = models.ForeignKey('base.Warehouse', related_name='house_in')
    kucun_out_order = models.ForeignKey('KucunOrder', related_name='order_out')  # 连out库单
    kucun_in_order = models.ForeignKey('KucunOrder', related_name='order_in')  # 连in库单
    change_time = models.CharField(max_length=64)  # 调拨日期,手写
    # commit_time = models.CharField()  # 到库日期，手写
    create_time = models.DateTimeField(auto_now_add=True)


class ChangeOrderDetail(models.Model):  # 调拨详细单
    goods = models.ForeignKey('base.Goods')
    num = models.FloatField()
    batch = models.CharField(max_length=32)  # 注意商品批次号不要放在总单
    order = models.ForeignKey(ChangeOrder)  # 连调拨总单


class WorkGoodsOrder(models.Model):  # 加工商品总单
    identifier = models.CharField(max_length=64)  # 编号
    warehouse_out = models.ForeignKey('base.Warehouse', related_name='work_house_out')
    warehouse_in = models.ForeignKey('base.Warehouse', related_name='work_house_in')
    kucun_out_order = models.ForeignKey(KucunOrder, related_name='work_order_out')  # 连out库单
    kucun_in_order = models.ForeignKey(KucunOrder, related_name='work_order_in')  # 连in库单
    work_time = models.CharField(max_length=64)  # 加工日期
    create_time = models.DateTimeField(auto_now_add=True)


class WorkGoodsOrderDetail(models.Model):  # 加工商品详细单，对加工有负有正
    goods = models.ForeignKey('base.Goods')
    # price = models.FloatField()  #
    batch = models.CharField(max_length=32)  # 注意商品批次号不要放在总单
    num = models.FloatField()
    # total_price = models.FloatField()
    order = models.ForeignKey(WorkGoodsOrder)  # 连加工总单
