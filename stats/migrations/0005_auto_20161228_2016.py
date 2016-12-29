# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 19:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20161228_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partyvotebehaviour',
            name='submitter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='party_vote_behaviour_submitter', to='parliament.PoliticalParty'),
        ),
        migrations.AlterField(
            model_name='partyvotebehaviour',
            name='voting_type',
            field=models.CharField(choices=[('BILL', 'Wetsvoorstel'), ('OTHER', 'Overig (Motie, Amendement)')], default='OTHER', max_length=5),
            preserve_default=False,
        ),
    ]
