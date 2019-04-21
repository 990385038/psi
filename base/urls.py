# -*- coding:utf-8 -*-
"""sh_psi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from base import views

urlpatterns = [
    url('^all_goods$', views.all_goods),  # 查询所有商品条目列表
    url('^all_goods_valid$', views.all_goods_valid),  # 查询商品,有效
    url('^add_goods$', views.add_goods),  # 增加商品
    url('^edit_goods_before$', views.edit_goods_before),  # 编辑商品前查询单条商品信息
    url('^edit_goods$', views.edit_goods),  # 编辑商品
    url('^del_goods$', views.del_goods),  # 删除商品

    url('^all_class$', views.all_class),  # 查商品分类
    url('^all_class_valid$', views.all_class_valid),  # 查商品分类，有效
    url('^edit_class_before$', views.edit_class_before),  # 编辑分类前
    url('^edit_class$', views.edit_class),  # 编辑分类
    url('^del_class$', views.del_class),  # 删除分类
    url('^add_class$', views.add_class),  # 添加分类

    url('^all_spec$', views.all_spec),  # 查商品规格
    url('^all_spec_valid$', views.all_spec_valid),  # 查商品规格，有效
    url('^edit_spec_before$', views.edit_spec_before),  # 编辑商品规格前
    url('^edit_spec$', views.edit_spec),  # 编辑商品规格
    url('^del_spec$', views.del_spec),  # 删除商品规格
    url('^add_spec$', views.add_spec),  # 增加商品规格

    url('^all_client$', views.all_client),  # 查所有供应商/顾客
    url('^all_client_valid$', views.all_client_valid),  # 查所有供应商/顾客，有效
    url('^edit_client_before$', views.edit_client_before),  # 编辑供应商/顾客前
    url('^edit_client$', views.edit_client),  # 编辑供应商/顾客
    url('^add_client$', views.add_client),  # 添加供应商/顾客
    url('^del_client$', views.del_client),  # 删除供应商/顾客

    url('^all_warehouse$', views.all_warehouse),  # 查所有仓库/门店
    url('^all_warehouse_valid$', views.all_warehouse_valid),  # 查所有仓库/门店，有效
    url('^add_warehouse$', views.add_warehouse),  # 添加仓库/门店
    url('^del_warehouse$', views.del_warehouse),  # 删除仓库/门店
    url('^edit_warehouse_before$', views.edit_warehouse_before),  # 编辑仓库/门店前
    url('^edit_warehouse$', views.edit_warehouse),  # 编辑仓库/门店
]
