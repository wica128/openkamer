# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-08 18:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0040_auto_20170308_1808'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='footnote',
            options={'ordering': ['nr']},
        ),
    ]
