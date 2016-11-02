# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-31 15:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0014_besluitenlijst_besluititem_besluititemcase'),
    ]

    operations = [
        migrations.AddField(
            model_name='besluititem',
            name='besluiten_lijst',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='document.BesluitenLijst'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='besluititemcase',
            name='besluit_item',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='document.BesluitItem'),
            preserve_default=False,
        ),
    ]