# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parliament', '0003_auto_20161126_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='politicalparty',
            name='current_parliament_seats',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]