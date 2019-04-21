# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import Client
from django.test import TestCase


# Create your tests here.
class BaseTestCase(TestCase):

    # 测试开始前的工作
    def setUp(self):
        # print('开始测试base')
        pass

    # 测试结束的收尾工作
    def tearDown(self):
        # print('结束测试base')
        pass

    # 自己定义的测试方法，必须以"test_"开头
    def test_all_goods(self):
        print('测试查询所有商品条目列表')
        c = Client()
        response = c.get('/base/all_goods')
        self.assertEqual(response.status_code, 200)

    # 增加商品
    def test_add_goods(self):
        print('测试增加商品')
        pass

    # 编辑商品
    def test_edit_goods_before(self):
        print('测试编辑商品')

        pass

    # 删除商品
    def test_del_goods(self):
        print('测试删除商品')


    # 查商品分类
    def test_all_class(self):
        print('测试查商品分类')

    # 编辑分类
    def test_edit_class(self):
        pass

    # 删除分类
    def test_del_class(self):
        pass

    # 添加分类
    def test_add_class(self):
        pass

    # 查商品规格
    def test_all_spec(self):
        pass

    # 编辑商品规格
    def test_edit_spec(self):
        pass

    # 删除商品规格
    def test_del_spec(self):
        pass

    # 增加商品规格
    def test_add_spec(self):
        pass

    # 查所有供应商/顾客
    def test_all_client(self):
        pass

    # 编辑供应商/顾客
    def test_edit_client(self):
        pass

    # 添加供应商/顾客
    def test_add_client(self):
        pass

    # 删除供应商/顾客
    def test_del_client(self):
        pass

    # 查所有仓库/门店
    def test_all_warehouse(self):
        pass

    # 添加仓库/门店
    def test_add_warehouse(self):
        pass

    # 删除仓库/门店
    def test_del_warehouse(self):
        pass

    # 编辑仓库/门店
    def test_edit_warehouse(self):
        pass
