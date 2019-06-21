# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_create_health_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='create_health_user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
