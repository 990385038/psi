# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-13 02:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0003_checkorder_create_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkorderdetail',
            name='create_time',
        ),
    ]
