# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='id_expiry',
            field=models.CharField(default=1, max_length=30, blank=True),
            preserve_default=False,
        ),
     
        migrations.AddField(
            model_name='profile',
            name='id_scan_ref',
            field=models.CharField(default=1, max_length=50, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='id_scanned',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='id_type',
            field=models.CharField(default=1, max_length=30, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='id_verify_ref',
            field=models.CharField(default=1, max_length=50, blank=True),
            preserve_default=False,
        ),
       
        migrations.AddField(
            model_name='profile',
            name='send_country_code',
            field=models.CharField(default=b'256', max_length=10),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_attempts',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
