# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-15 06:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parliament', '0006_auto_20160518_1506'),
        ('document', '0004_voting_is_dossier_voting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='party',
        ),
        migrations.CreateModel(
            name='VoteIndividual',
            fields=[
                ('vote_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='document.Vote')),
                ('parliament_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parliament.ParliamentMember')),
            ],
            bases=('document.vote',),
        ),
        migrations.CreateModel(
            name='VoteParty',
            fields=[
                ('vote_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='document.Vote')),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parliament.PoliticalParty')),
            ],
            bases=('document.vote',),
        ),
    ]