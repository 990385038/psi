# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-13 02:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20190313_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkorder',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
