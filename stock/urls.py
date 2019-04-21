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

from stock import views

urlpatterns = [
    url('^goods_kucun$', views.goods_kucun),  # 查询所有有进出库记录且存量大于0的物品(商品条目可能无效)，给创建销售单用
    url('^check_goods$', views.check_goods),  # 查询某库有进出库记录但可能库存为0的物品，给盘点，调拨，加工用

    url('^check_kucun$', views.check_kucun),  # 盘点商品单，一旦生成即改变库存,若需要临时保存功能另外补充接口
    url('^change_kucun$', views.change_kucun),  # 调拨商品（考虑批次）,一旦生成即改变库存
    url('^work_goods$', views.work_goods),  # 加工商品,一旦生成即改变库存，多种变多种

    url('^check_kucun_simple$', views.check_kucun_simple),  # 粗略查询盘点单
    url('^check_kucun_detail$', views.check_kucun_detail),  # 详细查询盘点单
    url('^change_kucun_simple$', views.change_kucun_simple),  # 粗略查询调拨单
    url('^change_kucun_detail$', views.change_kucun_detail),  # 详细查询调拨单
    url('^work_goods_simple$', views.change_work_goods_simple),  # 粗略查询加工单
    url('^work_goods_detail$', views.change_work_goods_detail),  # 详细查询加工单

    url('^kucun_order_simple$', views.kucun_order_simple),  # 粗略查询库存记录单
    url('^kucun_order_detail$', views.kucun_order_detail),  # 详细查询库存记录单
]
