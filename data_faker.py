# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sh_psi.settings")
django.setup()

from faker import Faker
from faker.providers import BaseProvider  # 引入基类

from base import models as base_models
from purchase_sales import models as purchase_sales_models

fake = Faker('zh-CN')


# 创建并继承，实现方法
class sh_psi(BaseProvider):
    def type_num(self):  # 返回0或1状态码
        return self.random_element([0, 1])


# 添加到实例中，之后可以调用sh_psi里面的方法产生结果了
fake.add_provider(sh_psi)


def create_client():
    for i in range(1000):  # 对Client模型
        try:
            client_obj = base_models.Client()
            fake_name = fake.name()
            client_obj.name = fake_name
            client_obj.tel = fake.phone_number()
            client_obj.contacts = fake_name
            client_obj.addr = fake.address()
            client_obj.account = fake.iban()
            client_obj.remarks = '测试'
            client_obj.type = fake.type_num()
            client_obj.save()
            print('生成数量:{}'.format(base_models.Client.objects.all().count()))
        except Exception as e:
            continue


def create_goods_class():
    for i in range(1000):
        try:
            goods_obj = base_models.Goods_Class()
            goods_obj.name = '分类{}'.format(i)
            goods_obj.save()
            print('生成数量:{}'.format(base_models.Goods_Class.objects.all().count()))
        except Exception as e:
            continue


def create_spec():
    for i in range(1000):
        try:
            spec_obj = base_models.Spec()
            spec_obj.name = '规格主名{}'.format(i)
            spec_obj.sub_spec = '规格辅助名{}'.format(i)
            spec_obj.save()
            print('生成数量:{}'.format(base_models.Spec.objects.all().count()))
        except Exception as e:
            continue


def create_goods():
    for i in range(1000):
        try:
            goods_obj = base_models.Goods()
            goods_obj.name = '商品名{}'.format(i)
            goods_obj.spec = base_models.Spec.objects.get(id=random.randint(1, 1000))
            goods_obj.goods_class = base_models.Goods_Class.objects.get(id=random.randint(1, 1000))
            goods_obj.rec_price = random.randint(5, 100)
            goods_obj.purchase_price = random.randint(5, 100)
            goods_obj.sale_price = random.randint(5, 100)
            goods_obj.save()
            print('生成数量:{}'.format(base_models.Goods.objects.all().count()))
        except Exception as e:
            continue


def create_warehouse():
    for i in range(1000):
        try:
            warehouse_obj = base_models.Warehouse()
            warehouse_obj.name = '仓库名{}'.format(i)
            warehouse_obj.addr = fake.address()
            warehouse_obj.tel = fake.phone_number()
            warehouse_obj.contacts = fake.phone_number()
            warehouse_obj.volume = random.randint(100, 1000)
            warehouse_obj.type = random.randint(1, 2)
            warehouse_obj.storage_state = random.randint(0, 2)
            warehouse_obj.save()
            print('生成数量:{}'.format(base_models.Warehouse.objects.all().count()))
        except Exception as e:
            continue


def create_order():
    for i in range(1000):
        try:
            order_obj = purchase_sales_models.Order()
            order_obj.identifier = fake.iban()
            order_obj.type = fake.type_num()
            order_obj.client = base_models.Client.objects.get(id=random.randint(1, 1000))
            order_obj.warehouse = base_models.Warehouse.objects.get(id=random.randint(1, 1000))
            order_obj.cabinets = fake.bban()
            order_obj.send_way = '{}号快递'.format(i)
            order_obj.count_type = random.randint(0, 5)
            order_obj.real_price = random.randint(100, 1000)
            order_obj.need_price = random.randint(100, 1000)
            order_obj.approval_status = random.randint(0, 2)
            order_obj.save()
            print('生成数量:{}'.format(purchase_sales_models.Order.objects.all().count()))
        except Exception as e:
            continue


def create_detailorder():
    for i in range(1000):
        try:
            detailorder_obj = purchase_sales_models.DetailOrder()
            detailorder_obj.num = random.randint(1, 100)
            detailorder_obj.price = random.randint(1, 100)
            detailorder_obj.need_price = detailorder_obj.num * detailorder_obj.price
            detailorder_obj.new_need_price = detailorder_obj.num * detailorder_obj.price
            detailorder_obj.batch = fake.license_plate()
            detailorder_obj.order = purchase_sales_models.Order.objects.get(id=random.randint(1, 100))
            detailorder_obj.goods = base_models.Goods.objects.get(id=random.randint(1, 100))
            detailorder_obj.save()
            print('生成数量:{}'.format(purchase_sales_models.DetailOrder.objects.all().count()))
        except Exception as e:
            continue


# create_client()
# create_goods_class()
# Spec()
# create_goods()
# create_warehouse()
# create_order()
# create_detailorder()
