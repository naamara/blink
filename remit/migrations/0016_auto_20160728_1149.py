# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0015_transaction_utility_pegpay_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='utility_pegpay_id',
            field=models.CharField(default=b'0', max_length=230, blank=True),
        ),
    ]
