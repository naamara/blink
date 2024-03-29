# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0008_wallettransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='current_balance',
            field=models.DecimalField(default=0.0, max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
