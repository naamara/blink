# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_create_health_user_date_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='create_health_user',
            name='info',
            field=models.CharField(max_length=900, blank=True),
        ),
    ]
