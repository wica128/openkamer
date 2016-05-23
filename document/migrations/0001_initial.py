# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 12:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_id', models.CharField(blank=True, max_length=200)),
                ('title_full', models.CharField(max_length=500)),
                ('title_short', models.CharField(max_length=200)),
                ('publication_type', models.CharField(max_length=200)),
                ('submitter', models.CharField(max_length=200)),
                ('category', models.CharField(max_length=200)),
                ('publisher', models.CharField(max_length=200)),
                ('date_published', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date_published'],
            },
        ),
        migrations.CreateModel(
            name='Dossier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dossier_id', models.CharField(blank=True, max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Kamerstuk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_main', models.CharField(blank=True, max_length=40)),
                ('id_sub', models.CharField(blank=True, max_length=40)),
                ('type_short', models.CharField(blank=True, max_length=40)),
                ('type_long', models.CharField(blank=True, max_length=100)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.Document')),
            ],
            options={
                'verbose_name_plural': 'Kamerstukken',
                'ordering': ['id_sub'],
            },
        ),
        migrations.AddField(
            model_name='document',
            name='dossier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='document.Dossier'),
        ),
    ]