# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-15 06:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20160915_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='decision',
            field=models.CharField(choices=[('FO', 'For'), ('AG', 'Against'), ('NO', 'None'), ('MI', 'Mistake')], max_length=2),
        ),
    ]
