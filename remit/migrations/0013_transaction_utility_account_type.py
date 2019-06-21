# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0012_charge_bill_minimum_ugx'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='utility_account_type',
            field=models.CharField(default=False, max_length=230, blank=True),
        ),
    ]
