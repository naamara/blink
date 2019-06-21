# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0011_auto_20160215_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='bill_minimum_ugx',
            field=models.DecimalField(default=5000.0, max_digits=10, decimal_places=2),
        ),
    ]
