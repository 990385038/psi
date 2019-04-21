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

from purchase_sales import views

urlpatterns = [
    url('^add_order$', views.add_order),  # 创建进货/销售订单
    url('^all_order_simple$', views.all_order_simple),  # 粗略查询有效进货订单
    url('^all_sell_simple$', views.all_sell_simple),  # 粗略查询有效销售订单
    url('^unite_order_detail$', views.unite_order_detail),  # 详细查询某张订单
    url('^edit_order$', views.edit_order),  # 修改订单，已出库不能修改，且只能修改基本信息
    url('^del_order$', views.del_order),  # 删除订单
    url('^kucun_order$', views.kucun_order),  # 将订单进出库
    url('^bill_order$', views.bill_order),  # 自助收款/付款订单
    url('^finish_order$', views.finish_order),  # 结案订单
    url('^all_reviewing_order$', views.all_reviewing_order),  # 粗略查询所有审核中订单
    url('^reviewed_order$', views.reviewed_order),  # 将订单审核通过，权限控制未知
    url('^all_del_order$', views.all_del_order),  # 查询所有已删除/失效订单
    url('^all_uncount_purchase$', views.all_uncount_purchase),  # 查询所有未结案、有效、审核通过的进货订单
    url('^all_uncount_sale$', views.all_uncount_sale),  # 查询所有未结案、有效、审核通过的销售订单
]
