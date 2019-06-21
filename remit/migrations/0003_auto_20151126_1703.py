# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0002_auto_20151120_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonebook',
            name='utility',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='referencenumber',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='utility',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
