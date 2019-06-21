# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0003_auto_20151126_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='billtype',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
    ]
