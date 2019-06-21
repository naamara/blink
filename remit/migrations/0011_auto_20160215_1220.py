# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0010_transaction_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='bill_transfer_minimum_ugx',
            field=models.DecimalField(default=5000.0, max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='utility_account_name',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
    ]
