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

from report import views

urlpatterns = [
    url('remain_money', views.remain_money),  # 当下应付/应发统计
    url('export_1', views.export_1),  # 导出报表 商品库存
    url('export_2', views.export_2),  # 导出报表 销售明细表
    url('export_3', views.export_3),  # 导出报表 客户销售汇总表
    url('export_4', views.export_4),  # 导出报表 供应商明细表
    url('export_5', views.export_5),  # 导出报表 供应商付款汇总表
    url('export_6', views.export_6),  # 导出报表 日报表

]
