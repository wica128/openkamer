# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-19 11:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Government',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date_formed', models.DateField()),
                ('wikidata_id', models.CharField(blank=True, max_length=200)),
            ],
        ),
    ]
