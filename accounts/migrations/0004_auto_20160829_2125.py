# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20160314_0828'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='signup_location',
            field=models.CharField(default=False, max_length=600, blank=True),
        ),
    ]
