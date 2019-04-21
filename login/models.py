# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=32)
    vip_level = models.IntegerField(choices=(
        (1, '星耀1'),
        (2, '星耀2'),
        (3, '星耀3'),
    ))
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField()

