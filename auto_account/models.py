# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from base import models as base_models


# Create your models here.
# 客户在订单上会有欠费，可以算出欠费总和，客户可以进账，订单收费会产生负的进账
class ClientIncome(models.Model):  # 客户/供应商账单模型
    client = models.ForeignKey(base_models.Client)
    money = models.FloatField()
    create_time = models.DateTimeField(auto_now_add=True)