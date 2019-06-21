# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0014_transaction_utility_receipt_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='utility_pegpay_id',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
    ]
