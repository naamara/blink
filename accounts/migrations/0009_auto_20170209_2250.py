# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_create_health_user_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='create_health_user',
            name='category',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
