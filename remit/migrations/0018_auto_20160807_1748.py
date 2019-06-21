# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0017_transaction_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='location',
            field=models.CharField(default=False, max_length=600, blank=True),
        ),
    ]
