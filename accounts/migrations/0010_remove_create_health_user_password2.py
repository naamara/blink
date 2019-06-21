# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20170209_2250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='create_health_user',
            name='password2',
        ),
    ]
