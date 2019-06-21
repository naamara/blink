# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remit', '0016_auto_20160728_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='location',
            field=models.CharField(default=False, max_length=300, blank=True),
        ),
    ]
