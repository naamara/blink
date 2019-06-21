# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0013_transaction_utility_account_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='utility_receipt_id',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
    ]
