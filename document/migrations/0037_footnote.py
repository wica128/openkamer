# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-08 10:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0036_auto_20170308_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='FootNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nr', models.IntegerField()),
                ('text', models.CharField(blank=True, max_length=1000)),
                ('url', models.URLField(blank=True, max_length=1000)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.Document')),
            ],
        ),
    ]