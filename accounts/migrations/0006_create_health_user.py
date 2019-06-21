# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20161017_1220'),
    ]

    operations = [
        migrations.CreateModel(
            name='Create_Health_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50, blank=True)),
                ('email', models.CharField(max_length=50, blank=True)),
                ('cat_name', models.CharField(max_length=50, blank=True)),
                ('doct_name', models.CharField(max_length=50, blank=True)),
                ('speciality', models.CharField(max_length=100, blank=True)),
                ('password', models.CharField(max_length=100, blank=True)),
                ('category', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('password2', models.CharField(max_length=50, blank=True)),
                ('region', models.CharField(max_length=50, blank=True)),
                ('districts', models.CharField(max_length=50, blank=True)),
            ],
        ),
    ]
