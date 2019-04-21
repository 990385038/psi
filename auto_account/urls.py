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

from auto_account import views

# auto_account自助结账app
urlpatterns = [
    url('^client_income$', views.client_income),  # 客户入账功能，另外对客户每次自助结账一张销售总单时，产生一个负的入账
    url('^client_income_total$', views.client_income_total),  # 查询某个客户目前入账余额,正数加负数，余额不足不可结账
    url('^client_income_now$', views.client_income_now),  # 查询所有客户目前余额
    url('^client_income_history$', views.client_income_history),  # 查询某个客户历史记账记录
    # 如果url很相似，需要正则匹配，不然../client_income/total访问了../client_income
]
