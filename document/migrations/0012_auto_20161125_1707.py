# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 16:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0011_auto_20161125_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendaitem',
            name='item_text',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='kamerstuk',
            name='type_long',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='kamerstuk',
            name='type_short',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
