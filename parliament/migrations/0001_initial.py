# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-15 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parliament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('wikidata_id', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ParliamentMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined', models.DateField(blank=True, null=True)),
                ('left', models.DateField(blank=True, null=True)),
                ('parliament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parliament.Parliament')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PartyMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined', models.DateField(blank=True, null=True)),
                ('left', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PoliticalParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_short', models.CharField(max_length=10)),
                ('founded', models.DateField(blank=True, null=True)),
                ('dissolved', models.DateField(blank=True, null=True)),
                ('wikidata_id', models.CharField(blank=True, max_length=200)),
                ('wikimedia_logo_url', models.URLField(blank=True)),
                ('wikipedia_url', models.URLField(blank=True)),
                ('official_website_url', models.URLField(blank=True)),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'verbose_name_plural': 'Political parties',
            },
        ),
        migrations.AddField(
            model_name='partymember',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parliament.PoliticalParty'),
        ),
        migrations.AddField(
            model_name='partymember',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partymember', to='person.Person'),
        ),
    ]