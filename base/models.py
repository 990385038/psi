# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# 供应商/谷歌、商品分类、商品规格、商品、库、权限、员工/角色、日志


class Client(models.Model):  # 供应商/顾客
    name = models.CharField(max_length=32, unique=True)
    tel = models.CharField(max_length=32)
    contacts = models.CharField(max_length=32)  # 联系人名
    addr = models.CharField(max_length=64)
    account = models.CharField(max_length=32)
    status = models.IntegerField(choices=(
        (0, '停用'),
        (1, '启用'),
        (2, '删除/失效'),), default=1)
    remarks = models.CharField(max_length=32)  # 备注
    type = models.IntegerField(choices=(
        (0, '供应商'),
        (1, '顾客'),))
    create_time = models.DateTimeField(auto_now_add=True)


class Goods_Class(models.Model):  # 商品分类
    name = models.CharField(max_length=16, unique=True)  # 删除了，新加找回对象再修改
    status = models.IntegerField(choices=(
        (0, '停用'),
        (1, '启用'),
        (2, '删除/失效'),), default=1)


class Spec(models.Model):  # 商品规格
    name = models.CharField(max_length=16, unique=True)  # 主名
    sub_spec = models.CharField(max_length=16)  # 副名
    status = models.IntegerField(choices=(
        (0, '停用'),
        (1, '启用'),
        (2, '删除/失效')), default=1)


class Goods(models.Model):  # 商品
    name = models.CharField(max_length=32)
    spec = models.ForeignKey(Spec)
    goods_class = models.ForeignKey(Goods_Class)
    # supplier = models.ForeignKey(Client)
    rec_price = models.FloatField()  # 建议价
    purchase_price = models.FloatField()  # 采购价
    sale_price = models.FloatField()  # 销售价
    status = models.IntegerField(choices=(
        (0, '停用'),
        (1, '启用'),
        (2, '删除/失效')), default=1)


class Warehouse(models.Model):  # 库,仓库名也唯一
    name = models.CharField(max_length=32, unique=True)
    addr = models.CharField(max_length=32)
    tel = models.CharField(max_length=32)
    contacts = models.CharField(max_length=32)
    status = models.IntegerField(choices=(
        (0, '停用'),
        (1, '启用'),
        (2, '删除/失效')), default=1)
    volume = models.FloatField()  # 仓库的容量
    type = models.IntegerField(choices=(
        (1, '仓库'),
        (2, '门店'),
    ), default=1, )

    storage_state = models.IntegerField(choices=(
        (0, "已满"),
        (1, "未满"),
        (2, "空")))
    create_time = models.DateTimeField(auto_now_add=True)


class Power(models.Model):  # 权限    # 和企业微信的关系
    name = models.CharField(max_length=32)
    # staff = models.ManyToManyField(Staff)


class Staff(models.Model):  # 员工/角色
    name = models.CharField(max_length=32)
    tel = models.CharField(max_length=32)
    work_id = models.IntegerField(unique=True)
    job = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    status = models.IntegerField(choices=(
        (0, '失效'),
        (1, '有效'),), default=1)
    power = models.ManyToManyField(Power, default=None)
    create_time = models.DateTimeField(auto_now_add=True)


class Log(models.Model):  # 日志
    User = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=64)
